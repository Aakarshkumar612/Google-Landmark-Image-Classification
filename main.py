import os
from fastapi import FastAPI
from nicegui import ui
from dotenv import load_dotenv
from src.engine import LandmarkEngine  # Import your new Brain

# 1. Load Secrets and Config
load_dotenv() # This automatically reads your .env file
app = FastAPI()

# 2. Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'landmark_model.h5')
CLASS_NAMES = ["Eiffel Tower", "Taj Mahal", "Statue of Liberty"]

# 3. Initialize the AI Engine
# We wrap this in a try/except so the server tells us EXACTLY what is wrong
try:
    ai_guide = LandmarkEngine(MODEL_PATH, CLASS_NAMES)
    print("✅ Pro Engine Started Successfully")
except Exception as e:
    print(f"❌ Startup Error: {e}")
    ai_guide = None

# --- FRONTEND ---
@ui.page('/')
def index():
    ui.colors(primary='#385261')
    ui.label('🌍 Landmark AI Guide').classes('text-h3 text-center w-full q-pa-md')
    
    with ui.card().classes('w-full max-w-xl mx-auto q-pa-lg shadow-10'):
        # Placeholders
        result_label = ui.label('').classes('text-h5 text-primary')
        history_label = ui.label('').classes('text-body1 italic text-gray-600')

        async def handle_upload(e):
            if not ai_guide:
                ui.notify('Engine not loaded. Check terminal.', type='negative')
                return
            
            # Show a loading spinner so the user knows it's working
            with result_label:
                ui.spinner(size='lg')
            
            # Execute the AI logic from engine.py
            data = await ai_guide.get_landmark_info(e.content)
            
            # Update the UI with results
            result_label.set_text(f"Result: {data['name']} ({data['confidence']}%)")
            history_label.set_text(data['history'])

        ui.upload(on_upload=handle_upload, auto_upload=True, label="Upload Landmark Photo").classes('w-full')

ui.run_with(app)