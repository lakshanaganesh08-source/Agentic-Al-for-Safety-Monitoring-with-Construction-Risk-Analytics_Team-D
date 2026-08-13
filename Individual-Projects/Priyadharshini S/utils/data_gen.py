import numpy as np
import pandas as pd
import streamlit as st

REGIONS = ["North", "South", "East", "West", "Central"]
STATUSES = ["Planning", "In Progress", "Delayed", "Completed", "On Hold"]
PROJECT_TYPES = ["Residential", "Commercial", "Industrial", "Infrastructure", "Renovation"]
SITE_TYPES = ["Urban", "Suburban", "Rural", "Coastal"]
CONTRACTORS = [
    "Everest Builders", "Meridian Constructions", "Bluepeak Infra",
    "Apex Structures", "Horizon Contractors", "Granite & Co.",
]


@st.cache_data(show_spinner=False)
def generate_project_data(n: int = 150, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    budget = rng.uniform(500_000, 40_000_000, n)
    planned_duration_days = rng.integers(60, 720, n)
    workers_assigned = rng.integers(15, 450, n)
    equipment_count = rng.integers(2, 60, n)
    material_cost_index = rng.uniform(0.6, 2.0, n)
    weather_risk_score = rng.uniform(0.0, 1.0, n)
    site_complexity = rng.uniform(1.0, 10.0, n)
    supplier_reliability = rng.uniform(0.4, 1.0, n)

    project_type = rng.choice(PROJECT_TYPES, n)
    region = rng.choice(REGIONS, n)
    site_type = rng.choice(SITE_TYPES, n)
    contractor = rng.choice(CONTRACTORS, n)
    status = rng.choice(STATUSES, n, p=[0.12, 0.38, 0.18, 0.24, 0.08])

    # cost overrun driven mainly by weather risk, complexity, and supplier unreliability
    overrun_factor = (
        0.02
        + weather_risk_score * 0.18
        + (site_complexity / 10) * 0.14
        + (1 - supplier_reliability) * 0.16
        + rng.normal(0, 0.05, n)
    )
    overrun_factor = np.clip(overrun_factor, -0.1, 0.6)
    actual_cost = budget * (1 + overrun_factor)
    cost_overrun_pct = overrun_factor * 100

    delay_days = (
        (weather_risk_score * 40)
        + (site_complexity * 6)
        + ((1 - supplier_reliability) * 50)
        - (workers_assigned / 15)
        + rng.normal(0, 12, n)
    ).round().astype(int)

    delay_risk = pd.cut(
        delay_days, bins=[-999, 5, 25, 9999], labels=["Low", "Medium", "High"]
    ).astype(str)

    ppe_compliance = np.clip(
        0.9 - weather_risk_score * 0.1 - (site_complexity / 10) * 0.15 + rng.normal(0, 0.08, n),
        0.35, 1.0,
    )
    safety_incident_prob = np.clip(
        0.05 + (1 - ppe_compliance) * 0.35 + (site_complexity / 10) * 0.1, 0, 0.9
    )
    safety_incident = rng.binomial(1, safety_incident_prob)

    project_id = [f"CIH-{1000 + i}" for i in range(n)]
    project_name = [
        f"{pt} Project {i + 1}" for i, pt in enumerate(project_type)
    ]

    start_dates = pd.to_datetime("2023-01-01") + pd.to_timedelta(
        rng.integers(0, 700, n), unit="D"
    )
    end_dates = start_dates + pd.to_timedelta(planned_duration_days, unit="D")

    df = pd.DataFrame(
        {
            "project_id": project_id,
            "project_name": project_name,
            "project_type": project_type,
            "region": region,
            "site_type": site_type,
            "contractor": contractor,
            "status": status,
            "budget": budget,
            "actual_cost": actual_cost,
            "cost_overrun_pct": cost_overrun_pct,
            "planned_duration_days": planned_duration_days,
            "delay_days": delay_days,
            "delay_risk": delay_risk,
            "workers_assigned": workers_assigned,
            "equipment_count": equipment_count,
            "material_cost_index": material_cost_index,
            "weather_risk_score": weather_risk_score,
            "site_complexity": site_complexity,
            "supplier_reliability": supplier_reliability,
            "ppe_compliance": ppe_compliance,
            "safety_incident": safety_incident,
            "start_date": start_dates,
            "end_date": end_dates,
        }
    )
    return df


@st.cache_data(show_spinner=False)
def generate_incident_timeseries(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    months = pd.date_range("2024-08-01", periods=24, freq="MS").strftime("%b %Y")
    incidents = np.clip(rng.poisson(2.2, 24) + np.round(np.sin(np.arange(24) / 3) * 1.2), 0, None)
    near_miss = np.clip(incidents * rng.uniform(1.8, 3.2, 24), 0, None).round()
    return pd.DataFrame({"month": months, "incidents": incidents, "near_miss": near_miss})


def generate_faq_data():
    """Curated FAQ knowledge base for the CIH Assistant chatbot (TF-IDF matched)."""
    return [
        ("What is Construction Intelligence Hub?",
         "Construction Intelligence Hub is an AI-powered dashboard that combines project "
         "management with machine learning to help construction companies track progress, "
         "predict cost overruns, assess delay risk, and monitor safety from a single platform."),
        ("How does the cost prediction model work?",
         "It's a Random Forest regression model trained on project features like budget, "
         "duration, workforce, site complexity, weather risk, and supplier reliability. It "
         "outputs a predicted final cost and estimated overrun percentage."),
        ("How does the delay risk model work?",
         "A Random Forest classifier looks at duration, complexity, weather exposure, "
         "supplier reliability, and workforce/equipment levels to classify a project as "
         "Low, Medium, or High delay risk."),
        ("What is PPE?",
         "PPE stands for Personal Protective Equipment — items like helmets, hi-visibility "
         "vests, gloves, and safety boots that protect workers on a construction site."),
        ("How can I improve site safety?",
         "Increase PPE compliance monitoring, run regular safety inspections, address "
         "near-miss reports quickly, and use the Vision Scanner to spot-check site photos "
         "for PPE coverage and hazard indicators."),
        ("What does the Vision Scanner do?",
         "It analyzes an uploaded site photo using classical computer vision — HSV color "
         "masking to estimate high-visibility PPE coverage, Canny edge detection for "
         "possible surface cracks, and Laplacian variance to flag blurry images."),
        ("How is the AI report generated?",
         "The AI Reports module pulls live project data — budget, delay status, and safety "
         "metrics — and assembles it into a structured executive summary automatically."),
        ("What technologies power this platform?",
         "Python, Streamlit, Pandas, Plotly, scikit-learn (Random Forest models), OpenCV "
         "for computer vision, and a TF-IDF cosine-similarity chatbot."),
        ("Is the data in this app real?",
         "No — all project, cost, and safety data is procedurally generated for "
         "demonstration purposes. Predictions are illustrative, not for real-world use."),
    ]
