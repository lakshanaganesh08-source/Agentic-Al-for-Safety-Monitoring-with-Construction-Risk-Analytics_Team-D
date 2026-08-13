import streamlit as st

from utils.styling import inject_css
from utils.data_gen import generate_project_data
from modules import dashboard, cost_prediction, delay_prediction, cv_module, chatbot, about

st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

PAGES = {
    "📊 Dashboard": "dashboard",
    "🏗️ Project Management": "project_management",
    "💰 Cost Prediction": "cost_prediction",
    "⏱️ Delay Risk Prediction": "delay_prediction",
    "🦺 Safety Analytics": "safety_module",
    "📷 Vision Scanner": "cv_module",
    "💬 AI Assistant": "chatbot",
    "📄 AI Reports": "reports",
    "ℹ️ About": "about",
}

with st.sidebar:
    st.markdown(
        "<div style='font-family:Barlow Condensed; font-size:1.4rem; font-weight:800; "
        "color:#F59E0B; padding:6px 0 0 0;'>🏗️ CONSTRUCTION<br>INTELLIGENCE HUB</div>",
        unsafe_allow_html=True,
    )
    st.caption("AI-powered project intelligence")
    st.write("")
    selection = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
    st.write("")
    st.caption("Milestone 2 · Streamlit + scikit-learn + OpenCV")

df = generate_project_data()
page_key = PAGES[selection]

if page_key == "dashboard":
    dashboard.render(df)
elif page_key == "cost_prediction":
    cost_prediction.render(df)
elif page_key == "delay_prediction":
    delay_prediction.render(df)
elif page_key == "cv_module":
    cv_module.render()
elif page_key == "chatbot":
    chatbot.render(df)
elif page_key == "about":
    about.render()
elif page_key in ("project_management", "safety_module", "reports"):
    st.warning(
        f"The **{selection}** module hasn't been built yet in this version — "
        "only Dashboard, Cost Prediction, Delay Risk, Vision Scanner, AI Assistant, "
        "and About are wired up so far. Let me know and I can build this module next."
    )
