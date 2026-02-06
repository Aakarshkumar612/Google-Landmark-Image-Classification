# 🌍 Smart Landmark AI Guide 

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16+-FF6F00?logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Pro-Cloud_AI-8E75B2?logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, hybrid-cloud Image Classification application. This project utilizes a local **TensorFlow CNN** for rapid identification and leverages **Google Gemini 2.5 Pro** via API to generate rich, bilingual historical insights.



---

## 🚀 Key Features
- **Hybrid AI Pipeline**: Initial fast-scan with a local `.h5` model; automatic fallback to **Gemini 2.5 Pro Vision** for complex or uncertain landmark identification.
- **Bilingual Historical Context**: Generates detailed architectural and cultural history in both **English and Hindi**.
- **Hardware Optimized**: Built to handle high-resolution (**14.4MB+**) images efficiently on modern GPUs like the **RTX 5050**.
- **Real-Time VRAM Monitoring**: Integrated tracking of system resources to ensure stable performance during heavy inference.
- **Universal Format Support**: Auto-converts PNG, WebP, and HEIC uploads to model-compliant RGB JPEG format.

---

## 🛠️ Tech Stack
- **Inference Engine**: TensorFlow 2.16+, Keras 3.0
- **Cloud Intelligence**: Google Generative AI (Gemini 2.5 Pro SDK)
- **Web Framework**: NiceGUI (Modern Interface), FastAPI (Backend)
- **Image Processing**: Pillow, NumPy
- **System Monitoring**: NVML (Nvidia Management Library)

---

## 📂 Project Structure
```text
Google-Landmark-AI/
├── app.py              # Production entry point (FastAPI + NiceGUI mount)
├── main.py             # Frontend UI components & event logic
├── src/                
│   └── engine.py       # Core AI Engine (CNN Inference + Gemini API)
├── models/             
│   └── landmark_model.h5 # Pre-trained CNN model weights
├── test_images/        # Sample images for verification
├── .env                # API Keys & Secrets (Git-ignored)
├── .gitignore          # Optimized for lean cloud deployment
├── requirements.txt    # Pinned production dependencies
└── README.md           # Documentation

⚙️ Setup & Installation
1. Prerequisites
Python 3.11+

Nvidia GPU (Required for the pynvml monitoring and local CNN speed)

Google AI Studio Key (Get it here)

2. Local Setup
# Clone the repository
git clone [https://github.com/Aakarshkumar612/Google-Landmark-Image-Classification.git](https://github.com/Aakarshkumar612/Google-Landmark-Image-Classification.git)
cd Google-Landmark-Image-Classification

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

3. Environment Configuration
Create a .env file in the root directory and add your credentials:
GEMINI_API_KEY=your_google_api_key_here
STORAGE_SECRET=create_any_random_string_for_sessions

4. Running the App
# Development Mode
python main.py

# Production Mode
python app.py

Visit http://127.0.0.1:8000 in your browser.

🌐 Deployment Strategy
This project is engineered for easy migration to AWS or Vercel:

Deployment Safety: Includes a specific .gitignore to prevent large binary "bloat," keeping the repository under 250MB.

Dependency Management: Uses tensorflow-cpu configurations where GPU hardware is unavailable to save 300MB+ of disk space.

📝 1. The LICENSE File

For a modern AI project, the MIT License is the industry standard. It’s short, simple, and permissive, allowing others to use your code while protecting you from liability.

MIT License

Copyright (c) 2026 Aakarsh Kumar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

2. The CONTRIBUTING.md File
This file is a "welcome mat" for other developers. It explains exactly how they can help you improve the Landmark AI Guide.

# Contributing to Smart Landmark AI Guide

First off, thank you for considering contributing to this project! It’s people like you that make the open-source community such a great place to learn and build.

## 🚀 How Can I Contribute?

### Reporting Bugs
- Use the [GitHub Issues](https://github.com/Aakarshkumar612/Google-Landmark-Image-Classification/issues) to report bugs.
- Describe the actual behavior and what you expected to see.
- Include screenshots and your system specs (GPU, Python version).

### Suggesting Enhancements
- If you have an idea for a new feature (like "Export to PDF" or "New Landmark Models"), open an issue to discuss it.

### Your First Code Contribution
1. **Fork** the repository.
2. Create a new **branch** (`git checkout -b feature/AmazingFeature`).
3. Make your changes and **test** them locally with `test.py`.
4. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
5. **Push** to the branch (`git push origin feature/AmazingFeature`).
6. Open a **Pull Request**.

## 🛠️ Development Setup
- Follow the installation steps in the `README.md`.
- Ensure your `.env` file is set up with a valid Gemini API key for testing.
- **Note:** Never commit your `.env` file!

## 📜 Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all. Please be respectful and constructive in your communication.

---
*By contributing, you agree that your contributions will be licensed under its MIT License.*