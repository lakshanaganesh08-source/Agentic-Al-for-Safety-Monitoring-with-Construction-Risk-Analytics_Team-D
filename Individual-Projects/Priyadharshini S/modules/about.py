import streamlit as st

from utils.styling import hero, section_label


def render():
    hero(
        "About This Project",
        "Construction Intelligence Hub — an AI powered smart construction management "
        "system built to demonstrate applied AI, ML, computer vision, and full-stack "
        "engineering in a single production-style application.",
        badge="FINAL YEAR PROJECT",
    )

    section_label("SYSTEM ARCHITECTURE")
    st.markdown(
        """
| Layer | Technology | Purpose |
|---|---|---|
| Frontend / UI | Streamlit, custom CSS, Plotly | Enterprise dashboard experience, responsive layout, animations |
| Data Layer | NumPy / Pandas (synthetic generator) | Seeded, reproducible construction project dataset |
| ML — Cost | Random Forest Regression (scikit-learn) | Predicts final project cost & overrun percentage |
| ML — Schedule | Random Forest Classification | Classifies delay risk as Low / Medium / High |
| ML — Safety | Random Forest Classification (class-balanced) | Predicts probability of a safety incident |
| Computer Vision | OpenCV (HSV color segmentation, Canny edges, Laplacian variance) | PPE coverage estimation & crack risk indicators from site photos |
| Generative AI | TF-IDF + cosine similarity chatbot, rule-based NLG report engine | Conversational assistant & automated executive reporting |
        """
    )

    section_label("KEY CAPABILITIES DEMONSTRATED")
    cols = st.columns(3)
    features = [
        ("📊", "Data Analytics", "Interactive KPI dashboards, trend analysis, and portfolio-wide filtering."),
        ("🤖", "Machine Learning", "Three trained models covering cost, schedule, and safety risk prediction."),
        ("📷", "Computer Vision", "Image-processing based PPE and structural crack risk scanning."),
        ("💬", "Generative AI", "NLP chatbot and automated natural-language project reporting."),
        ("🎨", "UI/UX Design", "Custom design system with a blueprint-industrial visual identity."),
        ("🏗️", "Domain Modeling", "Realistic construction industry attributes and risk relationships."),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"""<div class="cih-card" style="margin-bottom:14px;">
                <div style="font-size:1.6rem;">{icon}</div>
                <div style="font-family:'Barlow Condensed'; font-size:1.15rem; font-weight:700; margin-top:4px;">{title}</div>
                <div style="color:#8CA0BF; font-size:0.85rem; margin-top:4px;">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    section_label("DISCLAIMER")
    st.caption(
        "All project, cost, and safety data in this application is procedurally generated "
        "for demonstration purposes. Predictions are illustrative outputs of models trained "
        "on synthetic data and should not be used for real financial or safety decisions."
    )
