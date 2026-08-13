import streamlit as st
import pandas as pd
from utils.styling import page_hero, stat_card


def render():
    page_hero(
        "📋", "Project Task Management",
        "Track, Filter, and Manage Site Operations &amp; Work Assignments",
        badge="OPERATIONS CONTROL"
    )

    tasks_data = [
        {"Task": "Foundation Concrete Pouring", "Status": "Completed", "Assignee": "John Doe", "Priority": "High"},
        {"Task": "Steel Framing Phase 1", "Status": "In Progress", "Assignee": "Sarah Smith", "Priority": "Critical"},
        {"Task": "Electrical Wiring - Floor 2", "Status": "Pending", "Assignee": "Mike Johnson", "Priority": "Medium"},
        {"Task": "HVAC Ductwork Installation", "Status": "In Progress", "Assignee": "Alex Rivera", "Priority": "High"},
        {"Task": "Site Safety Inspection Audit", "Status": "Completed", "Assignee": "Sarah Smith", "Priority": "Medium"},
    ]
    df = pd.DataFrame(tasks_data)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("📌", "Total Tasks", str(len(df)), None, "#F0F6FC"), unsafe_allow_html=True)
    with c2:
        completed_cnt = len(df[df["Status"] == "Completed"])
        st.markdown(stat_card("✅", "Completed", str(completed_cnt), None, "#00E676"), unsafe_allow_html=True)
    with c3:
        in_prog_cnt = len(df[df["Status"] == "In Progress"])
        st.markdown(stat_card("🔄", "In Progress", str(in_prog_cnt), None, "#00E5FF"), unsafe_allow_html=True)
    with c4:
        pending_cnt = len(df[df["Status"] == "Pending"])
        st.markdown(stat_card("⏳", "Pending", str(pending_cnt), None, "#FFAB00"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
        <div class="hub-card" style="padding: 16px 20px; margin-bottom: 16px;">
            <h4>🔍 Filters</h4>
            <span class="hub-card-tag">Narrow down the active work schedule below</span>
        </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2 = st.columns([1, 1])
    with f_col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=["Completed", "In Progress", "Pending"],
            default=["Completed", "In Progress", "Pending"]
        )
    with f_col2:
        priority_filter = st.multiselect(
            "🚨 Filter by Priority",
            options=["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"]
        )

    filtered_df = df[
        (df["Status"].isin(status_filter)) &
        (df["Priority"].isin(priority_filter))
    ]

    st.markdown("<h4 style='color: #00E5FF; margin: 20px 0 10px 0;'>📌 Active Work Schedule</h4>", unsafe_allow_html=True)

    st.dataframe(
        filtered_df,
        column_config={
            "Task": st.column_config.TextColumn("Task Description", width="large"),
            "Status": st.column_config.SelectboxColumn(
                "Current Status", options=["Completed", "In Progress", "Pending"], width="medium", required=True
            ),
            "Assignee": st.column_config.TextColumn("Assigned Engineer", width="medium"),
            "Priority": st.column_config.SelectboxColumn(
                "Priority Level", options=["Critical", "High", "Medium", "Low"], width="medium", required=True
            ),
        },
        use_container_width=True,
        hide_index=True
    )
