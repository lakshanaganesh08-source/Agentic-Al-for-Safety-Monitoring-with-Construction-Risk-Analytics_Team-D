"""
SQLite connection management and schema initialization.

Uses Python's built-in sqlite3 module — no external ORM required.
Connections are opened per-request and closed via context managers.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator

from config.settings import DATABASE_DIR, DATABASE_PATH, SCHEMA_PATH


def _ensure_database_dir() -> None:
    """Create the database directory if it does not exist."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """
    Open a new SQLite connection with row-factory enabled.

    Returns:
        sqlite3.Connection configured for dict-like row access.
    """
    _ensure_database_dir()
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields a connection and commits on success.

    Yields:
        Active SQLite connection. Commits on clean exit, rolls back on error.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(force_schema: bool = True) -> Path:
    """
    Apply schema.sql to create or migrate tables.

    Safe to call on every app startup — uses CREATE TABLE IF NOT EXISTS.

    Args:
        force_schema: When True, executes schema SQL even if DB file exists.

    Returns:
        Path to the SQLite database file.
    """
    _ensure_database_dir()

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_db() as conn:
        conn.executescript(schema_sql)
        _apply_migrations(conn)

    return DATABASE_PATH


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Add columns introduced after initial deployments."""
    if _table_exists(conn, "projects"):
        for col, col_type in [
            ("client_name", "TEXT"),
            ("location", "TEXT"),
            ("project_type", "TEXT DEFAULT 'Commercial'"),
            ("actual_spending", "REAL DEFAULT 0"),
            ("actual_start_date", "TEXT"),
            ("actual_end_date", "TEXT"),
            ("project_manager", "TEXT"),
            ("description", "TEXT"),
        ]:
            if not _column_exists(conn, "projects", col):
                conn.execute(f"ALTER TABLE projects ADD COLUMN {col} {col_type}")

    if _table_exists(conn, "tasks"):
        for col, col_type in [
            ("description", "TEXT"),
            ("start_date", "TEXT"),
            ("due_date", "TEXT"),
            ("progress", "REAL DEFAULT 0"),
        ]:
            if not _column_exists(conn, "tasks", col):
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {col} {col_type}")

    if _table_exists(conn, "risk_logs") and not _column_exists(conn, "risk_logs", "risk_type"):
        conn.execute(
            "ALTER TABLE risk_logs ADD COLUMN risk_type TEXT NOT NULL DEFAULT 'delay'"
        )
    if _table_exists(conn, "safety_logs"):
        if not _column_exists(conn, "safety_logs", "unsafe_behavior"):
            conn.execute("ALTER TABLE safety_logs ADD COLUMN unsafe_behavior TEXT")
        if not _column_exists(conn, "safety_logs", "zone"):
            conn.execute("ALTER TABLE safety_logs ADD COLUMN zone TEXT")


def database_exists() -> bool:
    """Return True if the SQLite database file has been created."""
    return DATABASE_PATH.exists()


def table_row_count(conn: sqlite3.Connection, table: str) -> int:
    """Return the number of rows in a table."""
    cursor = conn.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
    row = cursor.fetchone()
    return int(row["cnt"]) if row else 0
