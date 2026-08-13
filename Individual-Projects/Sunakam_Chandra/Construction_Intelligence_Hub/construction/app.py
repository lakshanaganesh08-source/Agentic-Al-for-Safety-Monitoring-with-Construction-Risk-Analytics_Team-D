import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

from modules import (
    document_analyzer,
    project_questionnaire,
    risk_detection,
    site_safety,
    material_estimation,
    chatbot,
    daily_report,
)

st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Load CSS ----------
def load_css(file_path):
    css_file = Path(file_path)
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/style.css")

# =========================================================
# ---------------------- AUTHENTICATION --------------------
# =========================================================

USER_CREDENTIALS = {
    "admin": "admin123",
    "manager": "manager123",
    "engineer": "engineer123",
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""


def show_login_form():
    st.markdown("""
    <div style="max-width:420px; margin: 60px auto 0 auto;">
        <h1 style="text-align:center; font-size:2rem;">🏗️ Construction Intelligence Hub</h1>
        <p style="text-align:center; color:#94a3b8; margin-bottom:30px;">
            Please sign in to continue
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

        with st.expander("Demo credentials"):
            st.code("Username: admin\nPassword: admin123")


if not st.session_state.authenticated:
    show_login_form()
    st.stop()

# =========================================================
# ------------------- SIDEBAR NAVIGATION -------------------
# =========================================================

with st.sidebar:
    st.markdown(f"👤 Logged in as **{st.session_state.username}**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧭 Navigation")

    page = st.radio(
        "Go to",
        [
            "🏠 Dashboard",
            "📄 Document Analyzer",
            "📝 Project Questionnaire",
            "⚠️ Risk Detection",
            "🦺 Site Safety",
            "🧱 Material Estimation",
            "💬 Chatbot",
            "📊 Daily Report",
        ],
        label_visibility="collapsed",
    )

# =========================================================
# ------------------- SHARED MOCK DATA ----------------------
# =========================================================

if "projects" not in st.session_state:
    st.session_state.projects = pd.DataFrame({
        "Project ID": ["PRJ-001", "PRJ-002", "PRJ-003", "PRJ-004", "PRJ-005"],
        "Name": ["Skyline Towers", "Green Valley Homes", "Metro Bridge", "Sunrise Mall", "Harbor Apartments"],
        "Location": ["Hyderabad", "Bengaluru", "Chennai", "Nellore", "Vizag"],
        "Status": ["In Progress", "Completed", "In Progress", "Delayed", "Planning"],
        "Budget (₹L)": [450, 220, 780, 320, 510],
        "Spent (₹L)": [310, 220, 540, 290, 90],
        "Progress (%)": [68, 100, 62, 55, 12],
        "Start Date": pd.to_datetime(["2024-01-10", "2023-06-15", "2024-03-01", "2023-11-20", "2025-02-01"]),
        "Deadline": pd.to_datetime(["2026-01-10", "2024-06-15", "2026-03-01", "2025-11-20", "2027-02-01"]),
    })

if "workers" not in st.session_state:
    st.session_state.workers = pd.DataFrame({
        "Worker ID": [f"W-{i:03d}" for i in range(1, 13)],
        "Name": ["Ramesh K", "Suresh V", "Anjali P", "Vikram S", "Lakshmi N",
                 "Arjun R", "Priya M", "Kiran T", "Divya S", "Mahesh B",
                 "Sneha J", "Ravi G"],
        "Role": ["Mason", "Electrician", "Site Engineer", "Plumber", "Carpenter",
                 "Mason", "Site Engineer", "Welder", "Painter", "Electrician",
                 "Site Supervisor", "Mason"],
        "Project": ["Skyline Towers", "Green Valley Homes", "Metro Bridge", "Sunrise Mall",
                    "Harbor Apartments", "Skyline Towers", "Metro Bridge", "Sunrise Mall",
                    "Skyline Towers", "Green Valley Homes", "Metro Bridge", "Harbor Apartments"],
        "Attendance (%)": [92, 88, 97, 85, 90, 78, 95, 82, 89, 91, 99, 80],
        "Daily Wage (₹)": [800, 950, 1500, 850, 900, 800, 1500, 1000, 750, 950, 1800, 800],
        "Status": ["Active", "Active", "Active", "On Leave", "Active",
                   "Active", "Active", "On Leave", "Active", "Active", "Active", "Active"]
    })

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame({
        "Item": ["Cement (bags)", "Steel (tons)", "Bricks (units)", "Sand (cu.ft)",
                 "Water (liters)", "Paint (liters)", "Tiles (sq.ft)", "Wood (cu.ft)"],
        "Available Stock": [2400, 45, 185000, 9800, 50000, 620, 12500, 340],
        "Reorder Level": [1000, 20, 50000, 4000, 20000, 200, 5000, 150],
        "Unit Cost (₹)": [380, 62000, 8, 55, 0.02, 250, 65, 1800],
        "Supplier": ["UltraTech", "TATA Steel", "Local Kiln Co.", "River Sand Supplies",
                     "Municipal Corp", "Asian Paints", "Kajaria", "Greenwood Timber"]
    })

# =========================================================
# ------------------------ ROUTING --------------------------
# =========================================================

if page == "🏠 Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <h1 style="font-size:2.6rem;">🏗️ Construction Intelligence Hub</h1>
        <p style="color:#cbd5e1; font-size:1.1rem;">
            An AI-powered command center for construction project management — track progress,
            predict materials, estimate costs, assess risk, and manage inventory, all in one place.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    total_projects = len(st.session_state.projects)
    active_projects = len(st.session_state.projects[st.session_state.projects["Status"] == "In Progress"])
    total_workers = len(st.session_state.workers)
    total_budget = st.session_state.projects["Budget (₹L)"].sum()
    total_spent = st.session_state.projects["Spent (₹L)"].sum()

    kpis = [
        (col1, "📁", total_projects, "Total Projects"),
        (col2, "🚧", active_projects, "Active Projects"),
        (col3, "👷", total_workers, "Total Workers"),
        (col4, f"₹{total_budget}L", "", "Total Budget"),
        (col5, f"₹{total_spent}L", "", "Total Spent"),
    ]

    for col, val, extra, label in kpis:
        with col:
            display_val = f"{val}{extra}" if extra != "" else val
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{display_val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    c1, c2 = st.columns([1.3, 1])

    with c1:
        st.markdown("### 📈 Project Progress Overview")
        fig = px.bar(
            st.session_state.projects,
            x="Name", y="Progress (%)",
            color="Status",
            color_discrete_map={
                "In Progress": "#f97316", "Completed": "#22c55e",
                "Delayed": "#ef4444", "Planning": "#3b82f6"
            },
            text="Progress (%)"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", height=380, margin=dict(t=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### 🥧 Status Distribution")
        status_counts = st.session_state.projects["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig2 = px.pie(
            status_counts, names="Status", values="Count", hole=0.55,
            color="Status",
            color_discrete_map={
                "In Progress": "#f97316", "Completed": "#22c55e",
                "Delayed": "#ef4444", "Planning": "#3b82f6"
            }
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0", height=380,
            margin=dict(t=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 💰 Budget vs Spending by Project")
    fig3 = px.bar(
        st.session_state.projects, x="Name", y=["Budget (₹L)", "Spent (₹L)"],
        barmode="group",
        color_discrete_sequence=["#facc15", "#f97316"]
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0", height=380, legend_title_text=""
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="footer-text">
        Construction Intelligence Hub © 2026 | Built with Streamlit & Plotly
    </div>
    """, unsafe_allow_html=True)

elif page == "📄 Document Analyzer":
    document_analyzer.render()

elif page == "📝 Project Questionnaire":
    project_questionnaire.render()

elif page == "⚠️ Risk Detection":
    risk_detection.render()

elif page == "🦺 Site Safety":
    site_safety.render()

elif page == "🧱 Material Estimation":
    material_estimation.render()

elif page == "💬 Chatbot":
    chatbot.render()

elif page == "📊 Daily Report":
    daily_report.render()