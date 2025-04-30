# AI Health Coach

A personalized wellness and lifestyle assistant powered by AI.

## Overview
The AI Health Coach helps users maintain health routines by:
- Collecting user profiles (age, weight, activity level, dietary preferences).
- Providing daily personalized meal and exercise plans.
- Offering motivational messages and health tips using OpenAI's GPT and RAG.

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: FastAPI, MongoDB
- **LLM**: OpenAI GPT-3.5-turbo
- **RAG**: LangChain with FAISS

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-health-coach.git 


uvicorn main:app --reload used to run backend
streamlit run app.py used to run frontend