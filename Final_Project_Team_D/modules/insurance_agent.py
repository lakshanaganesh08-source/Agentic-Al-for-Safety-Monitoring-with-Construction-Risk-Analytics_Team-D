"""
Insurance Agent — Streamlit page for insurance exposure analysis and claim risk prediction.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database.db import get_db
from database import models
from utils.insurance_agent import (
    assess_insurance_risk,
    save_insurance_assessment,
    get_insurance_trend,
    document_claim,
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
    return {"LOW": "#00E676", "MODERATE": "#FFAB00", "HIGH": "#FF5252", "CRITICAL": "#FF1744"}.get(severity, "#8B949E")


def render():
    project = _get_project()
    project_id = int(project["id"]) if project else None
    project_name = project["name"] if project else "No Project"

    page_hero(
        "🛡️", "Insurance Agent",
        f"Insurance exposure analysis, incident severity assessment &amp; claim risk prediction for <b>{project_name}</b>",
        badge="RISK MANAGEMENT AGENT",
    )

    # Latest insurance risk score KPI row
    latest_score = None
    latest_severity = "—"
    if project_id:
        with get_db() as conn:
            latest_score = models.get_insurance_risk_score(conn, project_id)
            logs = models.list_insurance_logs(conn, project_id, limit=1)
            if logs:
                latest_severity = logs[0].get("severity") or "—"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        val = f"{latest_score:.0f}" if latest_score is not None else "—"
        color = _severity_color(latest_severity)
        st.markdown(stat_card("📊", "Insurance Risk Score", val, latest_severity, color), unsafe_allow_html=True)
    with k2:
        with get_db() as conn:
            total_exposure = models.calculate_total_exposure(conn, project_id) if project_id else 0
        st.markdown(stat_card("💰", "Total Exposure", f"₹{total_exposure:,.0f}", "Estimated liability", "#FF5252" if total_exposure > 50000 else "#00E676"), unsafe_allow_html=True)
    with k3:
        with get_db() as conn:
            incidents = models.list_incidents(conn, project_id, limit=50) if project_id else []
        high_severity = sum(1 for i in incidents if i.get("severity") in ["High", "CRITICAL"])
        st.markdown(stat_card("⚠️", "High-Severity Incidents", str(high_severity), f"of {len(incidents)} total", "#FF5252" if high_severity > 2 else "#00E676"), unsafe_allow_html=True)
    with k4:
        with get_db() as conn:
            logs = models.list_insurance_logs(conn, project_id, limit=1) if project_id else []
        st.markdown(stat_card("📈", "Risk Assessments", str(len(logs)), "Total conducted", "#00E5FF"), unsafe_allow_html=True)

    st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>🔍 Insurance Risk Assessment Controls</h4>
            <span class="hub-card-tag">Run comprehensive insurance risk analysis using project data</span>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("##### 📋 Assessment Scope")
        assessment_scope = st.multiselect(
            "Risk Analysis Components",
            [
                "Incident Severity Analysis",
                "Insurance Exposure Calculation",
                "Claim Risk Prediction",
                "Coverage Adequacy Review",
            ],
            default=[
                "Incident Severity Analysis",
                "Insurance Exposure Calculation",
                "Claim Risk Prediction",
                "Coverage Adequacy Review",
            ],
        )

    with col_b:
        st.markdown("##### ⚙️ Assessment Options")
        include_recommendations = st.checkbox("Generate Risk Mitigation Recommendations", value=True)
        save_to_db = st.checkbox("Save Assessment to Database", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔎 Run Insurance Risk Assessment", type="primary", use_container_width=True):
        if not project_id:
            st.error("No active project found. Initialize the database first.")
        else:
            with st.spinner("🔄 Analyzing insurance risk data..."):
                with get_db() as conn:
                    assessment = assess_insurance_risk(conn, project_id)
                    
                    if save_to_db:
                        log_id = save_insurance_assessment(conn, project_id, assessment)
                    else:
                        log_id = "N/A"

            color = _severity_color(assessment.risk_category)
            st.markdown(f"""
                <div class="hub-card" style="text-align: center; border: 2px solid {color};
                            margin-bottom: 20px; box-shadow: 0 0 40px {color}22;">
                    <span style="color: {color}; font-weight: 700; letter-spacing: 1px;">{assessment.risk_category} INSURANCE RISK</span>
                    <h1 style="color: {color}; font-size: 3.2rem; margin: 8px 0;">{assessment.insurance_risk_score:.0f}</h1>
                    <p style="color: #C9D1D9;">Assessment #{log_id} saved to insurance history</p>
                </div>
            """, unsafe_allow_html=True)

            # Display exposure breakdown
            st.markdown("<h5 style='color: #F0F6FC;'>💰 Insurance Exposure Breakdown</h5>", unsafe_allow_html=True)
            e1, e2, e3, e4 = st.columns(4)
            with e1:
                st.markdown(stat_card("💵", "Total Exposure", f"₹{assessment.exposure.total_exposure:,.0f}", "Estimated liability", "#F0F6FC"), unsafe_allow_html=True)
            with e2:
                st.markdown(stat_card("🔴", "High-Risk Incidents", str(assessment.exposure.high_risk_incidents), "Critical attention needed", "#FF5252"), unsafe_allow_html=True)
            with e3:
                st.markdown(stat_card("🟡", "Moderate-Risk Incidents", str(assessment.exposure.moderate_risk_incidents), "Monitor closely", "#FFAB00"), unsafe_allow_html=True)
            with e4:
                st.markdown(stat_card("🟢", "Low-Risk Incidents", str(assessment.exposure.low_risk_incidents), "Routine tracking", "#00E676"), unsafe_allow_html=True)
            
            st.markdown(status_strip(
                "#00E5FF" if assessment.exposure.coverage_adequacy == "ADEQUATE" else "#FFAB00",
                "Coverage Adequacy",
                assessment.exposure.coverage_adequacy
            ), unsafe_allow_html=True)

            # Display claim prediction
            st.markdown("<h5 style='color: #F0F6FC; margin-top: 16px;'>📊 Claim Risk Prediction</h5>", unsafe_allow_html=True)
            cp_color = _severity_color(assessment.claim_prediction.risk_level)
            st.markdown(status_strip(
                cp_color,
                f"Claim Probability: {assessment.claim_prediction.claim_probability:.0f}%",
                f"Risk Level: {assessment.claim_prediction.risk_level}"
            ), unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="hub-strip" style="border-left-color: #00E5FF;">
                    <b>Estimated Annual Claims</b>
                    <p>₹{assessment.claim_prediction.estimated_annual_claims:,.0f} (Range: ₹{assessment.claim_prediction.confidence_interval[0]:,.0f} - ₹{assessment.claim_prediction.confidence_interval[1]:,.0f})</p>
                </div>
            """, unsafe_allow_html=True)

            if assessment.claim_prediction.contributing_factors:
                st.markdown("<p style='color: #8B949E; font-size: 0.85rem; margin-top: 8px;'>Contributing Factors:</p>", unsafe_allow_html=True)
                for factor in assessment.claim_prediction.contributing_factors:
                    st.markdown(f"<p style='color: #F0F6FC; margin-left: 20px; font-size: 0.8rem;'>• {factor}</p>", unsafe_allow_html=True)

            # Display severity analysis
            if assessment.severity_analysis:
                st.markdown("<h5 style='color: #F0F6FC; margin-top: 16px;'>⚠️ Incident Severity Analysis</h5>", unsafe_allow_html=True)
                for severity in assessment.severity_analysis[:5]:  # Show top 5
                    sc = _severity_color(severity.severity)
                    st.markdown(status_strip(sc, f"{severity.incident_type} — {severity.severity}", f"Score: {severity.severity_score:.1f} | Potential Claim: ₹{severity.potential_claim_cost:,.0f}"), unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #00E5FF; margin-left: 20px; font-size: 0.8rem;'>📋 {severity.recommended_action}</p>", unsafe_allow_html=True)

            # Display recommendations
            if include_recommendations and assessment.recommendations:
                st.markdown("<h5 style='color: #F0F6FC; margin-top: 16px;'>💡 Risk Mitigation Recommendations</h5>", unsafe_allow_html=True)
                for rec in assessment.recommendations:
                    st.markdown(status_strip(color, "• Action", rec), unsafe_allow_html=True)

    # Insurance history charts
    if project_id:
        with get_db() as conn:
            history = get_insurance_trend(conn, project_id, limit=15)

        if history:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00E5FF;'>📈 Insurance Risk History</h4>", unsafe_allow_html=True)

            hist_df = pd.DataFrame(history)
            theme = _chart_theme()
            c1, c2 = st.columns(2, gap="large")

            with c1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist_df["date"], y=hist_df["risk_score"],
                    mode="lines+markers", name="Insurance Risk Score",
                    line=dict(color="#FF5252", width=3), marker=dict(size=8),
                ))
                fig.update_layout(**theme, yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig_bar = px.bar(
                    hist_df, x="date", y="exposure",
                    color="severity",
                    color_discrete_map={"LOW": "#00E676", "MODERATE": "#FFAB00", "HIGH": "#FF5252", "CRITICAL": "#FF1744"}
                )
                fig_bar.update_layout(**theme, showlegend=True, yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_bar, use_container_width=True)

        # Recent insurance logs
        with get_db() as conn:
            recent_logs = models.list_insurance_logs(conn, project_id, limit=8)
        
        if recent_logs:
            st.markdown("<h4 style='color: #00E5FF; margin-top: 20px;'>📋 Recent Insurance Logs</h4>", unsafe_allow_html=True)
            for log in recent_logs:
                color = _severity_color(log.get("severity", "UNKNOWN"))
                st.markdown(f"""
                    <div class="hub-strip" style="border-left-color: {color};">
                        <b>{log.get('severity', 'Unknown')}</b> — Exposure: ₹{log.get('exposure', 0):,.0f}
                        <p>Risk Score: {log.get('claim_risk_score', 0):.0f} | {log.get('created_at', '')}</p>
                    </div>
                """, unsafe_allow_html=True)

    # Claim documentation section
    st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>📝 Document New Claim</h4>
            <span class="hub-card-tag">Record actual insurance claims for tracking and analysis</span>
        </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2, gap="large")
    
    with col_c1:
        with get_db() as conn:
            incidents = models.list_incidents(conn, project_id, limit=20) if project_id else []
        incident_options = {f"{i['id']}: {i['incident_type']}": i["id"] for i in incidents}
        selected_incident = st.selectbox("Select Incident", options=list(incident_options.keys()))
    
    with col_c2:
        claim_type = st.selectbox("Claim Type", ["Property Damage", "Bodily Injury", "Equipment", "Liability", "Other"])
        claim_amount = st.number_input("Claim Amount (₹)", min_value=0, value=0, step=1000)
    
    claim_description = st.text_area("Claim Description", placeholder="Describe the claim details...")
    
    if st.button("📝 Document Claim", type="primary", use_container_width=True):
        if not project_id:
            st.error("No active project found.")
        elif not selected_incident:
            st.error("Please select an incident.")
        else:
            incident_id = incident_options[selected_incident]
            with get_db() as conn:
                claim_log_id = document_claim(
                    conn,
                    project_id,
                    incident_id,
                    claim_amount,
                    claim_type,
                    claim_description
                )
            st.success(f"✅ Claim documented successfully (Log ID: {claim_log_id})")
