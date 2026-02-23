import os
import io
import tensorflow as tf
import numpy as np
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)

# Ensure legacy Keras behavior for older models
os.environ.setdefault('TF_USE_LEGACY_KERAS', '1')

# Hardcoded fallback — guarantees Gemini always works
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "AIzaSyDvTwGSlBAjhPhe3pblLvO_LA_Tu5LFQQs"
genai.configure(api_key=GEMINI_API_KEY)
print(f"✅ Gemini configured with key: {GEMINI_API_KEY[:8]}...")

class LandmarkEngine:
    def __init__(self, model_path, class_names):
        # --- LOCAL CNN SETUP ---
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception:
            from tensorflow.keras import layers, utils
            class DepthwiseConv2DShim(layers.DepthwiseConv2D):
                def __init__(self, *args, **kwargs):
                    kwargs.pop('groups', None)
                    super().__init__(*args, **kwargs)
            utils.get_custom_objects()['DepthwiseConv2D'] = DepthwiseConv2DShim
            self.model = tf.keras.models.load_model(model_path)
        
        self.class_names = class_names
        self.img_size = (224, 224)

        # --- GEMINI CLOUD SETUP ---
        self.gemini = genai.GenerativeModel('gemini-2.5-flash')

    def _normalize_image(self, data):
        """Standardizes images to RGB JPEG bytes to prevent processing errors."""
        try:
            with Image.open(io.BytesIO(data)) as img:
                img = img.convert('RGB')
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                return buf.getvalue()
        except Exception as e:
            print(f"Image Normalization Error: {e}")
            return data

    def predict(self, image_bytes, threshold=0.90):
        """Stage 1: Local CNN Prediction."""
        clean_bytes = self._normalize_image(image_bytes)
        img = Image.open(io.BytesIO(clean_bytes)).resize(self.img_size)
        img_array = tf.keras.utils.img_to_array(img) / 255.0
        
        preds = self.model.predict(tf.expand_dims(img_array, 0), verbose=0)
        idx = np.argmax(preds[0])
        conf = float(preds[0][idx])
        
        return (self.class_names[idx], conf) if conf >= threshold else ("Uncertain", conf)

    def predict_with_vision(self, image_bytes):
        """Stage 2: Gemini Vision Fallback."""
        try:
            clean_bytes = self._normalize_image(image_bytes)
            img = Image.open(io.BytesIO(clean_bytes))
            
            prompt = (
                "Identify this landmark precisely. Mention architectural style and history. "
                "Format output exactly like this:\n"
                "NAME: [Landmark Name]\n"
                "ENGLISH_START\n[Detailed history in English]\nENGLISH_END\n"
                "HINDI_START\n[Detailed history in Hindi]\nHINDI_END"
            )

            response = self.gemini.generate_content([prompt, img])
            out = response.text
            
            name = out.split("NAME:")[1].split("\n")[0].strip() if "NAME:" in out else "Unknown"
            en_info = out.split("ENGLISH_START")[1].split("ENGLISH_END")[0].strip() if "ENGLISH_START" in out else "No info."
            hi_info = out.split("HINDI_START")[1].split("HINDI_END")[0].strip() if "HINDI_START" in out else "जानकारी नहीं।"
            
            return {"name": name, "english": en_info, "hindi": hi_info}
        except Exception as e:
            return {"name": "API Error", "english": f"Gemini Error: {e}", "hindi": f"त्रुटि: {e}"}

    def get_expert_response(self, name):
        """Retrieves history via Gemini Text Generation."""
        prompt = f"Provide a detailed history of {name} in English and Hindi. Use [ENGLISH] and [HINDI] markers."
        try:
            response = self.gemini.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"