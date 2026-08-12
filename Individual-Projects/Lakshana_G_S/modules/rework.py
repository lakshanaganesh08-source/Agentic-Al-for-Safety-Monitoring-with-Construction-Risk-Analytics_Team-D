import streamlit as st

from components.cards import metric_card
from components.charts import (
    rework_rootcause_chart,
    rework_trade_chart,
    rework_trend_chart,
    rework_status_chart
)


def show(data):

    st.title("🔧 AI Construction Rework Intelligence")

    st.caption(
        "Identify construction defects, analyze root causes and estimate rework impact using AI."
    )

    st.divider()

    rework = data["rework"]

    # ==========================================================
    # FILTERS
    # ==========================================================

    c1, c2 = st.columns(2)

    with c1:
        project = st.selectbox(
            "Project",
            ["All"] + sorted(rework["Project_ID"].unique().tolist())
        )

    with c2:
        trade = st.selectbox(
            "Trade",
            ["All"] + sorted(rework["Trade"].unique().tolist())
        )

    # ==========================================================
    # FILTER DATA
    # ==========================================================

    df = rework.copy()

    if project != "All":
        df = df[df["Project_ID"] == project]

    if trade != "All":
        df = df[df["Trade"] == trade]

    # ==========================================================
    # KPI CALCULATIONS
    # ==========================================================

    total_cases = len(df)

    total_cost = df["Rework_Cost"].sum()

    resolved = len(df[df["Resolved"] == "Yes"])

    pending = len(df[df["Resolved"] == "No"])

    quality = round((resolved / max(total_cases, 1)) * 100, 1)

    st.divider()

    # ==========================================================
    # KPI CARDS
    # ==========================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Rework Cases",
            total_cases,
            "🔧",
            "#2563EB"
        )

    with c2:
        metric_card(
            "Rework Cost",
            f"₹ {total_cost/10000000:.2f} Cr",
            "💰",
            "#EF4444"
        )

    with c3:
        metric_card(
            "Resolved",
            resolved,
            "✅",
            "#22C55E"
        )

    with c4:
        metric_card(
            "Quality Score",
            f"{quality:.1f}%",
            "⭐",
            "#F59E0B"
        )

    # ==========================================================
    # CHARTS
    # ==========================================================

    st.divider()

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            rework_rootcause_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            rework_status_chart(df),
            use_container_width=True
        )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            rework_trade_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            rework_trend_chart(df),
            use_container_width=True
        )

    # ==========================================================
    # AI INSIGHTS
    # ==========================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🤖 AI Root Cause Analysis")

        top_root = df["Root_Cause"].mode()[0]

        top_trade = df["Trade"].mode()[0]

        st.success(f"Most frequent root cause: **{top_root}**")

        st.info(f"Highest rework observed in **{top_trade}** trade.")

        st.warning(
            f"{pending} rework cases are still pending resolution."
        )

        st.success(
            "Quality inspections can significantly reduce future defects."
        )

    with col2:

        st.subheader("✅ AI Recommendations")

        st.success("Increase quality inspections before project handover.")

        st.success("Conduct weekly quality audits.")

        st.success("Train labour on standard construction practices.")

        st.success("Improve material quality verification.")

    # ==========================================================
    # REWORK INCIDENTS TABLE
    # ==========================================================

    st.divider()

    st.subheader("📋 Rework Incidents")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    st.divider()

    st.caption(
        "🔧 ConstructIQ AI Enterprise • Construction Rework Intelligence "
    )