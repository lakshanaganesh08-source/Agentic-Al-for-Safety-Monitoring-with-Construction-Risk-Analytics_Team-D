"""
Repository layer — CRUD operations for SQLite tables.

Each function accepts an optional connection so callers can batch operations
inside a single transaction via ``get_db()``.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Optional


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def create_project(
    conn: sqlite3.Connection,
    name: str,
    client_name: str | None = None,
    location: str | None = None,
    project_type: str = "Commercial",
    status: str = "In Progress",
    budget: float = 0.0,
    actual_spending: float = 0.0,
    start_date: str | None = None,
    end_date: str | None = None,
    actual_start_date: str | None = None,
    actual_end_date: str | None = None,
    project_manager: str | None = None,
    description: str | None = None,
    progress: float = 0.0,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO projects (
            name, client_name, location, project_type, status, budget,
            actual_spending, start_date, end_date, actual_start_date,
            actual_end_date, project_manager, description, progress
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name, client_name, location, project_type, status, budget,
            actual_spending, start_date, end_date, actual_start_date,
            actual_end_date, project_manager, description, progress
        ),
    )
    return int(cursor.lastrowid)


def update_project(
    conn: sqlite3.Connection,
    project_id: int,
    **kwargs: Any,
) -> bool:
    if not kwargs:
        return False
    allowed = {
        "name", "client_name", "location", "project_type", "status",
        "budget", "actual_spending", "start_date", "end_date",
        "actual_start_date", "actual_end_date", "project_manager",
        "description", "progress"
    }
    updates = []
    params = []
    for k, v in kwargs.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    updates.append("updated_at = datetime('now')")
    params.append(project_id)
    sql = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
    cursor = conn.execute(sql, tuple(params))
    return cursor.rowcount > 0


def delete_project(conn: sqlite3.Connection, project_id: int) -> bool:
    cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    return cursor.rowcount > 0


def get_project_by_id(conn: sqlite3.Connection, project_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return _row_to_dict(row)


def get_default_project(conn: sqlite3.Connection) -> dict[str, Any] | None:
    """Return the first active project, or any project if none are active."""
    row = conn.execute(
        "SELECT * FROM projects WHERE status IN ('In Progress', 'Active', 'Planning') ORDER BY id LIMIT 1"
    ).fetchone()
    if row is None:
        row = conn.execute("SELECT * FROM projects ORDER BY id LIMIT 1").fetchone()
    return _row_to_dict(row)


def list_projects(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def create_task(
    conn: sqlite3.Connection,
    task_name: str,
    status: str = "In Progress",
    assignee: str | None = None,
    priority: str = "Medium",
    project_id: int | None = None,
    description: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    progress: float = 0.0,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO tasks (
            project_id, task_name, description, status, assignee,
            priority, start_date, due_date, progress
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (project_id, task_name, description, status, assignee, priority, start_date, due_date, progress),
    )
    return int(cursor.lastrowid)


def update_task(
    conn: sqlite3.Connection,
    task_id: int,
    **kwargs: Any,
) -> bool:
    if not kwargs:
        return False
    allowed = {
        "task_name", "description", "status", "assignee",
        "priority", "start_date", "due_date", "progress", "project_id"
    }
    updates = []
    params = []
    for k, v in kwargs.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    updates.append("updated_at = datetime('now')")
    params.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    cursor = conn.execute(sql, tuple(params))
    return cursor.rowcount > 0


def delete_task(conn: sqlite3.Connection, task_id: int) -> bool:
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount > 0


def list_tasks(
    conn: sqlite3.Connection,
    project_id: int | None = None,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY id DESC",
            (project_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    return _rows_to_dicts(rows)


def tasks_as_dataframe_records(conn: sqlite3.Connection, project_id: int | None = None) -> list[dict[str, Any]]:
    """Return tasks formatted for the Project Management UI DataFrame."""
    tasks = list_tasks(conn, project_id=project_id)
    return [
        {
            "Task": t["task_name"],
            "Status": t["status"],
            "Assignee": t["assignee"] or "",
            "Priority": t["priority"],
        }
        for t in tasks
    ]


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------

def create_milestone(
    conn: sqlite3.Connection,
    project_id: int,
    milestone_name: str,
    target_date: str | None = None,
    actual_date: str | None = None,
    status: str = "Upcoming",
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO milestones (project_id, milestone_name, target_date, actual_date, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, milestone_name, target_date, actual_date, status),
    )
    return int(cursor.lastrowid)


def update_milestone(conn: sqlite3.Connection, milestone_id: int, **kwargs: Any) -> bool:
    if not kwargs:
        return False
    allowed = {"milestone_name", "target_date", "actual_date", "status"}
    updates = []
    params = []
    for k, v in kwargs.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    params.append(milestone_id)
    sql = f"UPDATE milestones SET {', '.join(updates)} WHERE id = ?"
    cursor = conn.execute(sql, tuple(params))
    return cursor.rowcount > 0


def delete_milestone(conn: sqlite3.Connection, milestone_id: int) -> bool:
    cursor = conn.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))
    return cursor.rowcount > 0


def list_milestones(conn: sqlite3.Connection, project_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM milestones WHERE project_id = ? ORDER BY id ASC",
        (project_id,),
    ).fetchall()
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Project Issues / Risks
# ---------------------------------------------------------------------------

def create_project_issue(
    conn: sqlite3.Connection,
    project_id: int,
    title: str,
    description: str | None = None,
    severity: str = "Medium",
    responsible_person: str | None = None,
    status: str = "Open",
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO project_issues (project_id, title, description, severity, responsible_person, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_id, title, description, severity, responsible_person, status),
    )
    return int(cursor.lastrowid)


def update_project_issue(conn: sqlite3.Connection, issue_id: int, **kwargs: Any) -> bool:
    if not kwargs:
        return False
    allowed = {"title", "description", "severity", "responsible_person", "status"}
    updates = []
    params = []
    for k, v in kwargs.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    params.append(issue_id)
    sql = f"UPDATE project_issues SET {', '.join(updates)} WHERE id = ?"
    cursor = conn.execute(sql, tuple(params))
    return cursor.rowcount > 0


def delete_project_issue(conn: sqlite3.Connection, issue_id: int) -> bool:
    cursor = conn.execute("DELETE FROM project_issues WHERE id = ?", (issue_id,))
    return cursor.rowcount > 0


def list_project_issues(conn: sqlite3.Connection, project_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM project_issues WHERE project_id = ? ORDER BY id DESC",
        (project_id,),
    ).fetchall()
    return _rows_to_dicts(rows)


def update_task_status(conn: sqlite3.Connection, task_id: int, status: str) -> None:
    conn.execute(
        """
        UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (status, task_id),
    )


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

INCIDENT_SEVERITY_MAP: dict[str, str] = {
    "Near Miss": "Moderate",
    "Property Damage": "High",
    "Hazard Identification": "Low",
    "Minor Injury": "High",
}


def create_incident(
    conn: sqlite3.Connection,
    incident_type: str,
    description: str,
    project_id: int | None = None,
    zone: str | None = None,
    reported_by: str | None = None,
    severity: str | None = None,
) -> int:
    if severity is None:
        severity = INCIDENT_SEVERITY_MAP.get(incident_type, "Moderate")

    cursor = conn.execute(
        """
        INSERT INTO incidents
            (project_id, incident_type, severity, description, zone, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_id, incident_type, severity, description.strip(), zone, reported_by),
    )
    return int(cursor.lastrowid)


def list_incidents(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT * FROM incidents
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT * FROM incidents
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_incident_by_id(conn: sqlite3.Connection, incident_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return _row_to_dict(row)


def count_incidents(conn: sqlite3.Connection, project_id: Optional[int] = None) -> int:
    if project_id is not None:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM incidents WHERE project_id = ?",
            (project_id,),
        ).fetchone()
    else:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM incidents").fetchone()
    return int(row["cnt"]) if row else 0


# ---------------------------------------------------------------------------
# Material records
# ---------------------------------------------------------------------------

def create_material_record(
    conn: sqlite3.Connection,
    material: str,
    quantity: float,
    unit: str,
    unit_cost: float,
    project_id: int | None = None,
    waste_pct: float = 0,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO material_records (project_id, material, quantity, unit, unit_cost, waste_pct)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_id, material, quantity, unit, unit_cost, waste_pct),
    )
    return int(cursor.lastrowid)


def bulk_create_material_records(
    conn: sqlite3.Connection,
    records: list[dict[str, Any]],
    project_id: int | None = None,
) -> int:
    """Insert multiple material records; returns count inserted."""
    for rec in records:
        create_material_record(
            conn,
            material=rec["material"],
            quantity=rec["quantity"],
            unit=rec["unit"],
            unit_cost=rec["unit_cost"],
            project_id=project_id,
            waste_pct=rec.get("waste_pct", 0),
        )
    return len(records)


def list_material_records(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT * FROM material_records
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM material_records ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_material_cost_summary(
    conn: sqlite3.Connection,
    project_id: int | None = None,
) -> dict[str, Any]:
    """Aggregate material cost including waste allowance."""
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT quantity, unit_cost, waste_pct FROM material_records
            WHERE project_id = ?
            """,
            (project_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT quantity, unit_cost, waste_pct FROM material_records"
        ).fetchall()

    total = 0.0
    for row in rows:
        qty = float(row["quantity"] or 0)
        cost = float(row["unit_cost"] or 0)
        waste = float(row["waste_pct"] or 0)
        total += qty * (1 + waste / 100) * cost

    return {"total_cost": round(total, 2), "item_count": len(rows)}


def clear_material_records(conn: sqlite3.Connection, project_id: int) -> None:
    conn.execute("DELETE FROM material_records WHERE project_id = ?", (project_id,))


# ---------------------------------------------------------------------------
# Risk logs (delay prediction)
# ---------------------------------------------------------------------------

def create_risk_log(
    conn: sqlite3.Connection,
    score: float,
    priority: str,
    factors_json: str,
    project_id: int | None = None,
    risk_type: str = "delay",
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO risk_logs (project_id, risk_type, score, priority, factors_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, risk_type, score, priority, factors_json),
    )
    return int(cursor.lastrowid)


def list_risk_logs(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 20,
    risk_type: str | None = None,
) -> list[dict[str, Any]]:
    query = "SELECT * FROM risk_logs WHERE 1=1"
    params: list[Any] = []

    if project_id is not None:
        query += " AND project_id = ?"
        params.append(project_id)
    if risk_type is not None:
        query += " AND risk_type = ?"
        params.append(risk_type)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    return _rows_to_dicts(rows)


def get_latest_risk_score(
    conn: sqlite3.Connection,
    project_id: int,
    risk_type: str = "site",
) -> float | None:
    row = conn.execute(
        """
        SELECT score FROM risk_logs
        WHERE project_id = ? AND risk_type = ?
        ORDER BY created_at DESC LIMIT 1
        """,
        (project_id, risk_type),
    ).fetchone()
    return float(row["score"]) if row else None


# ---------------------------------------------------------------------------
# Inspections (computer vision)
# ---------------------------------------------------------------------------

def create_inspection(
    conn: sqlite3.Connection,
    result: str,
    checklist_json: str,
    project_id: int | None = None,
    inspector: str = "CV Engine",
    inspection_date: str | None = None,
) -> int:
    if inspection_date is None:
        inspection_date = conn.execute("SELECT date('now')").fetchone()[0]

    cursor = conn.execute(
        """
        INSERT INTO inspections (project_id, inspector, checklist_json, result, inspection_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, inspector, checklist_json, result, inspection_date),
    )
    return int(cursor.lastrowid)


def list_inspections(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT * FROM inspections WHERE project_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM inspections ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def create_report(
    conn: sqlite3.Connection,
    report_type: str,
    period: str | None = None,
    file_path: str | None = None,
    project_id: int | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO reports (project_id, report_type, period, file_path)
        VALUES (?, ?, ?, ?)
        """,
        (project_id, report_type, period, file_path),
    )
    return int(cursor.lastrowid)


def list_reports(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT * FROM reports WHERE project_id = ?
            ORDER BY generated_at DESC LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM reports ORDER BY generated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

def create_worker(
    conn: sqlite3.Connection,
    name: str,
    role: str | None = None,
    site_zone: str | None = None,
    ppe_status: str = "Unknown",
    project_id: int | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO workers (project_id, name, role, site_zone, ppe_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, name, role, site_zone, ppe_status),
    )
    return int(cursor.lastrowid)


def list_workers(
    conn: sqlite3.Connection,
    project_id: int | None = None,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            "SELECT * FROM workers WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM workers ORDER BY id").fetchall()
    return _rows_to_dicts(rows)


def update_worker_ppe_status(
    conn: sqlite3.Connection,
    worker_id: int,
    ppe_status: str,
) -> None:
    conn.execute(
        "UPDATE workers SET ppe_status = ? WHERE id = ?",
        (ppe_status, worker_id),
    )


# ---------------------------------------------------------------------------
# Safety logs
# ---------------------------------------------------------------------------

def create_safety_log(
    conn: sqlite3.Connection,
    safety_score: float,
    project_id: int | None = None,
    worker_id: int | None = None,
    ppe_helmet: int = 0,
    ppe_vest: int = 0,
    unsafe_behavior: str | None = None,
    zone: str | None = None,
    notes: str | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO safety_logs
            (worker_id, project_id, ppe_helmet, ppe_vest, safety_score,
             unsafe_behavior, zone, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            worker_id, project_id, ppe_helmet, ppe_vest, safety_score,
            unsafe_behavior, zone, notes,
        ),
    )
    return int(cursor.lastrowid)


def list_safety_logs(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT * FROM safety_logs WHERE project_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM safety_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_latest_safety_score(
    conn: sqlite3.Connection,
    project_id: int,
) -> float | None:
    row = conn.execute(
        """
        SELECT safety_score FROM safety_logs
        WHERE project_id = ? AND safety_score IS NOT NULL
        ORDER BY created_at DESC LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    return float(row["safety_score"]) if row else None


def get_accident_zone_counts(
    conn: sqlite3.Connection,
    project_id: int | None = None,
) -> list[dict[str, Any]]:
    """Incident counts grouped by zone for accident-prone zone analysis."""
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT COALESCE(zone, 'Unspecified') AS zone, COUNT(*) AS incident_count
            FROM incidents
            WHERE project_id = ?
            GROUP BY zone
            ORDER BY incident_count DESC
            """,
            (project_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT COALESCE(zone, 'Unspecified') AS zone, COUNT(*) AS incident_count
            FROM incidents
            GROUP BY zone
            ORDER BY incident_count DESC
            """
        ).fetchall()
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Compliance logs
# ---------------------------------------------------------------------------

def create_compliance_log(
    conn: sqlite3.Connection,
    standard: str,
    status: str,
    project_id: int | None = None,
    violation: str | None = None,
    percentage: float | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO compliance_logs (project_id, standard, status, violation, percentage)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, standard, status, violation, percentage),
    )
    return int(cursor.lastrowid)


def list_compliance_logs(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT * FROM compliance_logs WHERE project_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM compliance_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_compliance_percentage(
    conn: sqlite3.Connection,
    project_id: int,
) -> float:
    """Calculate overall compliance percentage from logs."""
    row = conn.execute(
        """
        SELECT AVG(percentage) as avg_pct FROM compliance_logs
        WHERE project_id = ? AND percentage IS NOT NULL
        """,
        (project_id,),
    ).fetchone()
    return float(row["avg_pct"]) if row and row["avg_pct"] else 0.0


def get_latest_compliance_score(
    conn: sqlite3.Connection,
    project_id: int,
) -> float | None:
    row = conn.execute(
        """
        SELECT percentage FROM compliance_logs
        WHERE project_id = ? AND percentage IS NOT NULL
        ORDER BY created_at DESC LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    return float(row["percentage"]) if row else None


# ---------------------------------------------------------------------------
# Insurance logs
# ---------------------------------------------------------------------------

def create_insurance_log(
    conn: sqlite3.Connection,
    exposure: float,
    severity: str,
    project_id: int | None = None,
    incident_id: int | None = None,
    claim_risk_score: float | None = None,
    notes: str | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO insurance_logs (incident_id, project_id, exposure, severity, claim_risk_score, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (incident_id, project_id, exposure, severity, claim_risk_score, notes),
    )
    return int(cursor.lastrowid)


def list_insurance_logs(
    conn: sqlite3.Connection,
    project_id: int | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    if project_id is not None:
        rows = conn.execute(
            """
            SELECT * FROM insurance_logs WHERE project_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM insurance_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_insurance_risk_score(
    conn: sqlite3.Connection,
    project_id: int,
) -> float | None:
    """Get latest insurance risk score for a project."""
    row = conn.execute(
        """
        SELECT claim_risk_score FROM insurance_logs
        WHERE project_id = ? AND claim_risk_score IS NOT NULL
        ORDER BY created_at DESC LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    return float(row["claim_risk_score"]) if row else None


def calculate_total_exposure(
    conn: sqlite3.Connection,
    project_id: int | None = None,
) -> float:
    """Calculate total insurance exposure from logs."""
    if project_id is not None:
        row = conn.execute(
            """
            SELECT SUM(exposure) as total FROM insurance_logs
            WHERE project_id = ? AND exposure IS NOT NULL
            """,
            (project_id,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT SUM(exposure) as total FROM insurance_logs WHERE exposure IS NOT NULL"
        ).fetchone()
    return float(row["total"]) if row and row["total"] else 0.0


# ---------------------------------------------------------------------------
# Users & Authentication Repository
# ---------------------------------------------------------------------------

import hashlib
import os


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Securely hash password using PBKDF2-HMAC-SHA256 with salt."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return hashed, salt


def create_user(
    conn: sqlite3.Connection,
    full_name: str,
    email: str,
    password: str,
    role: str = "User",
) -> tuple[dict[str, Any] | None, str | None]:
    """Create a new user account with hashed password."""
    email_clean = email.strip().lower()
    full_name_clean = full_name.strip()

    existing = get_user_by_email(conn, email_clean)
    if existing:
        return None, "An account with this email already exists."

    password_hash, salt = hash_password(password)

    try:
        cursor = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, salt, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name_clean, email_clean, password_hash, salt, role),
        )
        user_id = cursor.lastrowid
        user = get_user_by_id(conn, int(user_id))
        return user, None
    except sqlite3.IntegrityError:
        return None, "An account with this email already exists."


def get_user_by_email(conn: sqlite3.Connection, email: str) -> dict[str, Any] | None:
    """Retrieve user record by email address."""
    row = conn.execute(
        "SELECT * FROM users WHERE LOWER(email) = LOWER(?)",
        (email.strip(),),
    ).fetchone()
    return _row_to_dict(row)


def get_user_by_id(conn: sqlite3.Connection, user_id: int) -> dict[str, Any] | None:
    """Retrieve user record by user ID."""
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def authenticate_user(
    conn: sqlite3.Connection,
    email: str,
    password: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Authenticate user credentials against stored PBKDF2 hashes."""
    email_clean = email.strip().lower()
    user = get_user_by_email(conn, email_clean)

    if not user:
        return None, "Email or password is incorrect."

    computed_hash, _ = hash_password(password, user["salt"])
    if computed_hash == user["password_hash"]:
        return user, None

    return None, "Email or password is incorrect."

