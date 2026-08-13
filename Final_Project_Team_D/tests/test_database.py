"""
Unit tests for the SQLite database layer (Phase 1).

Run:
    python -m pytest tests/ -v
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Patch DATABASE_PATH before importing db/models so tests use an isolated file.
_TEST_DIR = tempfile.mkdtemp()
_TEST_DB = Path(_TEST_DIR) / "test_construction_hub.db"


class DatabasePhase1Tests(unittest.TestCase):
    """Verify schema, seeding, and CRUD for Phase 1 entities."""

    def setUp(self) -> None:
        if _TEST_DB.exists():
            _TEST_DB.unlink()

        self._patches = [
            patch("database.db.DATABASE_PATH", _TEST_DB),
            patch("database.db.DATABASE_DIR", Path(_TEST_DIR)),
        ]
        for p in self._patches:
            p.start()

        from database.db import init_database
        from database.seed import run_seed

        init_database()
        self.seed_summary = run_seed(include_demo_incidents=True)

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()
        if _TEST_DB.exists():
            _TEST_DB.unlink()

    def test_database_file_created(self) -> None:
        self.assertTrue(_TEST_DB.exists())

    def test_seed_creates_project_and_tasks(self) -> None:
        self.assertGreaterEqual(self.seed_summary["tasks"], 5)
        self.assertIn("project_id", self.seed_summary)

    def test_seed_creates_demo_incidents(self) -> None:
        self.assertGreaterEqual(self.seed_summary["incidents"], 2)

    def test_seed_is_idempotent(self) -> None:
        from database.seed import run_seed

        second = run_seed(include_demo_incidents=True)
        self.assertEqual(second["tasks"], self.seed_summary["tasks"])
        self.assertEqual(second["incidents"], self.seed_summary["incidents"])

    def test_create_incident(self) -> None:
        from database.db import get_db
        from database import models

        with get_db() as conn:
            project = models.get_default_project(conn)
            self.assertIsNotNone(project)
            incident_id = models.create_incident(
                conn,
                incident_type="Near Miss",
                description="Test incident for unit test.",
                project_id=int(project["id"]),
                reported_by="tester",
            )
            incident = models.get_incident_by_id(conn, incident_id)

        self.assertIsNotNone(incident)
        assert incident is not None
        self.assertEqual(incident["incident_type"], "Near Miss")
        self.assertEqual(incident["severity"], "Moderate")

    def test_tasks_dataframe_records_match_ui_columns(self) -> None:
        from database.db import get_db
        from database import models

        with get_db() as conn:
            records = models.tasks_as_dataframe_records(conn)

        self.assertGreater(len(records), 0)
        for row in records:
            self.assertEqual(set(row.keys()), {"Task", "Status", "Assignee", "Priority"})

    def test_foreign_keys_enabled(self) -> None:
        from database.db import get_connection

        conn = get_connection()
        try:
            row = conn.execute("PRAGMA foreign_keys").fetchone()
            self.assertEqual(row[0], 1)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
