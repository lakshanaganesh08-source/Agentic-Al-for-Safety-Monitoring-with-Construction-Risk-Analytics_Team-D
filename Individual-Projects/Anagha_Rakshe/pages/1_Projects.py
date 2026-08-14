import streamlit as st
import pandas as pd

st.set_page_config(page_title="Projects", page_icon="🏗️", layout="wide")


def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# -------------------------
# HEADER
# -------------------------

st.title("🏗️ Project Management")

st.write(
    """
    Manage construction projects, monitor their progress,
    and keep track of budgets and project status.
    """
)

st.divider()

# -------------------------
# PROJECT SUMMARY
# -------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Projects", "12")

with col2:
    st.metric("Completed", "8")

with col3:
    st.metric("Ongoing", "3")

with col4:
    st.metric("Planning", "1")

st.divider()

# -------------------------
# ADD PROJECT FORM
# -------------------------

st.subheader("➕ Add New Project")

with st.form("project_form"):

    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input("Project Name")

        location = st.text_input("Location")

        manager = st.text_input("Project Manager")

    with col2:

        budget = st.number_input(
            "Budget (₹ Crores)",
            min_value=1
        )

        duration = st.number_input(
            "Duration (Months)",
            min_value=1
        )

        status = st.selectbox(
            "Status",
            [
                "Planning",
                "Ongoing",
                "Completed"
            ]
        )

    submitted = st.form_submit_button("Add Project")

    if submitted:

        st.success("✅ Project added successfully!")

st.divider()

# -------------------------
# SEARCH
# -------------------------

st.subheader("🔍 Search Projects")

search = st.text_input(
    "Search by Project Name"
)

st.divider()

# -------------------------
# PROJECT TABLE
# -------------------------

projects = pd.DataFrame({

    "Project":[
        "Metro Station",
        "Shopping Mall",
        "City Hospital",
        "Residential Towers",
        "IT Park"
    ],

    "Location":[
        "Pune",
        "Mumbai",
        "Nagpur",
        "Nashik",
        "Pimpri"
    ],

    "Manager":[
        "Rahul Sharma",
        "Sneha Patil",
        "Amit Verma",
        "Rohit Desai",
        "Neha Joshi"
    ],

    "Status":[
        "Completed",
        "Ongoing",
        "Planning",
        "Ongoing",
        "Completed"
    ],

    "Budget":[
        "₹12 Cr",
        "₹20 Cr",
        "₹15 Cr",
        "₹25 Cr",
        "₹18 Cr"
    ]
})

if search:

    projects = projects[
        projects["Project"].str.contains(
            search,
            case=False
        )
    ]

st.subheader("📋 Project List")

st.dataframe(
    projects,
    use_container_width=True,
    hide_index=True
)

st.divider()

# -------------------------
# PROJECT STATUS
# -------------------------

st.subheader("🏗️ Current Project Progress")

col1, col2, col3 = st.columns(3)

with col1:

    st.write("Metro Station")

    st.progress(100)

with col2:

    st.write("Shopping Mall")

    st.progress(70)

with col3:

    st.write("City Hospital")

    st.progress(30)

st.divider()

# -------------------------
# PROJECT INFORMATION
# -------------------------

st.info(
    """
    📌 **Features Available**

    • Add New Projects

    • Search Existing Projects

    • Monitor Project Progress

    • Track Budget

    • View Project Status

    *(Database integration will be added in the next milestone.)*
    """
)