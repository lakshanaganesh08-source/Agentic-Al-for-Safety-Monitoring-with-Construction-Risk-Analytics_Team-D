"""
Safety Agent — worker compliance, PPE CV analysis, behavior detection,
accident zone analysis, safety scoring, and Ollama recommendations.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Any

from database import models
from utils.cv_analyzer import CVAnalysisResult, analyze_site_image
from utils.ollama_client import generate_with_ollama


UNSAFE_BEHAVIOR_KEYWORDS: dict[str, str] = {
    "scaffolding": "Working at height without fall protection",
    "crane": "Proximity to suspended load / crane swing zone",
    "walkway": "Entering restricted equipment pathway",
    "guardrail": "Bypassing guardrail or barrier",
    "ppe": "PPE non-compliance observed",
    "speed": "Unsafe vehicle/equipment speed in pedestrian zone",
}


@dataclass
class WorkerCompliance:
    worker_id: int
    name: str
    role: str
    zone: str
    ppe_status: str
    helmet_ok: bool
    vest_ok: bool
    compliance_pct: float


@dataclass
class UnsafeBehaviorFinding:
    zone: str
    behavior: str
    severity: str
    source: str


@dataclass
class SafetyAssessment:
    safety_score: float
    ppe_violations: int
    workers_compliant: int
    workers_total: int
    accident_zones: list[dict[str, Any]]
    behavior_findings: list[UnsafeBehaviorFinding] = field(default_factory=list)
    cv_result: CVAnalysisResult | None = None


def analyze_ppe_image(image) -> CVAnalysisResult:
    """Run computer-vision PPE detection on a site image."""
    return analyze_site_image(image)


def _worker_compliance_from_logs(
    conn: sqlite3.Connection,
    project_id: int,
) -> list[WorkerCompliance]:
    workers = models.list_workers(conn, project_id)
    logs = models.list_safety_logs(conn, project_id, limit=100)

    log_by_worker: dict[int, dict] = {}
    for log in logs:
        wid = log.get("worker_id")
        if wid and wid not in log_by_worker:
            log_by_worker[wid] = log

    results: list[WorkerCompliance] = []
    for w in workers:
        log = log_by_worker.get(w["id"])
        helmet = bool(log["ppe_helmet"]) if log else w.get("ppe_status") == "Compliant"
        vest = bool(log["ppe_vest"]) if log else w.get("ppe_status") == "Compliant"
        if log:
            pct = float(log.get("safety_score") or 0)
        elif w.get("ppe_status") == "Compliant":
            pct = 95.0
        elif w.get("ppe_status") == "Partial":
            pct = 72.0
        else:
            pct = 55.0

        results.append(WorkerCompliance(
            worker_id=int(w["id"]),
            name=w["name"],
            role=w.get("role") or "Worker",
            zone=w.get("site_zone") or "General",
            ppe_status=w.get("ppe_status") or "Unknown",
            helmet_ok=helmet,
            vest_ok=vest,
            compliance_pct=round(pct, 1),
        ))
    return results


def detect_unsafe_behaviors(
    conn: sqlite3.Connection,
    project_id: int,
) -> list[UnsafeBehaviorFinding]:
    """Derive unsafe behavior findings from incidents and safety logs."""
    findings: list[UnsafeBehaviorFinding] = []
    incidents = models.list_incidents(conn, project_id, limit=50)
    safety_logs = models.list_safety_logs(conn, project_id, limit=50)

    for inc in incidents:
        desc_lower = (inc.get("description") or "").lower()
        zone = inc.get("zone") or "Unspecified"
        for keyword, behavior in UNSAFE_BEHAVIOR_KEYWORDS.items():
            if keyword in desc_lower:
                sev = "danger" if inc.get("severity") in ("High", "Critical") else "warning"
                findings.append(UnsafeBehaviorFinding(
                    zone=zone,
                    behavior=behavior,
                    severity=sev,
                    source=f"Incident #{inc['id']}",
                ))
                break
        else:
            if inc.get("incident_type") in ("Near Miss", "Minor Injury"):
                findings.append(UnsafeBehaviorFinding(
                    zone=zone,
                    behavior=inc["incident_type"],
                    severity="warning",
                    source=f"Incident #{inc['id']}",
                ))

    for log in safety_logs:
        behavior = log.get("unsafe_behavior")
        if behavior:
            findings.append(UnsafeBehaviorFinding(
                zone=log.get("zone") or "General",
                behavior=behavior,
                severity="danger" if float(log.get("safety_score") or 100) < 70 else "warning",
                source=f"Safety log #{log['id']}",
            ))

    return findings


def get_accident_prone_zones(
    conn: sqlite3.Connection,
    project_id: int,
) -> list[dict[str, Any]]:
    """Return zones ranked by incident frequency."""
    zones = models.get_accident_zone_counts(conn, project_id)
    if not zones:
        return [
            {"zone": "Zone A", "incident_count": 0, "risk_level": "LOW"},
            {"zone": "Zone B", "incident_count": 0, "risk_level": "LOW"},
        ]
    result = []
    for z in zones:
        count = int(z["incident_count"])
        if count >= 3:
            level = "HIGH"
        elif count >= 1:
            level = "MODERATE"
        else:
            level = "LOW"
        result.append({
            "zone": z["zone"],
            "incident_count": count,
            "risk_level": level,
        })
    return result


def compute_safety_score(
    conn: sqlite3.Connection,
    project_id: int,
    cv_result: CVAnalysisResult | None = None,
) -> SafetyAssessment:
    """
    Aggregate worker compliance, incidents, and optional CV results
    into a project safety score.
    """
    workers = _worker_compliance_from_logs(conn, project_id)
    behaviors = detect_unsafe_behaviors(conn, project_id)
    zones = get_accident_prone_zones(conn, project_id)

    if workers:
        avg_compliance = sum(w.compliance_pct for w in workers) / len(workers) if len(workers) > 0 else 85.0
        ppe_violations = sum(1 for w in workers if not (w.helmet_ok and w.vest_ok))
        compliant = sum(1 for w in workers if w.helmet_ok and w.vest_ok)
    else:
        avg_compliance = 85.0
        ppe_violations = 0
        compliant = 0

    incident_count = models.count_incidents(conn, project_id)
    zone_penalty = sum(5 for z in zones if z["risk_level"] == "HIGH")
    behavior_penalty = len(behaviors) * 3

    score = avg_compliance - incident_count * 4 - zone_penalty - behavior_penalty

    if cv_result:
        score = score * 0.6 + cv_result.overall_score * 0.4
        if cv_result.hardhat_compliance_pct < 75:
            ppe_violations += 1
        if cv_result.vest_compliance_pct < 75:
            ppe_violations += 1

    latest = models.get_latest_safety_score(conn, project_id)
    if latest is not None and cv_result is None:
        score = score * 0.7 + latest * 0.3

    score = float(max(40, min(100, round(score, 1))))

    return SafetyAssessment(
        safety_score=score,
        ppe_violations=ppe_violations,
        workers_compliant=compliant,
        workers_total=len(workers),
        accident_zones=zones,
        behavior_findings=behaviors,
        cv_result=cv_result,
    )


def save_safety_assessment(
    conn: sqlite3.Connection,
    project_id: int,
    assessment: SafetyAssessment,
    cv_result: CVAnalysisResult | None = None,
) -> int:
    """Persist aggregate safety score and optional CV findings."""
    helmet = 1 if cv_result and cv_result.hardhat_compliance_pct >= 75 else 0
    vest = 1 if cv_result and cv_result.vest_compliance_pct >= 75 else 0
    notes = None
    if cv_result:
        notes = json.dumps(cv_result.to_dict())

    behavior_note = None
    if assessment.behavior_findings:
        behavior_note = assessment.behavior_findings[0].behavior

    return models.create_safety_log(
        conn,
        safety_score=assessment.safety_score,
        project_id=project_id,
        ppe_helmet=helmet,
        ppe_vest=vest,
        unsafe_behavior=behavior_note,
        zone=assessment.accident_zones[0]["zone"] if assessment.accident_zones else None,
        notes=notes,
    )


def generate_safety_recommendations(
    assessment: SafetyAssessment,
    project_name: str = "Construction Site",
) -> tuple[str, bool]:
    """
    Use Ollama to produce actionable safety recommendations.
    Falls back to rule-based tips when Ollama is unavailable.
    """
    zone_summary = ", ".join(
        f"{z['zone']} ({z['incident_count']} incidents, {z['risk_level']})"
        for z in assessment.accident_zones[:5]
    ) or "No zones flagged"
    behavior_summary = "; ".join(b.behavior for b in assessment.behavior_findings[:5]) or "None detected"

    prompt = f"""You are a construction safety officer AI. Provide 4-5 concise, actionable safety recommendations.

Project: {project_name}
Safety Score: {assessment.safety_score}%
PPE Violations: {assessment.ppe_violations}
Workers Compliant: {assessment.workers_compliant}/{assessment.workers_total}
Accident-Prone Zones: {zone_summary}
Unsafe Behaviors: {behavior_summary}

Format as a numbered list. Be specific to construction sites. Keep each point under 2 sentences."""

    text, ok = generate_with_ollama(prompt, max_tokens=280, temperature=0.4)
    if ok:
        return text.strip(), True

    fallback = _fallback_recommendations(assessment)
    return fallback, False


def _fallback_recommendations(assessment: SafetyAssessment) -> str:
    tips = []
    if assessment.ppe_violations > 0:
        tips.append("1. Enforce mandatory hardhat and high-vis vest checks at all zone entry points.")
    high_zones = [z for z in assessment.accident_zones if z["risk_level"] == "HIGH"]
    if high_zones:
        tips.append(f"2. Increase supervision in {', '.join(z['zone'] for z in high_zones)} — highest incident density.")
    if assessment.behavior_findings:
        tips.append("3. Conduct toolbox talk addressing crane proximity and fall protection violations.")
    if assessment.safety_score < 75:
        tips.append("4. Schedule an unannounced safety audit within 48 hours.")
    tips.append("5. Review and update site-specific JSA documents for active work fronts.")
    return "\n".join(tips)
