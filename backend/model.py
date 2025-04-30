from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel
import os

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))  # Replace with env variable in main.py
db = client["health_coach"]
users_collection = db["users"]

# Pydantic models for validation
class DailyLog(BaseModel):
    date: datetime = datetime.now()
    food: str
    mood: str
    energy: int
    sleep: float
    plan: Dict[str, str] = {}

class User(BaseModel):
    name: str
    age: int
    weight: float
    activity_level: str
    dietary_preference: str
    goals: List[str]
    daily_logs: List[DailyLog] = []