import streamlit as st
from PIL import Image
from utils.styling import page_hero, stat_card, status_strip


def render():
    page_hero(
        "👁️", "Computer Vision Site Inspection",
        "Automated PPE Compliance &amp; Real-Time Hazard Detection",
        badge="AI VISION ENGINE"
    )

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>📸 Image Upload & Analysis</h4>
            <span class="hub-card-tag">Upload a site photo to run automated inspection</span>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Site Image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("<p style='color: #8B949E; font-weight: 600; font-size: 0.9rem;'>INSPECTED SITE FRAME</p>", unsafe_allow_html=True)
            st.image(image, caption="Uploaded Construction Site Image", use_container_width=True)

        with col2:
            st.markdown("<p style='color: #8B949E; font-weight: 600; font-size: 0.9rem;'>AUTOMATED ANALYSIS REPORT</p>", unsafe_allow_html=True)

            with st.spinner("🔍 Running neural vision model..."):
                st.markdown(status_strip("#FFAB00", "⚠️ Inspection Warning",
                                          "Site is mostly compliant, but 1 active hazard requires immediate attention."),
                            unsafe_allow_html=True)

                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(stat_card("🪖", "Hardhat Compliance", "95%", None, "#00E676"), unsafe_allow_html=True)
                with m2:
                    st.markdown(stat_card("🦺", "Safety Vest Compliance", "100%", None, "#00E676"), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<h5 style='color: #F0F6FC; margin-bottom: 10px;'>Detailed Audit Breakdown</h5>", unsafe_allow_html=True)

                st.markdown(status_strip("#00E676", "✅ Hardhat Verification",
                                          "19 of 20 detected personnel are wearing required head protection."),
                            unsafe_allow_html=True)
                st.markdown(status_strip("#00E676", "✅ High-Visibility Gear",
                                          "All detected personnel are equipped with compliant high-vis jackets/vests."),
                            unsafe_allow_html=True)
                st.markdown(status_strip("#FFAB00", "⚠️ Hazard Warning (Zone B)",
                                          "Unsecured scaffolding and missing guardrail noticed near Zone B framework."),
                            unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="hub-card" style="text-align:center; padding: 40px 20px;">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">🖼️</div>
                <h4>No Image Uploaded Yet</h4>
                <p class="hub-card-body">Upload a site photo above to see PPE compliance scoring and hazard detection results here.</p>
            </div>
        """, unsafe_allow_html=True)
