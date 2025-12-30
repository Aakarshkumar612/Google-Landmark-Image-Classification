import os
import io
import numpy as np
import tensorflow as tf
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from nicegui import app, ui
from google import genai

app = FastAPI()

# --- 1. DYNAMIC MODEL LOADING WITH DIAGNOSTICS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'landmark_model.h5')

model = None
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ SUCCESS: Deep Learning Model Loaded.")
    except Exception as e:
        print(f"❌ ERROR: Model exists but failed to load: {e}")
else:
    print(f"❌ ERROR: Model file NOT found at: {MODEL_PATH}")
    # Diagnostics: Let's see what folders DO exist
    print(f"Current Directory: {os.getcwd()}")
    print(f"Contents of BASE_DIR: {os.listdir(BASE_DIR)}")
    models_dir = os.path.join(BASE_DIR, 'models')
    if os.path.exists(models_dir):
        print(f"Contents of 'models' folder: {os.listdir(models_dir)}")
    else:
        print("The 'models' folder does not exist in the root directory.")

# --- 2. GENAI SETUP ---
# The client automatically uses the 'GEMINI_API_KEY' environment variable
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
CLASS_NAMES = ["Eiffel Tower", "Taj Mahal", "Statue of Liberty"] 

@ui.page('/')
def index_page():
    ui.label('🌍 Landmark AI Guide').classes('text-h4 text-center mt-4')
    
    with ui.card().classes('w-full max-w-lg mx-auto p-4'):
        result_label = ui.label('').classes('text-xl font-bold mt-4 text-primary')
        history_label = ui.label('').classes('text-gray-600 italic mt-2')

        async def handle_upload(e):
            if model is None:
                result_label.set_text("⚠️ Error: Model not loaded on server.")
                return

            try:
                result_label.set_text("Processing image...")
                
                # Preprocess image for the model
                img = Image.open(io.BytesIO(e.content)).convert('RGB').resize((224, 224))
                img_array = np.expand_dims(np.array(img), axis=0) / 255.0
                
                # Predict landmark
                prediction = model.predict(img_array)[0]
                landmark = CLASS_NAMES[np.argmax(prediction)]
                
                # Fetch history from Gemini GenAI
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=f"Tell me a fascinating 2-sentence history of {landmark}."
                )
                
                result_label.set_text(f"Predicted: {landmark}")
                history_label.set_text(response.text)
            except Exception as err:
                result_label.set_text(f"⚠️ Error: {str(err)}")
                print(f"Full Error Log: {err}")

        ui.upload(on_upload=handle_upload, label='Select Image', auto_upload=True).classes('w-full')

# Mount NiceGUI to FastAPI
ui.run_with(app, reconnect_timeout=10.0)