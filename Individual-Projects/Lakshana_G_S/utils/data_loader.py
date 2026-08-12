import pandas as pd
import streamlit as st


@st.cache_data
def load_data():

    data = {

        # ============================================
        # Core Project Data
        # ============================================

        "projects": pd.read_csv("data/projects.csv"),
        "employees": pd.read_csv("data/employees.csv"),
        "activities": pd.read_csv("data/activities.csv"),

        # ============================================
        # Cost & Estimation
        # ============================================

        "cost_estimation": pd.read_csv("data/cost_estimation.csv"),
        "material_estimation": pd.read_csv("data/material_estimation.csv"),
        "budget": pd.read_csv("data/budget.csv"),

        # ============================================
        # AI Estimation Datasets
        # ============================================

        "estimation_rates": pd.read_csv("data/estimation_rates.csv"),
        "estimation_materials": pd.read_csv("data/estimation_materials.csv"),
        "labour_rates": pd.read_csv("data/labour_rates.csv"),
        "equipment_rates": pd.read_csv("data/equipment_rates.csv"),
        "project_templates": pd.read_csv("data/project_templates.csv"),

        # ============================================
        # Resources
        # ============================================

        "materials": pd.read_csv("data/materials.csv"),
        "vendors": pd.read_csv("data/vendors.csv"),
        "equipment": pd.read_csv("data/equipment.csv"),

        # ============================================
        # Project Intelligence
        # ============================================

        "delays": pd.read_csv("data/delays.csv"),
        "rework": pd.read_csv("data/rework.csv"),
        "risks": pd.read_csv("data/risks.csv"),
        "safety": pd.read_csv("data/safety.csv"),
        "weather": pd.read_csv("data/weather.csv"),

        # ============================================
        # Reports & Documents
        # ============================================

        "daily_reports": pd.read_csv("data/daily_reports.csv"),
        "documents": pd.read_csv("data/documents.csv"),
    }

    return data