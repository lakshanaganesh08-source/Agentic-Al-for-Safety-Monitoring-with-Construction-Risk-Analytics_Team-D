import numpy as np
import streamlit as st
from sklearn.linear_model import LinearRegression

@st.cache_resource
def train_cost_model() -> LinearRegression:
    """
    Trains and caches the linear regression model for construction cost estimation.
    Uses @st.cache_resource to prevent redundant model retraining across Streamlit reruns.
    """
    # Features: [Area (sqft), Floors, Workers, Expected_Days]
    X = np.array([
        [1000, 1, 10, 30],
        [2500, 2, 20, 90],
        [5000, 4, 50, 180],
        [10000, 8, 120, 365],
        [20000, 15, 250, 600]
    ])
    
    # Target: Total Cost in USD
    y = np.array([50000, 150000, 400000, 1000000, 2500000])
    
    model = LinearRegression()
    model.fit(X, y)
    return model


def predict_cost(model: LinearRegression, area: float, floors: int, workers: int, days: int) -> float:
    """
    Predicts construction project cost given physical and operational parameters.
    Guarantees non-negative financial projections.
    """
    features = np.array([[area, floors, workers, days]])
    predicted_price = model.predict(features)[0]
    
    # Ensure prediction never yields negative cost values for edge-case inputs
    return float(np.maximum(0, predicted_price))
