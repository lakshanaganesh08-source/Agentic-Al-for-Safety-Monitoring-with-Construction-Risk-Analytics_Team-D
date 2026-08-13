import streamlit as st
import plotly.express as px
from utils.data_gen import get_sample_project_data
from utils.styling import page_hero, stat_card


def render():
    page_hero(
        "📊", "Project Executive Dashboard",
        "High-Level Overview of Project Financials, Timeline Health &amp; Safety Telemetry",
        badge="LIVE OVERVIEW"
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(stat_card("💰", "Total Budget", "$10.0M", "▲ +5% vs initial", "#00E5FF"), unsafe_allow_html=True)
    with col2:
        st.markdown(stat_card("💸", "Spent To Date", "$4.25M", "42.5% Utilized", "#F0F6FC"), unsafe_allow_html=True)
    with col3:
        st.markdown(stat_card("📅", "Schedule Variance", "-4 Days", "▼ Behind Schedule", "#FF5252"), unsafe_allow_html=True)
    with col4:
        st.markdown(stat_card("🦺", "Safety Score", "98%", "▲ +2% Incident-free", "#00E676"), unsafe_allow_html=True)

    st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

    df = get_sample_project_data()
    col_a, col_b = st.columns(2, gap="large")

    chart_theme = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8B949E", family="Plus Jakarta Sans, sans serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False),
        hoverlabel=dict(bgcolor="#161B22", font_color="#F0F6FC", bordercolor="#00E5FF"),
    )

    with col_a:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                <h4>📈 Budget vs Actual Spend ($)</h4>
                <span class="hub-card-tag">Financial Trend</span>
            </div>
        """, unsafe_allow_html=True)
        fig_cost = px.line(df, x="Month", y=["Planned_Budget", "Actual_Cost"], markers=True, color_discrete_sequence=["#8B949E", "#00E5FF"])
        fig_cost.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_cost.update_layout(**chart_theme)
        st.plotly_chart(fig_cost, use_container_width=True)

    with col_b:
        st.markdown("""
            <div class="hub-card" style="margin-bottom: 15px; padding: 18px 20px;">
                <h4>📊 Progress Tracking (%)</h4>
                <span class="hub-card-tag">Planned vs Actual</span>
            </div>
        """, unsafe_allow_html=True)
        fig_prog = px.bar(df, x="Month", y=["Planned_Progress", "Actual_Progress"], barmode="group", color_discrete_sequence=["#30363D", "#FF2E93"])
        fig_prog.update_layout(**chart_theme)
        st.plotly_chart(fig_prog, use_container_width=True)
