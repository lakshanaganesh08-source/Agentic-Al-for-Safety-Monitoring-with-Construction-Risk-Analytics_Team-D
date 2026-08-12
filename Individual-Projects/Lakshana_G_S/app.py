import streamlit as st
import config

from components.sidebar import show_sidebar
from utils.session import initialize_session
from utils.data_loader import load_data
from auth.login import show_login

# Import Modules
from modules import (
    dashboard,
    project_management,
    cost_estimation,
    material_estimation,
    delay_prediction,
    rework,
    site_safety,
    risk_intelligence,
    documents,
    chatbot,
    reports,
    executive_report,
    executive_dashboard
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# LOAD CSS
# =====================================================

with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# =====================================================
# INITIALIZE
# =====================================================

initialize_session()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.logged_in:

    show_login()

    st.stop()
    
data = load_data()

# =====================================================
# SIDEBAR
# =====================================================

show_sidebar()

# =====================================================
# ROUTER
# =====================================================

page = st.session_state.current_page

if page == "🏠 Dashboard":
    dashboard.show(data)

elif page == "📁 Project Management":
    project_management.show(data)

elif page == "💰 Cost Estimation":
    cost_estimation.show(data)

elif page == "🧱 Material Estimation":
    material_estimation.show(data)

elif page == "⏳ Delay Prediction":
    delay_prediction.show(data)

elif page == "🔧 Construction Rework":
    rework.show(data)

elif page == "⚠️ Risk Intelligence":
    risk_intelligence.show(data)

elif page == "💬 AI Chatbot":
    chatbot.show(data)

elif page == "🧠 Executive AI Dashboard":
    executive_dashboard.show(data)

elif page == "📄 Executive Report":
    executive_report.show(data)

elif page == "📝 Daily Reports":
    reports.show(data)