import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Workers", page_icon="👷", layout="wide")

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# -------------------------
# HEADER
# -------------------------

st.title("👷 Workforce Management")

st.write(
    """
    Manage construction workers, monitor attendance,
    assign projects, and ensure workforce efficiency.
    """
)

st.divider()

# -------------------------
# METRICS
# -------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Workers", "120")

with col2:
    st.metric("Present Today", "110")

with col3:
    st.metric("Absent", "10")

with col4:
    st.metric("Safety Compliance", "97%")

st.divider()

# -------------------------
# WORKER DATA
# -------------------------

workers = pd.DataFrame({

    "Name":[
        "Rahul Sharma",
        "Amit Verma",
        "Sneha Patil",
        "Neha Joshi",
        "Rohit Desai",
        "Karan Singh"
    ],

    "Role":[
        "Engineer",
        "Supervisor",
        "Architect",
        "Site Manager",
        "Civil Engineer",
        "Labour"
    ],

    "Attendance":[
        "Present",
        "Present",
        "Absent",
        "Present",
        "Present",
        "Present"
    ],

    "Project":[
        "Metro",
        "Mall",
        "Hospital",
        "Metro",
        "IT Park",
        "Mall"
    ]
})

# -------------------------
# SEARCH
# -------------------------

st.subheader("🔍 Search Worker")

search = st.text_input("Enter worker name")

if search:
    workers = workers[
        workers["Name"].str.contains(search, case=False)
    ]

st.dataframe(
    workers,
    use_container_width=True,
    hide_index=True
)

st.divider()

# -------------------------
# ATTENDANCE CHART
# -------------------------

attendance = pd.DataFrame({

    "Status":[
        "Present",
        "Absent"
    ],

    "Workers":[
        110,
        10
    ]
})

fig = px.pie(
    attendance,
    values="Workers",
    names="Status",
    hole=0.5,
    title="Today's Attendance"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# -------------------------
# PROJECT ASSIGNMENT
# -------------------------

st.subheader("🏗 Project Allocation")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("Metro Project")
    st.progress(90)

with col2:
    st.write("Shopping Mall")
    st.progress(70)

with col3:
    st.write("City Hospital")
    st.progress(50)

st.divider()

# -------------------------
# SAFETY
# -------------------------

st.success(
    """
    ✅ PPE Compliance : 97%

    ✅ No major incidents reported today

    ✅ Equipment inspection completed
    """
)

st.info(
    """
    Future Enhancement:

    • Live attendance using QR Code

    • Face Recognition

    • AI-based safety monitoring

    • Worker productivity analysis
    """
)