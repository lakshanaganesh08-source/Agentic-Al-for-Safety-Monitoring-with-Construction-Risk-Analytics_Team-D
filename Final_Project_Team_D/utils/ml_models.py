import json
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression


@st.cache_resource
def train_cost_model() -> LinearRegression:
    """
    Trains and caches the linear regression model for construction cost estimation.
    Uses expanded training data with project-type variance.
    """
    # Features: [Area (sqft), Floors, Workers, Expected_Days]
    X = np.array([
        [1000, 1, 10, 30],
        [2500, 2, 20, 90],
        [5000, 4, 50, 180],
        [10000, 8, 120, 365],
        [20000, 15, 250, 600],
        [1500, 1, 15, 60],
        [8000, 6, 80, 240],
        [12000, 10, 150, 400],
    ])

    y = np.array([2000000, 5500000, 12000000, 26000000, 55000000, 3200000, 20000000, 31000000])

    model = LinearRegression()
    model.fit(X, y)
    return model


PROJECT_TYPE_MULTIPLIERS = {
    "Residential": 1.0,
    "Commercial": 1.18,
    "Industrial": 1.28,
    "Infrastructure": 1.45,
}


def predict_cost(
    model: LinearRegression,
    area: float,
    floors: int,
    workers: int,
    days: int,
    project_type: str = "Residential",
) -> float:
    """Predicts total construction cost with project-type adjustment."""
    features = np.array([[area, floors, workers, days]])
    base = float(model.predict(features)[0])
    multiplier = PROJECT_TYPE_MULTIPLIERS.get(project_type, 1.0)
    return float(np.maximum(0, base * multiplier))


def cost_breakdown(total_cost: float) -> dict[str, float]:
    """Return category breakdown percentages for a total estimate."""
    return {
        "Materials": round(total_cost * 0.35, 2),
        "Labor": round(total_cost * 0.40, 2),
        "Equipment": round(total_cost * 0.15, 2),
        "Overhead & Contingency": round(total_cost * 0.10, 2),
    }


@st.cache_resource
def train_delay_model() -> RandomForestClassifier:
    """
    Train a delay-risk classifier from synthetic site-condition scenarios.
    Labels: 0=Low, 1=Moderate, 2=High
    """
    # Features: [weather_risk, supply_chain_risk, labor_capacity_pct, complexity]
    X = np.array([
        [0, 0, 95, 1], [0, 1, 90, 1], [1, 0, 85, 2], [1, 1, 80, 2],
        [2, 0, 75, 2], [2, 1, 70, 3], [2, 2, 60, 3], [1, 2, 65, 2],
        [0, 0, 100, 1], [1, 1, 55, 3], [2, 2, 50, 3], [0, 1, 88, 1],
    ])
    y = np.array([0, 0, 1, 1, 1, 2, 2, 2, 0, 2, 2, 1])

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model


def _encode_weather(value: str) -> int:
    return {"Low": 0, "Medium": 1, "High": 2}.get(value, 0)


def _encode_supply(value: str) -> int:
    return {"High": 0, "Moderate": 1, "Low": 2}.get(value, 0)


def predict_delay_risk(
    model: RandomForestClassifier,
    weather_risk: str,
    supply_chain: str,
    labor_avail: int,
    complexity: int = 2,
) -> dict:
    """
    Predict delay risk level and score.

    Returns dict with risk_level, risk_score (0-100), predicted_days_delay, factors.
    """
    features = np.array([[
        _encode_weather(weather_risk),
        _encode_supply(supply_chain),
        labor_avail,
        complexity,
    ]])
    proba = model.predict_proba(features)[0]
    predicted_class = int(model.predict(features)[0])

    level_map = {0: "LOW", 1: "MODERATE", 2: "HIGH"}
    score_map = {0: (5, 25), 1: (26, 55), 2: (56, 95)}

    low, high = score_map[predicted_class]
    risk_score = int(low + (high - low) * max(proba))

    if labor_avail < 60:
        risk_score = min(100, risk_score + 15)
    if labor_avail < 70:
        risk_score = min(100, risk_score + 8)

    days_delay = {0: 2, 1: 8, 2: 21}[predicted_class]
    if risk_score > 70:
        days_delay += 7

    return {
        "risk_level": level_map[predicted_class],
        "risk_score": risk_score,
        "predicted_days_delay": days_delay,
        "confidence": round(float(max(proba)) * 100, 1),
        "factors": {
            "weather": weather_risk,
            "supply_chain": supply_chain,
            "labor_capacity_pct": labor_avail,
            "complexity": complexity,
        },
    }


@st.cache_resource
def train_progress_forecast_model() -> RandomForestRegressor:
    """Forecast completion progress given current metrics."""
    X = np.array([
        [30, 5, 80], [42, 3, 85], [55, 2, 90], [65, 4, 75],
        [75, 1, 95], [85, 2, 88], [92, 0, 98],
    ])
    y = np.array([45, 52, 60, 68, 78, 88, 95])
    model = RandomForestRegressor(n_estimators=30, random_state=42)
    model.fit(X, y)
    return model
