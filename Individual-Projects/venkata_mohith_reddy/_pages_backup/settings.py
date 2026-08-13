import streamlit as st
from ui_components import UIComponents

class SettingsPage:
    """
    Renders the app settings panel, allowing users to customize AI optimization weights,
    configure theme settings, and view developer details / system specifications.
    """
    
    @staticmethod
    def render():
        st.markdown("<h2 style='margin-bottom: 20px; color: #E2E8F0 !important;'>⚙️ System Settings & Core Profile</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1.2, 1], gap="large")
        
        with col1:
            st.markdown('<div class="glass-card neon-card-blue">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🛠️ AI Optimization Weight Customization</h4>", unsafe_allow_html=True)
            st.write("Fine-tune the neural layout calculation engine weight multipliers:")
            
            # Simulated weights
            safety_weight = st.slider("Structural Safety Margin Weight", 1.0, 2.0, 1.2, 0.1, help="Adjust safety margin factor. Higher values add thicker columns.")
            eco_weight = st.slider("Eco-Efficiency Threshold Factor", 0.5, 1.5, 1.0, 0.05, help="Controls sustainability recommendation triggers.")
            contingency_buffer = st.slider("Cost Contingency Buffer (%)", 1, 20, 5, 1, help="Add safety buffer to estimated building costing.")
            
            st.write("")
            if st.button("💾 SAVE CONFIGURATION ENGINE WEIGHTS"):
                st.success("✅ AI Engine weights compiled and saved successfully!")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
            # About Project
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🏗️ About Construction Intelligence Hub</h4>", unsafe_allow_html=True)
            st.write(
                """
                The Construction Intelligence Hub is a mock CAD-AI platform designed to bridge 
                generative spatial engineering with interactive 3D browser-native visualizers.
                By feeding plot sizes, orientations, and requirements into mathematical zoning equations, 
                it simulates real-life civil engineering planning choices in real-time.
                """
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="glass-card neon-card-purple" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>👤 Developer & Engineering Profiles</h4>", unsafe_allow_html=True)
            
            # Dev details
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 25px;">
                    <h3 style="margin-bottom: 5px; color: #00B4D8 !important;">Advanced AI Agent</h3>
                    <p style="color: #A0AEC0; font-size: 0.9rem;">Lead Developer & 3D Systems Architect</p>
                </div>
                <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 15px 0;">
                <p><b>Platform Tech Stack Specifications:</b></p>
                <ul style="line-height: 2; padding-left: 15px; font-size: 0.95rem;">
                    <li><b>Web Framework:</b> Streamlit 1.58.0</li>
                    <li><b>Graphics Engine:</b> Plotly 6.8.0 3D Rendering</li>
                    <li><b>GIS Coordinates Layer:</b> Pydeck 0.9.3 GIS Mapping</li>
                    <li><b>Data Analysis Core:</b> Pandas & NumPy</li>
                    <li><b>File Exporters:</b> ReportLab PDF & Openpyxl Excel</li>
                </ul>
                """,
                unsafe_allow_html=True
            )
            
            # Theme switcher demo
            st.write("---")
            st.write("**Visual Interface Theme Configurations**")
            theme_choice = st.radio(
                "Select Color Space Theme",
                ["Dark Futuristic Nebula (Blue + Purple)", "Tesla Cyberpunk Dark (Red + Charcoal)", "Apple Glassmorphism Light Mode"],
                index=0
            )
            if theme_choice != "Dark Futuristic Nebula (Blue + Purple)":
                st.info("💡 Selected theme profile active. Local components updated.")
                
            st.markdown('</div>', unsafe_allow_html=True)
