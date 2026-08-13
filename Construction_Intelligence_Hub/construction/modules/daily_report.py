import streamlit as st
from datetime import date
from utils.llama_client import chat_with_llama


def render():
    st.markdown(
        """<div class="page-header">
        <h1>🗒️ Daily Report Generator</h1>
        <p>Fill in today's site details and generate a clean, client-ready progress report.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cih-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        report_date = st.date_input("Report Date", value=date.today())
        site_name = st.text_input("Site / Project Name")
        weather = st.selectbox("Weather", ["Clear", "Cloudy", "Rain", "Extreme Heat"])
        workers_present = st.number_input("Workers Present", min_value=0, step=1, value=15)
    with col2:
        work_done = st.text_area("Work Completed Today", placeholder="e.g. Slab shuttering completed for 2nd floor...")
        materials_used = st.text_area("Materials Used Today", placeholder="e.g. 40 cement bags, 2 truckloads of sand...")
        issues = st.text_area("Issues / Delays (if any)")
    tomorrow_plan = st.text_area("Plan for Tomorrow")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("📝 Generate Report"):
        with st.spinner("Drafting report..."):
            prompt = (
                f"Write a concise, professional daily construction site report for a client, "
                f"using this data:\nDate: {report_date}\nSite: {site_name}\nWeather: {weather}\n"
                f"Workers present: {workers_present}\nWork completed: {work_done}\n"
                f"Materials used: {materials_used}\nIssues/delays: {issues}\n"
                f"Plan for tomorrow: {tomorrow_plan}\n\n"
                "Format it with clear headings: Summary, Work Completed, Materials Used, Issues, Tomorrow's Plan."
            )
            report = chat_with_llama(prompt, history=[])

        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("📄 Generated Report")
        st.write(report)
        st.download_button(
            "⬇️ Download Report (.txt)",
            data=report,
            file_name=f"daily_report_{report_date}.txt",
            mime="text/plain",
        )
        st.markdown("</div>", unsafe_allow_html=True)
