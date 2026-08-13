"""
Dashboard metrics aggregated from SQLite for the executive dashboard.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from database.db import get_db
from database import models


def _format_currency(value: float) -> str:
    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"
    if value >= 100_000:
        return f"₹{value / 100_000:.2f} Lakhs"
    return f"₹{value:,.0f}"


def get_executive_metrics() -> dict:
    with get_db() as conn:
        project = models.get_default_project(conn)
        if not project:
            return {
                "project_name": "No Project",
                "budget": 0,
                "spent": 0,
                "spent_pct": 0,
                "progress": 0,
                "tasks_total": 0,
                "tasks_completed": 0,
                "incidents_total": 0,
                "latest_site_risk": 0,
                "latest_safety": 0,
                "latest_compliance": 0,
                "latest_insurance": 0,
            }
        
        project_id = project["id"]
        budget = project.get("budget", 0) or 0
        spent = project.get("spent", 0) or 0
        spent_pct = (spent / budget * 100) if budget > 0 else 0
        progress = project.get("progress", 0) or 0

        tasks = models.list_tasks(conn, project_id)
        open_tasks = sum(1 for t in tasks if t["status"] in ("Pending", "In Progress"))

        incident_count = models.count_incidents(conn, project_id)
        material_summary = models.get_material_cost_summary(conn, project_id)

        # Safety score: prefer safety_logs, fallback to incident penalty
        safety_from_logs = models.get_latest_safety_score(conn, project_id)
        if safety_from_logs is not None:
            safety_score = round(safety_from_logs, 1)
        else:
            safety_score = max(60, 100 - incident_count * 5)

        # Site risk score from latest site-type risk log
        site_risk_score = models.get_latest_risk_score(conn, project_id, risk_type="site")
        if site_risk_score is None:
            site_risk_score = min(45, 20 + incident_count * 8)

        # Compliance score from compliance_logs
        compliance_score = models.get_latest_compliance_score(conn, project_id)
        if compliance_score is None:
            compliance_score = 85  # Default baseline

        # Insurance risk score from insurance_logs
        insurance_score = models.get_insurance_risk_score(conn, project_id)
        if insurance_score is None:
            insurance_score = 30  # Default baseline (lower is better)

        # Schedule variance from task completion ratio
        completed = sum(1 for t in tasks if t["status"] == "Completed")
        total_tasks = len(tasks) or 1
        expected_progress = (completed / total_tasks) * 100
        schedule_variance = int((progress - expected_progress) / 5)

        return {
            "project_name": project["name"],
            "project_id": project_id,
            "budget": budget,
            "budget_display": _format_currency(budget),
            "spent": spent,
            "spent_display": _format_currency(spent),
            "spent_pct": round(progress, 1),
            "progress": progress,
            "schedule_variance_days": schedule_variance,
            "safety_score": safety_score,
            "site_risk_score": round(site_risk_score, 1),
            "compliance_score": round(compliance_score, 1),
            "insurance_score": round(insurance_score, 1),
            "incident_count": incident_count,
            "open_tasks": open_tasks,
            "material_cost": material_summary["total_cost"],
            "material_display": _format_currency(material_summary["total_cost"]),
            "material_items": material_summary["item_count"],
            "status": project.get("status", "Active"),
    }


def get_budget_progress_chart() -> pd.DataFrame:
    """Monthly budget vs actual spend derived from project budget and progress."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        if not project:
            return pd.DataFrame(columns=["Month", "Planned_Budget", "Actual_Cost", "Planned_Progress", "Actual_Progress"])

        budget = float(project.get("budget") or 10_000_000)
        progress = float(project.get("progress") or 42.5)

    months = pd.date_range(start="2025-01-01", periods=12, freq="ME")
    planned_budget = [budget * (i + 1) / 12 for i in range(12)]
    planned_progress = [(i + 1) * 100 / 12 for i in range(12)]

    # Actual trails planned with realistic variance
    actual_cost = []
    actual_progress = []
    for i, pb in enumerate(planned_budget):
        variance = 1.0 + (0.02 if i % 3 == 0 else -0.01)
        actual_cost.append(min(pb * variance, budget * (progress / 100 + 0.05)))
        pp = planned_progress[i]
        actual_progress.append(min(pp + (progress - 50) / 12, progress if i == 11 else pp - 2))

    return pd.DataFrame({
        "Month": months.strftime("%b %Y"),
        "Planned_Budget": [round(v, 2) for v in planned_budget],
        "Actual_Cost": [round(v, 2) for v in actual_cost],
        "Planned_Progress": planned_progress,
        "Actual_Progress": [round(v, 1) for v in actual_progress],
    })


def get_incident_heatmap_data() -> pd.DataFrame:
    """Incident counts by zone for heatmap visualization."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        project_id = int(project["id"]) if project else None
        incidents = models.list_incidents(conn, project_id, limit=100)

    if not incidents:
        zones = ["Zone A", "Zone B", "Zone C", "North Yard", "South Gate"]
        return pd.DataFrame({"Zone": zones, "Incidents": [0] * len(zones)})

    zone_counts: dict[str, int] = {}
    for inc in incidents:
        zone = inc.get("zone") or "Unspecified"
        zone_counts[zone] = zone_counts.get(zone, 0) + 1

    return pd.DataFrame({
        "Zone": list(zone_counts.keys()),
        "Incidents": list(zone_counts.values()),
    })


def get_task_status_breakdown() -> pd.DataFrame:
    """Task counts by status for pie/donut chart."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        project_id = int(project["id"]) if project else None
        tasks = models.list_tasks(conn, project_id)

    if not tasks:
        return pd.DataFrame({"Status": ["No Data"], "Count": [0]})

    counts: dict[str, int] = {}
    for t in tasks:
        status = t["status"]
        counts[status] = counts.get(status, 0) + 1

    return pd.DataFrame({"Status": list(counts.keys()), "Count": list(counts.values())})


def get_recent_risk_scores() -> pd.DataFrame:
    """Recent delay risk assessments from risk_logs."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        project_id = int(project["id"]) if project else None
        logs = models.list_risk_logs(conn, project_id, limit=10, risk_type="delay")

    if not logs:
        return pd.DataFrame(columns=["Date", "Risk Score", "Priority"])

    return pd.DataFrame({
        "Date": [log["created_at"][:10] for log in reversed(logs)],
        "Risk Score": [log["score"] for log in reversed(logs)],
        "Priority": [log.get("priority") or "—" for log in reversed(logs)],
    })


def get_site_risk_history() -> pd.DataFrame:
    """Recent site risk assessments for executive dashboard."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        project_id = int(project["id"]) if project else None
        logs = models.list_risk_logs(conn, project_id, limit=10, risk_type="site")

    if not logs:
        return pd.DataFrame(columns=["Date", "Site Risk Score", "Priority"])

    return pd.DataFrame({
        "Date": [log["created_at"][:10] for log in reversed(logs)],
        "Site Risk Score": [log["score"] for log in reversed(logs)],
        "Priority": [log.get("priority") or "—" for log in reversed(logs)],
    })


def get_safety_score_history() -> pd.DataFrame:
    """Recent safety scores from safety_logs."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        project_id = int(project["id"]) if project else None
        logs = models.list_safety_logs(conn, project_id, limit=10) if project_id else []

    scored = [l for l in logs if l.get("safety_score") is not None]
    if not scored:
        return pd.DataFrame(columns=["Date", "Safety Score"])

    return pd.DataFrame({
        "Date": [l["created_at"][:10] for l in reversed(scored)],
        "Safety Score": [l["safety_score"] for l in reversed(scored)],
    })


def get_compliance_score_history() -> pd.DataFrame:
    """Recent compliance scores from compliance_logs."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        project_id = int(project["id"]) if project else None
        logs = models.list_compliance_logs(conn, project_id, limit=10) if project_id else []

    # Filter for overall assessments only
    overall_logs = [log for log in logs if log.get("standard") == "Overall Compliance Assessment"]
    
    if not overall_logs:
        return pd.DataFrame(columns=["Date", "Compliance Score"])

    return pd.DataFrame({
        "Date": [log["created_at"][:10] for log in reversed(overall_logs)],
        "Compliance Score": [log.get("percentage", 0) for log in reversed(overall_logs)],
    })


def get_insurance_risk_history() -> pd.DataFrame:
    """Recent insurance risk scores from insurance_logs."""
    with get_db() as conn:
        project = models.get_default_project(conn)
        project_id = int(project["id"]) if project else None
        logs = models.list_insurance_logs(conn, project_id, limit=10) if project_id else []

    if not logs:
        return pd.DataFrame(columns=["Date", "Insurance Risk Score"])

    return pd.DataFrame({
        "Date": [log["created_at"][:10] for log in reversed(logs)],
        "Insurance Risk Score": [log.get("claim_risk_score", 0) for log in reversed(logs)],
    })
