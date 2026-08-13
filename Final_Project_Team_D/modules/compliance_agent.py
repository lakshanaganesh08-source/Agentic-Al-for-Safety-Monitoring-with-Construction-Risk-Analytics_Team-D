"""
Compliance Agent — Streamlit page for construction standards validation and regulatory compliance.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database.db import get_db
from database import models
from utils.compliance_agent import (
    assess_compliance,
    detect_policy_violations,
    save_compliance_assessment,
    get_compliance_trend,
)
from utils.styling import page_hero, stat_card, status_strip


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
    return {"COMPLIANT": "#00E676", "AT_RISK": "#FFAB00", "NON_COMPLIANT": "#FF5252", "PARTIAL": "#7C3AED"}.get(severity, "#8B949E")


def render():
    project = _get_project()
    project_id = int(project["id"]) if project else None
    project_name = project["name"] if project else "No Project"

    page_hero(
        "📋", "Compliance Agent",
        f"Construction standards validation, regulation monitoring &amp; policy violation detection for <b>{project_name}</b>",
        badge="REGULATORY COMPLIANCE AGENT",
    )

    # Latest compliance score KPI row
    latest_score = None
    latest_status = "—"
    if project_id:
        with get_db() as conn:
            latest_score = models.get_latest_compliance_score(conn, project_id)
            logs = models.list_compliance_logs(conn, project_id, limit=1)
            if logs:
                latest_status = logs[0].get("status") or "—"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        val = f"{latest_score:.0f}%" if latest_score is not None else "—"
        color = _severity_color(latest_status)
        st.markdown(stat_card("📊", "Compliance Score", val, latest_status, color), unsafe_allow_html=True)
    with k2:
        with get_db() as conn:
            violations = detect_policy_violations(conn, project_id) if project_id else []
        st.markdown(stat_card("⚠️", "Policy Violations", str(len(violations)), "Active violations", "#FF5252" if violations else "#00E676"), unsafe_allow_html=True)
    with k3:
        with get_db() as conn:
            inspections = models.list_inspections(conn, project_id, limit=10) if project_id else []

        compliant = sum(1 for i in inspections if i.get("result") == "COMPLIANT")
        total = len(inspections)

        if total > 0:
            inspection_ratio = compliant / total
            rate = f"{inspection_ratio * 100:.0f}%"
            subtitle = f"{compliant}/{total} compliant"
        else:
            inspection_ratio = 0
            rate = "0%"
            subtitle = "No inspections"

        color = "#00E676" if inspection_ratio >= 0.9 else "#FFAB00"

        st.markdown(
            stat_card(
                "👁️",
                "Inspection Rate",
                rate,
                subtitle,
                color,
            ),
            unsafe_allow_html=True,
        )

    with k4:
        with get_db() as conn:
            logs = models.list_compliance_logs(conn, project_id, limit=1) if project_id else []
        st.markdown(stat_card("📈", "Assessments", str(len(logs)), "Total conducted", "#00E5FF"), unsafe_allow_html=True)

    st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>🔍 Compliance Assessment Controls</h4>
            <span class="hub-card-tag">Run comprehensive compliance analysis using project data</span>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("##### 📋 Assessment Scope")
        assessment_scope = st.multiselect(
            "Compliance Areas to Check",
            [
                "Site Inspections",
                "Incident Rate Compliance",
                "PPE Requirements (OSHA 1926)",
                "Safety Training Documentation",
                "Equipment Safety Standards",
            ],
            default=[
                "Site Inspections",
                "Incident Rate Compliance",
                "PPE Requirements (OSHA 1926)",
                "Safety Training Documentation",
                "Equipment Safety Standards",
            ],
        )

    with col_b:
        st.markdown("##### ⚙️ Assessment Options")
        include_violations = st.checkbox("Include Policy Violation Detection", value=True)
        generate_recommendations = st.checkbox("Generate Recommendations", value=True)
        save_to_db = st.checkbox("Save Assessment to Database", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔎 Run Compliance Assessment", type="primary", use_container_width=True):
        if not project_id:
            st.error("No active project found. Initialize the database first.")
        else:
            with st.spinner("🔄 Analyzing compliance data..."):
                with get_db() as conn:
                    assessment = assess_compliance(conn, project_id)
                    
                    if save_to_db:
                        log_id = save_compliance_assessment(conn, project_id, assessment)
                    else:
                        log_id = "N/A"

            color = _severity_color(assessment.status)
            st.markdown(f"""
                <div class="hub-card" style="text-align: center; border: 2px solid {color};
                            margin-bottom: 20px; box-shadow: 0 0 40px {color}22;">
                    <span style="color: {color}; font-weight: 700; letter-spacing: 1px;">{assessment.status} COMPLIANCE</span>
                    <h1 style="color: {color}; font-size: 3.2rem; margin: 8px 0;">{assessment.overall_percentage:.0f}%</h1>
                    <p style="color: #C9D1D9;">Assessment #{log_id} saved to compliance history</p>
                </div>
            """, unsafe_allow_html=True)

            # Display individual compliance checks
            st.markdown("<h5 style='color: #F0F6FC;'>📋 Individual Compliance Checks</h5>", unsafe_allow_html=True)
            for check in assessment.checks:
                cc = _severity_color(check.status)
                st.markdown(status_strip(cc, f"{check.standard} — {check.score:.0f}%", check.notes), unsafe_allow_html=True)
                if check.violations:
                    for violation in check.violations:
                        st.markdown(f"<p style='color: #FF5252; margin-left: 20px; font-size: 0.85rem;'>• {violation}</p>", unsafe_allow_html=True)

            # Display recommendations
            if generate_recommendations and assessment.recommendations:
                st.markdown("<h5 style='color: #F0F6FC; margin-top: 16px;'>💡 Compliance Recommendations</h5>", unsafe_allow_html=True)
                for rec in assessment.recommendations:
                    st.markdown(status_strip(color, "• Action", rec), unsafe_allow_html=True)

            # Display policy violations
            if include_violations:
                with get_db() as conn:
                    violations = detect_policy_violations(conn, project_id)
                
                if violations:
                    st.markdown("<h5 style='color: #FF5252; margin-top: 16px;'>⚠️ Detected Policy Violations</h5>", unsafe_allow_html=True)
                    for violation in violations:
                        vc = {"CRITICAL": "#FF5252", "HIGH": "#FF5252", "MODERATE": "#FFAB00", "LOW": "#00E676"}.get(violation["severity"], "#8B949E")
                        st.markdown(status_strip(vc, f"{violation['type']} — {violation['severity']}", violation["description"]), unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #8B949E; margin-left: 20px; font-size: 0.8rem;'>📍 {violation['location']} | 🕒 {violation['detected_at']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #00E5FF; margin-left: 20px; font-size: 0.8rem;'>📋 {violation['action_required']}</p>", unsafe_allow_html=True)
                else:
                    st.success("✅ No policy violations detected.")

    # Compliance history charts
    if project_id:
        with get_db() as conn:
            history = get_compliance_trend(conn, project_id, limit=15)

        if history:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00E5FF;'>📈 Compliance Score History</h4>", unsafe_allow_html=True)

            hist_df = pd.DataFrame(history)
            theme = _chart_theme()
            c1, c2 = st.columns(2, gap="large")

            with c1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist_df["date"], y=hist_df["percentage"],
                    mode="lines+markers", name="Compliance Score",
                    line=dict(color="#00E5FF", width=3), marker=dict(size=8),
                ))
                fig.update_layout(**theme, yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                status_counts = hist_df["status"].value_counts()
                fig_pie = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    hole=0.4,
                    color_discrete_sequence=["#00E676", "#FFAB00", "#FF5252", "#7C3AED"]
                )
                fig_pie.update_layout(**theme, yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_pie, use_container_width=True)

        # Recent compliance logs
        with get_db() as conn:
            recent_logs = models.list_compliance_logs(conn, project_id, limit=8)
        
        if recent_logs:
            st.markdown("<h4 style='color: #00E5FF; margin-top: 20px;'>📋 Recent Compliance Logs</h4>", unsafe_allow_html=True)
            for log in recent_logs:
                color = _severity_color(log.get("status", "UNKNOWN"))
                st.markdown(f"""
                    <div class="hub-strip" style="border-left-color: {color};">
                        <b>{log.get('standard', 'Unknown')}</b> — {log.get('status', 'Unknown')}
                        <p>Score: {log.get('percentage', 0):.0f}% | {log.get('created_at', '')}</p>
                    </div>
                """, unsafe_allow_html=True)
