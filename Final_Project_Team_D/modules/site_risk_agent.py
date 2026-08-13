"""
Site Risk Agent — Streamlit page for construction site risk monitoring.
"""

from __future__ import annotations

import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database.db import get_db
from database import models
from utils.site_risk_agent import (
    assess_site_risk,
    prioritize_risks,
    save_site_risk_assessment,
)
from utils.styling import page_hero, stat_card, status_strip


PRIORITY_COLORS = {
    "CRITICAL": "#FF5252",
    "HIGH": "#FF7043",
    "MODERATE": "#FFAB00",
    "LOW": "#00E676",
}


def _chart_theme() -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8B949E", family="Plus Jakarta Sans, sans serif"),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, zeroline=False),
        hoverlabel=dict(bgcolor="#161B22", font_color="#F0F6FC", bordercolor="#00E5FF"),
    )


def _get_project() -> dict | None:
    with get_db() as conn:
        return models.get_default_project(conn)


def _severity_color(severity: str) -> str:
    return {"pass": "#00E676", "warning": "#FFAB00", "danger": "#FF5252"}.get(severity, "#8B949E")


def render():
    project = _get_project()
    project_id = int(project["id"]) if project else None
    project_name = project["name"] if project else "No Project"

    page_hero(
        "⚠️", "Site Risk Agent",
        f"Monitor site activities, detect hazards &amp; score environmental risk for <b>{project_name}</b>",
        badge="RISK INTELLIGENCE AGENT",
    )

    # Latest score KPI row
    latest_score = None
    latest_priority = "—"
    if project_id:
        with get_db() as conn:
            latest_score = models.get_latest_risk_score(conn, project_id, risk_type="site")
            logs = models.list_risk_logs(conn, project_id, limit=1, risk_type="site")
            if logs:
                latest_priority = logs[0].get("priority") or "—"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        val = f"{latest_score:.0f}%" if latest_score is not None else "—"
        color = PRIORITY_COLORS.get(latest_priority, "#00E5FF")
        st.markdown(stat_card("📊", "Site Risk Score", val, latest_priority, color), unsafe_allow_html=True)
    with k2:
        with get_db() as conn:
            inc = models.count_incidents(conn, project_id) if project_id else 0
        st.markdown(stat_card("🚨", "Incidents Logged", str(inc), "DB telemetry", "#FF5252" if inc > 2 else "#F0F6FC"), unsafe_allow_html=True)
    with k3:
        with get_db() as conn:
            insp = models.list_inspections(conn, project_id, limit=5) if project_id else []
        failed = sum(1 for i in insp if i.get("result") != "COMPLIANT")
        st.markdown(stat_card("👁️", "CV Flagged", str(failed), "Recent inspections", "#FFAB00"), unsafe_allow_html=True)
    with k4:
        with get_db() as conn:
            tasks = models.list_tasks(conn, project_id) if project_id else []
        active = sum(1 for t in tasks if t["status"] == "In Progress")
        st.markdown(stat_card("🏗️", "Active Tasks", str(active), "Site operations", "#00E5FF"), unsafe_allow_html=True)

    st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>🔍 Site Activity &amp; Condition Assessment</h4>
            <span class="hub-card-tag">Configure current site state for risk scoring</span>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("##### 🌦️ Environmental Factors")
        weather = st.selectbox("Weather Conditions", ["Clear", "Windy", "Rain", "Storm Warning"])
        air_quality = st.selectbox("Air Quality", ["Good", "Moderate", "Poor / Dusty"])
        ground_condition = st.selectbox("Ground Condition", ["Stable", "Wet / Slippery", "Unstable Soil"])

        st.markdown("##### 🏗️ Active Site Activities")
        active_activities = st.multiselect(
            "High-Risk Activities in Progress",
            list([
                "Crane Operations", "Excavation / Trenching", "Concrete Pouring",
                "Scaffolding Work", "Hot Work (Welding)", "Electrical Installation", "General Labor",
            ]),
            default=["Scaffolding Work"],
        )

    with col_b:
        st.markdown("##### 🚜 Equipment Status")
        crane_status = st.selectbox("Tower Crane", list(["All Certified", "Minor Maintenance Due", "Overdue Inspection", "Fault Reported"]))
        excavator_status = st.selectbox("Excavator", list(["All Certified", "Minor Maintenance Due", "Overdue Inspection", "Fault Reported", "Out of Service"]))
        scaffold_status = st.selectbox("Scaffolding Systems", list(["All Certified", "Minor Maintenance Due", "Overdue Inspection", "Fault Reported"]))

        st.markdown("##### ⚠️ Unsafe Conditions Observed")
        unsafe_conditions = st.multiselect(
            "Flagged Conditions",
            [
                "Unsecured scaffolding", "Missing guardrails", "Poor housekeeping / debris",
                "Inadequate lighting", "Blocked emergency exits", "Water pooling",
            ],
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔎 Run Site Risk Assessment", type="primary", use_container_width=True):
        if not project_id:
            st.error("No active project found. Initialize the database first.")
        else:
            equipment_status = {
                "Tower Crane": crane_status,
                "Excavator": excavator_status,
                "Scaffolding": scaffold_status,
            }
            with get_db() as conn:
                assessment = assess_site_risk(
                    conn,
                    project_id=project_id,
                    weather=weather,
                    air_quality=air_quality,
                    ground_condition=ground_condition,
                    active_activities=active_activities,
                    equipment_status=equipment_status,
                    unsafe_conditions=unsafe_conditions,
                )
                log_id = save_site_risk_assessment(conn, project_id, assessment)

            color = PRIORITY_COLORS.get(assessment.priority, "#FFAB00")
            st.markdown(f"""
                <div class="hub-card" style="text-align: center; border: 2px solid {color};
                            margin-bottom: 20px; box-shadow: 0 0 40px {color}22;">
                    <span style="color: {color}; font-weight: 700; letter-spacing: 1px;">{assessment.priority} SITE RISK</span>
                    <h1 style="color: {color}; font-size: 3.2rem; margin: 8px 0;">{assessment.score}%</h1>
                    <p style="color: #C9D1D9;">Assessment #{log_id} saved to risk history</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<h5 style='color: #F0F6FC;'>📋 Risk Factor Breakdown (Prioritized)</h5>", unsafe_allow_html=True)
            for factor in prioritize_risks(assessment.factors):
                fc = _severity_color(factor.severity)
                st.markdown(status_strip(fc, f"{factor.label} — {factor.score:.0f} pts", factor.detail), unsafe_allow_html=True)

            st.markdown("<h5 style='color: #F0F6FC; margin-top: 16px;'>💡 Recommended Actions</h5>", unsafe_allow_html=True)
            for tip in assessment.recommendations:
                st.markdown(status_strip(color, "• Action", tip), unsafe_allow_html=True)

    # Risk history charts
    if project_id:
        with get_db() as conn:
            history = models.list_risk_logs(conn, project_id, limit=15, risk_type="site")

        if history:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00E5FF;'>📈 Site Risk History</h4>", unsafe_allow_html=True)

            hist_df = pd.DataFrame({
                "Date": [h["created_at"][:16] for h in reversed(history)],
                "Score": [h["score"] for h in reversed(history)],
                "Priority": [h.get("priority") or "—" for h in reversed(history)],
            })

            theme = _chart_theme()
            c1, c2 = st.columns(2, gap="large")

            with c1:
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    x=hist_df["Date"], y=hist_df["Score"],
                    mode="lines+markers", name="Site Risk Score",
                    line=dict(color="#FF7043", width=3), marker=dict(size=8),
                ))
                fig_line.update_layout(**theme, yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_line, use_container_width=True)

            with c2:
                # Latest factor breakdown from most recent log
                latest = history[0]
                try:
                    factors_data = json.loads(latest.get("factors_json") or "{}")
                    factor_rows = factors_data.get("factors", [])
                except json.JSONDecodeError:
                    factor_rows = []

                if factor_rows:
                    fdf = pd.DataFrame({
                        "Factor": [f["label"] for f in factor_rows],
                        "Score": [f["score"] for f in factor_rows],
                    })
                    fig_bar = px.bar(fdf, x="Factor", y="Score", color="Score",
                                     color_continuous_scale=["#00E676", "#FFAB00", "#FF5252"])
                    fig_bar.update_layout(**theme, showlegend=False, coloraxis_showscale=False, yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False))
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Run an assessment to see factor breakdown.")

            st.markdown("<h5 style='color: #F0F6FC;'>🗂️ Assessment Log</h5>", unsafe_allow_html=True)
            log_rows = [
                {
                    "ID": f"#{h['id']}",
                    "Score": f"{h['score']:.1f}%",
                    "Priority": h.get("priority") or "—",
                    "Date": h["created_at"],
                }
                for h in history
            ]
            st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)
