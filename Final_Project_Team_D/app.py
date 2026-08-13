import os
import sys

# Make the project root importable before Streamlit initializes.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st

# Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from database.db import init_database
from database.seed import run_seed
from utils.styling import apply_custom_css

@st.cache_resource
def setup_database_once():
    init_database()
    run_seed(include_demo_incidents=True)
    return True

# Initialize SQLite schema and demo data on first run only
setup_database_once()

apply_custom_css()

# ----------------- AUTH GATE (INSTANT LOGIN RENDER) -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    from modules import login
    login.render()
    st.stop()  # Prevent heavy module imports & processing until logged in

# Import Heavy Module Renders only AFTER authentication succeeds
from modules import (
    about,
    chatbot,
    compliance_agent,
    cost_prediction,
    cv_module,
    dashboard,
    delay_prediction,
    insurance_agent,
    login,
    material_estimation,
    project_management,
    reports,
    safety_module,
    safety_risk_agent,
)

# Initialize Active Page Session State
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Navigation Items Mapping: Label -> (Icon, Module Render Function)
PAGES = {
    "Dashboard": ("📊", dashboard.render),

    "Safety & Risk Intelligence": (
        "🛡️",
        safety_risk_agent.render
    ),

    "Compliance Agent": (
        "📋",
        compliance_agent.render
    ),

    "Insurance Agent": (
        "🛡️",
        insurance_agent.render
    ),

    "Material Estimation": (
        "🧱",
        material_estimation.render
    ),

    "💬 General Assistant": (
        "💬",
        chatbot.render
    ),

    "Cost Prediction": (
        "💰",
        cost_prediction.render
    ),

    "Delay Risk Prediction": (
        "⏳",
        delay_prediction.render
    ),

    "CV Inspection": (
        "👁️",
        cv_module.render
    ),

    "Project Management": (
        "📋",
        project_management.render
    ),

    "Safety & Compliance": (
        "🦺",
        safety_module.render
    ),

    "Reports": (
        "📄",
        reports.render
    ),

    "About": (
        "ℹ️",
        about.render
    ),
}

# ----------------- SIDEBAR NAVIGATION -----------------
with st.sidebar:
    user_role = st.session_state.get('role', 'User')
    user_name = st.session_state.get('username', 'user')
    st.markdown(f"""
        <div style="text-align: center; padding: 10px 0 15px 0;">
            <h2 style="margin: 0; font-size: 1.4rem; color: #F0F6FC;">🏗️ Intelligence Hub</h2>
            <p style="color: #8B949E; font-size: 0.8rem; margin-top: 4px;">Next-Gen Construction Management</p>
            <p style="color: #00E5FF; font-size: 0.78rem; margin-top: 6px;">👋 Signed in as <b>{user_name}</b> <span style="color:#7C3AED; font-weight:700;">({user_role})</span></p>
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

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="nav_logout", width="stretch"):
        login.logout()

# ----------------- MAIN ROUTER -----------------
current_page_name = st.session_state.page
if current_page_name in PAGES:
    _, render_func = PAGES[current_page_name]
    render_func()
else:
    dashboard.render()