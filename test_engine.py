# test_engine.py

import asyncio
import os
from dotenv import load_dotenv
from src.engine import LandmarkEngine

# Load your secret key
load_dotenv()

async def test():
    MODEL_PATH = "models/landmark_model.h5"
    CLASSES = ["Eiffel Tower", "Taj Mahal", "Statue of Liberty", "Burj Khalifa", "Red Fort", "The GreatWall Of China"]
    TEST_IMAGE_PATH = "test_images/taj.jpg"  # Change to any test image you want

    print("🔍 Testing AI Engine...")
    ai = LandmarkEngine(MODEL_PATH, CLASSES)
    print("✅ Engine Initialized Successfully!")
    print(f"Gemini Key Found: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'No'}")

    # Test prediction on a real image
    try:
        with open(TEST_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
        label, confidence = ai.predict(image_bytes)
        print(f"Prediction: {label} (Confidence: {confidence:.2f})")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())