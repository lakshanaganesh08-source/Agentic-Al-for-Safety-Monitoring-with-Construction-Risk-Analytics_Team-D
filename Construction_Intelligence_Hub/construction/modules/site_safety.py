import streamlit as st
import pandas as pd
from datetime import date

CHECKLIST_ITEMS = [
    "Workers wearing helmets & safety shoes",
    "Safety harnesses used above 2m height",
    "Scaffolding inspected & tagged today",
    "Fire extinguishers accessible & in-date",
    "First-aid kit stocked and accessible",
    "Electrical panels covered / grounded",
    "Excavation edges barricaded",
    "Material storage stable (no toppling risk)",
    "Site clearly signed (hazard/PPE signage)",
    "Emergency contact numbers displayed",
]


def render():
    st.markdown(
        """<div class="page-header">
        <h1>🦺 Site Safety</h1>
        <p>Daily safety checklist and incident tracking to keep every site compliant.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if "safety_logs" not in st.session_state:
        st.session_state.safety_logs = []

    st.markdown('<div class="cih-card">', unsafe_allow_html=True)
    st.subheader("✅ Daily Safety Checklist")
    checked = []
    cols = st.columns(2)
    for i, item in enumerate(CHECKLIST_ITEMS):
        with cols[i % 2]:
            checked.append(st.checkbox(item, key=f"safety_{i}"))
    score = sum(checked)
    pct = int((score / len(CHECKLIST_ITEMS)) * 100)

    st.progress(pct / 100)
    if pct >= 90:
        st.markdown(f'<span class="badge badge-success">Safety Score: {pct}%</span>', unsafe_allow_html=True)
    elif pct >= 60:
        st.markdown(f'<span class="badge badge-warning">Safety Score: {pct}%</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="badge badge-danger">Safety Score: {pct}%</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="cih-card">', unsafe_allow_html=True)
    st.subheader("🚨 Log an Incident / Observation")
    with st.form("incident_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            incident_date = st.date_input("Date", value=date.today())
            severity = st.select_slider("Severity", options=["Low", "Medium", "High", "Critical"])
        with c2:
            reported_by = st.text_input("Reported By")
            location = st.text_input("Location on Site")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Log Incident")
    if submitted and description:
        st.session_state.safety_logs.append(
            dict(date=str(incident_date), severity=severity, reported_by=reported_by,
                 location=location, description=description)
        )
        st.success("Incident logged.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.safety_logs:
        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("📁 Incident Log")
        st.dataframe(pd.DataFrame(st.session_state.safety_logs), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
