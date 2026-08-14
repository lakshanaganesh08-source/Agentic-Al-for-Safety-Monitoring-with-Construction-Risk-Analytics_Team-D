import streamlit as st

from AI.llm import ask_llama
from AI.prompts import RISK_PROMPT

from components.sidebar import show_sidebar

st.set_page_config(
    page_title="Risk Detection",
    page_icon="⚠️"
)

show_sidebar()

st.title("⚠️ AI Construction Risk Detection")

st.write(
    "Analyze potential project risks using AI."
)

st.divider()

project = st.text_input("Project Name")

budget = st.number_input(
    "Project Budget (₹)",
    min_value=0.0
)

duration = st.number_input(
    "Project Duration (Months)",
    min_value=1
)

workers = st.number_input(
    "Number of Workers",
    min_value=1
)

weather = st.selectbox(
    "Weather Forecast",
    [
        "Sunny",
        "Rainy",
        "Cloudy",
        "Storm Expected"
    ]
)

materials = st.selectbox(
    "Material Availability",
    [
        "High",
        "Medium",
        "Low"
    ]
)

complexity = st.selectbox(
    "Project Complexity",
    [
        "Low",
        "Medium",
        "High"
    ]
)

additional = st.text_area(
    "Additional Information"
)

if st.button("🔍 Analyze Risk"):

    prompt = f"""
Project Name:
{project}

Budget:
₹{budget}

Duration:
{duration} months

Workers:
{workers}

Weather:
{weather}

Material Availability:
{materials}

Project Complexity:
{complexity}

Additional Notes:
{additional}
"""

    with st.spinner("Analyzing Project Risks..."):

        response = ask_llama(
            prompt,
            RISK_PROMPT
        )

    st.success("Risk Analysis Complete")

    st.subheader("🤖 AI Analysis")

    with st.container(border=True):
        st.markdown(response)