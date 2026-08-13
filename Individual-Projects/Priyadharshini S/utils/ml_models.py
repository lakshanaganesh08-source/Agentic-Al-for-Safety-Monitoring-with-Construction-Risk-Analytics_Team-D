import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

NUMERIC_COST = [
    "budget", "planned_duration_days", "workers_assigned", "material_cost_index",
    "weather_risk_score", "site_complexity", "supplier_reliability", "equipment_count",
]
NUMERIC_DELAY = [
    "planned_duration_days", "site_complexity", "weather_risk_score",
    "supplier_reliability", "workers_assigned", "equipment_count",
]
CATEGORICAL = ["project_type", "region", "site_type"]


def _build_preprocessor(numeric_cols):
    return ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )


def _grouped_importances(model, preprocessor, numeric_cols):
    """Map one-hot feature importances back to their original column names."""
    ohe = preprocessor.named_transformers_["cat"]
    cat_feature_names = ohe.get_feature_names_out(CATEGORICAL)
    all_feature_names = list(numeric_cols) + list(cat_feature_names)
    raw_importances = pd.Series(model.feature_importances_, index=all_feature_names)

    grouped = {}
    for col in numeric_cols:
        grouped[col] = raw_importances.get(col, 0.0)
    for col in CATEGORICAL:
        matching = [f for f in cat_feature_names if f.startswith(col + "_")]
        grouped[col] = raw_importances[matching].sum()

    result = pd.Series(grouped).sort_values(ascending=False).head(8)
    return result


@st.cache_resource(show_spinner=False)
def train_cost_model(df: pd.DataFrame):
    X = df[NUMERIC_COST + CATEGORICAL]
    y = df["actual_cost"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = _build_preprocessor(NUMERIC_COST)
    pipeline = Pipeline([
        ("prep", preprocessor),
        ("model", RandomForestRegressor(n_estimators=250, max_depth=10, random_state=42)),
    ])
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    metrics = {
        "r2": round(r2_score(y_test, preds), 3),
        "mae": mean_absolute_error(y_test, preds),
    }

    importances = _grouped_importances(
        pipeline.named_steps["model"], pipeline.named_steps["prep"], NUMERIC_COST
    )
    return pipeline, metrics, importances


@st.cache_resource(show_spinner=False)
def train_delay_model(df: pd.DataFrame):
    X = df[NUMERIC_DELAY + CATEGORICAL]
    y = df["delay_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = _build_preprocessor(NUMERIC_DELAY)
    pipeline = Pipeline([
        ("prep", preprocessor),
        ("model", RandomForestClassifier(
            n_estimators=250, max_depth=10, class_weight="balanced", random_state=42
        )),
    ])
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 3),
        "f1_weighted": round(f1_score(y_test, preds, average="weighted"), 3),
    }

    importances = _grouped_importances(
        pipeline.named_steps["model"], pipeline.named_steps["prep"], NUMERIC_DELAY
    )
    return pipeline, metrics, importances
