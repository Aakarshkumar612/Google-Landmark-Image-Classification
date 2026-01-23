import os
import time
import io
from PIL import Image
from fastapi import FastAPI
from nicegui import app as nicegui_app, ui, events
from src.engine import LandmarkEngine 
from starlette.formparsers import MultiPartParser
import sys
import threading
import subprocess
import json
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlShutdown
import asyncio

def _log(msg):
    try:
        print(msg, flush=True)
    except Exception:
        pass
    try:
        with open('server_debug.log', 'a', encoding='utf-8') as fh:
            fh.write(str(msg) + '\n')
    except Exception:
        pass

# Force RAM spooling to fix 405/413 errors on Windows
MultiPartParser.max_file_size = 1024 * 1024 * 20 
MultiPartParser.spool_max_size = 1024 * 1024 * 20 

os.environ["TF_USE_LEGACY_KERAS"] = "1"
app = nicegui_app

# Initialization Logic
MODEL_PATH = './models/landmark_model.h5'
CLASS_NAMES = ["Burj Khalifa", "Eiffel Tower", "Red Fort", "Taj Mahal", "Great Wall of China"]
ai_guide = LandmarkEngine(MODEL_PATH, CLASS_NAMES)

ai_guide._llm_init_notified = False
ai_guide._llm_init_running = False

@ui.page('/')
def main():
    ui.colors(primary='#385261')
    with ui.header().classes('bg-primary q-pa-md'):
        ui.label('🌍 Smart Landmark AI Guide').classes('text-white text-h4 font-bold')
        ui.label('Using Hybrid Vision (CNN + Ollama LLM)').classes('text-white text-subtitle2')

    with ui.column().classes('w-full max-w-2xl mx-auto q-pa-md mt-10 gap-6'):
        
        # --- NEW: SYSTEM MONITORING SECTION ---
        vram_status = ui.label('GPU VRAM: Monitoring...').classes('text-caption text-grey-6')
        analysis_progress = ui.linear_progress(value=0, show_value=False).props('instant-feedback color="secondary"')
        analysis_progress.set_visibility(False)

        def _init_llm_in_thread():
            try:
                ai_guide._llm_init_running = True
                _log('LLM init started (background)')
                ai_guide._init_llm_models()
                _log('LLM init finished')
            finally:
                ai_guide._llm_init_running = False

        def start_llm_init():
            if ai_guide._llm_initialized or ai_guide._llm_init_running:
                ui.notify('LLM already initializing or initialized', timeout=3)
                return
            threading.Thread(target=_init_llm_in_thread, daemon=True).start()
            ui.notify('LLM initialization started in background.', timeout=3)

        ui.row().classes('w-full justify-end').style('margin-bottom: 8px')
        ui.button('Initialize AI Intelligence', on_click=lambda: start_llm_init()).classes('primary')
        
        status_row = ui.row().classes('items-center q-gutter-sm')
        with status_row:
            status_label = ui.label('System: Ready').classes('text-subtitle1')
            status_spinner = ui.spinner(size='md').style('display: none')
            ui.button('Show Logs', on_click=lambda: log_card.set_visibility(not log_card.visible)).classes('secondary')
            ui.button('Run Full Init', on_click=lambda: _run_full_init_subprocess()).classes('secondary')
            
        log_card = ui.card().classes('w-full bg-grey-50 q-pa-md').style('display: none; max-height: 320px; overflow: auto')
        with log_card:
            ui.label('System Debug Logs').classes('text-subtitle2')
            log_code = ui.code('', language='text').classes('w-full')

        result_card = ui.card().classes('w-full bg-white q-pa-xl shadow-2xl rounded-lg flex flex-col items-center').style('min-height: 180px;')
        with result_card:
            res_label = ui.label('').classes('text-h5 font-bold text-primary mb-2')
            history_md = ui.markdown('').classes('text-body1 text-grey-8')
            predict_btn = ui.button("Predict Landmark").classes('primary q-mt-md')
            predict_btn.disable()
            info_btn = ui.button("More Info").classes('secondary q-ml-md')
            info_btn.disable()
            
            lang_sel = ui.select(["English", "Hindi"], value="English", label="Choose Language", on_change=lambda: show_landmark_info()).classes('q-ml-md q-mt-md')

        main.best_guess = None
        main.current_data = {"en": "Analysis not started.", "hi": "विश्लेषण शुरू नहीं हुआ है।"}

        def show_landmark_name():
            res_label.set_text(f"📍 {main.best_guess if main.best_guess else 'Scanning...'}")

        def show_landmark_info():
            lang = lang_sel.value
            if lang == "Hindi":
                history_md.set_content(main.current_data["hi"])
            else:
                history_md.set_content(main.current_data["en"])

        predict_btn.on('click', show_landmark_name)
        info_btn.on('click', show_landmark_info)

        async def process_file(e: events.UploadEventArguments):
            result_card.set_visibility(True)
            analysis_progress.set_visibility(True)
            analysis_progress.set_value(0.1)
            n = ui.notification('Running Multi-Stage Vision Analysis...', spinner=True, timeout=None)
            
            try:
                start = time.perf_counter()

                async def _read_maybe_async(content):
                    if hasattr(content, 'read'):
                        data = content.read()
                        if hasattr(data, '__await__'):
                            return await data
                        return data
                    return content

                img_bytes = None
                if hasattr(e, 'content'): img_bytes = await _read_maybe_async(e.content)
                elif hasattr(e, 'file'): img_bytes = await _read_maybe_async(e.file)

                if img_bytes is None: raise ValueError('File read failed')

                # STAGE 1: Fast CNN Check (.h5 model)
                analysis_progress.set_value(0.3)
                name, conf = ai_guide.predict(img_bytes, threshold=0.9)
                _log(f"CNN Stage Result: {name} ({conf})")

                # STAGE 2: If CNN is unsure, use LLM Vision (Llama 3.2)
                if name == "Uncertain":
                    analysis_progress.set_value(0.5)
                    _log("CNN Unsure. Activating LLM Vision Stage...")
                    n.message = "CNN unsure. Activating LLM Vision..."
                    
                    llm_result = await ai_guide.predict_with_vision(img_bytes) 
                    analysis_progress.set_value(0.9)
                    
                    main.best_guess = llm_result.get('name', 'Unknown Landmark')
                    main.current_data["en"] = llm_result.get('english', 'No English info found.')
                    main.current_data["hi"] = llm_result.get('hindi', 'कोई हिंदी जानकारी नहीं मिली।')
                else:
                    main.best_guess = name
                    raw_info = ai_guide.get_expert_response(name)
                    
                    if "[HINDI]" in raw_info:
                        main.current_data["en"] = raw_info.split("[ENGLISH]")[-1].split("[HINDI]")[0].strip()
                        main.current_data["hi"] = raw_info.split("[HINDI]")[-1].strip()
                    else:
                        main.current_data["en"] = raw_info
                        main.current_data["hi"] = "हिंदी अनुवाद उपलब्ध नहीं है।"

                res_label.set_text(f"📍 {main.best_guess}")
                history_md.set_content("Analysis complete. Click 'More Info' to view details.")
                predict_btn.enable()
                info_btn.enable()

                analysis_progress.set_value(1.0)
                ui.timer(3.0, lambda: analysis_progress.set_visibility(False), once=True)
                
                n.message = f'Analysis Finished! Latency: {time.perf_counter()-start:.2f}s'
                n.spinner = False
                n.icon = 'check_circle'
            except Exception as ex:
                _log(f"[ERROR] Logic failed: {ex}")
                ui.notify(f'Vision Error: {ex}', type='negative')
            finally:
                n.dismiss()

        ui.upload(on_upload=process_file, auto_upload=True, label="Upload Landmark Photo").classes('w-full q-mb-md')

        def _update_status_and_logs():
            try:
                # 1. Update GPU Stats
                try:
                    nvmlInit()
                    handle = nvmlDeviceGetHandleByIndex(0)
                    info = nvmlDeviceGetMemoryInfo(handle)
                    used = info.used / 1024**3
                    total = info.total / 1024**3
                    vram_status.set_text(f"RTX 5050 VRAM: {used:.2f}GB / {total:.2f}GB")
                    nvmlShutdown()
                except Exception:
                    vram_status.set_text("VRAM Monitor: Offline")

                # 2. Update Logs
                content = _tail_log('server_debug.log', max_lines=400)
                if content: log_code.content = content # Fix for ui.code property
            except Exception:
                pass

        ui.timer(2.0, _update_status_and_logs)

        def _run_full_init_subprocess():
            def _worker():
                try:
                    ai_guide._llm_init_running = True
                    _log('Starting Full AI Optimization...')
                    proc = subprocess.Popen([sys.executable, 'scripts/init_llm.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for line in proc.stdout: _log(line.rstrip())
                    proc.wait()
                    ai_guide._llm_initialized = True
                    ai_guide._init_llm_models()
                except Exception as e: _log(f'Init Error: {e}')
                finally: ai_guide._llm_init_running = False
            threading.Thread(target=_worker, daemon=True).start()

def _tail_log(path, max_lines=400):
    try:
        if not os.path.exists(path): return ""
        with open(path, 'r', encoding='utf-8') as fh:
            lines = fh.read().splitlines()
        return '\n'.join(lines[-max_lines:]) if len(lines) > max_lines else '\n'.join(lines)
    except: return ''

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Landmark AI", host='127.0.0.1', port=8000)