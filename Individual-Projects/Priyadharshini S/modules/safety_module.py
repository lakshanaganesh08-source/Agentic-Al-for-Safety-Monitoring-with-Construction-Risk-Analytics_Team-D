import streamlit as st
from utils.styling import page_hero


def render():
    page_hero(
        "🦺", "Site Safety & Compliance",
        "Log Site Incidents, Track Near-Misses, and Maintain OSHA Audit Compliance",
        badge="SAFETY OPERATIONS"
    )

    st.markdown("""
        <div class="hub-card" style="padding: 16px 20px; margin-bottom: 18px;">
            <h4>📝 Log Safety Incident / Observation</h4>
            <span class="hub-card-tag">Select a category and describe what happened</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        incident_type = st.selectbox(
            "⚠️ Observation Category",
            ["Near Miss", "Property Damage", "Hazard Identification", "Minor Injury"],
            help="Select the classification that best describes the event."
        )

        severity_colors = {
            "Near Miss": ("#FFAB00", "MODERATE ATTENTION", "Potential safety event that was narrowly avoided."),
            "Property Damage": ("#FF5252", "HIGH SEVERITY", "Physical site asset or equipment destruction reported."),
            "Hazard Identification": ("#00E5FF", "PREVENTATIVE OBS", "Proactive reporting of unsanitary or risky conditions."),
            "Minor Injury": ("#FF5252", "HIGH SEVERITY", "Personnel required first-aid or medical assistance.")
        }
        color, level, label_desc = severity_colors.get(incident_type, ("#00E5FF", "INFO", ""))

        st.markdown(f"""
            <div class="hub-strip" style="border-left-color:{color}; margin-top: 10px;">
                <span style="color: {color}; font-size: 0.75rem; font-weight: 700; letter-spacing: 1px;">{level}</span>
                <p style="margin: 4px 0 0 0;">{label_desc}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        desc = st.text_area(
            "📄 Incident Description",
            placeholder="Describe what occurred, exact zone/location on site, personnel involved, and immediate actions taken...",
            height=130
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚨 Submit Incident Report", type="primary", use_container_width=True):
        if not desc.strip():
            st.warning("⚠️ Please provide a brief description before submitting the incident report.")
        else:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

            st.markdown("""
                <div class="hub-card" style="text-align: center; border-color: rgba(0,230,118,0.4);">
                    <span style="color: #00E676; font-size: 1.5rem;">✅</span>
                    <h3 style="color: #00E676; margin: 5px 0;">Safety Incident Logged Successfully</h3>
                    <p class="hub-card-body">
                        The report has been registered in the compliance database and dispatched to the Safety Officer.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="hub-card" style="margin-top: 15px;">
                    <p style="color: #8B949E; margin: 0 0 5px 0; font-size: 0.8rem; font-weight: 600;">LOG ENTRY SUMMARY</p>
                    <p style="color: #F0F6FC; margin: 0; font-weight: 600;">Category: <span style="color: {color};">{incident_type}</span></p>
                    <p style="color: #C9D1D9; margin: 5px 0 0 0; font-size: 0.9rem;">"{desc}"</p>
                </div>
            """, unsafe_allow_html=True)
