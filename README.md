# 🌍 Google Landmark AI Guide

A professional-grade Image Classification application that identifies global landmarks and generates rich historical context using Generative AI. This project replaces a standard Gradio interface with a modular **FastAPI + NiceGUI** architecture for a production-ready experience.

## 🚀 Key Features
- **CNN Classification**: Employs a custom TensorFlow model to identify famous landmarks with high confidence.
- **AI Historical Insights**: Integrates **Google Gemini 2.0 Flash** to generate fascinating 2-sentence histories for identified sites.
- **Modern Web Interface**: A responsive, server-side UI built with **NiceGUI** and **FastAPI**.
- **Modular Architecture**: Logic is strictly separated into a UI layer (`main.py`) and an AI Engine (`src/engine.py`).

## 🛠️ Tech Stack
- **AI Engine**: TensorFlow, Google GenAI (Gemini)
- **Web Framework**: NiceGUI, FastAPI
- **Image Processing**: Pillow, NumPy
- **Environment**: Python Dotenv (Secrets Management)

## 📂 Project Structure
```text
Google-Landmark-AI/
├── main.py             # Entry point & NiceGUI Web UI
├── src/                
│   ├── __init__.py    # Python package marker
│   └── engine.py      # Core logic (TensorFlow + Gemini)
├── models/             
│   └── landmark_model.h5  # Trained model weights
├── .env                # API Keys (Excluded from Git)
├── requirements.txt    # Pinned dependencies
└── README.md           # Documentation

⚙️ Setup & Installation
1. Prerequisites
. Python 3.9+

. A Google Gemini API Key

2. Installation
# Clone the repository
git clone [https://github.com/Aakarshkumar612/Google-Landmark-Image-Classification.git](https://github.com/Aakarshkumar612/Google-Landmark-Image-Classification.git)
cd Google-Landmark-Image-Classification

# Install dependencies
pip install -r requirements.txt

3. Environment Secrets
Create a .env file in the root directory and add your API key:
GEMINI_API_KEY=your_actual_api_key_here

4. Run the Application
python -m uvicorn main:app --reload
Open your browser at http://127.0.0.1:8000.

📝 License
Distributed under the MIT License. See LICENSE for more information.

### Why this is an improvement:
* **Refined Tech Stack**: It removes Gradio and adds the more powerful NiceGUI/FastAPI combo.
* **Modular Description**: It highlights the `src/` folder, which shows you understand software engineering patterns like **Separation of Concerns**.
* **Clear Setup**: It provides the exact commands needed to get the app running, including the critical `.env` step.

## LLM / RAG Status

- **Current:** LLM (RAG/embeddings) initialization has not been completed in this repository by default. The app will still perform image classification using the local TensorFlow model in `models/landmark_model.h5` and will return bilingual landmark descriptions from local `data/*.txt` files.
- **Implication:** Retrieval-augmented generation (chat, LLM-produced content, and similarity search using embeddings) will not be available until the heavy initialization step is run.
- **To enable full LLM/RAG functionality:** run the heavy initializer which downloads embeddings and builds an index. From the repo root:

```powershell
conda activate landmark_project
python scripts/init_llm.py 2>&1 | tee init_llm_output.log
```

- After successful completion, start the UI and verify via the `Run Full Init (heavy)` and `Verify LLM` buttons at http://127.0.0.1:8000, or inspect `server_debug.log` and `data/index_docs.json` for confirmation.

If you prefer to keep the app lightweight and avoid large downloads, the current setup (local model + `data/*.txt`) is fully functional for classification and static bilingual descriptions.



**Would you like me to help you create a `LICENSE` file for your repository to make it even more professional?**

[NiceGUI and FastAPI Tutorial](https://www.youtube.com/watch?v=FDUfaYsFQrc)
This video is relevant because it demonstrates how to use TensorFlow within a web application context, which is the core of your landmark classification project.


http://googleusercontent.com/youtube_content/3