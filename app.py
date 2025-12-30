from fastapi import FastAPI
from nicegui import app, ui
import main # Import your backend logic

# Mount the NiceGUI interface onto the FastAPI app
@ui.page('/')
def index():
    ui.label('Landmark Discovery AI').classes('text-h4')
    # ... your existing UI code ...

# This command combines both into one process for Render
ui.run_with(main.app, storage_secret='your_private_secret')