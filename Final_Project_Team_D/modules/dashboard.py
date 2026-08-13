import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.dashboard_data import (
    get_budget_progress_chart,
    get_compliance_score_history,
    get_executive_metrics,
    get_incident_heatmap_data,
    get_insurance_risk_history,
    get_recent_risk_scores,
    get_safety_score_history,
    get_site_risk_history,
    get_task_status_breakdown,
)
from utils.styling import page_hero, stat_card


def _chart_theme() -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8B949E", family="Plus Jakarta Sans, sans serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, zeroline=False),
        hoverlabel=dict(bgcolor="#161B22", font_color="#F0F6FC", bordercolor="#00E5FF"),
    )


def render():
    metrics = get_executive_metrics()
    page_hero(
        "📊", "Project Executive Dashboard",
        f"Live overview for <b>{metrics['project_name']}</b> — financials, schedule, safety &amp; materials",
        badge="LIVE OVERVIEW"
    )

    # Section 1 — Financial & Overall Project Performance
    st.markdown("<p style='color: #00E5FF; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.8px; margin-bottom: 8px;'>💰 FINANCIAL & OVERALL PERFORMANCE</p>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        st.markdown(stat_card("💰", "Total Budget", metrics["budget_display"], f"{metrics['status']}", "#00E5FF"), unsafe_allow_html=True)
    with col2:
        st.markdown(stat_card("💸", "Spent To Date", metrics["spent_display"], f"{metrics['spent_pct']}% Utilized", "#F0F6FC"), unsafe_allow_html=True)
    with col3:
        st.markdown(stat_card("📈", "Overall Progress", f"{metrics['progress']:.1f}%", "Completion percentage", "#00E5FF"), unsafe_allow_html=True)
    with col4:
        st.markdown(stat_card("🧱", "Material Spend", metrics["material_display"], f"{metrics.get('material_items', 0)} BOQ items", "#7C3AED"), unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Section 2 — Safety, Compliance & Site Intelligence
    st.markdown("<p style='color: #00E676; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.8px; margin-bottom: 8px;'>🛡️ SAFETY, COMPLIANCE & RISK INTELLIGENCE</p>", unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns(4, gap="medium")
    site_risk = metrics.get("site_risk_score", 0)
    site_color = "#FF5252" if site_risk >= 55 else ("#FFAB00" if site_risk >= 35 else "#00E676")
    compliance_score = metrics.get("compliance_score", 0)
    compliance_color = "#00E676" if compliance_score >= 90 else ("#FFAB00" if compliance_score >= 70 else "#FF5252")
    insurance_score = metrics.get("insurance_score", 0)
    insurance_color = "#00E676" if insurance_score < 40 else ("#FFAB00" if insurance_score < 60 else "#FF5252")

    with a1:
        st.markdown(stat_card("⚠️", "Site Risk Score", f"{site_risk:.0f}%", "Site Risk Agent", site_color), unsafe_allow_html=True)
    with a2:
        st.markdown(stat_card("⛑️", "Safety Score", f"{metrics['safety_score']}%", f"{metrics['incident_count']} incidents logged", "#00E676"), unsafe_allow_html=True)
    with a3:
        st.markdown(stat_card("📋", "Compliance Score", f"{compliance_score:.0f}%", "Regulatory compliance", compliance_color), unsafe_allow_html=True)
    with a4:
        st.markdown(stat_card("🛡️", "Insurance Risk", f"{insurance_score:.0f}", "Claim risk prediction", insurance_color), unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Section 3 — Work Schedule & Operations
    st.markdown("<p style='color: #FFAB00; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.8px; margin-bottom: 8px;'>📋 SCHEDULE & OPERATIONAL TELEMETRY</p>", unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4, gap="medium")
    var = metrics["schedule_variance_days"]
    var_label = f"{'▼' if var < 0 else '▲'} {abs(var)} Days"
    var_color = "#FF5252" if var < 0 else "#00E676"

    with b1:
        st.markdown(stat_card("📅", "Schedule Variance", var_label, "vs task baseline", var_color), unsafe_allow_html=True)
    with b2:
        st.markdown(stat_card("📋", "Open Tasks", str(metrics["open_tasks"]), "Pending + In Progress", "#FFAB00"), unsafe_allow_html=True)
    with b3:
        st.markdown(stat_card("👷", "Team Velocity", f"{metrics['open_tasks']} active", "Tasks in progress", "#00E5FF"), unsafe_allow_html=True)
    with b4:
        st.markdown(stat_card("🎯", "Project Status", metrics["status"], "Current phase", "#00E676"), unsafe_allow_html=True)

    st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

    df = get_budget_progress_chart()
    theme = _chart_theme()

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                <h4>📈 Budget vs Actual Spend (₹)</h4>
                <span class="hub-card-tag">Financial Trend — DB-backed</span>
            </div>
        """, unsafe_allow_html=True)
        fig_cost = px.line(df, x="Month", y=["Planned_Budget", "Actual_Cost"], markers=True, color_discrete_sequence=["#8B949E", "#00E5FF"])
        fig_cost.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_cost.update_layout(**theme)
        st.plotly_chart(fig_cost, use_container_width=True)

    with col_b:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                <h4>📊 Progress Tracking (%)</h4>
                <span class="hub-card-tag">Planned vs Actual</span>
            </div>
        """, unsafe_allow_html=True)
        fig_prog = px.bar(df, x="Month", y=["Planned_Progress", "Actual_Progress"], barmode="group", color_discrete_sequence=["#30363D", "#FF2E93"])
        fig_prog.update_layout(**theme)
        st.plotly_chart(fig_prog, use_container_width=True)

    col_c, col_d = st.columns(2, gap="large")

    with col_c:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                <h4>🔥 Incident Zone Heatmap</h4>
                <span class="hub-card-tag">Safety telemetry by zone</span>
            </div>
        """, unsafe_allow_html=True)
        heat_df = get_incident_heatmap_data()
        fig_heat = px.bar(
            heat_df, x="Zone", y="Incidents", color="Incidents",
            color_continuous_scale=["#21262D", "#FF5252"],
        )
        fig_heat.update_layout(**theme, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_d:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                <h4>📌 Task Status Breakdown</h4>
                <span class="hub-card-tag">Operations snapshot</span>
            </div>
        """, unsafe_allow_html=True)
        task_df = get_task_status_breakdown()
        fig_tasks = px.pie(task_df, names="Status", values="Count", hole=0.45, color_discrete_sequence=["#00E676", "#00E5FF", "#FFAB00"])
        fig_tasks.update_layout(**theme)
        st.plotly_chart(fig_tasks, use_container_width=True)

    risk_df = get_recent_risk_scores()
    site_risk_df = get_site_risk_history()
    safety_df = get_safety_score_history()
    compliance_df = get_compliance_score_history()
    insurance_df = get_insurance_risk_history()

    if not site_risk_df.empty or not safety_df.empty:
        col_e, col_f = st.columns(2, gap="large")
        with col_e:
            st.markdown("""
                <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                    <h4>⚠️ Site Risk History</h4>
                    <span class="hub-card-tag">Site Risk Agent assessments</span>
                </div>
            """, unsafe_allow_html=True)
            if not site_risk_df.empty:
                fig_site = go.Figure()
                fig_site.add_trace(go.Scatter(
                    x=site_risk_df["Date"], y=site_risk_df["Site Risk Score"],
                    mode="lines+markers", name="Site Risk",
                    line=dict(color="#FF7043", width=3), marker=dict(size=8),
                ))
                fig_site.update_layout(**theme, yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_site, use_container_width=True)
            else:
                st.info("📊 No historical data available. Run Site Risk Agent to populate history.")

        with col_f:
            st.markdown("""
                <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                    <h4>🦺 Safety Score History</h4>
                    <span class="hub-card-tag">Safety Agent telemetry</span>
                </div>
            """, unsafe_allow_html=True)
            if not safety_df.empty:
                fig_safe = go.Figure()
                fig_safe.add_trace(go.Scatter(
                    x=safety_df["Date"], y=safety_df["Safety Score"],
                    mode="lines+markers", name="Safety Score",
                    line=dict(color="#00E676", width=3), marker=dict(size=8),
                ))
                fig_safe.update_layout(**theme, yaxis=dict(range=[40, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_safe, use_container_width=True)
            else:
                st.info("📊 No historical data available. Run Safety Agent to populate history.")

    # New Phase 4: Compliance and Insurance history
    if not compliance_df.empty or not insurance_df.empty:
        st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
        col_g, col_h = st.columns(2, gap="large")
        
        with col_g:
            st.markdown("""
                <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                    <h4>📋 Compliance Score History</h4>
                    <span class="hub-card-tag">Compliance Agent assessments</span>
                </div>
            """, unsafe_allow_html=True)
            if not compliance_df.empty:
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Scatter(
                    x=compliance_df["Date"], y=compliance_df["Compliance Score"],
                    mode="lines+markers", name="Compliance Score",
                    line=dict(color="#7C3AED", width=3), marker=dict(size=8),
                ))
                fig_comp.update_layout(**theme, yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.info("📊 No historical data available. Run Compliance Agent to populate history.")
        
        with col_h:
            st.markdown("""
                <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                    <h4>🛡️ Insurance Risk History</h4>
                    <span class="hub-card-tag">Insurance Agent assessments</span>
                </div>
            """, unsafe_allow_html=True)
            if not insurance_df.empty:
                fig_ins = go.Figure()
                fig_ins.add_trace(go.Scatter(
                    x=insurance_df["Date"], y=insurance_df["Insurance Risk Score"],
                    mode="lines+markers", name="Insurance Risk",
                    line=dict(color="#FF5252", width=3), marker=dict(size=8),
                ))
                fig_ins.update_layout(**theme, yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
                st.plotly_chart(fig_ins, use_container_width=True)
            else:
                st.info("📊 No historical data available. Run Insurance Agent to populate history.")

    if not risk_df.empty:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                <h4>⏳ Delay Risk History</h4>
                <span class="hub-card-tag">Recent ML assessments</span>
            </div>
        """, unsafe_allow_html=True)
        fig_risk = go.Figure()
        fig_risk.add_trace(go.Scatter(
            x=risk_df["Date"], y=risk_df["Risk Score"],
            mode="lines+markers", name="Risk Score",
            line=dict(color="#FFAB00", width=3), marker=dict(size=8),
        ))
        fig_risk.update_layout(**theme, yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False))
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("📊 No historical data available. Run Delay Prediction to populate history.")
