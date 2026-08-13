"""
Demo seed data for Construction Intelligence Hub.

Populates projects, tasks, and optional sample incidents when tables are
empty. Safe to run multiple times — skips seeding if data already exists.
"""

from __future__ import annotations

import sqlite3

from config.settings import DEFAULT_PROJECT_NAME
from database import db
from database import models


DEFAULT_TASKS: list[dict[str, str]] = [
    {
        "task_name": "Foundation Concrete Pouring",
        "status": "Completed",
        "assignee": "John Doe",
        "priority": "High",
    },
    {
        "task_name": "Steel Framing Phase 1",
        "status": "In Progress",
        "assignee": "Sarah Smith",
        "priority": "Critical",
    },
    {
        "task_name": "Electrical Wiring - Floor 2",
        "status": "Pending",
        "assignee": "Mike Johnson",
        "priority": "Medium",
    },
    {
        "task_name": "HVAC Ductwork Installation",
        "status": "In Progress",
        "assignee": "Alex Rivera",
        "priority": "High",
    },
    {
        "task_name": "Site Safety Inspection Audit",
        "status": "Completed",
        "assignee": "Sarah Smith",
        "priority": "Medium",
    },
]


def seed_projects_and_tasks(conn: sqlite3.Connection) -> int:
    """
    Insert default project and tasks if the tasks table is empty.

    Returns:
        project_id of the default project.
    """
    if db.table_row_count(conn, "tasks") > 0:
        project = models.get_default_project(conn)
        if project:
            return int(project["id"])
        raise RuntimeError("Tasks exist but no project found.")

    project_id = models.create_project(
        conn,
        name=DEFAULT_PROJECT_NAME,
        client_name="Metro Infrastructure Corp",
        location="Bengaluru, KA",
        project_type="Commercial",
        status="In Progress",
        budget=50_000_000,
        actual_spending=32_000_000,
        start_date="2025-01-01",
        end_date="2025-12-31",
        actual_start_date="2025-01-05",
        project_manager="Sarah Smith",
        description="Construction of Executive Office Tower with modern RCC structure.",
        progress=64.0,
    )

    for task in DEFAULT_TASKS:
        models.create_task(
            conn,
            task_name=task["task_name"],
            status=task["status"],
            assignee=task["assignee"],
            priority=task["priority"],
            project_id=project_id,
            progress=100.0 if task["status"] == "Completed" else (50.0 if task["status"] == "In Progress" else 0.0),
            start_date="2025-01-10",
            due_date="2025-06-30",
        )

    # Seed default milestones
    sample_milestones = [
        ("Site Preparation Completed", "2025-02-15", "2025-02-14", "Completed"),
        ("Foundation Completed", "2025-04-30", "2025-05-02", "Completed"),
        ("Structural Framing Completed", "2025-08-31", None, "In Progress"),
        ("MEP & HVAC Installation", "2025-10-31", None, "Upcoming"),
        ("Final Inspection & Handover", "2025-12-31", None, "Upcoming"),
    ]
    for m_name, t_date, a_date, status in sample_milestones:
        models.create_milestone(conn, project_id, m_name, t_date, a_date, status)

    # Seed default risks/issues
    sample_issues = [
        ("Steel Rebar Delivery Delay", "High demand in region causing 2-week supply lag", "High", "Sarah Smith", "Open"),
        ("Foundation Waterproofing Inspection", "Quality audit required before backfilling", "Medium", "John Doe", "Resolved"),
    ]
    for title, desc, sev, resp, st in sample_issues:
        models.create_project_issue(conn, project_id, title, desc, sev, resp, st)

    return project_id


def seed_demo_incidents(conn: sqlite3.Connection, project_id: int) -> int:
    """
    Insert sample incidents when the incidents table is empty.

    Returns:
        Number of incidents inserted.
    """
    if db.table_row_count(conn, "incidents") > 0:
        return 0

    samples = [
        {
            "incident_type": "Hazard Identification",
            "description": "Unsecured scaffolding noted near Zone B — guardrail missing.",
            "zone": "Zone B",
            "reported_by": "Sarah Smith",
        },
        {
            "incident_type": "Near Miss",
            "description": "Crane load swing passed within 2m of personnel walkway.",
            "zone": "North Yard",
            "reported_by": "Mike Johnson",
        },
    ]

    for item in samples:
        models.create_incident(
            conn,
            incident_type=item["incident_type"],
            description=item["description"],
            project_id=project_id,
            zone=item["zone"],
            reported_by=item["reported_by"],
        )

    return len(samples)


DEFAULT_WORKERS: list[dict[str, str]] = [
    {"name": "John Doe", "role": "Foreman", "site_zone": "Zone A", "ppe_status": "Compliant"},
    {"name": "Sarah Smith", "role": "Safety Officer", "site_zone": "Zone B", "ppe_status": "Compliant"},
    {"name": "Mike Johnson", "role": "Electrician", "site_zone": "North Yard", "ppe_status": "Partial"},
    {"name": "Alex Rivera", "role": "Crane Operator", "site_zone": "North Yard", "ppe_status": "Compliant"},
    {"name": "Priya Patel", "role": "Scaffolder", "site_zone": "Zone B", "ppe_status": "Non-Compliant"},
    {"name": "Carlos Mendez", "role": "Laborer", "site_zone": "South Gate", "ppe_status": "Partial"},
]


def seed_workers(conn: sqlite3.Connection, project_id: int) -> int:
    """Insert demo workers when the workers table is empty."""
    if db.table_row_count(conn, "workers") > 0:
        return 0

    for w in DEFAULT_WORKERS:
        models.create_worker(
            conn,
            name=w["name"],
            role=w["role"],
            site_zone=w["site_zone"],
            ppe_status=w["ppe_status"],
            project_id=project_id,
        )
    return len(DEFAULT_WORKERS)


def seed_agent_logs(conn: sqlite3.Connection, project_id: int) -> dict[str, int]:
    """Seed sample site risk and safety logs for Phase 3 agents."""
    site_added = 0
    safety_added = 0

    existing_site = conn.execute(
        "SELECT COUNT(*) AS cnt FROM risk_logs WHERE risk_type = 'site'"
    ).fetchone()
    if existing_site and int(existing_site["cnt"]) == 0:
        import json
        from utils.site_risk_agent import assess_site_risk, save_site_risk_assessment

        assessment = assess_site_risk(
            conn,
            project_id=project_id,
            weather="Windy",
            air_quality="Moderate",
            ground_condition="Wet / Slippery",
            active_activities=["Scaffolding Work", "Crane Operations"],
            equipment_status={
                "Tower Crane": "Minor Maintenance Due",
                "Excavator": "All Certified",
                "Scaffolding": "Overdue Inspection",
            },
            unsafe_conditions=["Unsecured scaffolding", "Missing guardrails"],
        )
        save_site_risk_assessment(conn, project_id, assessment)
        site_added = 1

    if db.table_row_count(conn, "safety_logs") == 0:
        workers = models.list_workers(conn, project_id)
        for i, w in enumerate(workers[:4]):
            helmet = 1 if w.get("ppe_status") == "Compliant" else 0
            vest = 1 if w.get("ppe_status") in ("Compliant", "Partial") else 0
            score = 95.0 if w.get("ppe_status") == "Compliant" else (72.0 if w.get("ppe_status") == "Partial" else 58.0)
            models.create_safety_log(
                conn,
                safety_score=score,
                project_id=project_id,
                worker_id=int(w["id"]),
                ppe_helmet=helmet,
                ppe_vest=vest,
                zone=w.get("site_zone"),
                unsafe_behavior="PPE non-compliance observed" if w.get("ppe_status") == "Non-Compliant" else None,
            )
            safety_added += 1

    return {"site_risk_logs": site_added, "safety_logs": safety_added}


def seed_users(conn: sqlite3.Connection) -> int:
    """Seed default system users if users table is empty."""
    if db.table_row_count(conn, "users") > 0:
        return 0

    users_to_seed = [
        ("System Administrator", "admin@constructionhub.com", "AdminPass123!", "Admin"),
        ("Project Manager", "manager@constructionhub.com", "ManagerPass123!", "Manager"),
        ("Construction User", "user@constructionhub.com", "UserPass123!", "User"),
        # Backward-compatibility fallback demo accounts
        ("Admin User", "admin", "admin123", "Admin"),
        ("Manager User", "user", "password123", "Manager"),
        ("Demo Inspector", "demo", "demo", "User"),
    ]

    added = 0
    for name, email, pwd, role in users_to_seed:
        user, _ = models.create_user(conn, full_name=name, email=email, password=pwd, role=role)
        if user:
            added += 1
    return added


def run_seed(include_demo_incidents: bool = True) -> dict[str, int | str]:
    """
    Initialize schema and load demo data.

    Args:
        include_demo_incidents: When True, adds two sample incident records.

    Returns:
        Summary dict with project_id and counts.
    """
    db.init_database()

    with db.get_db() as conn:
        project_id = seed_projects_and_tasks(conn)
        incidents_added = 0
        if include_demo_incidents:
            incidents_added = seed_demo_incidents(conn, project_id)

        workers_added = seed_workers(conn, project_id)
        agent_logs = seed_agent_logs(conn, project_id)
        users_added = seed_users(conn)

        task_count = db.table_row_count(conn, "tasks")
        incident_count = db.table_row_count(conn, "incidents")
        worker_count = db.table_row_count(conn, "workers")
        user_count = db.table_row_count(conn, "users")

    return {
        "project_id": project_id,
        "tasks": task_count,
        "incidents": incident_count,
        "incidents_seeded": incidents_added,
        "workers": worker_count,
        "workers_seeded": workers_added,
        "users": user_count,
        "users_seeded": users_added,
        "site_risk_logs_seeded": agent_logs["site_risk_logs"],
        "safety_logs_seeded": agent_logs["safety_logs"],
        "database": str(db.DATABASE_PATH),
    }

