import streamlit as st

from utils.delay_engine import DelayPredictor
from components.cards import metric_card
from components.charts import (
    delay_trend_chart,
    delay_reason_chart,
    severity_chart,
)


def show(data):

    st.title("⏱️ AI Delay Prediction")

    st.caption(
        "Predict project delays and analyze historical delay data."
    )

    st.divider()

    delays = data["delays"]
    projects = data["projects"]

    # ======================================================
    # PROJECT SELECTION
    # ======================================================

    project_name = st.selectbox(
        "🏗 Select Project",
        projects["Project_Name"]
    )

    project_id = projects[
        projects["Project_Name"] == project_name
    ].iloc[0]["Project_ID"]

    project_delays = delays[
        delays["Project_ID"] == project_id
    ]

    st.divider()

    # ======================================================
    # INPUTS
    # ======================================================

    st.subheader("Prediction Factors")

    c1, c2 = st.columns(2)

    with c1:

        completion = st.slider(
            "Completion %",
            0,
            100,
            50
        )

        weather = st.selectbox(
            "Weather Risk",
            ["Low", "Medium", "High"]
        )

    with c2:

        labour = st.selectbox(
            "Labour Availability",
            ["High", "Medium", "Low"]
        )

        material = st.selectbox(
            "Material Availability",
            ["High", "Medium", "Low"]
        )

        budget = st.slider(
            "Budget Utilization %",
            0,
            100,
            60
        )

    st.divider()

    # ======================================================
    # PREDICT BUTTON
    # ======================================================

    if st.button(
        "🚀 Predict Delay",
        use_container_width=True
    ):

        predictor = DelayPredictor(delays)

        result = predictor.predict(
            completion,
            weather,
            labour,
            material,
            budget
        )

        st.success("Prediction completed successfully.")

        st.divider()

        # ==================================================
        # KPI CARDS
        # ==================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            metric_card(
                "Delay Probability",
                f"{result['Probability']}%",
                "📊",
                "#2563EB"
            )

        with col2:

            metric_card(
                "Expected Delay",
                f"{result['Expected Delay']} Days",
                "📅",
                "#F97316"
            )

        with col3:

            color = "#22C55E"

            if result["Risk"] == "Medium":
                color = "#EAB308"

            if result["Risk"] == "High":
                color = "#EF4444"

            metric_card(
                "Risk Level",
                result["Risk"],
                "⚠",
                color
            )

        st.divider()

        # ==================================================
        # REAL ANALYTICS
        # ==================================================

        c1, c2 = st.columns(2)

        with c1:

            st.plotly_chart(
                delay_trend_chart(project_delays),
                use_container_width=True
            )

        with c2:

            st.plotly_chart(
                delay_reason_chart(project_delays),
                use_container_width=True
            )

        st.plotly_chart(
            severity_chart(project_delays),
            use_container_width=True
        )

        st.divider()

        # ==================================================
        # HISTORY TABLE
        # ==================================================

        st.subheader("📋 Delay History")

        st.dataframe(
            project_delays,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ==================================================
        # AI INSIGHTS
        # ==================================================

        st.subheader("🤖 AI Recommendation")

        if result["Risk"] == "High":

            st.error("""
High delay risk detected.

Recommended Actions

• Increase labour allocation

• Procure materials early

• Improve equipment maintenance

• Weekly schedule monitoring
""")

        elif result["Risk"] == "Medium":

            st.warning("""
Moderate delay risk.

Recommended Actions

• Monitor labour attendance

• Review procurement weekly

• Monitor weather forecasts
""")

        else:

            st.success("""
Project schedule appears healthy.

Maintain the current execution plan.
""")
            
    st.divider()

    st.subheader("📊 Delay Statistics")

    col1, col2, col3, col4 = st.columns(4)

    total_delays = len(project_delays)

    avg_delay = (
        project_delays["Delay_Days"].mean()
        if total_delays > 0 else 0
    )

    max_delay = (
        project_delays["Delay_Days"].max()
        if total_delays > 0 else 0
    )

    high_severity = len(
        project_delays[
            project_delays["Severity"] == "High"
        ]
    )

    with col1:
        st.metric("Total Delay Events", total_delays)

    with col2:
        st.metric("Average Delay", f"{avg_delay:.1f} Days")

    with col3:
        st.metric("Maximum Delay", f"{max_delay} Days")

    with col4:
        st.metric("High Severity", high_severity)

    

    st.divider()

    st.subheader("🏆 Top Delay Reasons")

    reason_summary = (
        project_delays["Reason"]
        .value_counts()
        .reset_index()
    )

    reason_summary.columns = ["Reason", "Occurrences"]

    st.dataframe(
        reason_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🌦 Weather Impact")

    weather_summary = (
        project_delays["Weather"]
        .value_counts()
        .reset_index()
    )

    weather_summary.columns = ["Weather", "Count"]

    st.bar_chart(
        weather_summary.set_index("Weather")
    )

    st.divider()

    st.subheader("📦 Material Availability During Delays")

    material_summary = (
        project_delays["Material_Availability"]
        .value_counts()
        .reset_index()
    )

    material_summary.columns = ["Availability", "Count"]

    st.bar_chart(
        material_summary.set_index("Availability")
    )

    st.divider()

    st.subheader("👷 Labour Availability")

    labour_summary = (
        project_delays["Labour_Availability"]
        .value_counts()
        .reset_index()
    )

    labour_summary.columns = ["Availability", "Count"]

    st.bar_chart(
        labour_summary.set_index("Availability")
    )

    st.divider()

    st.caption(
        "⏳ ConstructIQ AI Enterprise | Delay Prediction"
    )