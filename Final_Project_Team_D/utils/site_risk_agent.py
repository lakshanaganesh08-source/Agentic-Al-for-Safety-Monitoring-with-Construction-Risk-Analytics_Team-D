"""
Site Risk Agent — assess construction site hazards and compute risk scores.

Combines live site inputs with SQLite telemetry (incidents, inspections, tasks)
to produce prioritized site risk assessments stored in risk_logs.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Any

from database import models


PRIORITY_THRESHOLDS = (
    (75, "CRITICAL"),
    (55, "HIGH"),
    (35, "MODERATE"),
    (0, "LOW"),
)

ACTIVITY_WEIGHTS: dict[str, float] = {
    "Crane Operations": 18,
    "Excavation / Trenching": 22,
    "Concrete Pouring": 12,
    "Scaffolding Work": 20,
    "Hot Work (Welding)": 16,
    "Electrical Installation": 14,
    "General Labor": 6,
}

EQUIPMENT_HAZARDS: dict[str, float] = {
    "All Certified": 0,
    "Minor Maintenance Due": 8,
    "Overdue Inspection": 18,
    "Fault Reported": 28,
    "Out of Service": 5,
}


@dataclass
class SiteRiskFactor:
    category: str
    label: str
    score: float
    severity: str
    detail: str


@dataclass
class SiteRiskAssessment:
    score: float
    priority: str
    factors: list[SiteRiskFactor] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def factors_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "priority": self.priority,
            "factors": [
                {
                    "category": f.category,
                    "label": f.label,
                    "score": f.score,
                    "severity": f.severity,
                    "detail": f.detail,
                }
                for f in self.factors
            ],
            "recommendations": self.recommendations,
        }


def _priority_from_score(score: float) -> str:
    for threshold, label in PRIORITY_THRESHOLDS:
        if score >= threshold:
            return label
    return "LOW"


def _severity_label(score: float) -> str:
    if score >= 20:
        return "danger"
    if score >= 10:
        return "warning"
    return "pass"


def _environmental_score(
    weather: str,
    air_quality: str,
    ground_condition: str,
) -> SiteRiskFactor:
    weather_map = {"Clear": 5, "Windy": 12, "Rain": 18, "Storm Warning": 28}
    air_map = {"Good": 3, "Moderate": 10, "Poor / Dusty": 18}
    ground_map = {"Stable": 4, "Wet / Slippery": 14, "Unstable Soil": 22}

    raw = weather_map.get(weather, 10) + air_map.get(air_quality, 8) + ground_map.get(ground_condition, 8)
    return SiteRiskFactor(
        category="environmental",
        label="Environmental Risk",
        score=float(raw),
        severity=_severity_label(raw),
        detail=f"Weather: {weather}, Air: {air_quality}, Ground: {ground_condition}",
    )


def _activity_score(active_activities: list[str]) -> SiteRiskFactor:
    if not active_activities:
        return SiteRiskFactor(
            category="activity",
            label="Site Activity",
            score=5.0,
            severity="pass",
            detail="No high-risk activities selected.",
        )
    raw = sum(ACTIVITY_WEIGHTS.get(a, 8) for a in active_activities)
    raw = min(raw, 45)
    return SiteRiskFactor(
        category="activity",
        label="Site Activity Monitoring",
        score=float(raw),
        severity=_severity_label(raw),
        detail=f"Active: {', '.join(active_activities)}",
    )


def _equipment_score(equipment_status: dict[str, str]) -> SiteRiskFactor:
    raw = sum(EQUIPMENT_HAZARDS.get(status, 10) for status in equipment_status.values())
    raw = min(raw, 40)
    labels = [f"{k}: {v}" for k, v in equipment_status.items()]
    return SiteRiskFactor(
        category="equipment",
        label="Equipment Hazards",
        score=float(raw),
        severity=_severity_label(raw),
        detail="; ".join(labels),
    )


def _unsafe_conditions_score(
    conn: sqlite3.Connection,
    project_id: int | None,
    site_conditions: list[str],
) -> SiteRiskFactor:
    condition_weights = {
        "Unsecured scaffolding": 15,
        "Missing guardrails": 14,
        "Poor housekeeping / debris": 10,
        "Inadequate lighting": 8,
        "Blocked emergency exits": 18,
        "Water pooling": 9,
    }
    raw = sum(condition_weights.get(c, 8) for c in site_conditions)

    incident_count = models.count_incidents(conn, project_id) if project_id else 0
    raw += min(incident_count * 3, 15)

    inspections = models.list_inspections(conn, project_id, limit=3) if project_id else []
    for insp in inspections:
        if insp.get("result") in ("ACTION REQUIRED", "MINOR ISSUES"):
            raw += 6

    raw = min(raw, 50)
    detail_parts = site_conditions or ["No conditions flagged"]
    if incident_count:
        detail_parts.append(f"{incident_count} incidents on record")
    return SiteRiskFactor(
        category="conditions",
        label="Unsafe Site Conditions",
        score=float(raw),
        severity=_severity_label(raw),
        detail="; ".join(detail_parts),
    )


def _build_recommendations(factors: list[SiteRiskFactor], priority: str) -> list[str]:
    tips: list[str] = []
    for factor in sorted(factors, key=lambda f: f.score, reverse=True):
        if factor.category == "environmental" and factor.score >= 15:
            tips.append("Suspend outdoor crane and elevation work until weather stabilizes.")
        elif factor.category == "equipment" and factor.score >= 15:
            tips.append("Quarantine flagged equipment and schedule immediate certified inspection.")
        elif factor.category == "activity" and factor.score >= 20:
            tips.append("Increase spotter coverage and enforce exclusion zones for concurrent high-risk trades.")
        elif factor.category == "conditions" and factor.score >= 12:
            tips.append("Conduct walk-through audit for housekeeping, guardrails, and emergency egress.")

    if priority in ("CRITICAL", "HIGH"):
        tips.append("Brief all crew leads on elevated risk level before next shift.")
    if not tips:
        tips.append("Maintain current safety protocols and continue routine monitoring.")
    return tips[:5]


def assess_site_risk(
    conn: sqlite3.Connection,
    *,
    project_id: int | None,
    weather: str,
    air_quality: str,
    ground_condition: str,
    active_activities: list[str],
    equipment_status: dict[str, str],
    unsafe_conditions: list[str],
) -> SiteRiskAssessment:
    """
    Compute a composite site risk score from operator inputs and DB telemetry.
    """
    factors = [
        _environmental_score(weather, air_quality, ground_condition),
        _activity_score(active_activities),
        _equipment_score(equipment_status),
        _unsafe_conditions_score(conn, project_id, unsafe_conditions),
    ]

    raw_total = sum(f.score for f in factors)
    score = float(min(max(raw_total, 5), 100))
    priority = _priority_from_score(score)
    recommendations = _build_recommendations(factors, priority)

    return SiteRiskAssessment(
        score=round(score, 1),
        priority=priority,
        factors=factors,
        recommendations=recommendations,
    )


def save_site_risk_assessment(
    conn: sqlite3.Connection,
    project_id: int,
    assessment: SiteRiskAssessment,
) -> int:
    """Persist a site risk assessment to risk_logs."""
    return models.create_risk_log(
        conn,
        score=assessment.score,
        priority=assessment.priority,
        factors_json=json.dumps(assessment.factors_dict()),
        project_id=project_id,
        risk_type="site",
    )


def prioritize_risks(factors: list[SiteRiskFactor]) -> list[SiteRiskFactor]:
    """Return risk factors sorted by score descending for prioritization display."""
    return sorted(factors, key=lambda f: f.score, reverse=True)
