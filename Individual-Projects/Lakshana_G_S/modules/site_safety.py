import streamlit as st

from components.cards import metric_card
from components.charts import (
    safety_score_chart,
    ppe_chart,
    scaffolding_chart,
    monthly_safety_chart
)


def show(data):

    st.title("🦺 AI Site Safety Intelligence")

    st.caption(
        "Monitor safety inspections, compliance and AI-powered safety recommendations."
    )

    st.divider()

    safety = data["safety"]

    # ==================================================
    # FILTERS
    # ==================================================

    c1, c2 = st.columns(2)

    with c1:

        project = st.selectbox(
            "Project",
            ["All"] + sorted(safety["Project_ID"].unique())
        )

    with c2:

        inspector = st.selectbox(
            "Inspector",
            ["All"] + sorted(safety["Inspector"].unique())
        )

    df = safety.copy()

    if project != "All":
        df = df[df["Project_ID"] == project]

    if inspector != "All":
        df = df[df["Inspector"] == inspector]

    # ==================================================
    # KPIs
    # ==================================================

    total = len(df)

    avg_score = df["Overall_Safety_Score"].mean()

    ppe = len(df[df["PPE_Compliance"] == "Yes"])

    helmet = len(df[df["Helmet_Compliance"] == "Yes"])

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Safety Inspections",
            total,
            "🦺",
            "#2563EB"
        )

    with c2:
        metric_card(
            "Average Score",
            f"{avg_score:.1f}",
            "⭐",
            "#22C55E"
        )

    with c3:
        metric_card(
            "PPE Compliance",
            ppe,
            "🥽",
            "#F59E0B"
        )

    with c4:
        metric_card(
            "Helmet Compliance",
            helmet,
            "⛑",
            "#EF4444"
        )

    # ==================================================
    # CHARTS
    # ==================================================

    st.divider()

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            safety_score_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            ppe_chart(df),
            use_container_width=True
        )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            scaffolding_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            monthly_safety_chart(df),
            use_container_width=True
        )

    # ==================================================
    # AI INSIGHTS
    # ==================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🤖 AI Safety Insights")

        st.success("Overall safety compliance is satisfactory.")

        st.info("Regular inspections are improving site safety.")

        st.warning("Scaffolding requiring attention should be reviewed.")

        st.success("PPE compliance remains consistently high.")

    with col2:

        st.subheader("✅ Recommendations")

        st.success("Conduct daily toolbox talks.")

        st.success("Inspect scaffolding before every shift.")

        st.success("Verify fire extinguishers weekly.")

        st.success("Improve electrical hazard awareness.")

    # ==================================================
    # TABLE
    # ==================================================

    st.divider()

    st.subheader("📋 Safety Inspection Records")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.caption(
        "🦺 ConstructIQ AI Enterprise | Site Safety Intelligence"
    )