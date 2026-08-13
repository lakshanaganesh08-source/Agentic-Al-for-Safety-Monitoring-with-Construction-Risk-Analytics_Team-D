import json
import streamlit as st
from database.db import get_db
from database import models
from utils.ml_models import train_delay_model, predict_delay_risk
from utils.styling import page_hero, status_strip


def _get_project_id() -> int | None:
    with get_db() as conn:
        project = models.get_default_project(conn)
        return int(project["id"]) if project else None


def _action_tips(risk_level: str) -> list[str]:
    if risk_level == "HIGH":
        return [
            "Negotiate expedited shipping options for delayed materials.",
            "Implement overtime shifts or reallocate workforce to critical path tasks.",
            "Review buffer allocations in project schedule baseline.",
            "Escalate to project steering committee for contingency budget release.",
        ]
    if risk_level == "MODERATE":
        return [
            "Track material lead times weekly with key suppliers.",
            "Prepare weather contingency measures for outdoor activities.",
            "Increase daily stand-up frequency for critical-path trades.",
        ]
    return ["Maintain current labor deployment and supply chain pacing."]


def render():
    page_hero(
        "⏳", "Schedule & Delay Risk Prediction",
        "ML-powered timeline bottleneck analysis with database-backed risk history",
        badge="RISK INTELLIGENCE"
    )

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>⚙️ Project Conditions Assessment</h4>
            <span class="hub-card-tag">Tell us about current site conditions</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        weather_risk = st.selectbox(
            "🌧️ Expected Weather Disruptions",
            ["Low", "Medium", "High"],
            help="Forecasted impact of adverse local weather conditions"
        )
        supply_chain = st.selectbox(
            "🚚 Supply Chain Reliability",
            ["High", "Moderate", "Low"],
            help="Availability and delivery timeline stability of critical materials"
        )

    with col2:
        labor_avail = st.slider(
            "👷 Labor Workforce Capacity (%)",
            min_value=50, max_value=100, value=85, step=5,
            help="Current vs planned on-site subcontractor staffing percentage"
        )
        complexity = st.slider(
            "🏗️ Project Complexity",
            min_value=1, max_value=3, value=2,
            help="Structural and MEP complexity factor"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚨 Assess Delay Risk", type="primary", use_container_width=True):
        model = train_delay_model()
        result = predict_delay_risk(model, weather_risk, supply_chain, labor_avail, complexity)

        risk_score = result["risk_score"]
        risk_level = result["risk_level"]
        days_delay = result["predicted_days_delay"]

        if risk_level == "HIGH":
            status_color, status_bg = "#FF5252", "rgba(255, 82, 82, 0.08)"
            status_title = "HIGH DELAY RISK"
            status_desc = f"High probability of critical path slippage (~{days_delay} days). Immediate intervention recommended."
        elif risk_level == "MODERATE":
            status_color, status_bg = "#FFAB00", "rgba(255, 171, 0, 0.08)"
            status_title = "MODERATE DELAY RISK"
            status_desc = f"Minor schedule friction expected (~{days_delay} days delay). Active monitoring required."
        else:
            status_color, status_bg = "#00E676", "rgba(0, 230, 118, 0.08)"
            status_title = "LOW DELAY RISK"
            status_desc = "Project timeline is healthy and well-optimized. Operations are on target."

        st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>📊 Risk Assessment Summary</h3>", unsafe_allow_html=True)

        st.markdown(f"""
            <div class="hub-card" style="text-align: center; border: 2px solid {status_color};
                        background: linear-gradient(180deg, {status_bg}, rgba(13,17,23,0.9));
                        margin-bottom: 25px; box-shadow: 0 0 40px {status_color}22;">
                <span style="color: {status_color}; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; font-size: 0.9rem;">
                    {status_title}
                </span>
                <h1 style="color: {status_color}; font-size: 3.4rem; margin: 6px 0; font-weight: 800;">
                    {risk_score}%
                </h1>
                <p style="color: #F0F6FC; font-size: 1rem; margin: 0 auto; font-weight: 500; max-width: 480px;">
                    {status_desc}
                </p>
                <p style="color: #8B949E; font-size: 0.85rem; margin-top: 8px;">
                    ML confidence: {result['confidence']}%
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h5 style='color: #F0F6FC; margin-bottom: 12px;'>💡 Recommended Action Plan</h5>", unsafe_allow_html=True)
        for tip in _action_tips(risk_level):
            st.markdown(status_strip(status_color, "• Action", tip), unsafe_allow_html=True)

        project_id = _get_project_id()
        if project_id:
            with get_db() as conn:
                models.create_risk_log(
                    conn,
                    score=float(risk_score),
                    priority=risk_level,
                    factors_json=json.dumps(result["factors"]),
                    project_id=project_id,
                )
            st.success("✅ Risk assessment saved to project history.")

    # Show recent history
    project_id = _get_project_id()
    if project_id:
        with get_db() as conn:
            logs = models.list_risk_logs(conn, project_id, limit=5)
        if logs:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00E5FF;'>📋 Recent Risk Assessments</h4>", unsafe_allow_html=True)
            for log in logs:
                color = {"HIGH": "#FF5252", "MODERATE": "#FFAB00", "LOW": "#00E676"}.get(log["priority"], "#8B949E")
                st.markdown(f"""
                    <div class="hub-strip" style="border-left-color: {color};">
                        <b>{log['priority']} — {log['score']:.0f}%</b>
                        <p>{log['created_at']}</p>
                    </div>
                """, unsafe_allow_html=True)
