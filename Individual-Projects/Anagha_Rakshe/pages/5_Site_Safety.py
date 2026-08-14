import streamlit as st

from AI.llm import ask_llama
from AI.prompts import SAFETY_PROMPT

from components.sidebar import show_sidebar

st.set_page_config(
    page_title="Site Safety Management",
    page_icon="🦺"
)

show_sidebar()

st.title("🦺 AI Site Safety Management")

st.write(
    "Analyze construction site conditions and receive AI-powered safety recommendations."
)

st.divider()

project = st.text_input("Project Name")

workers = st.number_input(
    "Number of Workers",
    min_value=1
)

activity = st.selectbox(
    "Current Activity",
    [
        "Excavation",
        "Concrete Work",
        "Scaffolding",
        "Electrical Installation",
        "Roof Work",
        "Heavy Equipment Operation",
        "General Construction"
    ]
)

weather = st.selectbox(
    "Weather",
    [
        "Sunny",
        "Cloudy",
        "Rainy",
        "Windy",
        "Storm Expected"
    ]
)

ppe = st.multiselect(
    "Available PPE",
    [
        "Helmet",
        "Safety Shoes",
        "Reflective Jacket",
        "Gloves",
        "Safety Goggles",
        "Harness",
        "Face Mask"
    ]
)

description = st.text_area(
    "Describe Current Site Conditions"
)

incident = st.radio(
    "Any Safety Incident Today?",
    ["No", "Yes"]
)

if st.button("🦺 Analyze Site Safety"):

    prompt = f"""
Project Name:
{project}

Workers:
{workers}

Current Activity:
{activity}

Weather:
{weather}

Available PPE:
{', '.join(ppe)}

Site Conditions:
{description}

Incident Reported:
{incident}

Analyze the construction site safety.

Provide:

1. Overall Safety Rating
2. Potential Hazards
3. Severity
4. PPE Recommendations
5. Corrective Actions
6. Emergency Preparedness
"""

    with st.spinner("Analyzing Site Safety..."):

        response = ask_llama(
            prompt,
            SAFETY_PROMPT
        )

    st.success("Safety Analysis Complete")

    st.subheader("🤖 AI Analysis")

    with st.container(border=True):
        st.markdown(response)