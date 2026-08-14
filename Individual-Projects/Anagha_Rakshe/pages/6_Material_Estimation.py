import streamlit as st

from AI.llm import ask_llama
from AI.prompts import MATERIAL_PROMPT

from components.sidebar import show_sidebar

st.set_page_config(
    page_title="Material Estimation",
    page_icon="🧱"
)

show_sidebar()

st.title("🧱 AI Material Estimation")

st.write(
    "Estimate construction materials using AI."
)

st.divider()

building = st.selectbox(
    "Building Type",
    [
        "Residential",
        "Commercial",
        "Industrial",
        "Hospital",
        "School"
    ]
)

floors = st.number_input(
    "Number of Floors",
    min_value=1
)

area = st.number_input(
    "Built-up Area (sq.ft)",
    min_value=100
)

foundation = st.selectbox(
    "Foundation Type",
    [
        "Shallow Foundation",
        "Pile Foundation",
        "Raft Foundation"
    ]
)

concrete = st.selectbox(
    "Concrete Grade",
    [
        "M20",
        "M25",
        "M30",
        "M35"
    ]
)

steel = st.selectbox(
    "Steel Grade",
    [
        "Fe415",
        "Fe500",
        "Fe550"
    ]
)

additional = st.text_area(
    "Additional Requirements"
)

if st.button("🧱 Estimate Materials"):

    prompt = f"""
Building Type:
{building}

Floors:
{floors}

Built-up Area:
{area} sq.ft

Foundation:
{foundation}

Concrete Grade:
{concrete}

Steel Grade:
{steel}

Additional Requirements:
{additional}

Estimate the approximate quantities of:

- Cement
- Sand
- Aggregate
- Steel
- Bricks
- Concrete

Also provide:

- Important assumptions
- Cost optimization suggestions
"""

    with st.spinner("Estimating Materials..."):

        response = ask_llama(
            prompt,
            MATERIAL_PROMPT
        )

    st.success("Material Estimation Complete")

    st.subheader("🤖 AI Analysis")

    with st.container(border=True):
        st.markdown(response)