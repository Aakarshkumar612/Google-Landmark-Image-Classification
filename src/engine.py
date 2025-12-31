import os
import io
import numpy as np
import tensorflow as tf
from PIL import Image
from google import genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class LandmarkEngine:
    def __init__(self, model_path, class_names):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
            
        self.model = tf.keras.models.load_model(model_path)
        self.class_names = class_names
        
        # Pull key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
            
        self.client = genai.Client(api_key=api_key)

    async def get_landmark_info(self, image_bytes):
        # Preprocess
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
        img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
        
        # Predict
        prediction = self.model.predict(img_array)[0]
        landmark = self.class_names[np.argmax(prediction)]
        confidence = float(np.max(prediction))

        # Gemini History
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Provide a 2-sentence fascinating history of {landmark}."
        )
        
        return {
            "name": landmark,
            "confidence": round(confidence * 100, 2),
            "history": response.text
        }