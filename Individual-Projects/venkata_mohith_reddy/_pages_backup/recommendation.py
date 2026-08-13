import streamlit as st
from ui_components import UIComponents

class RecommendationPage:
    """
    Renders the AI architectural recommendation dashboard, illustrating house types,
    construction costs, timelines, core quality scores, and custom structural feedback.
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
        
        st.markdown("<h2 style='margin-bottom: 20px; color: #8A2BE2 !important;'>🤖 AI Generative Recommendation</h2>", unsafe_allow_html=True)
        
        # Primary summary banner
        UIComponents.render_glass_card(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.1em; color: #A0AEC0;">Recommended Archetype</span>
                    <h2 style="margin: 5px 0 0 0; color: #FFFFFF; font-size: 2.2rem; text-shadow: 0 0 15px rgba(0, 180, 216, 0.4);">{data['suitable_type']}</h2>
                </div>
                <div style="text-align: right; background: rgba(0, 180, 216, 0.1); padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(0, 180, 216, 0.2);">
                    <span style="font-size: 0.85rem; color: #00B4D8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">AI Confidence Factor</span>
                    <h3 style="margin: 0; color: #00B4D8; font-size: 1.8rem;">{data['confidence']}%</h3>
                </div>
            </div>
            """,
            title="🔍 Optimization Solution Summary",
            card_type="blue"
        )
        
        # Grid of core spatial parameters
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.markdown('<div class="glass-card neon-card-purple" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="📐 Recommended Built-up Area",
                value=f"{data['recommended_built_up']:,} sq ft",
                help="Recommended ground-level coverage footprint combined with vertical floors."
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="glass-card neon-card-blue" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="🍃 Open Ventilation Space",
                value=f"{data['remaining_open']:,} sq ft",
                help="Remaining unbuilt land area reserved for setback, gardens, and light shafts."
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="glass-card neon-card-green" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="💰 Estimated Construction Cost",
                value=f"${data['estimated_cost']:,.2f}",
                help="Estimated baseline structural cost based on chosen materials and site location."
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="glass-card neon-card-orange" style="height: 100%;">', unsafe_allow_html=True)
            st.metric(
                label="⏱️ Construction Timeline",
                value=f"{data['construction_time']} Months",
                help="Estimated engineering delivery schedule from ground-breaking to handover."
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Quality Indices & Sustainability Metrics
        st.write("")
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🛡️ Engineering Safety & Sustainability</h4>", unsafe_allow_html=True)
            
            # Progress bar for Safety Index
            st.write(f"**Structural Safety Index: {data['safety_score']}%**")
            st.progress(data['safety_score'])
            
            # Progress bar for Energy Efficiency
            st.write(f"**Building Energy Efficiency Rating: {data['energy_efficiency']}%**")
            st.progress(data['energy_efficiency'])
            
            # Progress bar for Future Expansion Capability
            st.write(f"**Future Expansion Score: {data['future_expansion_score']}%**")
            st.progress(data['future_expansion_score'])
            
            # Rating star visualization
            st.write("")
            stars_html = "".join(["★" for _ in range(int(data['sustainability_rating']))])
            stars_html += "".join(["☆" for _ in range(5 - int(data['sustainability_rating']))])
            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.02); padding: 15px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight:600; color: #A0AEC0;">Sustainability Rating:</span>
                    <span style="color: #00F5D4; font-size: 1.4rem; letter-spacing: 0.1em;">{stars_html} ({data['sustainability_rating']}/5.0)</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="glass-card neon-card-purple" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>💡 Generative AI Insights</h4>", unsafe_allow_html=True)
            
            if "ollama_recommendation" in st.session_state and st.session_state.ollama_recommendation:
                # Render the markdown generated by Ollama
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(138, 43, 226, 0.2); padding: 15px; border-radius: 8px; font-size: 0.92rem; line-height: 1.5; color: #E2E8F0; max-height: 400px; overflow-y: auto;">
                        {st.session_state.ollama_recommendation}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif "ollama_error" in st.session_state and st.session_state.ollama_error:
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 59, 48, 0.08); border-left: 4px solid #ff3b30; padding: 12px; border-radius: 4px; color: #ff6b6b; font-size: 0.9rem; line-height: 1.4; margin-bottom: 15px;">
                        <strong>⚠️ Local Ollama Integration Error:</strong><br>{st.session_state.ollama_error}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Fallback to hardcoded recommendations if connection failed
                colors = ["#4D39E9", "#00B4D8", "#00F5D4", "#FF9F1C", "#8A2BE2"]
                for idx, insight in enumerate(data['insights']):
                    bg_color = colors[idx % len(colors)]
                    st.markdown(
                        f"""
                        <div style="background: rgba(255, 255, 255, 0.02); border-left: 3px solid {bg_color}; padding: 12px; margin-bottom: 12px; border-radius: 4px;">
                            <span style="font-size: 0.95rem; line-height: 1.4; color: #E2E8F0;">{insight}</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                # Default insights
                colors = ["#4D39E9", "#00B4D8", "#00F5D4", "#FF9F1C", "#8A2BE2"]
                for idx, insight in enumerate(data['insights']):
                    bg_color = colors[idx % len(colors)]
                    st.markdown(
                        f"""
                        <div style="background: rgba(255, 255, 255, 0.02); border-left: 3px solid {bg_color}; padding: 12px; margin-bottom: 12px; border-radius: 4px;">
                            <span style="font-size: 0.95rem; line-height: 1.4; color: #E2E8F0;">{insight}</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            st.markdown('</div>', unsafe_allow_html=True)
            
        # 3D Visualizer Section
        st.write("")
        st.markdown('<div class="glass-card neon-card-blue">', unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🗺️ Interactive 3D Digital Twin Layout (Plotly Model)</h4>", unsafe_allow_html=True)
        from utils.visualization_3d import Visualization3D
        try:
            fig_3d = Visualization3D.create_layout_figure(data['layout_3d'], raw['floor_pref'])
            st.plotly_chart(fig_3d, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering 3D digital twin: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
