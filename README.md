🏛️ LLM Based Landmark Image Analyzer
LLM Based Landmark Image Analyzer is a high-performance, hybrid AI application that identifies global landmarks and provides detailed historical context. By combining Deep Learning (CNN) for rapid image classification with Large Language Models (LLM) for expert knowledge retrieval, the system offers a seamless, bilingual (English/Hindi) user experience.

🚀 Live Demo
Production UI: Visit Vercel Frontend

API Endpoint: View Render Backend

✨ Key Features
Hybrid Inference Pipeline: Optimizes performance by using a local MobileNetV2 CNN for primary identification and Gemini 1.5 Pro as a high-reasoning fallback.

Bilingual Intelligence: Delivers architectural and historical insights in both English and Hindi.

Decoupled Architecture: Distributed deployment with a React frontend on Vercel and a FastAPI backend on Render.

Automated Data Persistence: Every search is logged into a PostgreSQL database using SQLModel for history tracking.

Hardware Monitoring: Real-time VRAM and GPU status reporting via integrated backend health checks.

🛠️ Tech Stack
Backend & AI
Framework: FastAPI (v0.115.0)

Deep Learning: TensorFlow-CPU (v2.15.1)

LLM SDK: Google Generative AI (v0.8.3)

Environment: Python 3.9.25

Frontend & Design
UI/UX: React (Architected via Bolt.new)

Styling: Modern, responsive dark-themed interface

Database & Infrastructure
ORM: SQLModel / SQLAlchemy

Database: PostgreSQL

Hosting: Vercel (Frontend), Render (Backend & DB)

📂 Project Structure
Plaintext
LLM-Based-Landmark-Image-Analyzer/
├── app.py              # FastAPI Main Application & API Routes
├── src/
│   └── engine.py       # Hybrid Inference Engine (CNN + LLM Logic)
├── models/
│   └── landmark_model.h5 # Pre-trained CNN Model Weights
├── requirements.txt    # Frozen Dependencies
├── .env                # Environment Configurations
└── README.md           # Documentation
⚙️ Local Setup & Installation
Clone the Repository

Bash
git clone https://github.com/Aakarshkumar612/LLM-Based-Landmark-Image-Analyzer.git
cd LLM-Based-Landmark-Image-Analyzer
Create Virtual Environment

Bash
conda create -n landmark_project python=3.9.25
conda activate landmark_project
Install Dependencies

Bash
pip install -r requirements.txt
Configure Environment Variables
Create a .env file:

Code snippet
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/landmark_db
Launch Backend

Bash
uvicorn app:app --reload
🏗️ Architecture Flow
Image Upload: User uploads an image via the Vercel-hosted React UI.

CNN Processing: The FastAPI backend processes the image using a local TensorFlow model.

LLM Enhancement: If the local model confidence is low, Gemini 1.5 Pro identifies the landmark and generates bilingual descriptions.

Persistence: The result is saved to PostgreSQL and returned to the UI.

🤝 Contact
Aakarsh Kumar

Degree: B.Tech in Artificial Intelligence (Final Year)

Institution: Gautam Buddha University

GitHub: @Aakarshkumar612

LinkedIn: Aakarsh Kumar