import os
import torch
from PIL import Image
from nicegui import ui

# 1. MODEL LOADING
# Ensure this path matches the folder on your GitHub
MODEL_PATH = 'models/landmark_model.pt'

# Load model safely on CPU (Render's free tier uses CPU)
device = torch.device('cpu')
model = torch.load(MODEL_PATH, map_location=device)
model.eval()

def predict(img_content):
    # Add your image preprocessing logic here (resize, normalize)
    # result = model(img)
    return "Eiffel Tower", 0.98

# 2. MODERN UI (NiceGUI - much more stable than Gradio)
@ui.page('/')
def main():
    ui.label('Google Landmark AI Classifier').classes('text-h4 text-center mt-4')
    
    with ui.card().classes('w-full max-w-lg mx-auto p-4 mt-8'):
        ui.markdown('Upload a photo to identify the landmark with high accuracy.')
        
        # File Upload component
        ui.upload(on_upload=lambda e: handle_upload(e), label='Select Image').classes('w-full')
        
        # Prediction Output
        result_label = ui.label('').classes('text-xl font-bold mt-4 text-primary')

    async def handle_upload(e):
        name, confidence = predict(e.content)
        result_label.set_text(f'Predicted: {name} ({confidence*100:.1f}%)')

# 3. RENDER CONFIGURATION
# Render provides the 'PORT' environment variable automatically
port = int(os.environ.get('PORT', 8080))
ui.run(port=port, title='Landmark AI', reload=False)