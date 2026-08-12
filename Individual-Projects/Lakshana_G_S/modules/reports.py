import streamlit as st

from components.cards import metric_card
from components.charts import (
    workers_chart,
    weather_chart,
    report_trend_chart,
    supervisor_chart
)


def show(data):

    st.title("📝 Daily Construction Reports")

    st.caption(
        "Monitor daily site activities, workforce, weather conditions and AI-generated summaries."
    )

    st.divider()

    reports = data["daily_reports"]

    # ====================================================
    # FILTERS
    # ====================================================

    c1, c2, c3 = st.columns(3)

    with c1:
        project = st.selectbox(
            "Project",
            ["All"] + sorted(reports["Project_ID"].unique())
        )

    with c2:
        supervisor = st.selectbox(
            "Supervisor",
            ["All"] + sorted(reports["Supervisor"].unique())
        )

    with c3:
        weather = st.selectbox(
            "Weather",
            ["All"] + sorted(reports["Weather"].unique())
        )

    df = reports.copy()

    if project != "All":
        df = df[df["Project_ID"] == project]

    if supervisor != "All":
        df = df[df["Supervisor"] == supervisor]

    if weather != "All":
        df = df[df["Weather"] == weather]

    # ====================================================
    # KPI CARDS
    # ====================================================

    total_reports = len(df)

    avg_workers = int(df["Workers_Present"].mean())

    projects = df["Project_ID"].nunique()

    issues = len(df[df["Issues"] != "None"])

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Reports",
            total_reports,
            "📝",
            "#2563EB"
        )

    with c2:
        metric_card(
            "Projects",
            projects,
            "🏗️",
            "#22C55E"
        )

    with c3:
        metric_card(
            "Avg Workers",
            avg_workers,
            "👷",
            "#F59E0B"
        )

    with c4:
        metric_card(
            "Open Issues",
            issues,
            "⚠",
            "#EF4444"
        )

    # ====================================================
    # CHARTS
    # ====================================================

    st.divider()

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            workers_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            weather_chart(df),
            use_container_width=True
        )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            report_trend_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            supervisor_chart(df),
            use_container_width=True
        )

    # ====================================================
    # REPORT PREVIEW
    # ====================================================

    st.divider()

    st.subheader("📋 Latest Daily Report")

    latest = df.sort_values("Date", ascending=False).iloc[0]

    with st.container(border=True):

        st.markdown(f"""
### 🏗️ {latest['Project_ID']}

**Date:** {latest['Date']}

**Supervisor:** {latest['Supervisor']}

**Weather:** {latest['Weather']}

**Workers Present:** {latest['Workers_Present']}

**Work Completed**

{latest['Work_Completed']}

**Materials Used**

{latest['Materials_Used']}

**Equipment Used**

{latest['Equipment_Used']}

**Issues**

{latest['Issues']}
""")

    # ====================================================
    # AI INSIGHTS
    # ====================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🤖 AI Summary")

        st.success("Daily productivity is stable.")

        st.info("Labour attendance is satisfactory.")

        st.success("Material utilization is normal.")

        st.warning("Monitor weather for tomorrow's activities.")

    with col2:

        st.subheader("✅ Recommendations")

        st.success("Schedule concrete work during clear weather.")

        st.success("Maintain equipment inspection logs.")

        st.success("Improve workforce allocation.")

        st.success("Continue daily reporting discipline.")

    # ====================================================
    # TABLE
    # ====================================================

    st.divider()

    st.subheader("📄 Daily Reports Register")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.caption(
        "📝 ConstructIQ AI Enterprise | Daily Reports"
    )
    