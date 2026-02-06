import os
import time
import traceback
from fastapi import FastAPI
from nicegui import app as nicegui_app, ui, events, run
from src.engine import LandmarkEngine 
from starlette.formparsers import MultiPartParser
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlShutdown

# --- 1. CONFIGURATION ---
MultiPartParser.max_file_size = 1024 * 1024 * 100  
MultiPartParser.spool_max_size = 1024 * 1024 * 100  

os.environ["TF_USE_LEGACY_KERAS"] = "1"
app = nicegui_app

MODEL_PATH = './models/landmark_model.h5'
CLASS_NAMES = ["Burj Khalifa", "Eiffel Tower", "Red Fort", "Taj Mahal", "Great Wall of China"]

ai_guide = LandmarkEngine(MODEL_PATH, CLASS_NAMES)

@ui.page('/')
def main():
    ui.colors(primary='#385261')
    with ui.header().classes('bg-primary q-pa-md'):
        ui.label('🌍 Smart Landmark AI Guide').classes('text-white text-h4 font-bold')
        ui.label('Powered by Gemini 2.5 Pro (Tier 1)').classes('text-white text-subtitle2')

    with ui.column().classes('w-full max-w-2xl mx-auto q-pa-md mt-10 gap-6'):
        
        vram_status = ui.label('GPU VRAM: Monitoring...').classes('text-caption text-grey-6')
        analysis_progress = ui.linear_progress(value=0, show_value=False).props('instant-feedback color="secondary"')
        analysis_progress.set_visibility(False)

        result_card = ui.card().classes('w-full bg-white q-pa-xl shadow-2xl rounded-lg flex flex-col items-center')
        with result_card:
            res_label = ui.label('Ready for Upload').classes('text-h5 font-bold text-primary mb-2')
            history_md = ui.markdown('Upload a photo to begin analysis.').classes('text-body1 text-grey-8')
            
            with ui.row().classes('q-mt-md'):
                # --- FIX: Split creation and disabling to avoid NoneType Error ---
                predict_btn = ui.button("Predict Landmark").classes('primary')
                predict_btn.disable() 
                
                info_btn = ui.button("More Info").classes('secondary')
                info_btn.disable()
            
            lang_sel = ui.select(["English", "Hindi"], value="English", label="Language")

        state = {'name': None, 'en': "Waiting for image...", 'hi': "छवि की प्रतीक्षा है..."}

        def update_ui():
            res_label.set_text(f"📍 {state['name'] if state['name'] else 'Unknown'}")
            history_md.set_content(state['hi'] if lang_sel.value == "Hindi" else state['en'])

        # Now these will work because buttons are not None
        predict_btn.on('click', update_ui)
        info_btn.on('click', update_ui)

        async def process_file(e: events.UploadEventArguments):
            analysis_progress.set_visibility(True)
            analysis_progress.set_value(0.1)
            n = ui.notification('Reading Image Data...', spinner=True, timeout=None)
            
            try:
                start = time.perf_counter()
                
                img_data = e.file.read()
                if hasattr(img_data, '__await__'):
                    img_data = await img_data
                
                if not img_data:
                    raise ValueError("File is empty or could not be read.")

                n.message = "Analyzing with Local CNN..."
                analysis_progress.set_value(0.3)
                name, conf = await run.io_bound(ai_guide.predict, img_data)
                
                if name == "Uncertain":
                    n.message = "CNN Uncertain. Asking Gemini Pro..."
                    analysis_progress.set_value(0.6)
                    api_result = await run.io_bound(ai_guide.predict_with_vision, img_data)
                    
                    state['name'] = api_result.get('name', 'Unknown')
                    state['en'] = api_result.get('english', 'No info found.')
                    state['hi'] = api_result.get('hindi', 'जानकारी नहीं मिली।')
                else:
                    state['name'] = name
                    n.message = "Fetching expert history..."
                    info = await run.io_bound(ai_guide.get_expert_response, name)
                    state['en'] = info
                    state['hi'] = "Translation available via Vision mode."

                analysis_progress.set_value(1.0)
                predict_btn.enable()
                info_btn.enable()
                update_ui() 
                
                n.message = f'Complete! ({time.perf_counter()-start:.2f}s)'
                n.spinner = False
                n.icon = 'check_circle'
                ui.timer(3.0, n.dismiss, once=True)

            except Exception as ex:
                print(f"CRASH LOG: {traceback.format_exc()}")
                ui.notify(f"Error: {str(ex)}", type='negative', duration=10)
                n.dismiss()
            finally:
                ui.timer(1.0, lambda: analysis_progress.set_visibility(False), once=True)

        ui.upload(on_upload=process_file, auto_upload=True, label="Upload Photo").classes('w-full')

        def _update_stats():
            try:
                nvmlInit()
                handle = nvmlDeviceGetHandleByIndex(0)
                info = nvmlDeviceGetMemoryInfo(handle)
                vram_status.set_text(f"RTX 5050 VRAM: {info.used/1024**3:.2f}GB / {info.total/1024**3:.2f}GB")
                nvmlShutdown()
            except: 
                vram_status.set_text("VRAM: Offline")
        
        ui.timer(2.0, _update_stats)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Gemini Landmark Guide", host='127.0.0.1', port=8000, reconnect_timeout=60, reload=False)