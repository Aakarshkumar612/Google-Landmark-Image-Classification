import streamlit as st
import requests
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Landmark.AI Dashboard", layout="wide", initial_sidebar_state="expanded")

# Professional AI Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #4CAF50; color: white; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1e2130; border-radius: 4px 4px 0 0; gap: 1px; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Landmark.AI: Hybrid Inference Engine")
st.write("Project by Aakarsh Kumar | Final Year B.Tech AI")

# 2. Sidebar: System Health & Hardware Monitoring
st.sidebar.header("🛠️ Engine Status")
try:
    # Connects to your FastAPI /vram endpoint
    vram_resp = requests.get("http://localhost:8000/vram", timeout=2).json()
    st.sidebar.success(f"GPU Active: {vram_resp['gpu_name']}")
    st.sidebar.metric("VRAM Load", f"{vram_resp['usage_percent']}%")
    st.sidebar.progress(vram_resp['usage_percent'] / 100)
except Exception:
    st.sidebar.error("Backend Offline! Run 'uvicorn app:app' in Terminal 1.")

# 3. Main Inference Section
st.subheader("📤 Upload Landmark for Identification")
uploaded_file = st.file_uploader("Upload Image (JPG/PNG)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        img = Image.open(uploaded_file)
        st.image(img, caption="Inference Target", use_container_width=True)
        
    with col2:
        if st.button("🚀 Execute Hybrid Prediction"):
            with st.spinner("Pipeline: CNN Feature Extraction -> Gemini Vision Fallback..."):
                files = {"file": uploaded_file.getvalue()}
                try:
                    # Pointing to your local FastAPI
                    response = requests.post("http://localhost:8000/predict", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.balloons()
                        st.markdown(f"### 🎯 Predicted: **{data['name']}**")
                        
                        # Tabs for Bilingual Results
                        tab1, tab2 = st.tabs(["📄 English Description", "🇮🇳 Hindi Description"])
                        with tab1:
                            st.info(data['english'])
                        with tab2:
                            st.success(data['hindi'])
                    else:
                        st.error(f"Inference Failed: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# 4. Database History Section
st.divider()
if st.checkbox("📜 View PostgreSQL Inference History"):
    try:
        history = requests.get("http://localhost:8000/history").json()
        st.dataframe(history, use_container_width=True)
    except Exception:
        st.warning("Could not retrieve history from database.")