import streamlit as st

from components.header import dashboard_header
from components.cards import metric_card
from components.charts import budget_chart, progress_chart


def show(data):

    # --------------------------------------------------------
    # Load Selected Project
    # --------------------------------------------------------

    projects = data["projects"]

    project = projects[
        projects["Project_ID"] == st.session_state.selected_project
    ].iloc[0]

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    dashboard_header(project)

    st.write(f"📍 {project['Location']}")

    st.divider()

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            title="Budget",
            value=f"₹ {project['Budget_INR']/10000000:.2f} Cr",
            icon="💰",
            color="#2563EB"
        )

    with col2:
        metric_card(
            title="Actual Cost",
            value=f"₹ {project['Actual_Cost_INR']/10000000:.2f} Cr",
            icon="💸",
            color="#F97316"
        )

    with col3:
        metric_card(
            title="Completion",
            value=f"{project['Completion_Percentage']}%",
            icon="📈",
            color="#22C55E"
        )

    with col4:
        metric_card(
            title="Priority",
            value=project["Priority"],
            icon="🚨",
            color="#EF4444"
        )

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    st.divider()

    chart1, chart2 = st.columns(2)

    with chart1:
        st.plotly_chart(
            budget_chart(project),
            use_container_width=True
        )

    with chart2:
        st.plotly_chart(
            progress_chart(project),
            use_container_width=True
        )

    # --------------------------------------------------------
    # PROJECT DETAILS
    # --------------------------------------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📋 Project Details")

        with st.container(border=True):

            st.markdown(f"""
**Client**

{project['Client_Name']}

---

**Project Manager**

{project['Project_Manager']}

---

**Project Type**

{project['Project_Type']}

---

**Location**

{project['Location']}

---

**Status**

{project['Current_Status']}
""")

    with col2:

        st.subheader("💰 Financial Summary")

        remaining = (
            project["Budget_INR"]
            - project["Actual_Cost_INR"]
        )

        utilization = (
            project["Actual_Cost_INR"]
            / project["Budget_INR"]
        ) * 100

        with st.container(border=True):

            st.markdown(f"""
**Budget**

₹ {project['Budget_INR']/10000000:.2f} Cr

---

**Spent**

₹ {project['Actual_Cost_INR']/10000000:.2f} Cr

---

**Remaining**

₹ {remaining/10000000:.2f} Cr

---

**Budget Utilization**

{utilization:.1f}%
""")

            st.progress(min(utilization / 100, 1.0))

    # --------------------------------------------------------
    # AI INSIGHTS
    # --------------------------------------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🤖 AI Insights")

        with st.container(border=True):

            st.success("Budget utilization is healthy.")

            st.info("Project progress matches the planned schedule.")

            st.info("Material consumption appears normal.")

            st.success("No major construction risks detected.")

    with col2:

        st.subheader("⚠ Risk Summary")

        with st.container(border=True):

            st.warning("Material Supply : Medium Risk")

            st.success("Weather : Low Risk")

            st.error("Labour Availability : High Risk")

            st.info("Equipment Health : Normal")

    # --------------------------------------------------------
    # ALERTS
    # --------------------------------------------------------

    st.divider()

    st.subheader("🚨 Project Alerts")

    if project["Completion_Percentage"] < 30:
        st.warning("Project is still in the early execution stage.")

    if project["Priority"] == "Critical":
        st.error("Critical Priority Project.")

    if project["Actual_Cost_INR"] > project["Budget_INR"] * 0.80:
        st.warning("Budget utilization has exceeded 80%.")

    if project["Current_Status"] == "Delayed":
        st.error("Project schedule is delayed.")

    if project["Current_Status"] == "In Progress":
        st.success("Project is progressing as planned.")

    # --------------------------------------------------------
    # RECENT ACTIVITIES
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Recent Activities")

    activities = [

        "✔ Cement delivery completed",

        "✔ Foundation inspection approved",

        "✔ Structural steel ordered",

        "✔ Daily report generated",

        "✔ Site safety inspection completed"

    ]

    with st.container(border=True):

        for activity in activities:
            st.write(activity)

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    st.divider()

    st.caption(
        "🏗️ ConstructIQ AI Enterprise | Infosys Springboard Internship | Version 1.0"
    )