import streamlit as st
import pandas as pd
from datetime import date


def render():
    st.markdown(
        """<div class="page-header">
        <h1>📝 Project Questionnaire</h1>
        <p>Capture client requirements up front to scope the project accurately.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if "questionnaire_responses" not in st.session_state:
        st.session_state.questionnaire_responses = []

    with st.form("project_questionnaire_form", clear_on_submit=True):
        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("Client & Project Details")
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client Name")
            project_type = st.selectbox(
                "Project Type", ["Residential", "Commercial", "Industrial", "Renovation", "Interior only"]
            )
            plot_area = st.number_input("Plot Area (sq.ft)", min_value=0.0, step=10.0)
            built_up_area = st.number_input("Expected Built-up Area (sq.ft)", min_value=0.0, step=10.0)
        with col2:
            location = st.text_input("Project Location")
            floors = st.number_input("Number of Floors", min_value=1, step=1, value=1)
            budget = st.number_input("Estimated Budget (INR)", min_value=0.0, step=50000.0)
            start_date = st.date_input("Preferred Start Date", value=date.today())

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("Preferences")
        col3, col4 = st.columns(2)
        with col3:
            quality_tier = st.select_slider("Construction Quality Tier", options=["Economy", "Standard", "Premium"])
            structure_type = st.selectbox("Structure Type", ["RCC Framed", "Load Bearing", "Steel Structure"])
        with col4:
            special_requirements = st.text_area("Special Requirements (Vastu, elevator, basement, solar, etc.)")
            timeline_months = st.number_input("Expected Timeline (months)", min_value=1, step=1, value=6)
        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Submit Questionnaire")

    if submitted:
        if not client_name or not location:
            st.warning("Please fill in at least Client Name and Location.")
        else:
            entry = dict(
                client_name=client_name, project_type=project_type, plot_area=plot_area,
                built_up_area=built_up_area, location=location, floors=floors,
                budget=budget, start_date=str(start_date), quality_tier=quality_tier,
                structure_type=structure_type, special_requirements=special_requirements,
                timeline_months=timeline_months,
            )
            st.session_state.questionnaire_responses.append(entry)
            st.success(f"✅ Questionnaire saved for **{client_name}**. You can now use this in Material Estimation.")

    if st.session_state.questionnaire_responses:
        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("📋 Saved Questionnaires")
        df = pd.DataFrame(st.session_state.questionnaire_responses)
        st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
