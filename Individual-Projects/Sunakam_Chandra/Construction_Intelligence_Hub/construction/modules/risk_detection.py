import streamlit as st


def _assess_risks(budget, area, timeline_months, floors, soil_type, location_type, monsoon_exposure):
    risks = []

    cost_per_sqft = (budget / area) if area else 0
    if area > 0 and cost_per_sqft < 1400:
        risks.append(("Budget looks tight for the built-up area (cost/sq.ft is low)", "High"))
    elif area > 0 and cost_per_sqft < 1800:
        risks.append(("Budget is on the lower side — expect quality trade-offs", "Medium"))

    if floors >= 3 and soil_type == "Loose / Sandy":
        risks.append(("Loose soil with 3+ floors — needs deep foundation & soil testing", "High"))
    elif soil_type == "Loose / Sandy":
        risks.append(("Loose soil detected — recommend soil test before foundation design", "Medium"))

    if timeline_months and area:
        rate = area / timeline_months
        if rate > 800:
            risks.append(("Timeline is aggressive relative to built-up area — quality/safety risk", "High"))

    if monsoon_exposure:
        risks.append(("Construction window overlaps monsoon season — plan for weather delays", "Medium"))

    if location_type == "Coastal":
        risks.append(("Coastal location — corrosion risk for steel, recommend coated rebar", "Medium"))
    elif location_type == "Seismic Zone":
        risks.append(("Seismic zone — ensure earthquake-resistant structural design", "High"))

    if not risks:
        risks.append(("No major red flags detected from current inputs", "Low"))

    return risks


def render():
    st.markdown(
        """<div class="page-header">
        <h1>⚠️ Risk Detection</h1>
        <p>AI-assisted flagging of budget, structural, and schedule risks before they become expensive.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cih-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        budget = st.number_input("Total Budget (INR)", min_value=0.0, step=50000.0, value=2500000.0)
        area = st.number_input("Built-up Area (sq.ft)", min_value=1.0, step=10.0, value=1500.0)
        floors = st.number_input("Number of Floors", min_value=1, step=1, value=2)
    with col2:
        timeline_months = st.number_input("Timeline (months)", min_value=1, step=1, value=8)
        soil_type = st.selectbox("Soil Type", ["Firm / Rocky", "Loose / Sandy", "Clayey", "Unknown"])
        location_type = st.selectbox("Location Type", ["Normal", "Coastal", "Seismic Zone", "Hilly"])
    monsoon_exposure = st.checkbox("Construction period overlaps monsoon season")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Run Risk Analysis"):
        risks = _assess_risks(budget, area, timeline_months, floors, soil_type, location_type, monsoon_exposure)
        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("🔍 Detected Risks")
        badge_map = {"High": "badge-danger", "Medium": "badge-warning", "Low": "badge-success"}
        for text, level in risks:
            st.markdown(
                f'<div style="margin-bottom:10px;">'
                f'<span class="badge {badge_map[level]}">{level}</span>&nbsp; {text}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("This is an automated heuristic screening tool — always confirm critical risks with a licensed structural engineer.")
