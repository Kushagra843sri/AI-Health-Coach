from fastapi import FastAPI, HTTPException
from model import User, DailyLog
from rag import initialize_rag, get_health_tip
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from bson import ObjectId
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

try:
    # MongoDB connection
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["health_coach"]
    users_collection = db["users"]
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

try:
    # Initialize RAG
    qa_chain = initialize_rag()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("Initialized RAG and LLM")
except Exception as e:
    logger.error(f"Failed to initialize RAG/LLM: {e}")
    raise

def serialize_mongo_document(doc):
    """Convert MongoDB document to JSON-serializable format."""
    if isinstance(doc, dict):
        return {k: serialize_mongo_document(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongo_document(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc

@app.post("/profile")
async def create_profile(user: User):
    try:
        user_dict = user.dict()
        result = users_collection.insert_one(user_dict)
        # Create response with serialized ID
        response = {
            "id": str(result.inserted_id),
            **user_dict
        }
        logger.info(f"Created profile for {user_dict['name']}")
        return serialize_mongo_document(response)
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to create profile")

@app.post("/daily/{user_id}")
async def add_daily_log(user_id: str, log: DailyLog):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate plan using LLM
        prompt = f"""
        User profile: age {user['age']}, weight {user['weight']}kg, activity {user['activity_level']}, dietary {user['dietary_preference']}.
        Daily input: Food: {log.food}, Mood: {log.mood}, Energy: {log.energy}/10, Sleep: {log.sleep} hours.
        Suggest a meal, exercise, and motivational message. Respond in this format:
        Meal: [Your suggestion]
        Exercise: [Your suggestion]
        Motivation: [Your message]
        """
        response = llm.invoke(prompt)
        plan = {
            "meal": response.content.split("Meal:")[1].split("\n")[0].strip() if "Meal:" in response.content else "Not provided",
            "exercise": response.content.split("Exercise:")[1].split("\n")[0].strip() if "Exercise:" in response.content else "Not provided",
            "motivation": response.content.split("Motivation:")[1].strip() if "Motivation:" in response.content else "Not provided"
        }
        
        # Get health tip using RAG
        health_tip = get_health_tip(f"Health tip for {log.mood} mood and {log.energy} energy", qa_chain)
        
        log_dict = log.dict()
        log_dict["plan"] = plan
        log_dict["health_tip"] = health_tip
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"daily_logs": log_dict}}
        )
        logger.info(f"Added daily log for user {user_id}")
        return serialize_mongo_document(log_dict)
    except Exception as e:
        logger.error(f"Error adding daily log: {e}")
        raise HTTPException(status_code=500, detail="Failed to add daily log")