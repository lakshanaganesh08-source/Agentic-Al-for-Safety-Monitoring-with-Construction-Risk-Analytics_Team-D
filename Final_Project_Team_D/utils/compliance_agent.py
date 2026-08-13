"""
Compliance Agent — validate construction standards and monitor regulatory compliance.

Combines inspection data, incident reports, and safety logs to compute compliance scores,
detect policy violations, and track regulatory adherence.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from database import models


COMPLIANCE_STANDARDS = [
    "OSHA 1926 Construction Standards",
    "ISO 45001 Occupational Health",
    "Local Building Code",
    "Environmental Regulations",
    "Fire Safety Code",
    "Electrical Safety Standards",
]

VIOLATION_CATEGORIES = [
    "PPE Non-Compliance",
    "Unsafe Scaffolding",
    "Electrical Violations",
    "Fire Safety Breach",
    "Fall Protection",
    "Hazardous Materials",
    "Documentation Gaps",
]


@dataclass
class ComplianceCheck:
    standard: str
    status: str  # COMPLIANT, NON_COMPLIANT, PARTIAL
    score: float
    violations: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ComplianceAssessment:
    overall_percentage: float
    status: str  # COMPLIANT, AT_RISK, NON_COMPLIANT
    checks: list[ComplianceCheck] = field(default_factory=list)
    violations_detected: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def assess_compliance(conn: sqlite3.Connection, project_id: int) -> ComplianceAssessment:
    """
    Perform comprehensive compliance assessment using project data.
    
    Combines inspection results, safety logs, incidents, and worker compliance
    to generate an overall compliance score.
    """
    checks = []
    violations = []
    
    # Get project data
    incidents = models.list_incidents(conn, project_id, limit=100)
    inspections = models.list_inspections(conn, project_id, limit=50)
    safety_logs = models.list_safety_logs(conn, project_id, limit=100)
    workers = models.list_workers(conn, project_id)
    
    # Check 1: Inspection Compliance
    inspection_score = _calculate_inspection_compliance(inspections)
    inspection_violations = [i["result"] for i in inspections if i.get("result") != "COMPLIANT"]
    checks.append(ComplianceCheck(
        standard="Site Inspections",
        status="COMPLIANT" if inspection_score >= 90 else "AT_RISK",
        score=inspection_score,
        violations=inspection_violations[:5],
        notes=f"{len(inspections)} inspections conducted"
    ))
    violations.extend(inspection_violations)
    
    # Check 2: Incident Rate Compliance
    incident_score = _calculate_incident_compliance(incidents)
    checks.append(ComplianceCheck(
        standard="Incident Rate Compliance",
        status="COMPLIANT" if incident_score >= 85 else "AT_RISK",
        score=incident_score,
        violations=[f"{len(incidents)} incidents logged"],
        notes="Based on total incident count vs project duration"
    ))
    
    # Check 3: PPE Compliance
    ppe_score = _calculate_ppe_compliance(safety_logs, workers)
    ppe_violations = [f"Worker {w['name']}: {w['ppe_status']}" 
                      for w in workers if w.get("ppe_status") == "Non-Compliant"]
    checks.append(ComplianceCheck(
        standard="PPE Requirements (OSHA 1926)",
        status="COMPLIANT" if ppe_score >= 90 else "NON_COMPLIANT",
        score=ppe_score,
        violations=ppe_violations[:3],
        notes=f"Based on {len(workers)} workers monitored"
    ))
    violations.extend(ppe_violations)
    
    # Check 4: Safety Training Compliance
    training_score = _calculate_training_compliance(safety_logs)
    checks.append(ComplianceCheck(
        standard="Safety Training Documentation",
        status="COMPLIANT" if training_score >= 80 else "PARTIAL",
        score=training_score,
        violations=[],
        notes="Estimated from safety log documentation"
    ))
    
    # Check 5: Equipment Safety Compliance
    equipment_score = _calculate_equipment_compliance(inspections)
    checks.append(ComplianceCheck(
        standard="Equipment Safety Standards",
        status="COMPLIANT" if equipment_score >= 85 else "AT_RISK",
        score=equipment_score,
        violations=[],
        notes="Based on inspection equipment checks"
    ))
    
    # Calculate overall percentage
    overall_percentage = sum(c.score for c in checks) / len(checks) if checks else 0.0
    
    # Determine overall status
    if overall_percentage >= 90:
        status = "COMPLIANT"
    elif overall_percentage >= 70:
        status = "AT_RISK"
    else:
        status = "NON_COMPLIANT"
    
    # Generate recommendations
    recommendations = _generate_compliance_recommendations(checks, violations)
    
    return ComplianceAssessment(
        overall_percentage=overall_percentage,
        status=status,
        checks=checks,
        violations_detected=violations[:10],
        recommendations=recommendations
    )


def _calculate_inspection_compliance(inspections: list[dict]) -> float:
    """Calculate compliance percentage from inspection results."""
    if not inspections:
        return 85.0  # Default score if no inspections
    
    compliant = sum(1 for i in inspections if i.get("result") == "COMPLIANT")
    return (compliant / len(inspections)) * 100 if len(inspections) > 0 else 85.0


def _calculate_incident_compliance(incidents: list[dict]) -> float:
    """Calculate compliance score based on incident rate."""
    # Fewer incidents = higher compliance score
    count = len(incidents)
    if count == 0:
        return 100.0
    elif count <= 2:
        return 90.0
    elif count <= 5:
        return 75.0
    elif count <= 10:
        return 60.0
    else:
        return 40.0


def _calculate_ppe_compliance(safety_logs: list[dict], workers: list[dict]) -> float:
    """Calculate PPE compliance from safety logs and worker data."""
    if not workers:
        return 85.0
    
    compliant_workers = sum(1 for w in workers if w.get("ppe_status") == "Compliant")
    return (compliant_workers / len(workers)) * 100 if len(workers) > 0 else 85.0


def _calculate_training_compliance(safety_logs: list[dict]) -> float:
    """Estimate training compliance from safety documentation."""
    # Use safety log count as proxy for documentation completeness
    if not safety_logs:
        return 70.0
    
    # More safety logs = better documentation = higher training compliance
    log_count = len(safety_logs)
    if log_count >= 20:
        return 95.0
    elif log_count >= 10:
        return 85.0
    elif log_count >= 5:
        return 75.0
    else:
        return 65.0


def _calculate_equipment_compliance(inspections: list[dict]) -> float:
    """Calculate equipment safety compliance from inspections."""
    if not inspections:
        return 80.0
    
    # Parse inspection checklists for equipment issues
    equipment_issues = 0
    total_inspections = len(inspections)
    
    for insp in inspections:
        try:
            checklist = insp.get("checklist_json", "{}")
            if isinstance(checklist, str):
                import json
                checklist = json.loads(checklist)
            
            # Check for equipment-related issues
            if isinstance(checklist, dict):
                if checklist.get("equipment_status") != "All Certified":
                    equipment_issues += 1
        except (json.JSONDecodeError, TypeError):
            pass
    
    if total_inspections == 0:
        return 80.0
    
    compliance_rate = 1 - (equipment_issues / total_inspections) if total_inspections > 0 else 1.0
    return compliance_rate * 100


def _generate_compliance_recommendations(checks: list[ComplianceCheck], violations: list[str]) -> list[str]:
    """Generate actionable recommendations based on compliance assessment."""
    recommendations = []
    
    for check in checks:
        if check.score < 85:
            if "PPE" in check.standard:
                recommendations.append("Conduct immediate PPE audit and provide refresher training")
            elif "Inspection" in check.standard:
                recommendations.append("Increase inspection frequency and address all non-compliant findings")
            elif "Incident" in check.standard:
                recommendations.append("Review incident root causes and implement preventive measures")
            elif "Training" in check.standard:
                recommendations.append("Update safety training documentation and schedule mandatory sessions")
            elif "Equipment" in check.standard:
                recommendations.append("Schedule comprehensive equipment certification and maintenance")
    
    if not recommendations:
        recommendations.append("Maintain current compliance practices and schedule regular reviews")
    
    return recommendations


def detect_policy_violations(conn: sqlite3.Connection, project_id: int) -> list[dict[str, Any]]:
    """
    Detect specific policy violations from project data.
    
    Returns a list of detected violations with severity and recommended actions.
    """
    violations = []
    
    # Get relevant data
    incidents = models.list_incidents(conn, project_id, limit=50)
    inspections = models.list_inspections(conn, project_id, limit=30)
    workers = models.list_workers(conn, project_id)
    
    # Check for PPE violations
    ppe_violators = [w for w in workers if w.get("ppe_status") == "Non-Compliant"]
    for worker in ppe_violators:
        violations.append({
            "type": "PPE Non-Compliance",
            "severity": "HIGH",
            "description": f"Worker {worker['name']} not compliant with PPE requirements",
            "location": worker.get("site_zone", "Unknown"),
            "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action_required": "Immediate PPE provision and training"
        })
    
    # Check for inspection failures
    failed_inspections = [i for i in inspections if i.get("result") != "COMPLIANT"]
    for insp in failed_inspections:
        violations.append({
            "type": "Inspection Non-Compliance",
            "severity": "MODERATE",
            "description": f"Inspection failed: {insp.get('result', 'Unknown')}",
            "location": "Site-wide",
            "detected_at": insp.get("inspection_date", datetime.now().strftime("%Y-%m-%d")),
            "action_required": "Rectify inspection findings and schedule re-inspection"
        })
    
    # Check for high-severity incidents
    severe_incidents = [i for i in incidents if i.get("severity") in ["HIGH", "CRITICAL"]]
    for inc in severe_incidents:
        violations.append({
            "type": "Safety Protocol Breach",
            "severity": "CRITICAL",
            "description": f"High-severity incident: {inc.get('incident_type', 'Unknown')}",
            "location": inc.get("zone", "Unknown"),
            "detected_at": inc.get("created_at", datetime.now().strftime("%Y-%m-%d")),
            "action_required": "Immediate safety review and protocol revision"
        })
    
    return violations


def save_compliance_assessment(conn: sqlite3.Connection, project_id: int, assessment: ComplianceAssessment) -> int:
    """Save compliance assessment to database."""
    # Save overall compliance percentage
    log_id = models.create_compliance_log(
        conn,
        standard="Overall Compliance Assessment",
        status=assessment.status,
        project_id=project_id,
        violation=f"{len(assessment.violations_detected)} violations detected",
        percentage=assessment.overall_percentage
    )
    
    # Save individual check results
    for check in assessment.checks:
        models.create_compliance_log(
            conn,
            standard=check.standard,
            status=check.status,
            project_id=project_id,
            violation="; ".join(check.violations) if check.violations else None,
            percentage=check.score
        )
    
    return log_id


def get_compliance_trend(conn: sqlite3.Connection, project_id: int, limit: int = 10) -> list[dict[str, Any]]:
    """Get historical compliance scores for trend analysis."""
    logs = models.list_compliance_logs(conn, project_id, limit=limit)
    
    # Filter for overall assessments only
    overall_logs = [log for log in logs if log.get("standard") == "Overall Compliance Assessment"]
    
    return [
        {
            "date": log["created_at"][:10],
            "percentage": log.get("percentage", 0),
            "status": log.get("status", "UNKNOWN")
        }
        for log in overall_logs
    ]
