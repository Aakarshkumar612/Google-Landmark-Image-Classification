import os
import io
import tensorflow as tf
import numpy as np
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Environment Variables (API Key)
load_dotenv()

# Ensure legacy Keras behavior for older models
os.environ.setdefault('TF_USE_LEGACY_KERAS', '1')

class LandmarkEngine:
    def __init__(self, model_path, class_names):
        # --- LOCAL CNN SETUP (Unchanged) ---
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception:
            # Fallback for Keras version mismatches
            from tensorflow.keras import layers, utils
            class DepthwiseConv2DShim(layers.DepthwiseConv2D):
                def __init__(self, *args, **kwargs):
                    kwargs.pop('groups', None)
                    super().__init__(*args, **kwargs)
            utils.get_custom_objects()['DepthwiseConv2D'] = DepthwiseConv2DShim
            self.model = tf.keras.models.load_model(model_path)
        
        self.class_names = class_names
        self.img_size = (224, 224) 

        # --- GEMINI CLOUD SETUP (The Update) ---
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("CRITICAL WARNING: GEMINI_API_KEY is missing from .env file!")
        
        genai.configure(api_key=api_key)
        # Initialize Gemini 2.5 Pro
        self.gemini = genai.GenerativeModel('gemini-2.5-pro')

    def _normalize_image(self, data):
        """
        Universal Converter: Turns any image (PNG, WebP, HEIC) 
        into RGB JPEG bytes for model safety.
        """
        try:
            with Image.open(io.BytesIO(data)) as img:
                img = img.convert('RGB')
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                return buf.getvalue()
        except Exception as e:
            print(f"Image Error: {e}")
            return data

    def predict(self, image_bytes, threshold=0.90):
        """
        Stage 1: Local CNN Prediction (Fast & Free).
        """
        clean_bytes = self._normalize_image(image_bytes)
        img = Image.open(io.BytesIO(clean_bytes)).resize(self.img_size)
        img_array = tf.keras.utils.img_to_array(img) / 255.0
        
        preds = self.model.predict(tf.expand_dims(img_array, 0), verbose=0)
        idx = np.argmax(preds[0])
        conf = float(preds[0][idx])
        
        return (self.class_names[idx], conf) if conf >= threshold else ("Uncertain", conf)

    def predict_with_vision(self, image_bytes):
        """
        Stage 2: Gemini 2.5 Pro Vision.
        Note: This is a synchronous 'def' so 'run.io_bound' in main.py works correctly.
        """
        try:
            # Prepare image for Gemini
            clean_bytes = self._normalize_image(image_bytes)
            img = Image.open(io.BytesIO(clean_bytes))
            
            prompt = (
                "Identify this landmark precisely. Mention architectural style and history. "
                "Format output exactly like this:\n"
                "NAME: [Landmark Name]\n"
                "ENGLISH_START\n[Detailed history in English]\nENGLISH_END\n"
                "HINDI_START\n[Detailed history in Hindi]\nHINDI_END"
            )

            # Call Gemini API
            response = self.gemini.generate_content([prompt, img])
            out = response.text
            
            # Robust Parsing Logic
            name = "Unknown"
            if "NAME:" in out:
                name = out.split("NAME:")[1].split("\n")[0].strip()

            en_info = "No info."
            if "ENGLISH_START" in out:
                en_info = out.split("ENGLISH_START")[1].split("ENGLISH_END")[0].strip()

            hi_info = "जानकारी नहीं।"
            if "HINDI_START" in out:
                hi_info = out.split("HINDI_START")[1].split("HINDI_END")[0].strip()
            
            return {
                "name": name,
                "english": en_info,
                "hindi": hi_info
            }
        except Exception as e:
            return {
                "name": "API Error", 
                "english": f"Gemini Error: {e}", 
                "hindi": f"त्रुटि: {e}"
            }

    def get_expert_response(self, name):
        """Retrieves history via Gemini Text Generation."""
        prompt = f"Provide a detailed history of {name} in English and Hindi. Use [ENGLISH] and [HINDI] markers."
        try:
            response = self.gemini.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"