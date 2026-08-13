import streamlit as st
from utils.styling import page_hero


def render():
    page_hero(
        "⏳", "Schedule & Delay Risk Prediction",
        "Predict potential timeline bottlenecks &amp; quantify site schedule vulnerability",
        badge="RISK INTELLIGENCE"
    )

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>⚙️ Project Conditions Assessment</h4>
            <span class="hub-card-tag">Tell us about current site conditions</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        weather_risk = st.selectbox(
            "🌧️ Expected Weather Disruptions",
            ["Low", "Medium", "High"],
            help="Forecasted impact of adverse local weather conditions"
        )
        supply_chain = st.selectbox(
            "🚚 Supply Chain Reliability",
            ["High", "Moderate", "Low"],
            help="Availability and delivery timeline stability of critical materials"
        )

    with col2:
        labor_avail = st.slider(
            "👷 Labor Workforce Capacity (%)",
            min_value=50, max_value=100, value=85, step=5,
            help="Current vs planned on-site subcontractor staffing percentage"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚨 Assess Delay Risk", type="primary", use_container_width=True):
        risk_score = 0
        if weather_risk == "High":
            risk_score += 35
        elif weather_risk == "Medium":
            risk_score += 15

        if supply_chain == "Low":
            risk_score += 40
        elif supply_chain == "Moderate":
            risk_score += 20

        if labor_avail < 70:
            risk_score += 25

        st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>📊 Risk Assessment Summary</h3>", unsafe_allow_html=True)

        if risk_score > 50:
            status_color, status_bg = "#FF5252", "rgba(255, 82, 82, 0.08)"
            status_title = "HIGH DELAY RISK"
            status_desc = "High probability of critical path schedule slippage. Immediate intervention recommended."
            action_tips = [
                "Negotiate expedited shipping options for delayed materials.",
                "Implement overtime shifts or reallocate workforce to critical path tasks.",
                "Review buffer allocations in project schedule baseline."
            ]
        elif risk_score > 25:
            status_color, status_bg = "#FFAB00", "rgba(255, 171, 0, 0.08)"
            status_title = "MODERATE DELAY RISK"
            status_desc = "Minor schedule friction expected. Active monitoring required."
            action_tips = [
                "Track material lead times weekly with key suppliers.",
                "Prepare weather contingency measures for outdoor activities."
            ]
        else:
            status_color, status_bg = "#00E676", "rgba(0, 230, 118, 0.08)"
            status_title = "LOW DELAY RISK"
            status_desc = "Project timeline is healthy and well-optimized. Operations are on target."
            action_tips = ["Maintain current labor deployment and supply chain pacing."]

        # Circular-feel gauge card
        st.markdown(f"""
            <div class="hub-card" style="text-align: center; border: 2px solid {status_color};
                        background: linear-gradient(180deg, {status_bg}, rgba(13,17,23,0.9));
                        margin-bottom: 25px; box-shadow: 0 0 40px {status_color}22;">
                <span style="color: {status_color}; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; font-size: 0.9rem;">
                    {status_title}
                </span>
                <h1 style="color: {status_color}; font-size: 3.4rem; margin: 6px 0; font-weight: 800;">
                    {risk_score}%
                </h1>
                <p style="color: #F0F6FC; font-size: 1rem; margin: 0 auto; font-weight: 500; max-width: 480px;">
                    {status_desc}
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h5 style='color: #F0F6FC; margin-bottom: 12px;'>💡 Recommended Action Plan</h5>", unsafe_allow_html=True)
        for tip in action_tips:
            st.markdown(f"""
                <div class="hub-strip" style="border-left-color: {status_color};">
                    <p style="margin:0;">• {tip}</p>
                </div>
            """, unsafe_allow_html=True)
