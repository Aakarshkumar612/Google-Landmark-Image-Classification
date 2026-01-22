import os
import time
from fastapi import FastAPI
from nicegui import app as nicegui_app, ui, events
from src.engine import LandmarkEngine 
from starlette.formparsers import MultiPartParser
import sys
import threading
import subprocess
import json

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
# Reordered to match model's internal class index mapping (predicted -> true)
CLASS_NAMES = ["Burj Khalifa", "Eiffel Tower", "Red Fort", "Taj Mahal", "Great Wall of China"]
ai_guide = LandmarkEngine(MODEL_PATH, CLASS_NAMES)

# background init flag
ai_guide._llm_init_notified = False
ai_guide._llm_init_running = False

@ui.page('/')
def main():
    ui.colors(primary='#385261')
    with ui.header().classes('bg-primary q-pa-md'):
        ui.label('🌍 Landmark AI Guide').classes('text-white text-h6')

    with ui.column().classes('w-full max-w-2xl mx-auto q-pa-md mt-10'):
        # LLM init controls
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
            ui.notify('LLM initialization started in background (check logs).', timeout=3)

        # optional auto-init via env var
        if os.environ.get('AUTO_INIT_LLM') == '1':
            start_llm_init()

        ui.row().classes('w-full').style('margin-bottom: 8px')
        ui.button('Initialize LLM (optional)', on_click=lambda: start_llm_init()).classes('primary')
        ui.label('Tip: click "Initialize LLM" to enable richer text responses. Local data files work without initialization.').classes('text-subtitle2')
        # LLM status + logs viewer
        status_row = ui.row().classes('items-center q-gutter-sm')
        with status_row:
            status_label = ui.label('LLM status: Not initialized').classes('text-subtitle1')
            status_spinner = ui.spinner(size='md').style('display: none')
            ui.button('Show Logs', on_click=lambda: log_card.set_visibility(not log_card.visible)).classes('secondary')
            # Heavy init and verify buttons
            ui.button('Run Full Init (heavy)', on_click=lambda: _run_full_init_subprocess()).classes('secondary')
            ui.button('Verify LLM', on_click=lambda: _verify_llm()).classes('secondary')
        log_card = ui.card().classes('w-full bg-grey-50 q-pa-md').style('display: none; max-height: 320px; overflow: auto')
        with log_card:
            ui.label('server_debug.log').classes('text-subtitle2')
            log_code = ui.code('', language='text').classes('w-full')

        result_card = ui.card().classes('w-full bg-blue-50 q-pa-md shadow-lg').style('display: none')
        with result_card:
            res_label = ui.label('').classes('text-h6 font-bold text-primary')
            history_md = ui.markdown('')

        async def process_file(e: events.UploadEventArguments):
            """Robust upload handler: supports multiple NiceGUI upload event shapes.
            Handles `e.content`, `e.file`, `e.files` and common dict/file-like variants.
            """
            result_card.set_visibility(False)
            n = ui.notification('Analyzing with GPU...', spinner=True, timeout=None)
            try:
                start = time.perf_counter()

                # Extract bytes from event (try several common variants)
                import asyncio

                async def _read_maybe_async(obj):
                    if obj is None:
                        return None
                    # bytes already
                    if isinstance(obj, (bytes, bytearray)):
                        return bytes(obj)
                    # file-like object with read()
                    if hasattr(obj, 'read'):
                        try:
                            data = obj.read()
                            if asyncio.iscoroutine(data):
                                data = await data
                            return data
                        except TypeError:
                            return None
                    # attribute 'content' may be bytes or awaitable
                    if hasattr(obj, 'content'):
                        data = getattr(obj, 'content')
                        if asyncio.iscoroutine(data):
                            data = await data
                        return data
                    # dict-like with 'content'
                    if isinstance(obj, dict) and 'content' in obj:
                        data = obj['content']
                        if asyncio.iscoroutine(data):
                            data = await data
                        return data
                    return None

                img_bytes = None
                # direct content attribute
                if hasattr(e, 'content'):
                    img_bytes = await _read_maybe_async(e.content)

                # single file attribute
                if img_bytes is None and hasattr(e, 'file'):
                    img_bytes = await _read_maybe_async(e.file)

                # multiple files attribute (list)
                if img_bytes is None and hasattr(e, 'files'):
                    files = e.files
                    if isinstance(files, (list, tuple)) and files:
                        img_bytes = await _read_maybe_async(files[0])

                if img_bytes is None:
                    raise ValueError('Uploaded file not found in event (no content/file/files)')

                # Ensure bytes
                if hasattr(img_bytes, 'encode') and not isinstance(img_bytes, (bytes, bytearray)):
                    # try to convert string-like to bytes
                    img_bytes = str(img_bytes).encode('utf-8')

                try:
                    name, conf = ai_guide.predict(img_bytes)
                    _log(f"[DEBUG] Predicted: {name} (confidence={conf})")

                    if name != "Uncertain":
                        history = ai_guide.get_expert_response(name)
                        _log(f"[DEBUG] Retrieved history length: {len(history) if hasattr(history, '__len__') else 'unknown'}")
                        res_label.set_text(f"📍 {name} ({conf:.1%})")
                        history_md.set_content(history)
                    else:
                        _log('[DEBUG] Prediction uncertain')
                        res_label.set_text("❓ Image Not Recognized")
                        history_md.set_content("Please try a clearer photo.")
                except Exception as predict_ex:
                    _log(f"[ERROR] Prediction failed: {predict_ex}")
                    res_label.set_text("Error during prediction")
                    history_md.set_content(f"Prediction error: {predict_ex}\n\nCheck server_debug.log for details.")

                result_card.set_visibility(True)
                n.message = f'Complete! Latency: {time.perf_counter()-start:.2f}s'
                n.spinner = False
                n.icon = 'check_circle'
            except Exception as ex:
                _log(f"[ERROR] Upload handler failed: {ex}")
                # ensure result card shows an error message so user isn't left with an empty UI
                try:
                    result_card.set_visibility(True)
                    res_label.set_text('Error processing upload')
                    history_md.set_content(f'Error: {ex}\n\nCheck server_debug.log for details.')
                except Exception:
                    pass
                ui.notify(f'Error: {ex}', type='negative')
            finally:
                n.dismiss()

        ui.upload(on_upload=process_file, auto_upload=True, label="Upload Photo").classes('w-full')

        # Poller: update status and logs periodically so user can watch init progress
        def _tail_log(path, max_lines=400):
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    lines = fh.read().splitlines()
                if len(lines) > max_lines:
                    return '\n'.join(lines[-max_lines:])
                return '\n'.join(lines)
            except Exception:
                return ''

        def _update_status_and_logs():
            try:
                if getattr(ai_guide, '_llm_init_running', False):
                    status_label.set_text('LLM status: Initializing...')
                    status_spinner.style('display: inline-block')
                elif getattr(ai_guide, '_llm_initialized', False):
                    status_label.set_text('LLM status: Initialized')
                    status_spinner.style('display: none')
                else:
                    status_label.set_text('LLM status: Not initialized')
                    status_spinner.style('display: none')

                # update logs
                content = _tail_log('server_debug.log', max_lines=400)
                if content:
                    log_code.set_text(content)
            except Exception:
                pass

        ui.timer(1.0, _update_status_and_logs)

        # Background subprocess runner for full init (writes output to server_debug.log)
        def _run_full_init_subprocess():
            if getattr(ai_guide, '_llm_init_running', False):
                ui.notify('LLM init already running', timeout=2)
                return

            def _worker():
                try:
                    ai_guide._llm_init_running = True
                    _log('Full init subprocess started')
                    # run the init script and stream output to server_debug.log
                    proc = subprocess.Popen([sys.executable, 'scripts/init_llm.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for line in proc.stdout:
                        _log(line.rstrip())
                    proc.wait()
                    _log(f'Full init subprocess exited with code {proc.returncode}')
                    if proc.returncode == 0:
                        ai_guide._llm_initialized = True
                    # try to load into memory (best-effort)
                    try:
                        ai_guide._init_llm_models()
                    except Exception as e:
                        _log(f'Post-init load failed: {e}')
                except Exception as e:
                    _log(f'Full init subprocess error: {e}')
                finally:
                    ai_guide._llm_init_running = False

            threading.Thread(target=_worker, daemon=True).start()

        def _verify_llm():
            # Try to ensure models are loaded and run a small query or return a local doc
            try:
                ui.notify('Verifying LLM/index — check logs for progress', timeout=3)
                # Attempt to load LLM models into memory (non-blocking best-effort)
                try:
                    ai_guide._init_llm_models()
                except Exception as e:
                    _log(f'Verify: _init_llm_models raised: {e}')

                # If chat engine is available, try a query
                if getattr(ai_guide, 'chat_engine', None):
                    try:
                        resp = None
                        try:
                            resp = ai_guide.chat_engine.chat('Provide a short ENGLISH and HINDI summary for Taj Mahal')
                        except Exception:
                            try:
                                resp = ai_guide.chat_engine.query('Provide a short ENGLISH and HINDI summary for Taj Mahal')
                            except Exception:
                                try:
                                    resp = ai_guide.chat_engine.run('Provide a short ENGLISH and HINDI summary for Taj Mahal')
                                except Exception:
                                    resp = None
                        _log(f'Verify: chat_engine response type: {type(resp)}')
                        ui.notify('Verify: chat_engine query sent — check logs for response', timeout=3)
                        return
                    except Exception as e:
                        _log(f'Verify chat query failed: {e}')

                # Fallback: return first document from data/index_docs.json
                try:
                    with open('data/index_docs.json', 'r', encoding='utf-8') as fh:
                        docs = json.load(fh)
                    if docs:
                        first = docs[0].get('text', '')
                        # show truncated doc in notification and log
                        ui.notify('Loaded local docs for verification (first doc shown in logs)', timeout=4)
                        _log('Verify: first doc (truncated): ' + first[:500].replace('\n',' '))
                        return
                except Exception as e:
                    _log(f'Verify fallback failed: {e}')

                ui.notify('Verify: No chat_engine or local docs available', type='negative')
            except Exception as e:
                _log(f'Verify button error: {e}')

if __name__ in {"__main__", "__mp_main__"}:
    print("\n" + "="*60)
    print("🚀 Landmark AI Guide Server Starting")
    print("📱 Visit: http://localhost:8000")
    print("="*60 + "\n")
    ui.run(title="Landmark AI Guide", host='127.0.0.1', port=8000)