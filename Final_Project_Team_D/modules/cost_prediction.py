import streamlit as st
import plotly.express as px
from database.db import get_db
from database import models
from utils.ml_models import train_cost_model, predict_cost, cost_breakdown
from utils.styling import page_hero, stat_card


def _get_project_id() -> int | None:
    with get_db() as conn:
        project = models.get_default_project(conn)
        return int(project["id"]) if project else None


def render():
    page_hero(
        "💰", "AI Construction Cost Estimator",
        "Predict total budget requirements powered by trained Machine Learning models",
        badge="ML-POWERED FORECASTING"
    )

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>📋 Project Parameters</h4>
            <span class="hub-card-tag">Fill in the details below to generate an estimate</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        area = st.number_input(
            "📐 Total Built-up Area (sq ft)",
            min_value=100, value=2500, step=100,
            help="Enter total gross floor area across all levels"
        )
        floors = st.number_input(
            "🏢 Number of Floors",
            min_value=1, value=2, step=1,
            help="Total vertical levels planned"
        )

    with col2:
        workers = st.number_input(
            "👷 Average On-site Workers",
            min_value=1, value=20, step=1,
            help="Estimated daily workforce presence"
        )
        days = st.number_input(
            "⏱️ Estimated Duration (Days)",
            min_value=1, value=90, step=5,
            help="Project completion timeline from ground-break to hand-off"
        )

    with col3:
        project_type = st.selectbox(
            "🏗️ Project Type",
            ["Residential", "Commercial", "Industrial", "Infrastructure"],
            help="Building type affects cost multiplier"
        )
        complexity = st.slider(
            "🔧 Complexity Factor",
            min_value=1, max_value=5, value=2,
            help="1=simple, 5=highly complex (affects contingency)"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Calculate Estimated Cost", type="primary", use_container_width=True):
        with st.spinner("🔄 Computing financial forecast..."):
            model = train_cost_model()
            predicted_cost = predict_cost(model, area, floors, workers, days, project_type)
            contingency = predicted_cost * (complexity * 0.02)
            predicted_cost += contingency
            breakdown = cost_breakdown(predicted_cost)

        cost_per_sqft = predicted_cost / area if area > 0 else 0
        daily_burn_rate = predicted_cost / days if days > 0 else 0

        st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 25px;'>📊 Financial Projection Summary</h3>", unsafe_allow_html=True)

        st.markdown(f"""
            <div class="hub-card" style="text-align: center; border: 2px solid #00E5FF; margin-bottom: 25px;
                        box-shadow: 0 0 40px rgba(0,229,255,0.15);">
                <span style="color: #8B949E; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; font-size: 0.9rem;">
                    Estimated Total Construction Cost ({project_type})
                </span>
                <h1 style="background: linear-gradient(135deg, #00E5FF, #7C3AED); -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent; font-size: 3rem; margin: 10px 0 0 0; font-weight: 800;">
                    ₹{predicted_cost:,.2f}
                </h1>
            </div>
        """, unsafe_allow_html=True)

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(stat_card("📐", "Unit Cost", f"₹{cost_per_sqft:,.2f}", "per sq ft", "#F0F6FC"), unsafe_allow_html=True)
        with m_col2:
            st.markdown(stat_card("🔥", "Daily Burn Rate", f"₹{daily_burn_rate:,.2f}", "per day", "#F0F6FC"), unsafe_allow_html=True)
        with m_col3:
            st.markdown(stat_card("👷", "Labor Allocation", f"{workers * days:,}", "man-days", "#F0F6FC"), unsafe_allow_html=True)

        st.markdown("<h5 style='color: #F0F6FC; margin: 20px 0 10px 0;'>Cost Category Breakdown</h5>", unsafe_allow_html=True)
        chart_col, table_col = st.columns([1, 1])
        with chart_col:
            fig = px.pie(
                names=list(breakdown.keys()),
                values=list(breakdown.values()),
                hole=0.4,
                color_discrete_sequence=["#00E5FF", "#7C3AED", "#FF2E93", "#FFAB00"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8B949E"), showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        with table_col:
            for category, amount in breakdown.items():
                pct = (amount / predicted_cost * 100) if predicted_cost else 0
                st.markdown(f"""
                    <div class="hub-strip" style="border-left-color: #00E5FF;">
                        <b>{category}</b>
                        <p>₹{amount:,.2f} ({pct:.1f}%)</p>
                    </div>
                """, unsafe_allow_html=True)

        project_id = _get_project_id()
        if project_id and st.checkbox("Save estimate summary to project records", value=True):
            with get_db() as conn:
                models.create_report(
                    conn,
                    report_type=f"Cost Estimate — {project_type}",
                    period=f"{area} sqft / {floors} floors",
                    file_path=f"estimated=₹{predicted_cost:.2f}",
                    project_id=project_id,
                )
            st.success("✅ Cost estimate logged to project reports.")
