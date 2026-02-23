import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="Landmark.AI Engine", layout="wide")

st.title("🏛️ Landmark.AI: Hybrid Vision Engine")
st.write("AI Engineer Demo | CNN Model + Gemini 1.5 Pro Fallback")

# --- Sidebar: System Health ---
st.sidebar.header("Backend Status")
try:
    health = requests.get("http://localhost:8000/vram", timeout=2).json()
    st.sidebar.success(f"Connected: {health['gpu_name']}")
    st.sidebar.progress(health['usage_percent'] / 100, text=f"GPU Load: {health['usage_percent']}%")
except Exception:
    st.sidebar.error("Backend Offline! Start 'app.py' first.")

# --- Main Interface ---
uploaded_file = st.file_uploader("Select Landmark Image", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        img = Image.open(uploaded_file)
        st.image(img, caption="Input Data", use_container_width=True)
    
    with col2:
        if st.button("Run Hybrid Inference"):
            with st.spinner("Consulting Hybrid Knowledge Base..."):
                files = {"file": uploaded_file.getvalue()}
                try:
                    response = requests.post("http://localhost:8000/predict", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.header(f"Result: {data['name']}")
                        st.subheader("Bilingual Intelligence")
                        st.info(f"**English:** {data['english']}")
                        st.success(f"**Hindi:** {data['hindi']}")
                    else:
                        st.error("Engine Inference Error.")
                except Exception as e:
                    st.error(f"Server Connection Failed: {e}")

# --- Bottom Section: PostgreSQL History ---
st.divider()
if st.checkbox("Show Search History from PostgreSQL"):
    try:
        history_resp = requests.get("http://localhost:8000/history").json()
        # Using st.table for a formal presentation look
        st.table(history_resp)
    except Exception:
        st.error("Failed to fetch database logs.")