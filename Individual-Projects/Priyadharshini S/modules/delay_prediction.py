import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.styling import hero, section_label
from utils.ml_models import train_delay_model

AMBER = "#F59E0B"
STEEL = "#3B82F6"
GREEN = "#22C55E"
RED = "#F87171"
TEXT = "#E7ECF5"
RISK_COLOR = {"Low": GREEN, "Medium": AMBER, "High": RED}


def render(df: pd.DataFrame):
    hero(
        "AI Schedule Delay Risk",
        "Random Forest classifier estimates the likelihood of schedule slippage so "
        "project managers can intervene before deadlines are missed.",
        badge="MACHINE LEARNING",
    )

    with st.spinner("Training classification model..."):
        model, metrics, importances = train_delay_model(df)

    m1, m2, m3 = st.columns(3)
    m1.metric("Model Accuracy", f"{metrics['accuracy']*100:.1f}%")
    m2.metric("Weighted F1 Score", metrics["f1_weighted"])
    m3.metric("Classes", "Low / Medium / High")

    st.write("")
    left, right = st.columns([1.1, 1])

    with left:
        section_label("ASSESS A PROJECT'S SCHEDULE RISK")
        with st.form("delay_form"):
            c1, c2 = st.columns(2)
            with c1:
                planned_duration = st.slider("Planned Duration (days)", 60, 720, 240)
                complexity = st.slider("Site Complexity (1-10)", 1.0, 10.0, 5.0, 0.1)
                workers = st.slider("Workers Assigned", 15, 450, 120)
            with c2:
                weather_risk = st.slider("Weather Risk Score", 0.0, 1.0, 0.3, 0.01)
                supplier_rel = st.slider("Supplier Reliability", 0.4, 1.0, 0.8, 0.01)
                equipment = st.slider("Equipment Count", 2, 60, 20)

            c3, c4, c5 = st.columns(3)
            with c3:
                ptype = st.selectbox("Project Type", sorted(df["project_type"].unique()))
            with c4:
                region = st.selectbox("Region", sorted(df["region"].unique()))
            with c5:
                site_type = st.selectbox("Site Type", sorted(df["site_type"].unique()))

            submitted = st.form_submit_button("🔮 Predict Delay Risk")

        if submitted:
            X_new = pd.DataFrame([{
                "planned_duration_days": planned_duration, "site_complexity": complexity,
                "weather_risk_score": weather_risk, "supplier_reliability": supplier_rel,
                "workers_assigned": workers, "equipment_count": equipment,
                "project_type": ptype, "region": region, "site_type": site_type,
            }])
            pred_class = model.predict(X_new)[0]
            proba = model.predict_proba(X_new)[0]
            classes = model.named_steps["model"].classes_
            st.session_state["delay_pred_result"] = dict(
                pred_class=pred_class,
                proba=dict(zip(classes, proba)),
                radar=dict(
                    complexity=complexity, weather=weather_risk * 10,
                    supplier_gap=(1 - supplier_rel) * 10,
                    duration_pressure=min(planned_duration / 72, 10),
                    workforce=min(workers / 45, 10),
                ),
            )

    with right:
        section_label("PREDICTION RESULT")
        result = st.session_state.get("delay_pred_result")
        if result:
            cls = result["pred_class"]
            color = RISK_COLOR.get(cls, AMBER)
            st.markdown(
                f"""<div style="text-align:center; padding:14px; border-radius:10px;
                background:{color}22; border:1px solid {color}66;">
                <span style="font-family:'Barlow Condensed'; font-size:2rem; font-weight:800; color:{color};">
                {cls.upper()} RISK</span></div>""",
                unsafe_allow_html=True,
            )
            st.write("")
            proba = result["proba"]
            fig = go.Figure(go.Bar(
                x=list(proba.values()), y=list(proba.keys()), orientation="h",
                marker_color=[RISK_COLOR.get(k, AMBER) for k in proba.keys()],
                text=[f"{v*100:.1f}%" for v in proba.values()], textposition="outside",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color=TEXT, height=220, margin=dict(l=10, r=30, t=10, b=10),
                xaxis=dict(range=[0, 1], showticklabels=False),
            )
            st.plotly_chart(fig, use_container_width=True)

            if cls == "High":
                st.error("🔴 High delay risk — recommend adding schedule buffer and reviewing supplier SLAs.")
            elif cls == "Medium":
                st.warning("🟡 Moderate delay risk — monitor weather exposure and workforce allocation.")
            else:
                st.success("🟢 Low delay risk — project is well positioned to finish on time.")
        else:
            st.info("Fill the form and click **Predict Delay Risk** to see AI results here.")

    st.write("")
    left2, right2 = st.columns(2)
    with left2:
        section_label("RISK FACTOR RADAR")
        result = st.session_state.get("delay_pred_result")
        if result:
            radar = result["radar"]
            categories = list(radar.keys())
            values = list(radar.values())
            fig = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                line_color=AMBER,
                fillcolor="rgba(245,158,11,0.25)",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=TEXT,
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 10], gridcolor="#16233B"),
                    angularaxis=dict(gridcolor="#16233B"),
                ),
                height=340,
                showlegend=False,
                margin=dict(l=30, r=30, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run a prediction to see the risk factor radar chart.")

    with right2:
        section_label("MODEL FEATURE IMPORTANCE")
        fig = go.Figure(go.Bar(
            x=importances.values[::-1], y=importances.index[::-1], orientation="h",
            marker_color=STEEL,
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT, height=340, margin=dict(l=10, r=10, t=10, b=10),
        )
        fig.update_xaxes(gridcolor="#16233B")
        fig.update_yaxes(gridcolor="#16233B")
        st.plotly_chart(fig, use_container_width=True)
