import streamlit as st
import pandas as pd

from components.cards import metric_card


def show(data):

    st.title("🧠 Executive AI Dashboard")

    st.caption(
        "Enterprise-level project portfolio intelligence."
    )

    st.divider()

    projects = data["projects"]
    delays = data["delays"]
    rework = data["rework"]
    safety = data["safety"]

    # ======================================
    # KPI CALCULATIONS
    # ======================================

    total_projects = len(projects)

    completed = len(
        projects[
            projects["Current_Status"] == "Completed"
        ]
    )

    in_progress = len(
        projects[
            projects["Current_Status"] == "In Progress"
        ]
    )

    delayed_projects = len(
        projects[
            projects["Current_Status"] == "Delayed"
        ]
    )

    total_budget = projects["Budget_INR"].sum()

    total_actual = projects["Actual_Cost_INR"].sum()

    utilization = (
        total_actual / total_budget
    ) * 100

    avg_safety = safety[
        "Overall_Safety_Score"
    ].mean()

    total_rework_cost = rework[
        "Rework_Cost"
    ].sum()

    # ======================================
    # KPI CARDS
    # ======================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Projects",
            total_projects,
            "🏗️",
            "#2563EB"
        )

    with c2:
        metric_card(
            "Completed",
            completed,
            "✅",
            "#22C55E"
        )

    with c3:
        metric_card(
            "In Progress",
            in_progress,
            "🚧",
            "#F59E0B"
        )

    with c4:
        metric_card(
            "Delayed",
            delayed_projects,
            "⏳",
            "#EF4444"
        )

    st.divider()

    # ======================================
    # FINANCIALS
    # ======================================

    st.subheader("💰 Portfolio Financials")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Budget",
            f"₹ {total_budget/10000000:.2f} Cr"
        )

    with c2:
        st.metric(
            "Actual Cost",
            f"₹ {total_actual/10000000:.2f} Cr"
        )

    with c3:
        st.metric(
            "Budget Utilization",
            f"{utilization:.1f}%"
        )

    st.progress(min(utilization / 100, 1.0))

    st.divider()

    # ======================================
    # QUALITY & SAFETY
    # ======================================

    st.subheader("🦺 Quality & Safety")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Average Safety Score",
            f"{avg_safety:.1f}"
        )

    with c2:
        st.metric(
            "Rework Cost",
            f"₹ {total_rework_cost/10000000:.2f} Cr"
        )

    st.divider()

    # ======================================
    # PROJECT HEALTH SCORE
    # ======================================

    health_score = 100

    health_score -= delayed_projects * 3

    health_score -= (
        total_rework_cost / 1000000
    )

    health_score += (
        avg_safety - 80
    )

    health_score = max(
        0,
        min(100, round(health_score))
    )

    st.subheader("📈 Enterprise Health Score")

    if health_score >= 85:

        st.success(
            f"🟢 {health_score}/100 - Excellent"
        )

    elif health_score >= 70:

        st.warning(
            f"🟡 {health_score}/100 - Moderate"
        )

    else:

        st.error(
            f"🔴 {health_score}/100 - Critical"
        )

    st.divider()

    # ======================================
    # AI EXECUTIVE SUMMARY
    # ======================================

    st.subheader("🤖 AI Executive Summary")

    with st.container(border=True):

        st.markdown(f"""
### Portfolio Overview

- Total Projects : **{total_projects}**
- Completed : **{completed}**
- Delayed : **{delayed_projects}**

### Financial Status

- Budget Utilization : **{utilization:.1f}%**

### Quality Status

- Rework Cost : **₹ {total_rework_cost/10000000:.2f} Cr**

### Safety Status

- Average Safety Score : **{avg_safety:.1f}**

### Recommendation

Continue monitoring delayed projects,
improve quality inspections,
and maintain current safety performance.
""")
        

    st.divider()

    st.caption(
        "🧠 ConstructIQ AI Enterprise | AI Executive"
    )