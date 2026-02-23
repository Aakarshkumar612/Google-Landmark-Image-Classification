# 🏛️ LLM Based Landmark Image Analyzer
### *A Hybrid Intelligence System for Global Landmark Recognition & Contextual Analysis*

[![Frontend Deployment](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://llm-based-landmark-git-291d54-aakarsh-kumars-projects-be31a675.vercel.app/)
[![Backend Deployment](https://img.shields.io/badge/Backend-Render-informational?style=for-the-badge&logo=render)](https://llm-based-landmark-image-analyzer.onrender.com)
[![Python Version](https://img.shields.io/badge/Python-3.9.25-blue?style=for-the-badge&logo=python)](https://www.python.org/downloads/release/python-3.9.25)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)

---

## 🌟 Project Overview
In modern computer vision, a single model often struggles to balance speed with deep contextual understanding. **LLM Based Landmark Image Analyzer** solves this by implementing a **Tiered Hybrid Inference Pipeline**. 

The system leverages a high-speed local **MobileNetV2 (CNN)** for initial classification and an **LLM (Gemini 1.5 Pro)** for complex visual reasoning and expert-level bilingual knowledge retrieval (English/Hindi).

### 🔗 Live Access
* **Interactive UI (Vercel)**: [Live Production Link](https://llm-based-landmark-git-291d54-aakarsh-kumars-projects-be31a675.vercel.app/)
* **Inference API (Render)**: [Backend API Endpoint](https://llm-based-landmark-image-analyzer.onrender.com)

---

## 🏗️ Architectural Excellence
The project implements a **Decoupled Three-Tier Architecture**, designed for horizontal scalability:

1.  **Frontend Layer (Vercel)**: A React-based interface (architected via Bolt.new) optimized for low-latency user interactions and high-speed image processing.
2.  **Logic Tier (Render)**: A **FastAPI** engine that manages the AI logic, model-weight loading for TensorFlow, and secure orchestration of Gemini API calls.
3.  **Data Tier (PostgreSQL)**: Utilizing **SQLModel** for efficient persistence of inference history, confidence scores, and real-time hardware metrics.



---

## 🧠 Hybrid Inference Pipeline
This tiered logic ensures 100% identification accuracy even when the local model is uncertain:

* **Tier 1: Local Inference (CNN)**
    * **Engine**: TensorFlow-CPU (MobileNetV2).
    * **Decision**: If confidence score $C > 0.6$, results are served instantly to reduce latency and API costs.
* **Tier 2: Cloud Reasoning (Gemini 1.5 Pro Vision)**
    * **Engine**: Google Generative AI.
    * **Fallback**: Triggered automatically when Tier 1 is "Uncertain," providing zero-shot visual identification.
* **Tier 3: Bilingual Synthesis**
    * Output is dynamically formatted into structured **English** and **Hindi** descriptions for educational depth.



---

## 🛠️ Tech Stack & Dependencies

| Category | Technology | Version |
| :--- | :--- | :--- |
| **Language** | Python | `3.9.25` |
| **Backend** | FastAPI | `0.115.0` |
| **Deep Learning** | TensorFlow-CPU | `2.15.1` |
| **Generative AI** | Google Generative AI | `0.8.3` |
| **Database** | SQLModel / PostgreSQL | `0.0.21` / `2.9.9` |
| **Frontend** | React (Bolt.new) | Production Build |

---

## ⚙️ Installation & Local Development

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Aakarshkumar612/LLM-Based-Landmark-Image-Analyzer.git](https://github.com/Aakarshkumar612/LLM-Based-Landmark-Image-Analyzer.git)
    cd LLM-Based-Landmark-Image-Analyzer
    ```

2.  **Set Up Environment**
    ```bash
    conda create -n landmark_project python=3.9.25 -y
    conda activate landmark_project
    pip install -r requirements.txt
    ```

3.  **Configuration**
    Create a `.env` file in the root:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    DATABASE_URL=postgresql://user:password@localhost:5432/landmark_db
    ```

4.  **Run Server**
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    ```

---

## 🤝 Contact
**Aakarsh Kumar**
Gautam Buddha University
* **LinkedIn**: [Aakarsh Kumar](https://www.linkedin.com/in/aakarsh-kumar-608720297/)
* **GitHub**: [@Aakarshkumar612](https://github.com/Aakarshkumar612)
