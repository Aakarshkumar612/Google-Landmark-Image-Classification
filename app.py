import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
import pynvml
from sqlmodel import SQLModel, Field, create_engine, Session, select

from src.engine import LandmarkEngine


import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os
from contextlib import asynccontextmanager
# ... rest of your imports

# 1. Environment & AI Configuration
# find_dotenv() ensures we locate the .env regardless of where uvicorn is called
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

GEMINI_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    print(f"✅ ENGINE SECURE: Gemini configured with key {GEMINI_KEY[:5]}...")
else:
    print("❌ CRITICAL: No API Key found in environment variables.")

# 2. Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Aakarsh@localhost:5432/landmark_db")
engine_db = create_engine(DATABASE_URL, echo=False)

class LandmarkHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    english_info: str
    hindi_info: str
    confidence: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Modern Lifespan Handler (Replaces @app.on_event("startup"))
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    SQLModel.metadata.create_all(engine_db)
    yield

# 3. FastAPI App Initialization
app = FastAPI(title="Landmark.AI Hybrid API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_session():
    with Session(engine_db) as session:
        yield session

# Initialize Global AI Engine
MODEL_PATH = "models/landmark_model.h5"
CLASSES = ["Burj Khalifa", "Eiffel Tower", "Red Fort", "Taj Mahal", "Great Wall of China"]
engine = LandmarkEngine(MODEL_PATH, CLASSES)

class VRAMStatus(BaseModel):
    gpu_name: str
    usage_percent: float

# 4. API Endpoints

@app.get("/vram", response_model=VRAMStatus)
async def get_vram_status():
    return {
        "gpu_name": "NVIDIA GPU (Monitoring Offline)",
        "usage_percent": 0.0
    }

@app.post("/predict")
async def predict_landmark(file: UploadFile = File(...), session: Session = Depends(get_session)):
    try:
        # Re-verify configuration to prevent ADC/API Key errors during long sessions
        if GEMINI_KEY:
            genai.configure(api_key=GEMINI_KEY)

        image_bytes = await file.read()
        name, conf = engine.predict(image_bytes)
        
        # Hybrid Logic: Local CNN -> Gemini Vision Fallback
        if name == "Uncertain" or float(conf) < 0.6:
            result = engine.predict_with_vision(image_bytes)
        else:
            raw_history = engine.get_expert_response(name)
            en_part, hi_part = "Info not found.", "जानकारी उपलब्ध नहीं है।"
            
            if "[ENGLISH]" in raw_history:
                en_part = raw_history.split("[ENGLISH]")[1].split("[HINDI]")[0].strip()
            if "[HINDI]" in raw_history:
                hi_part = raw_history.split("[HINDI]")[1].strip()
                
            result = {"name": name, "english": en_part, "hindi": hi_part}

        # SQL Logging
        history_entry = LandmarkHistory(
            name=result["name"],
            english_info=result["english"],
            hindi_info=result["hindi"],
            confidence=float(conf)
        )
        session.add(history_entry)
        session.commit()
        session.refresh(history_entry)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Failed: {str(e)}")

@app.get("/history", response_model=List[LandmarkHistory])
async def get_search_history(session: Session = Depends(get_session)):
    try:
        statement = select(LandmarkHistory).order_by(LandmarkHistory.created_at.desc())
        results = session.exec(statement).all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database Retrieval Failed.")

if __name__ == "__main__":
    import uvicorn
    # Bind to 0.0.0.0 for external network accessibility (mobile/demo)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)