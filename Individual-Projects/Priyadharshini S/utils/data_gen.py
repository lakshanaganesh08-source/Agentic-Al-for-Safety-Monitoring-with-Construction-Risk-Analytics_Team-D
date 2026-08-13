import pandas as pd
import numpy as np

def get_sample_project_data() -> pd.DataFrame:
    """
    Generates realistic monthly project financial and progress telemetry data
    for executive dashboard visualization and chart rendering.
    """
    np.random.seed(42)
    
    # 12-month project timeline
    dates = pd.date_range(start="2025-01-01", periods=12, freq="ME")
    
    # Baseline cumulative metrics
    planned_budget = np.linspace(100_000, 10_000_000, 12)
    cost_variances = np.random.uniform(-250_000, 600_000, 12)
    actual_cost = np.clip(planned_budget + cost_variances, a_min=50_000, a_max=None)
    
    planned_progress = np.linspace(8, 100, 12)
    actual_progress = np.clip(planned_progress + np.random.uniform(-8, 4, 12), a_min=0, a_max=100)
    
    df = pd.DataFrame({
        "Month": dates.strftime('%b %Y'),
        "Planned_Budget": np.round(planned_budget, 2),
        "Actual_Cost": np.round(actual_cost, 2),
        "Planned_Progress": np.round(planned_progress, 1),
        "Actual_Progress": np.round(actual_progress, 1)
    })
    
    return df


def get_sample_applications_data() -> pd.DataFrame:
    """
    Generates sample monthly permit/insurance application telemetry
    (created vs submitted counts) for the Compliance & Insurance module.
    """
    np.random.seed(7)

    dates = pd.date_range(start="2025-01-01", periods=10, freq="ME")

    created = np.random.randint(3, 14, size=10)
    # Submitted is always <= created, simulating in-progress applications
    submitted = np.array([
        max(0, c - np.random.randint(0, 4)) for c in created
    ])

    df = pd.DataFrame({
        "Month": dates.strftime('%b %Y'),
        "Created": created,
        "Submitted": submitted,
    })

    return df
