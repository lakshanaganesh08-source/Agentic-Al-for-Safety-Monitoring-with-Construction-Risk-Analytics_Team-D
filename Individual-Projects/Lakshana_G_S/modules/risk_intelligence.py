import streamlit as st

from utils.risk_engine import RiskPredictor
from components.cards import metric_card


def show(data):

    st.title("🛡 AI Risk Intelligence")

    st.caption(
        "Identify construction risks using AI-powered analytics."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        budget = st.slider(
            "Budget Risk",
            0,
            100,
            50
        )

        schedule = st.slider(
            "Schedule Risk",
            0,
            100,
            40
        )

        safety = st.slider(
            "Safety Risk",
            0,
            100,
            20
        )

    with col2:

        weather = st.slider(
            "Weather Risk",
            0,
            100,
            35
        )

        material = st.slider(
            "Material Risk",
            0,
            100,
            45
        )

        labour = st.slider(
            "Labour Risk",
            0,
            100,
            55
        )

    st.divider()

    if st.button(
        "🧠 Analyze Risk",
        use_container_width=True
    ):

        predictor = RiskPredictor()

        result = predictor.predict(
            budget,
            schedule,
            safety,
            weather,
            material,
            labour
        )

        c1, c2 = st.columns(2)

        with c1:

            metric_card(
                "Overall Risk Score",
                f"{result['Score']} %",
                "📊",
                "#2563EB"
            )

        with c2:

            color = "#22C55E"

            if result["Level"] == "Medium":
                color = "#EAB308"

            if result["Level"] == "High":
                color = "#EF4444"

            metric_card(
                "Risk Level",
                result["Level"],
                "⚠",
                color
            )

        st.divider()

        st.subheader("📋 Risk Summary")

        risks = {
            "Budget": budget,
            "Schedule": schedule,
            "Safety": safety,
            "Weather": weather,
            "Material": material,
            "Labour": labour
        }

        st.bar_chart(risks)

        st.divider()

        st.subheader("🤖 AI Recommendation")

        if result["Level"] == "High":

            st.error("""
High project risk detected.

• Review project schedule

• Increase inspections

• Improve procurement planning

• Allocate contingency budget

• Monitor project weekly
""")

        elif result["Level"] == "Medium":

            st.warning("""
Moderate project risk.

• Monitor progress

• Review suppliers

• Conduct safety audits
""")

        else:

            st.success("""
Project risk is under control.

Continue regular monitoring.
""")
            
    st.divider()

    st.caption(
        "⚠️ ConstructIQ AI Enterprise | Risk Intelligence"
    )