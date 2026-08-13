import os
import sys

# Make the project root importable before Streamlit initializes.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
from utils.styling import apply_custom_css

# Page Configuration
st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Import Module Renders
from modules import (
    about,
    chatbot,
    chatbot_construction,
    compliance_module,
    cost_prediction,
    cv_module,
    dashboard,
    delay_prediction,
    project_management,
    reports,
    safety_module,
)

# Initialize Active Page Session State
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Navigation Items Mapping: Label -> (Icon, Module Render Function)
PAGES = {
    "Dashboard": ("📊", dashboard.render),
    "💬 General Assistant": ("💬", chatbot.render),
    "🏗️ Construction Expert": ("🏗️", chatbot_construction.render),
    "Cost Prediction": ("💰", cost_prediction.render),
    "Delay Risk Prediction": ("⏳", delay_prediction.render),
    "CV Inspection": ("👁️", cv_module.render),
    "Project Management": ("📋", project_management.render),
    "Safety & Compliance": ("🦺", safety_module.render),
    "🛡️ Compliance & Insurance": ("🛡️", compliance_module.render),
    "Reports": ("📄", reports.render),
    "About": ("ℹ️", about.render),
}

# ----------------- SIDEBAR NAVIGATION -----------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 15px 0;">
            <h2 style="margin: 0; font-size: 1.4rem; color: #F0F6FC;">🏗️ Intelligence Hub</h2>
            <p style="color: #8B949E; font-size: 0.8rem; margin-top: 4px;">Next-Gen Construction Management</p>
        </div>
        <hr style="border: 0; height: 1px; background: #30363D; margin-bottom: 20px;">
    """, unsafe_allow_html=True)

    st.markdown("<p style='color: #8B949E; font-weight: 700; font-size: 0.75rem; letter-spacing: 1px;'>NAVIGATION MENU</p>", unsafe_allow_html=True)

    # Render Nav Buttons with Active Indicator
    for item_name, (icon, _) in PAGES.items():
        is_active = st.session_state.page == item_name
        label = f"{'🔹' if is_active else icon} {item_name}"
        
        if st.button(label, key=f"nav_{item_name}", width="stretch"):
            st.session_state.page = item_name
            st.rerun()

    st.markdown("<hr style='border: 0; height: 1px; background: #30363D; margin: 20px 0 15px 0;'>", unsafe_allow_html=True)
    
    # System Status Card
    st.markdown("""
        <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px; font-size: 0.8rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="color: #8B949E;">System Status:</span>
                <span style="color: #00E676; font-weight: 700;">● Operational</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span style="color: #8B949E;">LLM Engine:</span>
                <span style="color: #00E5FF; font-weight: 600;">Ollama (llama3.2)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ----------------- MAIN ROUTER -----------------
current_page_name = st.session_state.page
if current_page_name in PAGES:
    _, render_func = PAGES[current_page_name]
    render_func()
else:
    dashboard.render()
