import os
import time
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import pynvml
from sqlmodel import SQLModel, Field, create_engine, Session, select

# Import your local engine
from src.engine import LandmarkEngine

# 1. Configuration & Database Setup
load_dotenv()
app = FastAPI(title="Landmark.AI Hybrid API")

# Pro-Tip: Ensure your DATABASE_URL in .env matches your PostgreSQL credentials
# Format: postgresql://username:password@localhost:5432/landmark_db
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Aakarsh@localhost:5432/landmark_db")
engine_db = create_engine(DATABASE_URL, echo=False) # Set echo=True during development to see SQL logs

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SQLModel: Database Table Definition
# This model acts as both the database table schema and the data validation layer
class LandmarkHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True) # index=True speeds up history lookups by name
    english_info: str
    hindi_info: str
    confidence: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper to initialize tables
def create_db_and_tables():
    """Initializes the PostgreSQL database tables on startup."""
    SQLModel.metadata.create_all(engine_db)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Dependency for database sessions
def get_session():
    """Provides a database session for each request."""
    with Session(engine_db) as session:
        yield session

# Constants for AI Engine
MODEL_PATH = "models/landmark_model.h5"
CLASSES = ["Burj Khalifa", "Eiffel Tower", "Red Fort", "Taj Mahal", "Great Wall of China"]
engine = LandmarkEngine(MODEL_PATH, CLASSES)

# 3. Data Models for API Responses
class VRAMStatus(BaseModel):
    gpu_name: str
    total_mhz: float
    used_mhz: float
    free_mhz: float
    usage_percent: float

# 4. API Endpoints

@app.get("/vram", response_model=VRAMStatus)
async def get_vram_status():
    """Checks the real-time VRAM status of your RTX 5050."""
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        name = pynvml.nvmlDeviceGetName(handle)
        pynvml.nvmlShutdown()
        
        return {
            "gpu_name": name,
            "total_mhz": info.total / 1024**2,
            "used_mhz": info.used / 1024**2,
            "free_mhz": info.free / 1024**2,
            "usage_percent": (info.used / info.total) * 100
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPU Monitoring Failed: {str(e)}")

@app.post("/predict")
async def predict_landmark(
    file: UploadFile = File(...), 
    session: Session = Depends(get_session)
):
    """Processes an image and saves the identification to PostgreSQL."""
    try:
        # 1. Image Reading
        image_bytes = await file.read()
        
        # 2. Identification Logic (Hybrid Engine)
        name, conf = engine.predict(image_bytes)
        
        if name == "Uncertain":
            # Fallback to Cloud Vision for unidentified landmarks
            result = engine.predict_with_vision(image_bytes)
        else:
            # Local CNN results + Bilingual Knowledge Retrieval
            raw_history = engine.get_expert_response(name)
            en_part, hi_part = "Info not found.", "जानकारी उपलब्ध नहीं है।"
            
            if "[ENGLISH]" in raw_history:
                en_part = raw_history.split("[ENGLISH]")[1].split("[HINDI]")[0].strip()
            if "[HINDI]" in raw_history:
                hi_part = raw_history.split("[HINDI]")[1].strip()
                
            result = {"name": name, "english": en_part, "hindi": hi_part}

        # 3. Database Logging
        history_entry = LandmarkHistory(
            name=result["name"],
            english_info=result["english"],
            hindi_info=result["hindi"],
            confidence=conf
        )
        session.add(history_entry)
        session.commit()
        session.refresh(history_entry)

        return result
    except Exception as e:
        # Pro-Tip: Never return raw system errors; always use HTTPException for security
        raise HTTPException(status_code=500, detail=f"Landmark Prediction Failed: {str(e)}")

@app.get("/history", response_model=List[LandmarkHistory])
async def get_search_history(session: Session = Depends(get_session)):
    """Retrieves the full scan history from the PostgreSQL database."""
    try:
        statement = select(LandmarkHistory).order_by(LandmarkHistory.created_at.desc())
        results = session.exec(statement).all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not retrieve history from database.")

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 allows access from any network device; set to 127.0.0.1 for local only
    uvicorn.run(app, host="0.0.0.0", port=8000)