import streamlit as st

MENU_ITEMS = [
    "🏠 Dashboard",
    "📁 Project Management",
    "💰 Cost Estimation",
    "🧱 Material Estimation",
    "⏳ Delay Prediction",
    "🔧 Construction Rework",
    "🦺 Site Safety",
    "⚠ Risk Detection",
    "📄 Construction Documents",
    "🤖 AI Chatbot",
    "❓ Project Q&A",
    "📝 Daily Reports",
    "📊 Analytics"
]


def initialize_navigation():
    if "current_page" not in st.session_state:
        st.session_state.current_page = MENU_ITEMS[0]


def navigate(page):
    st.session_state.current_page = page