import streamlit as st
import time
from utils.analysis_engine import AnalysisEngine
from ui_components import UIComponents

class SpaceAnalysisPage:
    """
    Renders the primary space configuration form inside a glassmorphism container,
    including inputs for plot geometry, budget, structural style, and floor preferences.
    """
    
    @staticmethod
    def render():
        st.markdown("<h2 style='margin-bottom: 20px; color: #00B4D8 !important;'>📐 Spatial Configuration Panel</h2>", unsafe_allow_html=True)
        
        # Blueprint Scanner (OpenCV integration)
        with st.expander("📷 Optional: AI Blueprint & Site Sketch Scanner (OpenCV)", expanded=False):
            st.write("Upload a layout sketch, blueprint, or site boundaries image to auto-detect boundary aspect ratios and estimate plot dimensions:")
            uploaded_file = st.file_uploader("Upload Sketch (PNG/JPG)", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                from utils.blueprint_scanner import BlueprintScanner
                with st.spinner("Analyzing image contours..."):
                    proc_img, est_w, est_l = BlueprintScanner.scan_blueprint(uploaded_file)
                    if proc_img is not None:
                        col_img, col_det = st.columns([1, 1])
                        with col_img:
                            st.image(proc_img, caption="OpenCV Edge & Contour Analysis", use_container_width=True)
                        with col_det:
                            st.success("🎉 Boundaries scanned successfully!")
                            st.metric("Detected Width Estimate", f"{est_w} ft")
                            st.metric("Detected Length Estimate", f"{est_l} ft")
                            if st.button("Apply Scanned Dimensions to Inputs"):
                                st.session_state.scanned_width = est_w
                                st.session_state.scanned_length = est_l
                                st.session_state.scanned_area = est_w * est_l
                                st.toast("Applied scanned dimensions!")
                                st.rerun()

        # Set default values based on CV scanner or standard defaults
        default_width = st.session_state.get("scanned_width", 40.0)
        default_length = st.session_state.get("scanned_length", 60.0)
        default_area = st.session_state.get("scanned_area", 2400.0)

        # Wrapping input controls in st.form or styled columns
        st.markdown('<div class="glass-card neon-card-blue">', unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top:0; color: #FFFFFF;'>📐 Step 1: Input Land & Project Specifications</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="medium")
        
        with col1:
            st.markdown("##### 📍 Location & Land Boundary")
            location = st.selectbox(
                "📍 Location / Zone",
                ["Urban Core", "Suburban Sector", "Coastal District", "Industrial Extension", "Mountain Terrain"],
                index=0,
                help="Select the geographic and zoning classification of your land parcel."
            )
            
            total_area = st.number_input(
                "📐 Total Land Area (sq ft)",
                min_value=500.0,
                max_value=100000.0,
                value=default_area,
                step=100.0,
                help="Specify total area in square feet. Note: Area will automatically match Length x Width if specified."
            )
            
            length = st.number_input(
                "📏 Plot Length (ft)",
                min_value=10.0,
                max_value=500.0,
                value=default_length,
                step=5.0,
                help="Boundary dimension from front to back."
            )
            
            width = st.number_input(
                "↔️ Plot Width (ft)",
                min_value=10.0,
                max_value=500.0,
                value=default_width,
                step=5.0,
                help="Boundary dimension from left to right."
            )

            st.markdown("<br>##### 🏢 Structural Architecture", unsafe_allow_html=True)
            floor_pref = st.selectbox(
                "🏢 Floor Preference",
                ["Single Floor", "Duplex", "Triplex"],
                index=1,
                help="Desired height profile of the building."
            )
            
            family_size = st.slider(
                "👥 Family Size (Occupants)",
                min_value=1,
                max_value=15,
                value=4,
                step=1,
                help="Total number of residents to optimize bedroom and living space calculations."
            )
            
        with col2:
            st.markdown("##### 💰 Project Financials")
            budget = st.number_input(
                "💰 Allocated Budget ($)",
                min_value=10000.0,
                max_value=5000000.0,
                value=150000.0,
                step=5000.0,
                help="Max financial allocation for base construction."
            )
            
            construction_type = st.selectbox(
                "🏗️ Construction Style Type",
                ["Modern", "Smart/Futuristic", "Minimalist", "Traditional"],
                index=1,
                help="Design aesthetic style and technology profile of the building."
            )
            
            material_quality = st.selectbox(
                "💎 Material Quality Standard",
                ["Standard", "Premium", "Luxury"],
                index=1,
                help="The grade of structural and finishing materials."
            )
            
            st.markdown("<br>##### 🌿 Spatial Requirements & Constraints", unsafe_allow_html=True)
            
            # Use columns for toggles to save space nicely
            tcol1, tcol2 = st.columns(2)
            with tcol1:
                parking_needed = st.toggle("🚗 Parking Space", value=True, help="Include dedicated garage/parking zone.")
                garden_needed = st.toggle("🌿 Landscape Garden", value=True, help="Incorporate garden/green zone.")
            with tcol2:
                future_expansion = st.toggle("📈 Future Expansion", value=False, help="Incorporate structural design adjustments for future vertical/rear expansion.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Big glowing action button
        st.write("")
        if st.button("🔮 RUN SPATIAL INTELLIGENCE SIMULATION"):
            # Set simulation parameters
            st.session_state.is_simulating = True
            st.session_state.sim_inputs = {
                "total_area": total_area,
                "length": length,
                "width": width,
                "location": location,
                "budget": budget,
                "construction_type": construction_type,
                "material_quality": material_quality,
                "parking_needed": parking_needed,
                "garden_needed": garden_needed,
                "future_expansion": future_expansion,
                "floor_pref": floor_pref,
                "family_size": family_size
            }
            st.rerun()

    @staticmethod
    def render_simulation_loading():
        """
        Renders a beautiful high-tech AI calculation screen with terminal logging simulation.
        """
        st.markdown("<div style='text-align: center; margin-top: 50px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='background: linear-gradient(135deg, #00B4D8, #4D39E9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🧠 Synthesizing Spatial Optimization Model...</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        logs = [
            "Initializing deep neural spatial planning models...",
            "Loading terrain data and construction zoning codes...",
            "Validating boundary offsets and site set-backs...",
            "Synthesizing optimal built-up area ratios (Ground Coverage: 65%)...",
            "Allocating parking footprint & landscape gardens...",
            "Running finite element cost estimation algorithm...",
            "Computing structural safety indices and energy ratings...",
            "Synthesizing customized AI architectural advice...",
            "Rendering 3D digital-twin building mesh...",
            "Finalizing optimization matrices..."
        ]
        
        for percent_complete in range(100):
            time.sleep(0.02) # Fast simulation load
            progress_bar.progress(percent_complete + 1)
            log_idx = min(percent_complete // 10, len(logs) - 1)
            status_text.markdown(f"<code style='color:#00B4D8;'>[SYS_LOG]: {logs[log_idx]}</code>", unsafe_allow_html=True)
            
        # Perform actual analysis
        inputs = st.session_state.sim_inputs
        results = AnalysisEngine.analyze_construction(
            total_area=inputs["total_area"],
            length=inputs["length"],
            width=inputs["width"],
            location=inputs["location"],
            budget=inputs["budget"],
            construction_type=inputs["construction_type"],
            material_quality=inputs["material_quality"],
            parking_needed=inputs["parking_needed"],
            garden_needed=inputs["garden_needed"],
            future_expansion=inputs["future_expansion"],
            floor_pref=inputs["floor_pref"],
            family_size=inputs["family_size"]
        )
        
        # Call Ollama local AI model to generate professional architectural recommendations
        import ollama_helper
        with st.spinner("🧠 Querying local Ollama model (llama3.2)..."):
            ollama_resp, err = ollama_helper.get_recommendation_cached(inputs)
            if err:
                st.session_state.ollama_error = err
                st.session_state.ollama_recommendation = None
            else:
                st.session_state.ollama_error = None
                st.session_state.ollama_recommendation = ollama_resp
        
        # Save results, switch pages
        st.session_state.analysis_results = results
        st.session_state.is_simulating = False
        st.session_state.current_page = "🤖 AI Recommendation"
        st.rerun()
