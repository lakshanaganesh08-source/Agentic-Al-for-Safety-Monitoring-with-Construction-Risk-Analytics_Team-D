import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.styling import hero, section_label
from utils.ml_models import train_cost_model

AMBER = "#F59E0B"
STEEL = "#3B82F6"
TEXT = "#E7ECF5"


def render(df: pd.DataFrame):
    hero(
        "AI Cost Prediction",
        "Random Forest regression model trained on historical project data to forecast "
        "final project cost and overrun probability before you break ground.",
        badge="MACHINE LEARNING",
    )

    with st.spinner("Training regression model..."):
        model, metrics, importances = train_cost_model(df)

    m1, m2, m3 = st.columns(3)
    m1.metric("Model R² Score", metrics["r2"])
    m2.metric("Mean Absolute Error", f"₹{metrics['mae']:,.0f}")
    m3.metric("Training Samples", f"{len(df):,}")

    st.write("")
    left, right = st.columns([1.1, 1])

    with left:
        section_label("SIMULATE A NEW PROJECT")
        with st.form("cost_form"):
            c1, c2 = st.columns(2)
            with c1:
                budget = st.number_input("Planned Budget (₹)", 200000, 50000000, 5000000, step=100000)
                planned_duration = st.slider("Planned Duration (days)", 60, 720, 240)
                workers = st.slider("Workers Assigned", 15, 450, 120)
                equipment = st.slider("Equipment Count", 2, 60, 20)
            with c2:
                material_index = st.slider("Material Cost Index", 0.6, 2.0, 1.05, 0.01)
                weather_risk = st.slider("Weather Risk Score", 0.0, 1.0, 0.3, 0.01)
                complexity = st.slider("Site Complexity (1-10)", 1.0, 10.0, 5.0, 0.1)
                supplier_rel = st.slider("Supplier Reliability", 0.4, 1.0, 0.8, 0.01)

            c3, c4, c5 = st.columns(3)
            with c3:
                ptype = st.selectbox("Project Type", sorted(df["project_type"].unique()))
            with c4:
                region = st.selectbox("Region", sorted(df["region"].unique()))
            with c5:
                site_type = st.selectbox("Site Type", sorted(df["site_type"].unique()))

            submitted = st.form_submit_button("🔮 Predict Final Cost")

        if submitted:
            X_new = pd.DataFrame([{
                "budget": budget, "planned_duration_days": planned_duration,
                "workers_assigned": workers, "material_cost_index": material_index,
                "weather_risk_score": weather_risk, "site_complexity": complexity,
                "supplier_reliability": supplier_rel, "equipment_count": equipment,
                "project_type": ptype, "region": region, "site_type": site_type,
            }])
            pred_cost = model.predict(X_new)[0]
            overrun_pct = (pred_cost - budget) / budget * 100
            st.session_state["cost_pred_result"] = dict(
                pred_cost=pred_cost, overrun_pct=overrun_pct, budget=budget
            )

    with right:
        section_label("PREDICTION RESULT")
        result = st.session_state.get("cost_pred_result")
        if result:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=result["overrun_pct"],
                number={"suffix": "%", "font": {"color": TEXT}},
                delta={"reference": 0, "increasing": {"color": "#F87171"}, "decreasing": {"color": "#22C55E"}},
                gauge={
                    "axis": {"range": [-20, 60], "tickcolor": TEXT},
                    "bar": {"color": AMBER},
                    "steps": [
                        {"range": [-20, 5], "color": "#123322"},
                        {"range": [5, 25], "color": "#3a2c0d"},
                        {"range": [25, 60], "color": "#3a1414"},
                    ],
                },
                title={"text": "Predicted Cost Overrun", "font": {"color": TEXT, "size": 16}},
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=TEXT, height=300,
                               margin=dict(l=20, r=20, t=60, b=10))
            st.plotly_chart(fig, use_container_width=True)

            st.metric("Predicted Final Cost", f"₹{result['pred_cost']:,.0f}",
                       f"{result['overrun_pct']:+.1f}% vs budget of ₹{result['budget']:,.0f}")

            if result["overrun_pct"] > 25:
                st.error("🔴 High risk of significant cost overrun. Review supplier contracts and site complexity.")
            elif result["overrun_pct"] > 8:
                st.warning("🟡 Moderate overrun risk — recommend contingency buffer of 10-15%.")
            else:
                st.success("🟢 Cost outlook is healthy — within acceptable variance.")
        else:
            st.info("Fill the simulation form and click **Predict Final Cost** to see AI results here.")

    st.write("")
    section_label("TOP COST DRIVERS (FEATURE IMPORTANCE)")
    fig = go.Figure(go.Bar(
        x=importances.values[::-1], y=importances.index[::-1], orientation="h",
        marker_color=AMBER,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT, height=360, margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.update_xaxes(gridcolor="#16233B")
    fig.update_yaxes(gridcolor="#16233B")
    st.plotly_chart(fig, use_container_width=True)
