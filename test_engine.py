# test_engine.py
import asyncio
import os
from dotenv import load_dotenv
from src.engine import LandmarkAI

# Load your secret key
load_dotenv()

async def test():
    # Update these to your real paths
    MODEL_PATH = "models/landmark_model.h5"
    CLASSES = ["Eiffel Tower", "Taj Mahal", "Statue of Liberty"]
    
    print("🔍 Testing AI Engine...")
    ai = LandmarkAI(MODEL_PATH, CLASSES)
    
    # Test with any image bytes (even empty for a quick path check)
    print("✅ Engine Initialized Successfully!")
    print(f"Gemini Key Found: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'No'}")

if __name__ == "__main__":
    asyncio.run(test())