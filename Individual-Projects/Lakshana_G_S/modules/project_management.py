import streamlit as st
import pandas as pd


def show(data):

    projects = data["projects"].copy()

    st.title("📂 Project Management")
    st.caption("Manage and monitor all construction projects")

    st.divider()

    # =====================================================
    # FILTERS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        search = st.text_input(
            "🔍 Search Project"
        )

    with c2:
        status = st.selectbox(
            "Status",
            ["All"] + sorted(projects["Current_Status"].unique().tolist())
        )

    with c3:
        priority = st.selectbox(
            "Priority",
            ["All"] + sorted(projects["Priority"].unique().tolist())
        )

    with c4:
        project_type = st.selectbox(
            "Project Type",
            ["All"] + sorted(projects["Project_Type"].unique().tolist())
        )

    # =====================================================
    # FILTER DATA
    # =====================================================

    if search:

        projects = projects[

            projects["Project_Name"].str.contains(
                search,
                case=False,
                na=False
            )

            |

            projects["Project_ID"].str.contains(
                search,
                case=False,
                na=False
            )

        ]

    if status != "All":
        projects = projects[
            projects["Current_Status"] == status
        ]

    if priority != "All":
        projects = projects[
            projects["Priority"] == priority
        ]

    if project_type != "All":
        projects = projects[
            projects["Project_Type"] == project_type
        ]

    # =====================================================
    # SUMMARY CARDS
    # =====================================================

    st.divider()

    total_budget = projects["Budget_INR"].sum()

    total_cost = projects["Actual_Cost_INR"].sum()

    completed = len(
        projects[
            projects["Current_Status"] == "Completed"
        ]
    )

    delayed = len(
        projects[
            projects["Current_Status"] == "Delayed"
        ]
    )

    a, b, c, d = st.columns(4)

    a.metric(
        "Total Projects",
        len(projects)
    )

    b.metric(
        "Total Budget",
        f"₹ {total_budget/10000000:.1f} Cr"
    )

    c.metric(
        "Completed",
        completed
    )

    d.metric(
        "Delayed",
        delayed
    )

    # =====================================================
    # PROJECT TABLE
    # =====================================================

    st.divider()

    st.subheader("📋 Projects")

    display = projects[
        [
            "Project_ID",
            "Project_Name",
            "Client_Name",
            "Location",
            "Budget_INR",
            "Actual_Cost_INR",
            "Completion_Percentage",
            "Current_Status",
            "Priority",
        ]
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # SELECT PROJECT
    # =====================================================

    st.divider()

    if projects.empty:

        st.warning("No project found.")

        st.stop()

    selected = st.selectbox(

        "Select Project",

        projects["Project_Name"]

    )

    row = projects[
        projects["Project_Name"] == selected
    ].iloc[0]

    # =====================================================
    # PROJECT DETAILS
    # =====================================================

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("📄 Project Details")

        with st.container(border=True):

            st.write("**Project ID** :", row["Project_ID"])
            st.write("**Client** :", row["Client_Name"])
            st.write("**Manager** :", row["Project_Manager"])
            st.write("**Location** :", row["Location"])
            st.write("**Status** :", row["Current_Status"])
            st.write("**Priority** :", row["Priority"])

    with c2:

        st.subheader("📊 Progress")

        with st.container(border=True):

            st.metric(
                "Completion",
                f"{row['Completion_Percentage']}%"
            )

            st.progress(
                row["Completion_Percentage"] / 100
            )

            remaining = (
                row["Budget_INR"]
                - row["Actual_Cost_INR"]
            )

            st.metric(
                "Budget Remaining",
                f"₹ {remaining/10000000:.2f} Cr"
            )

    # =====================================================
    # PROJECT SUMMARY
    # =====================================================

    st.divider()

    st.subheader("📌 Project Summary")

    left, right = st.columns(2)

    # ---------------------------------------
    # Left Card
    # ---------------------------------------

    with left:

        with st.container(border=True):

            st.markdown("### 🏗 Project Overview")

            st.write(f"**Project Name:** {row['Project_Name']}")
            st.write(f"**Client:** {row['Client_Name']}")
            st.write(f"**Project Type:** {row['Project_Type']}")
            st.write(f"**Location:** {row['Location']}")
            st.write(f"**Priority:** {row['Priority']}")
            st.write(f"**Current Status:** {row['Current_Status']}")

    # ---------------------------------------
    # Right Card
    # ---------------------------------------

    with right:

        utilization = (
            row["Actual_Cost_INR"] /
            row["Budget_INR"]
        ) * 100

        if utilization < 60:
            budget_status = "🟢 Healthy"
        elif utilization < 85:
            budget_status = "🟡 Monitor"
        else:
            budget_status = "🔴 Critical"

        if row["Completion_Percentage"] >= 90:
            schedule_status = "🟢 On Track"
        elif row["Completion_Percentage"] >= 60:
            schedule_status = "🟡 Moderate"
        else:
            schedule_status = "🔴 Behind Schedule"

        with st.container(border=True):

            st.markdown("### 📈 Project Health")

            st.write(f"**Budget Status:** {budget_status}")

            st.write(f"**Schedule Status:** {schedule_status}")

            st.write(f"**Budget Utilization:** {utilization:.1f}%")

            st.write(f"**Completion:** {row['Completion_Percentage']}%")

            st.write(f"**Remaining Budget:** ₹ {remaining/10000000:.2f} Cr")


    st.divider()

    st.caption(
        "📁 ConstructIQ AI Enterprise | Project Management"
    )