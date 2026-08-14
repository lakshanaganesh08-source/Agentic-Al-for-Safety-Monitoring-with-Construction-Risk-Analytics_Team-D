import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------
# PAGE CONFIGURATION
# ------------------------------------
st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide"
)

# ------------------------------------
# LOAD CSS
# ------------------------------------
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ------------------------------------
# SIDEBAR
# ------------------------------------
with st.sidebar:

    st.image("images/logo.jpg", width=150)

    st.markdown(
        "<h2 style='text-align:center;'>🏗️ Construction Intelligence Hub</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;color:gray;'>AI Powered Construction Management</p>",
        unsafe_allow_html=True
    )

    st.success("🟢 AI System Online")

    st.metric("AI Model", "Llama 3.2")
    st.metric("AI Engine", "Ollama")
    st.metric("Version", "Milestone 2")

    st.markdown("---")

    st.subheader("🤖 AI Modules")

    st.markdown("""
✅ AI Chatbot

✅ Document Analysis

✅ Project Q&A

✅ Risk Detection

✅ Site Safety

✅ Material Estimation

✅ Daily Reports
""")

    st.markdown("---")

    st.progress(100)

    st.caption("Development Progress")

    st.metric("Completed Modules", "7 / 7")

    st.markdown("---")

    st.success("Infosys Springboard Internship 7.0")

    st.caption("Powered by Streamlit + Ollama + Llama 3.2")

# ------------------------------------
# HEADER
# ------------------------------------

st.title("🏗️ Construction Intelligence Hub")

st.success(
    """
### 🤖 Welcome!

An **AI-powered Construction Management Platform** that helps project managers analyze documents, generate reports, estimate materials, detect project risks, improve site safety, and interact with project data using **Llama 3.2**.
"""
)

st.divider()

# ------------------------------------
# KPI CARDS
# ------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🏗️ Projects",
        "12",
        "+2"
    )

with col2:
    st.metric(
        "👷 Workers",
        "120",
        "+15"
    )

with col3:
    st.metric(
        "🤖 AI Modules",
        "7",
        "Completed"
    )

with col4:
    st.metric(
        "📄 Reports Generated",
        "56",
        "+8"
    )

st.divider()

# ------------------------------------
# AI FEATURES
# ------------------------------------

st.subheader("🚀 AI Powered Features")

c1, c2 = st.columns(2)

with c1:

    st.info("""
📄 **Construction Documentation Analysis**

Analyze project documents instantly using AI.

---

❓ **Project Question & Answer**

Ask questions directly from uploaded PDFs.

---

📝 **Daily Report Generator**

Generate professional construction reports automatically.
""")

with c2:

    st.success("""
⚠️ **Risk Detection**

Identify potential construction risks before they occur.

---

🦺 **Site Safety Management**

Receive AI-powered safety recommendations.

---

🧱 **Material Estimation**

Estimate construction materials with AI assistance.
""")

st.divider()

# ------------------------------------
# CHARTS
# ------------------------------------

left, right = st.columns(2)

progress = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Progress": [12, 28, 46, 65, 81, 95]
})

fig1 = px.line(
    progress,
    x="Month",
    y="Progress",
    markers=True,
    title="Project Progress Over Time"
)

fig1.update_layout(
    template="plotly_white",
    height=400
)

with left:
    st.plotly_chart(fig1, use_container_width=True)

status = pd.DataFrame({
    "Status": ["Completed", "Ongoing", "Planning"],
    "Projects": [8, 3, 1]
})

fig2 = px.pie(
    status,
    values="Projects",
    names="Status",
    title="Project Status Distribution",
    hole=0.45
)

fig2.update_layout(height=400)

with right:
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ------------------------------------
# PROJECT PROGRESS
# ------------------------------------

st.subheader("🏗️ Current Project Progress")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("Metro Station")
    st.progress(90)

with col2:
    st.write("Shopping Mall")
    st.progress(70)

with col3:
    st.write("Residential Apartments")
    st.progress(45)

st.divider()

# ------------------------------------
# ACTIVE PROJECTS
# ------------------------------------

st.subheader("📋 Active Construction Projects")

projects = pd.DataFrame({
    "Project": [
        "Metro Station",
        "Shopping Mall",
        "Residential Apartment",
        "City Hospital"
    ],
    "Location": [
        "Pune",
        "Mumbai",
        "Nashik",
        "Nagpur"
    ],
    "Status": [
        "Completed",
        "Ongoing",
        "Planning",
        "Ongoing"
    ],
    "Budget": [
        "₹12 Cr",
        "₹20 Cr",
        "₹18 Cr",
        "₹25 Cr"
    ]
})

st.dataframe(
    projects,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ------------------------------------
# PROJECT STATUS
# ------------------------------------

st.subheader("📌 Project Status")

left, right = st.columns(2)

with left:
    st.success("✅ 8 Projects Completed Successfully")

with right:
    st.warning("⚠️ 3 Projects Require Attention")

st.divider()

# ------------------------------------
# QUICK INSIGHTS
# ------------------------------------

st.subheader("📊 AI Insights")

c1, c2 = st.columns(2)

with c1:
    st.info("""
### 📈 Performance

✅ Budget Utilization : **82%**

✅ Worker Efficiency : **94%**

✅ Safety Compliance : **97%**

✅ Project Completion : **82%**
""")

with c2:
    st.warning("""
### ⚠️ AI Alerts

• Material stock running low

• Heavy rainfall expected this week

• Crane maintenance overdue

• One project delayed by five days
""")

st.divider()

# ------------------------------------
# FOOTER
# ------------------------------------

st.caption(
    "🏗️ Construction Intelligence Hub | Powered by Llama 3.2 • Ollama • Streamlit | Infosys Springboard Internship 7.0"
)