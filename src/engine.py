import os
import io
import pathlib
import base64
import tensorflow as tf
import numpy as np
import ollama
from PIL import Image

# Ensure legacy Keras behavior for loading older HDF5 models
os.environ.setdefault('TF_USE_LEGACY_KERAS', '1')

class LandmarkEngine:
    def __init__(self, model_path, class_names):
        # --- 1. VISION SETUP ---
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception:
            # Fallback shim for older/newer Keras layer config mismatches
            try:
                from tensorflow.keras import layers
                from tensorflow.keras.utils import get_custom_objects

                class DepthwiseConv2DShim(layers.DepthwiseConv2D):
                    def __init__(self, *args, **kwargs):
                        kwargs.pop('groups', None)
                        super().__init__(*args, **kwargs)

                get_custom_objects()['DepthwiseConv2D'] = DepthwiseConv2DShim
                self.model = tf.keras.models.load_model(model_path)
            except Exception as e:
                raise
        
        self.class_names = class_names
        self.img_size = (224, 224) 

        # --- 2. NLP SETUP ---
        self.llm = None
        self.embed_model = None
        self.index = None
        self.chat_engine = None
        self._llm_initialized = False

    def _init_llm_models(self):
        """Initialize LLM on-demand."""
        if self._llm_initialized:
            return
        self._llm_initialized = True

    def predict(self, image_bytes, threshold=0.90):
        """Fast Stage: CNN Prediction using the .h5 model."""
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize(self.img_size)
        img_array = tf.keras.utils.img_to_array(img) / 255.0
        
        predictions = self.model.predict(tf.expand_dims(img_array, 0), verbose=0)
        idx = np.argmax(predictions[0])
        confidence = float(predictions[0][idx])
        label = self.class_names[idx]

        return (label, confidence) if confidence >= threshold else ("Uncertain", confidence)

    async def predict_with_vision(self, image_bytes):
        """
        Advanced Stage: Bilingual Multimodal Identification.
        Method 2: Uses Base64 encoding to send raw image pixels to the LLM.
        """
        try:
            # Prepare image for Ollama API by encoding to Base64
            # This ensures the AI "sees" the pixels, not just the file name.
            img_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Professional historian prompt to minimize false-positive refusals
            prompt = (
                "You are an expert architectural historian. Look at the attached image pixels. "
                "Identify this landmark precisely. Mention specific visual details you see. "
                "Provide information in this exact format:\n"
                "NAME: [Landmark Name]\n"
                "ENGLISH_START\n[Detailed history in English]\nENGLISH_END\n"
                "HINDI_START\n[Detailed history in Hindi]\nHINDI_END"
            )

            # Call the Llama 3.2 Vision model via Ollama SDK
            response = ollama.generate(
                model='llama3.2-vision',
                prompt=prompt,
                images=[img_b64], # Sends the raw pixel data
                stream=False
            )
            
            output = response.get('response', '')
            
            # --- Parsing logic to separate bilingual features ---
            name = "Unknown Landmark"
            if "NAME:" in output:
                name = output.split("NAME:")[1].split("\n")[0].strip()
            
            en_info = "English info not available."
            if "ENGLISH_START" in output and "ENGLISH_END" in output:
                en_info = output.split("ENGLISH_START")[1].split("ENGLISH_END")[0].strip()
            
            hi_info = "हिंदी जानकारी उपलब्ध नहीं है।"
            if "HINDI_START" in output and "HINDI_END" in output:
                hi_info = output.split("HINDI_START")[1].split("HINDI_END")[0].strip()
            
            return {
                "name": name,
                "english": en_info,
                "hindi": hi_info
            }
        except Exception as e:
            return {
                "name": "Vision Error", 
                "english": f"Ollama Error: {e}", 
                "hindi": f"ओलामा त्रुटि: {e}"
            }

    def get_expert_response(self, landmark_name):
        """Retrieves history for known landmarks (CNN matches)."""
        try:
            data_dir = pathlib.Path('data')
            target = landmark_name.lower().replace(' ', '_')
            if data_dir.exists():
                for f in data_dir.glob('*.txt'):
                    if target in f.stem.lower():
                        return f.read_text(encoding='utf-8')
            
            # Fallback to LLM if local text file is missing
            prompt = (
                f"Provide a detailed history of {landmark_name}. Respond in this format:\n"
                "[ENGLISH] ... [HINDI] ..."
            )
            resp = ollama.generate(model='llama3.2-vision', prompt=prompt)
            return resp.get('response', 'Information not found.')
        except Exception as e:
            return f"Error: {e}"