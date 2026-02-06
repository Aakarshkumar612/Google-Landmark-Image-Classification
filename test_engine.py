# test_engine.py

import asyncio
import os
import time
from dotenv import load_dotenv
from src.engine import LandmarkEngine

# Load GEMINI_API_KEY from .env
load_dotenv()

async def test():
    # --- CONFIGURATION ---
    MODEL_PATH = "models/landmark_model.h5"
    CLASSES = ["Burj Khalifa", "Eiffel Tower", "Red Fort", "Taj Mahal", "Great Wall of China"]
    # Ensure this image exists in your test_images folder
    TEST_IMAGE_PATH = "test_images/taj.jpg" 

    print("🚀 [1/4] INITIALIZING PROFESSIONAL ENGINE...")
    try:
        ai = LandmarkEngine(MODEL_PATH, CLASSES)
        print("✅ Engine Initialized Successfully!")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return

    # Check for API Key
    api_key = os.environ.get('GEMINI_API_KEY')
    print(f"🔑 Gemini API Key Found: {'Yes' if api_key else 'NO (Check your .env file)'}")

    # --- TEST 1: LOCAL CNN PREDICTION ---
    print(f"\n📸 [2/4] TESTING LOCAL CNN (Stage 1)...")
    try:
        with open(TEST_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
        
        start_time = time.perf_counter()
        label, confidence = ai.predict(image_bytes)
        latency = time.perf_counter() - start_time
        
        print(f"📍 CNN Result: {label} ({confidence:.2f})")
        print(f"⏱️ Local Latency: {latency:.4f}s")
    except Exception as e:
        print(f"❌ Local Prediction failed: {e}")

    # --- TEST 2: GEMINI CLOUD VISION ---
    print(f"\n☁️ [3/4] TESTING GEMINI 2.5 PRO CLOUD (Stage 2)...")
    if not api_key:
        print("⏭️ Skipping Cloud Test: No API Key.")
    else:
        try:
            start_time = time.perf_counter()
            # Calling the method we updated in engine.py
            result = await ai.predict_with_vision(image_bytes)
            latency = time.perf_counter() - start_time

            print(f"✅ Gemini Response Received in {latency:.2f}s")
            print(f"📝 Identified Name: {result.get('name')}")
            print(f"🇬🇧 English Preview: {result.get('english')[:70]}...")
            print(f"🇮🇳 Hindi Preview: {result.get('hindi')[:70]}...")
        except Exception as e:
            print(f"❌ Gemini API call failed: {e}")

    # --- TEST 3: VRAM USAGE ---
    print(f"\n📊 [4/4] RESOURCE CHECK...")
    # This will help verify that the Gemini call didn't spike your VRAM
    print("💡 Tip: Check your RTX 5050 usage now. It should be stable (~1GB).")

if __name__ == "__main__":
    # Ensure any previous event loops are closed before running
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass