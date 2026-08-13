import streamlit as st
import plotly.graph_objects as go
from ui_components import UIComponents

class DashboardPage:
    """
    Renders the central executive dashboard (KPIs, efficiency gauge,
    and high-level project summary widgets).
    """
    
    @staticmethod
    def render():
        if "analysis_results" not in st.session_state or st.session_state.analysis_results is None:
            st.warning("⚠️ No simulation data found. Please run the analysis first in the Space Analysis tab.")
            if st.button("📐 Go to Space Analysis"):
                st.session_state.current_page = "📐 Space Analysis"
                st.rerun()
            return
            
        data = st.session_state.analysis_results
        raw = data['raw_inputs']
        
        st.markdown("<h2 style='margin-bottom: 20px; color: #00B4D8 !important;'>🏠 Executive Project Dashboard</h2>", unsafe_allow_html=True)
        
        # 1. KPI CARDS
        # Available Area, Used Area, Efficiency %, Construction Cost, Completion Score, Prediction Accuracy
        col1, col2, col3 = st.columns(3, gap="medium")
        col4, col5, col6 = st.columns(3, gap="medium")
        
        efficiency = (data['recommended_built_up'] / raw['total_area']) * 100
        budget_completion = (data['estimated_cost'] / raw['budget']) * 100 if raw['budget'] > 0 else 100
        # If construction cost is within budget, score is high. If it exceeds, score decreases
        completion_score = max(0.0, min(100.0, 100.0 - (budget_completion - 100.0))) if budget_completion > 100 else 100.0
        
        with col1:
            st.markdown('<div class="glass-card neon-card-blue" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="🗺️ Available Land Area",
                value=f"{raw['total_area']:,} sq ft",
                delta=f"{raw['width']:.0f}' x {raw['length']:.0f}' plot"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="glass-card neon-card-purple" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="🏢 Recommended Used Area",
                value=f"{data['recommended_built_up']:,} sq ft",
                delta=f"{data['suitable_type']}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="glass-card neon-card-green" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="⚡ Space Utilization Efficiency",
                value=f"{efficiency:.1f}%",
                delta="Optimal range 60-80%"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="glass-card neon-card-orange" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="💰 Predicted Construction Cost",
                value=f"${data['estimated_cost']:,.2f}",
                delta=f"Budget: ${raw['budget']:,.0f}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col5:
            st.markdown('<div class="glass-card neon-card-blue" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="📈 Budget Completion Score",
                value=f"{completion_score:.1f}%",
                delta="Cost vs Budget Index"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col6:
            st.markdown('<div class="glass-card neon-card-purple" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="🎯 Model Prediction Accuracy",
                value=f"{data['confidence'] - 1.2:.1f}%",
                delta="Neural confidence weight"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Detailed middle section (Gauge Chart and Summary)
        st.write("")
        col_left, col_right = st.columns([1.2, 1], gap="large")
        
        with col_left:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>⚡ Space Efficiency Index Gauge</h4>", unsafe_allow_html=True)
            fig = DashboardPage._create_gauge_chart(efficiency)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="glass-card neon-card-blue" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🏡 Architectural Brief Summary</h4>", unsafe_allow_html=True)
            
            # Simple summary list in HTML
            summary_html = f"""
            <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem; line-height: 2;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="color: #A0AEC0;">Target Location:</td>
                    <td style="color: #FFFFFF; font-weight:600; text-align:right;">{raw['location']}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="color: #A0AEC0;">Construction Style:</td>
                    <td style="color: #FFFFFF; font-weight:600; text-align:right;">{raw['construction_type']}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="color: #A0AEC0;">Material Standard:</td>
                    <td style="color: #FFFFFF; font-weight:600; text-align:right;">{raw['material_quality']}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="color: #A0AEC0;">Floor Configuration:</td>
                    <td style="color: #FFFFFF; font-weight:600; text-align:right;">{raw['floor_pref']}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="color: #A0AEC0;">Landscape / Garden:</td>
                    <td style="color: #00F5D4; font-weight:600; text-align:right;">{"Requested" if raw['garden_needed'] else "None"}</td>
                </tr>
                <tr>
                    <td style="color: #A0AEC0;">Parking Lot:</td>
                    <td style="color: #00B4D8; font-weight:600; text-align:right;">{"Requested" if raw['parking_needed'] else "None"}</td>
                </tr>
            </table>
            """
            st.markdown(summary_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _create_gauge_chart(val: float) -> go.Figure:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = val,
            domain = {'x': [0, 1], 'y': [0, 1]},
            number = {'suffix': "%", 'font': {'color': "#FFFFFF", 'family': "Space Grotesk", 'size': 40}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#A0AEC0"},
                'bar': {'color': "#00B4D8"},
                'bgcolor': "rgba(255,255,255,0.03)",
                'borderwidth': 1,
                'bordercolor': "rgba(255,255,255,0.1)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(255, 59, 48, 0.1)'},
                    {'range': [50, 80], 'color': 'rgba(0, 245, 212, 0.1)'},
                    {'range': [80, 100], 'color': 'rgba(138, 43, 226, 0.1)'}
                ],
                'threshold': {
                    'line': {'color': "#00F5D4", 'width': 4},
                    'thickness': 0.75,
                    'value': 70.0
                }
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#E2E8F0"},
            height=260,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        return fig
