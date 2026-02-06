import os
from fastapi import FastAPI
from nicegui import app as nicegui_app, ui
import main  # This pulls in your Landmark AI logic
from dotenv import load_dotenv

# Load secret keys for session storage
load_dotenv()

# 1. Initialize the FastAPI app
fastapi_app = FastAPI()

# 2. Define the NiceGUI Landing Page
@ui.page('/')
def index():
    # We call the main content from your main.py to keep things organized
    main.main()

# 3. Mount NiceGUI onto FastAPI
# storage_secret is CRITICAL for app.storage.user to work
# Use a secure environment variable for the secret in production
ui.run_with(
    fastapi_app, 
    storage_secret=os.getenv('STORAGE_SECRET', 'fallback_local_secret_123'),
    title="Landmark AI Guide",
    reconnect_timeout=60 # Matches the 60s timeout in your main logic
)

# 4. For Render/Production deployment
if __name__ == '__main__':
    import uvicorn
    # Render uses the 'PORT' environment variable
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(fastapi_app, host='0.0.0.0', port=port)