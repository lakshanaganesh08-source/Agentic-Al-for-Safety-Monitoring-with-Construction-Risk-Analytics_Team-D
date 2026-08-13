"""
Safety Agent — Streamlit page for worker safety monitoring, PPE CV,
behavior detection, accident zones, and AI recommendations.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image

from database.db import get_db
from database import models
from utils.safety_agent import (
    analyze_ppe_image,
    compute_safety_score,
    detect_unsafe_behaviors,
    generate_safety_recommendations,
    get_accident_prone_zones,
    save_safety_assessment,
    _worker_compliance_from_logs,
)
from utils.cv_analyzer import bgr_to_rgb
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
    return {"pass": "#00E676", "warning": "#FFAB00", "danger": "#FF5252"}.get(severity, "#8B949E")


def render():
    project = _get_project()
    project_id = int(project["id"]) if project else None
    project_name = project["name"] if project else "No Project"

    page_hero(
        "🦺", "Safety Agent",
        f"Worker compliance, safety incidents &amp; AI recommendations for <b>{project_name}</b>",
        badge="WORKER SAFETY AGENT",
    )

    assessment = None
    if project_id:
        with get_db() as conn:
            assessment = compute_safety_score(conn, project_id)

    score = assessment.safety_score if assessment else 100.0
    score_color = "#00E676" if score >= 85 else ("#FFAB00" if score >= 70 else "#FF5252")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(stat_card("🛡️", "Safety Score", f"{score:.0f}%", "Composite index", score_color), unsafe_allow_html=True)
    with k2:
        total_incidents = len(assessment.accident_zones) if assessment else 0
        st.markdown(stat_card("⚠️", "Active Hazards", str(total_incidents), "Site zones monitored", "#FFAB00" if total_incidents else "#00E676"), unsafe_allow_html=True)
    with k3:
        comp = f"{assessment.workers_compliant}/{assessment.workers_total}" if assessment else "—"
        st.markdown(stat_card("👷", "Compliant Workers", comp, "Safety roster", "#00E5FF"), unsafe_allow_html=True)
    with k4:
        zones_high = sum(1 for z in (assessment.accident_zones if assessment else []) if z["risk_level"] == "HIGH")
        st.markdown(stat_card("📍", "High-Risk Zones", str(zones_high), "Accident-prone areas", "#FFAB00"), unsafe_allow_html=True)

    st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

    tab_monitor, tab_zones, tab_ai = st.tabs([
        "👷 Worker Compliance", "📍 Accident Zones", "🤖 AI Recommendations",
    ])

    # --- Worker Compliance Tab ---
    with tab_monitor:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
                <h4>👷 Worker Safety Compliance Monitor</h4>
                <span class="hub-card-tag">Live roster from SQLite with safety compliance tracking</span>
            </div>
        """, unsafe_allow_html=True)

        if project_id:
            with get_db() as conn:
                workers = _worker_compliance_from_logs(conn, project_id)
                behaviors = detect_unsafe_behaviors(conn, project_id)

            if workers:
                rows = [{
                    "Worker": w.name,
                    "Role": w.role,
                    "Zone": w.zone,
                    "Helmet": "✅" if w.helmet_ok else "❌",
                    "Vest": "✅" if w.vest_ok else "❌",
                    "Compliance": f"{w.compliance_pct:.0f}%",
                    "Status": w.ppe_status,
                } for w in workers]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                comp_df = pd.DataFrame({
                    "Worker": [w.name for w in workers],
                    "Compliance %": [w.compliance_pct for w in workers],
                })
                theme = _chart_theme()
                fig = px.bar(comp_df, x="Worker", y="Compliance %", color="Compliance %",
                             color_continuous_scale=["#FF5252", "#FFAB00", "#00E676"])
                fig.update_layout(**theme, showlegend=False, coloraxis_showscale=False, yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No workers seeded for this project.")

            if behaviors:
                st.markdown("<h5 style='color: #FFAB00;'>⚠️ Unsafe Behavior Detections</h5>", unsafe_allow_html=True)
                for b in behaviors:
                    bc = _severity_color(b.severity)
                    st.markdown(status_strip(bc, f"{b.zone} — {b.behavior}", f"Source: {b.source}"), unsafe_allow_html=True)
            else:
                st.success("No unsafe behaviors detected from incident and safety logs.")

            if st.button("💾 Save Safety Score Snapshot", type="primary", key="save_safety"):
                with get_db() as conn:
                    fresh = compute_safety_score(conn, project_id)
                    log_id = save_safety_assessment(conn, project_id, fresh)
                st.success(f"Safety assessment #{log_id} saved (score: {fresh.safety_score}%).")

    # --- Accident Zones Tab ---
    with tab_zones:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
                <h4>📍 Accident-Prone Zone Analysis</h4>
                <span class="hub-card-tag">Incident density heatmap by site zone</span>
            </div>
        """, unsafe_allow_html=True)

        if project_id:
            with get_db() as conn:
                zones = get_accident_prone_zones(conn, project_id)

            zdf = pd.DataFrame(zones)
            theme = _chart_theme()

            c1, c2 = st.columns(2, gap="large")
            with c1:
                fig_bar = px.bar(
                    zdf, x="zone", y="incident_count", color="risk_level",
                    color_discrete_map={"HIGH": "#FF5252", "MODERATE": "#FFAB00", "LOW": "#00E676"},
                )
                fig_bar.update_layout(**theme, xaxis_title="Zone", yaxis_title="Incidents", yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_bar, use_container_width=True)

            with c2:
                fig_pie = px.pie(zdf, names="zone", values="incident_count", hole=0.4,
                                 color_discrete_sequence=px.colors.sequential.Reds_r)
                fig_pie.update_layout(**theme)
                st.plotly_chart(fig_pie, use_container_width=True)

            st.dataframe(zdf.rename(columns={
                "zone": "Zone", "incident_count": "Incidents", "risk_level": "Risk Level",
            }), use_container_width=True, hide_index=True)

    # --- AI Recommendations Tab ---
    with tab_ai:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
                <h4>🤖 AI Safety Recommendations</h4>
                <span class="hub-card-tag">Powered by Ollama (local LLM)</span>
            </div>
        """, unsafe_allow_html=True)

        if project_id and assessment:
            if st.button("🧠 Generate Safety Recommendations", type="primary", use_container_width=True):
                with st.spinner("Consulting Ollama safety advisor..."):
                    text, ollama_ok = generate_safety_recommendations(assessment, project_name)

                if ollama_ok:
                    st.markdown("""
                        <div class="hub-strip" style="border-left-color: #00E676;">
                            <span style="color: #00E676;">✅ Ollama Connected</span>
                            <p>Recommendations generated by local llama3.2 model.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Ollama unavailable — showing rule-based fallback recommendations.")

                st.markdown(f"""
                    <div class="hub-card" style="margin-top: 12px;">
                        <h4 style="color: #00E5FF;">Safety Advisory Report</h4>
                        <p class="hub-card-body" style="white-space: pre-wrap;">{text}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Safety score history
            with get_db() as conn:
                logs = models.list_safety_logs(conn, project_id, limit=10)

            if logs:
                st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color: #00E5FF;'>📈 Safety Score History</h5>", unsafe_allow_html=True)
                ldf = pd.DataFrame({
                    "Date": [l["created_at"][:16] for l in reversed(logs)],
                    "Score": [l["safety_score"] for l in reversed(logs) if l.get("safety_score")],
                })
                if not ldf.empty:
                    theme = _chart_theme()
                    fig = px.line(ldf, x="Date", y="Score", markers=True, color_discrete_sequence=["#00E676"])
                    fig.update_traces(line=dict(width=3))
                    fig.update_layout(**theme, yaxis=dict(range=[40, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                    st.plotly_chart(fig, use_container_width=True)
