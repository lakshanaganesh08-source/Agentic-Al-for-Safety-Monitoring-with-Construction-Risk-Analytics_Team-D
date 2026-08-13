import streamlit as st
from utils.pdf_generator import PDFGenerator
from utils.excel_generator import ExcelGenerator
from ui_components import UIComponents

class ReportsPage:
    """
    Renders the reporting panel, allowing users to compile and download
    comprehensive PDF documents and multi-sheet Excel files of their simulation results.
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
        
        st.markdown("<h2 style='margin-bottom: 20px; color: #FF9F1C !important;'>📈 Project Report Compilation</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown('<div class="glass-card neon-card-orange">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>📝 Export Formats</h4>", unsafe_allow_html=True)
            st.write("Generate and download legal/planning structural documents synthesized from the intelligence model:")
            
            # PDF Download
            st.write("")
            st.markdown("**1. Formal PDF Report Document**")
            st.write("Includes formatted text parameters, intelligence scores (safety, eco, expansion), and customized AI tactical advice in a print-ready document.")
            
            try:
                pdf_data = PDFGenerator.generate_report(data)
                st.download_button(
                    label="📥 Download PDF Recommendation",
                    data=pdf_data,
                    file_name="Construction_Intelligence_Recommendation.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error compiling PDF: {str(e)}")
                
            # Excel Download
            st.write("")
            st.write("---")
            st.markdown("**2. Technical Excel Spreadsheet Book**")
            st.write("Contains full parameter indexes, raw numerical inputs, engineering ratios, and list spreadsheets for project management integration.")
            
            try:
                excel_data = ExcelGenerator.generate_report(data)
                st.download_button(
                    label="📥 Download Construction Summary (Excel)",
                    data=excel_data,
                    file_name="Construction_Planning_Summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error compiling Excel: {str(e)}")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="glass-card neon-card-blue" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🔍 Document Content Preview</h4>", unsafe_allow_html=True)
            
            raw = data['raw_inputs']
            preview_text = f"""
            <div style="font-size: 0.95rem; line-height: 1.8;">
                <p><b>Project Title:</b> Construction Intelligence Briefing</p>
                <p><b>ArchType Recommendation:</b> {data['suitable_type']} (Confidence: {data['confidence']}%)</p>
                <p><b>Boundary Dimension:</b> {raw['width']:.0f}' x {raw['length']:.0f}' ({raw['total_area']:.1f} sq ft)</p>
                <p><b>Optimal Built-up Area:</b> {data['recommended_built_up']:.1f} sq ft</p>
                <p><b>Estimated Base Cost:</b> ${data['estimated_cost']:,.2f}</p>
                <p><b>Expected Build Span:</b> {data['construction_time']} Months</p>
                <p><b>Strategic Insights Compiled:</b> {len(data['insights'])} Tactical Bullet Points</p>
                <p><b>Safety & Eco Indexes:</b> Safety: {data['safety_score']}%, Eco Rating: {data['sustainability_rating']}/5</p>
            </div>
            """
            st.markdown(preview_text, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
