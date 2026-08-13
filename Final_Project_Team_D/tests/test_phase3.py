"""
Phase 3 unit tests — Site Risk Agent & Safety Agent.

Run:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

_TEST_DIR = tempfile.mkdtemp()
_TEST_DB = Path(_TEST_DIR) / "test_phase3.db"


class Phase3DatabaseMixin:
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
        self.seed = run_seed(include_demo_incidents=True)

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()
        if _TEST_DB.exists():
            _TEST_DB.unlink()


class Phase3SiteRiskTests(Phase3DatabaseMixin, unittest.TestCase):
    def test_assess_site_risk_returns_valid_score(self) -> None:
        from database.db import get_db
        from utils.site_risk_agent import assess_site_risk, prioritize_risks

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            result = assess_site_risk(
                conn,
                project_id=project_id,
                weather="Rain",
                air_quality="Poor / Dusty",
                ground_condition="Unstable Soil",
                active_activities=["Crane Operations", "Excavation / Trenching"],
                equipment_status={"Tower Crane": "Fault Reported", "Excavator": "Overdue Inspection"},
                unsafe_conditions=["Missing guardrails", "Blocked emergency exits"],
            )

        self.assertGreaterEqual(result.score, 5)
        self.assertLessEqual(result.score, 100)
        self.assertIn(result.priority, ("CRITICAL", "HIGH", "MODERATE", "LOW"))
        self.assertGreater(len(result.factors), 0)
        self.assertGreater(len(result.recommendations), 0)
        prioritized = prioritize_risks(result.factors)
        self.assertGreaterEqual(prioritized[0].score, prioritized[-1].score)

    def test_save_site_risk_log(self) -> None:
        from database.db import get_db
        from database import models
        from utils.site_risk_agent import assess_site_risk, save_site_risk_assessment

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            assessment = assess_site_risk(
                conn,
                project_id=project_id,
                weather="Clear",
                air_quality="Good",
                ground_condition="Stable",
                active_activities=["General Labor"],
                equipment_status={"Tower Crane": "All Certified"},
                unsafe_conditions=[],
            )
            log_id = save_site_risk_assessment(conn, project_id, assessment)
            logs = models.list_risk_logs(conn, project_id, risk_type="site")

        self.assertGreater(log_id, 0)
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0]["risk_type"], "site")

    def test_seed_creates_workers_and_agent_logs(self) -> None:
        self.assertGreaterEqual(self.seed.get("workers", 0), 5)
        self.assertGreaterEqual(self.seed.get("site_risk_logs_seeded", 0), 1)
        self.assertGreaterEqual(self.seed.get("safety_logs_seeded", 0), 1)


class Phase3SafetyTests(Phase3DatabaseMixin, unittest.TestCase):
    def test_compute_safety_score(self) -> None:
        from database.db import get_db
        from utils.safety_agent import compute_safety_score

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            assessment = compute_safety_score(conn, project_id)

        self.assertGreaterEqual(assessment.safety_score, 40)
        self.assertLessEqual(assessment.safety_score, 100)
        self.assertGreater(assessment.workers_total, 0)

    def test_detect_unsafe_behaviors(self) -> None:
        from database.db import get_db
        from utils.safety_agent import detect_unsafe_behaviors

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            findings = detect_unsafe_behaviors(conn, project_id)

        self.assertIsInstance(findings, list)

    def test_accident_prone_zones(self) -> None:
        from database.db import get_db
        from utils.safety_agent import get_accident_prone_zones

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            zones = get_accident_prone_zones(conn, project_id)

        self.assertGreater(len(zones), 0)
        self.assertIn("zone", zones[0])
        self.assertIn("risk_level", zones[0])

    def test_ppe_cv_integration(self) -> None:
        from database.db import get_db
        from utils.safety_agent import analyze_ppe_image, compute_safety_score, save_safety_assessment

        arr = np.zeros((200, 300, 3), dtype=np.uint8)
        arr[20:60, 50:150] = [255, 255, 0]
        arr[10:40, 100:200] = [255, 255, 255]
        image = Image.fromarray(arr)
        try:
            cv_result = analyze_ppe_image(image)

            project_id = int(self.seed["project_id"])
            with get_db() as conn:
                assessment = compute_safety_score(conn, project_id, cv_result=cv_result)
                log_id = save_safety_assessment(conn, project_id, assessment, cv_result=cv_result)

            self.assertGreater(log_id, 0)
            self.assertGreaterEqual(cv_result.overall_score, 0)
        except ImportError:
            self.skipTest("Ultralytics package not installed.")

    def test_fallback_recommendations(self) -> None:
        from database.db import get_db
        from utils.safety_agent import compute_safety_score, generate_safety_recommendations

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            assessment = compute_safety_score(conn, project_id)

        with patch("utils.safety_agent.generate_with_ollama", return_value=("fail", False)):
            text, ok = generate_safety_recommendations(assessment, "Test Project")

        self.assertFalse(ok)
        self.assertIn("1.", text)


class Phase3DashboardTests(Phase3DatabaseMixin, unittest.TestCase):
    def test_executive_metrics_include_site_risk(self) -> None:
        from utils.dashboard_data import (
            get_executive_metrics,
            get_site_risk_history,
            get_safety_score_history,
        )

        metrics = get_executive_metrics()
        self.assertIn("site_risk_score", metrics)
        self.assertIn("safety_score", metrics)

        site_df = get_site_risk_history()
        safety_df = get_safety_score_history()
        self.assertFalse(site_df.empty)
        self.assertFalse(safety_df.empty)


class Phase3MigrationTests(unittest.TestCase):
    def test_risk_type_column_migration(self) -> None:
        if _TEST_DB.exists():
            _TEST_DB.unlink()
        patches = [
            patch("database.db.DATABASE_PATH", _TEST_DB),
            patch("database.db.DATABASE_DIR", Path(_TEST_DIR)),
        ]
        for p in patches:
            p.start()
        try:
            import sqlite3
            from database.db import init_database, get_db, _apply_migrations

            _TEST_DB.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(_TEST_DB))
            conn.execute(
                """
                CREATE TABLE risk_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    score REAL NOT NULL,
                    priority TEXT,
                    factors_json TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                "INSERT INTO risk_logs (project_id, score, priority, factors_json) VALUES (1, 50.0, 'MODERATE', '{}')"
            )
            conn.commit()
            conn.close()

            with get_db() as conn:
                _apply_migrations(conn)

            with get_db() as conn:
                row = conn.execute("SELECT risk_type FROM risk_logs LIMIT 1").fetchone()
            self.assertEqual(row["risk_type"], "delay")
        finally:
            for p in patches:
                p.stop()
            if _TEST_DB.exists():
                _TEST_DB.unlink()


if __name__ == "__main__":
    unittest.main()
