import streamlit as st

def initialize_session():
    """Initialize session state variables."""

    if "selected_project" not in st.session_state:
        st.session_state.selected_project = None

    if "selected_project_name" not in st.session_state:
        st.session_state.selected_project_name = None

    if "ollama_status" not in st.session_state:
        st.session_state.ollama_status = "🟢 Connected"

    if "user_name" not in st.session_state:
        st.session_state.user_name = "Project Manager"