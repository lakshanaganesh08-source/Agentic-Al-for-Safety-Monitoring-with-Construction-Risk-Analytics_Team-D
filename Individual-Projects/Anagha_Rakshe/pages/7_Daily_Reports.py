import streamlit as st

from AI.llm import ask_llama
from AI.prompts import REPORT_PROMPT

from components.sidebar import show_sidebar

st.set_page_config(
    page_title="Daily Report Generator",
    page_icon="📝"
)

show_sidebar()

st.title("📝 Daily Construction Report Generator")

st.markdown(
"""
Generate professional AI-powered daily construction reports.
"""
)

project = st.text_input("Project Name")

date = st.date_input("Date")

work_completed = st.text_area(
    "Work Completed Today"
)

workers = st.number_input(
    "Workers Present",
    min_value=0,
    step=1
)

equipment = st.text_area(
    "Equipment Used"
)

weather = st.selectbox(
    "Weather",
    [
        "Sunny",
        "Cloudy",
        "Rainy",
        "Windy"
    ]
)

issues = st.text_area(
    "Issues / Delays"
)

tomorrow = st.text_area(
    "Planned Work for Tomorrow"
)

if st.button("📝 Generate Report"):

    prompt = f"""
Project Name:
{project}

Date:
{date}

Today's Work:
{work_completed}

Workers Present:
{workers}

Equipment Used:
{equipment}

Weather:
{weather}

Issues:
{issues}

Tomorrow's Plan:
{tomorrow}
"""

    with st.spinner("Generating Report..."):

        report = ask_llama(
            prompt,
            REPORT_PROMPT
        )

    st.success("Report Generated Successfully")

    st.markdown(report)

    st.download_button(
        "⬇ Download Report",
        report,
        file_name="Daily_Report.txt"
    )