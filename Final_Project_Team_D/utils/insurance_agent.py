"""
Insurance Agent — analyze insurance exposure, incident severity, and claim risk.

Combines incident data, safety logs, and risk assessments to compute insurance risk scores,
predict claim probability, and document insurance-related metrics.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from database import models


SEVERITY_WEIGHTS = {
    "Low": 1.0,
    "Moderate": 2.5,
    "High": 5.0,
    "CRITICAL": 8.0,
}

INCIDENT_TYPE_RISK_FACTORS = {
    "Near Miss": 1.0,
    "Hazard Identification": 1.5,
    "Property Damage": 3.0,
    "Minor Injury": 4.0,
    "Major Injury": 7.0,
    "Fatality": 10.0,
}

CLAIM_PROBABILITY_THRESHOLDS = {
    (0, 20): "VERY LOW",
    (20, 40): "LOW",
    (40, 60): "MODERATE",
    (60, 80): "HIGH",
    (80, 100): "VERY HIGH",
}


@dataclass
class IncidentSeverity:
    incident_id: int
    incident_type: str
    severity: str
    severity_score: float
    potential_claim_cost: float
    recommended_action: str


@dataclass
class InsuranceExposure:
    total_exposure: float
    high_risk_incidents: int
    moderate_risk_incidents: int
    low_risk_incidents: int
    coverage_adequacy: str


@dataclass
class ClaimRiskPrediction:
    claim_probability: float
    risk_level: str
    estimated_annual_claims: float
    confidence_interval: tuple[float, float]
    contributing_factors: list[str]


@dataclass
class InsuranceAssessment:
    insurance_risk_score: float
    risk_category: str  # LOW, MODERATE, HIGH, CRITICAL
    exposure: InsuranceExposure
    claim_prediction: ClaimRiskPrediction
    severity_analysis: list[IncidentSeverity]
    recommendations: list[str]


def assess_insurance_risk(conn: sqlite3.Connection, project_id: int) -> InsuranceAssessment:
    """
    Perform comprehensive insurance risk assessment.
    
    Analyzes incident history, safety logs, and risk assessments to compute
    overall insurance risk score and claim predictions.
    """
    # Get project data
    incidents = models.list_incidents(conn, project_id, limit=100)
    safety_logs = models.list_safety_logs(conn, project_id, limit=50)
    risk_logs = models.list_risk_logs(conn, project_id, limit=30)
    
    # Analyze incident severity
    severity_analysis = _analyze_incident_severity(incidents)
    
    # Calculate insurance exposure
    exposure = _calculate_insurance_exposure(incidents, safety_logs)
    
    # Predict claim risk
    claim_prediction = _predict_claim_risk(incidents, risk_logs, safety_logs)
    
    # Calculate overall insurance risk score
    insurance_risk_score = _calculate_insurance_risk_score(
        exposure, claim_prediction, severity_analysis
    )
    
    # Determine risk category
    risk_category = _determine_risk_category(insurance_risk_score)
    
    # Generate recommendations
    recommendations = _generate_insurance_recommendations(
        exposure, claim_prediction, severity_analysis
    )
    
    return InsuranceAssessment(
        insurance_risk_score=insurance_risk_score,
        risk_category=risk_category,
        exposure=exposure,
        claim_prediction=claim_prediction,
        severity_analysis=severity_analysis,
        recommendations=recommendations
    )


def _analyze_incident_severity(incidents: list[dict]) -> list[IncidentSeverity]:
    """Analyze each incident for severity and potential claim impact."""
    severity_analysis = []
    
    for inc in incidents:
        incident_type = inc.get("incident_type", "Unknown")
        severity = inc.get("severity", "Moderate")
        
        # Calculate severity score
        base_score = SEVERITY_WEIGHTS.get(severity, 2.5)
        type_multiplier = INCIDENT_TYPE_RISK_FACTORS.get(incident_type, 1.5)
        severity_score = base_score * type_multiplier
        
        # Estimate potential claim cost
        potential_claim_cost = _estimate_claim_cost(incident_type, severity)
        
        # Generate recommended action
        recommended_action = _get_severity_action(severity, incident_type)
        
        severity_analysis.append(IncidentSeverity(
            incident_id=inc["id"],
            incident_type=incident_type,
            severity=severity,
            severity_score=severity_score,
            potential_claim_cost=potential_claim_cost,
            recommended_action=recommended_action
        ))
    
    return severity_analysis


def _estimate_claim_cost(incident_type: str, severity: str) -> float:
    """Estimate potential claim cost based on incident type and severity."""
    base_costs = {
        "Near Miss": 0,
        "Hazard Identification": 500,
        "Property Damage": 5000,
        "Minor Injury": 15000,
        "Major Injury": 75000,
        "Fatality": 500000,
    }
    
    base_cost = base_costs.get(incident_type, 2500)
    
    severity_multipliers = {
        "Low": 0.5,
        "Moderate": 1.0,
        "High": 2.0,
        "CRITICAL": 5.0,
    }
    
    multiplier = severity_multipliers.get(severity, 1.0)
    return base_cost * multiplier


def _get_severity_action(severity: str, incident_type: str) -> str:
    """Generate recommended action based on severity."""
    if severity == "CRITICAL":
        return "IMMEDIATE: Stop work, investigate fully, notify insurance carrier"
    elif severity == "High":
        return "URGENT: Detailed investigation, safety review, document thoroughly"
    elif severity == "Moderate":
        return "Standard investigation process, update safety protocols"
    else:
        return "Document for records, monitor for patterns"


def _calculate_insurance_exposure(incidents: list[dict], safety_logs: list[dict]) -> InsuranceExposure:
    """Calculate total insurance exposure from incidents and safety data."""
    total_exposure = 0.0
    high_risk = 0
    moderate_risk = 0
    low_risk = 0
    
    for inc in incidents:
        severity = inc.get("severity", "Moderate")
        incident_type = inc.get("incident_type", "Unknown")
        
        cost = _estimate_claim_cost(incident_type, severity)
        total_exposure += cost
        
        if severity in ["High", "CRITICAL"]:
            high_risk += 1
        elif severity == "Moderate":
            moderate_risk += 1
        else:
            low_risk += 1
    
    # Assess coverage adequacy based on safety performance
    safety_score = 0
    if safety_logs:
        safety_score = sum(log.get("safety_score", 70) for log in safety_logs) / len(safety_logs)
    
    if safety_score >= 90:
        coverage_adequacy = "ADEQUATE"
    elif safety_score >= 75:
        coverage_adequacy = "REVIEW RECOMMENDED"
    else:
        coverage_adequacy = "INADEQUATE - CONSIDER INCREASE"
    
    return InsuranceExposure(
        total_exposure=total_exposure,
        high_risk_incidents=high_risk,
        moderate_risk_incidents=moderate_risk,
        low_risk_incidents=low_risk,
        coverage_adequacy=coverage_adequacy
    )


def _predict_claim_risk(incidents: list[dict], risk_logs: list[dict], safety_logs: list[dict]) -> ClaimRiskPrediction:
    """Predict claim probability and estimate annual claims."""
    # Base claim probability from incident rate
    incident_count = len(incidents)
    base_probability = min(incident_count * 5, 80)  # Cap at 80%
    
    # Adjust based on risk scores
    avg_risk_score = 0
    if risk_logs:
        avg_risk_score = sum(log.get("score", 50) for log in risk_logs) / len(risk_logs)
    risk_adjustment = (avg_risk_score - 50) * 0.3
    
    # Adjust based on safety performance
    avg_safety_score = 70
    if safety_logs:
        avg_safety_score = sum(log.get("safety_score", 70) for log in safety_logs) / len(safety_logs)
    safety_adjustment = (70 - avg_safety_score) * 0.4
    
    # Calculate final claim probability
    claim_probability = base_probability + risk_adjustment + safety_adjustment
    claim_probability = max(0, min(100, claim_probability))  # Clamp between 0-100
    
    # Determine risk level
    risk_level = "LOW"
    for (low, high), level in CLAIM_PROBABILITY_THRESHOLDS.items():
        if low <= claim_probability < high:
            risk_level = level
            break
    
    # Estimate annual claims based on exposure
    total_exposure = sum(_estimate_claim_cost(
        inc.get("incident_type", "Unknown"), 
        inc.get("severity", "Moderate")
    ) for inc in incidents)
    
    estimated_annual_claims = total_exposure * (claim_probability / 100)
    
    # Calculate confidence interval
    confidence = 10  # +/- 10%
    confidence_interval = (
        max(0, estimated_annual_claims * (1 - confidence / 100)),
        estimated_annual_claims * (1 + confidence / 100)
    )
    
    # Identify contributing factors
    contributing_factors = []
    if incident_count > 5:
        contributing_factors.append(f"High incident count ({incident_count})")
    if avg_risk_score > 60:
        contributing_factors.append(f"Elevated risk scores ({avg_risk_score:.0f}%)")
    if avg_safety_score < 80:
        contributing_factors.append(f"Below-average safety performance ({avg_safety_score:.0f}%)")
    if not contributing_factors:
        contributing_factors.append("Normal operational risk profile")
    
    return ClaimRiskPrediction(
        claim_probability=claim_probability,
        risk_level=risk_level,
        estimated_annual_claims=estimated_annual_claims,
        confidence_interval=confidence_interval,
        contributing_factors=contributing_factors
    )


def _calculate_insurance_risk_score(
    exposure: InsuranceExposure,
    claim_prediction: ClaimRiskPrediction,
    severity_analysis: list[IncidentSeverity]
) -> float:
    """Calculate overall insurance risk score (0-100)."""
    # Exposure component (40% weight)
    exposure_score = min(exposure.total_exposure / 10000 * 40, 40)
    
    # Claim probability component (35% weight)
    claim_score = claim_prediction.claim_probability * 0.35
    
    # Severity component (25% weight)
    avg_severity = sum(s.severity_score for s in severity_analysis) / len(severity_analysis) if severity_analysis and len(severity_analysis) > 0 else 2.5
    severity_score = min(avg_severity * 5, 25)
    
    total_score = exposure_score + claim_score + severity_score
    return min(100, total_score)


def _determine_risk_category(risk_score: float) -> str:
    """Determine risk category from risk score."""
    if risk_score >= 75:
        return "CRITICAL"
    elif risk_score >= 55:
        return "HIGH"
    elif risk_score >= 35:
        return "MODERATE"
    else:
        return "LOW"


def _generate_insurance_recommendations(
    exposure: InsuranceExposure,
    claim_prediction: ClaimRiskPrediction,
    severity_analysis: list[IncidentSeverity]
) -> list[str]:
    """Generate actionable insurance recommendations."""
    recommendations = []
    
    # Coverage recommendations
    if exposure.coverage_adequacy != "ADEQUATE":
        recommendations.append(f"Review insurance coverage - {exposure.coverage_adequacy}")
    
    # High-severity incident recommendations
    high_severity = [s for s in severity_analysis if s.severity in ["High", "CRITICAL"]]
    if high_severity:
        recommendations.append(f"Address {len(high_severity)} high-severity incidents with carrier notification")
    
    # Claim probability recommendations
    if claim_prediction.risk_level in ["HIGH", "VERY HIGH"]:
        recommendations.append("Implement loss prevention program to reduce claim probability")
    
    # Exposure recommendations
    if exposure.total_exposure > 50000:
        recommendations.append("Consider umbrella policy for high exposure protection")
    
    # General recommendations
    if claim_prediction.estimated_annual_claims > 10000:
        recommendations.append("Budget for estimated annual claims in financial planning")
    
    if not recommendations:
        recommendations.append("Maintain current risk management practices")
    
    return recommendations


def save_insurance_assessment(conn: sqlite3.Connection, project_id: int, assessment: InsuranceAssessment) -> int:
    """Save insurance assessment to database."""
    log_id = models.create_insurance_log(
        conn,
        exposure=assessment.exposure.total_exposure,
        severity=assessment.risk_category,
        project_id=project_id,
        claim_risk_score=assessment.insurance_risk_score,
        notes=f"Claim risk: {assessment.claim_prediction.risk_level} ({assessment.claim_prediction.claim_probability:.0f}%)"
    )
    
    return log_id


def get_insurance_trend(conn: sqlite3.Connection, project_id: int, limit: int = 10) -> list[dict[str, Any]]:
    """Get historical insurance risk scores for trend analysis."""
    logs = models.list_insurance_logs(conn, project_id, limit=limit)
    
    return [
        {
            "date": log["created_at"][:10],
            "risk_score": log.get("claim_risk_score", 0),
            "severity": log.get("severity", "UNKNOWN"),
            "exposure": log.get("exposure", 0)
        }
        for log in logs
    ]


def document_claim(
    conn: sqlite3.Connection,
    project_id: int,
    incident_id: int,
    claim_amount: float,
    claim_type: str,
    description: str
) -> int:
    """Document a claim for insurance records."""
    log_id = models.create_insurance_log(
        conn,
        exposure=claim_amount,
        severity="CLAIM",
        project_id=project_id,
        incident_id=incident_id,
        claim_risk_score=0,  # Actual claim, not a prediction
        notes=f"Claim Type: {claim_type} - {description}"
    )
    
    return log_id
