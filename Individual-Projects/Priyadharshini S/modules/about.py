import streamlit as st
from utils.styling import page_hero, feature_card


def render():
    page_hero(
        "ℹ️", "About Construction Intelligence Hub",
        "Next-Generation AI &amp; Analytics for Modern Construction Management",
        badge="PLATFORM OVERVIEW"
    )

    st.markdown("""
        <div class="hub-banner">
            <p style="margin: 0; font-size: 1.05rem; line-height: 1.6; color: #F0F6FC;">
                <strong>Construction Intelligence Hub</strong> is an end-to-end platform built to streamline the
                construction project lifecycle. By uniting advanced artificial intelligence, predictive machine
                learning, and computer vision, it transforms complex site data into actionable, real-time insights.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color: #00E5FF; margin-bottom: 18px;'>🛠️ Core Capabilities</h4>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown(feature_card(
            "🤖", "Powered by Ollama", "LLM Intelligence",
            "Instant sitewide context querying, automated compliance checks, and intelligent building code navigation."
        ), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(feature_card(
            "👁️", "Automated Site Surveillance", "Computer Vision",
            "Real-time monitoring for Personal Protective Equipment (PPE) compliance and active site hazard detection."
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(feature_card(
            "📈", "Predictive Risk Modeling", "Machine Learning",
            "Accurate forecasting for cost overruns and potential schedule delays before they impact your timeline."
        ), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(feature_card(
            "📊", "Performance Dashboard", "Real-Time Analytics",
            "Unified telemetry tracking progress metrics, budget utilization, and critical project health indicators."
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="hub-card" style="text-align:center;">
            <span class="hub-card-tag">BUILT FOR MODERN SITE TEAMS</span>
            <h4 style="margin-top: 8px !important;">One Hub. Every Insight.</h4>
            <p class="hub-card-body">
                From ground-break to hand-off, Construction Intelligence Hub keeps budgets, schedules,
                safety, and site conditions visible in a single, connected workspace.
            </p>
        </div>
    """, unsafe_allow_html=True)
