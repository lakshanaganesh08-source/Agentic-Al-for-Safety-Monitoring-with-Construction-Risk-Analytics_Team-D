"""
Phase 2 unit tests — material estimation, ML models, reports, CV, dashboard.

Run:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

_TEST_DIR = tempfile.mkdtemp()
_TEST_DB = Path(_TEST_DIR) / "test_phase2.db"


class Phase2MaterialTests(unittest.TestCase):
    def test_estimate_materials_returns_boq(self) -> None:
        from utils.material_calculator import estimate_materials

        result = estimate_materials(2500, 2, "Residential", 90)
        self.assertGreater(result.material_cost, 0)
        self.assertGreater(result.labour_cost, 0)
        self.assertGreater(result.equipment_cost, 0)
        self.assertGreater(result.total_cost, 0)
        boq = result.boq_rows()
        self.assertGreater(len(boq), 10)
        categories = {row["Category"] for row in boq}
        self.assertIn("Material", categories)
        self.assertIn("Labour", categories)
        self.assertIn("Equipment", categories)

    def test_commercial_costs_more_than_residential(self) -> None:
        from utils.material_calculator import estimate_materials

        res = estimate_materials(5000, 3, "Residential", 120)
        com = estimate_materials(5000, 3, "Commercial", 120)
        self.assertGreater(com.total_cost, res.total_cost)

    def test_invalid_inputs_raise(self) -> None:
        from utils.material_calculator import estimate_materials

        with self.assertRaises(ValueError):
            estimate_materials(0, 2, "Residential", 90)


class Phase2MLTests(unittest.TestCase):
    def test_cost_prediction_non_negative(self) -> None:
        from utils.ml_models import train_cost_model, predict_cost, cost_breakdown

        model = train_cost_model()
        cost = predict_cost(model, 3000, 3, 25, 100, "Commercial")
        self.assertGreater(cost, 0)
        breakdown = cost_breakdown(cost)
        self.assertAlmostEqual(sum(breakdown.values()), cost, places=0)

    def test_delay_risk_returns_valid_score(self) -> None:
        from utils.ml_models import train_delay_model, predict_delay_risk

        model = train_delay_model()
        result = predict_delay_risk(model, "High", "Low", 55, 3)
        self.assertIn(result["risk_level"], ("LOW", "MODERATE", "HIGH"))
        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["risk_score"], 100)


class Phase2CVTests(unittest.TestCase):
    def test_analyze_site_image_on_synthetic_photo(self) -> None:
        from utils.cv_analyzer import analyze_site_image

        arr = np.zeros((200, 300, 3), dtype=np.uint8)
        arr[20:60, 50:150] = [255, 255, 0]   # yellow vest area
        arr[10:40, 100:200] = [255, 255, 255]  # white hardhat area
        image = Image.fromarray(arr)
        try:
            result = analyze_site_image(image)
            self.assertGreaterEqual(result.overall_score, 0)
            self.assertLessEqual(result.overall_score, 100)
            self.assertGreater(len(result.findings), 0)
        except ImportError:
            self.skipTest("Ultralytics package not installed.")


class Phase2DatabaseTests(unittest.TestCase):
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

    def test_material_records_crud(self) -> None:
        from database.db import get_db
        from database import models

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            models.create_material_record(
                conn, "Cement", 100, "bags", 12.0, project_id, waste_pct=5
            )
            summary = models.get_material_cost_summary(conn, project_id)
            records = models.list_material_records(conn, project_id)

        self.assertEqual(len(records), 1)
        self.assertGreater(summary["total_cost"], 0)

    def test_risk_log_and_inspection(self) -> None:
        from database.db import get_db
        from database import models

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            risk_id = models.create_risk_log(
                conn, 65.0, "MODERATE", json.dumps({"weather": "High"}), project_id
            )
            insp_id = models.create_inspection(
                conn, "COMPLIANT", "{}", project_id, inspector="test"
            )
            risks = models.list_risk_logs(conn, project_id, risk_type="delay")
            inspections = models.list_inspections(conn, project_id)

        self.assertGreater(risk_id, 0)
        self.assertGreater(insp_id, 0)
        self.assertEqual(len(risks), 1)
        self.assertEqual(len(inspections), 1)

    def test_report_creation(self) -> None:
        from database.db import get_db
        from database import models

        project_id = int(self.seed["project_id"])
        with get_db() as conn:
            report_id = models.create_report(
                conn, "Monthly Cost Analysis", "2026-08", "test.pdf", project_id
            )
            reports = models.list_reports(conn, project_id)

        self.assertGreater(report_id, 0)
        self.assertEqual(len(reports), 1)


class Phase2ReportTests(unittest.TestCase):
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
        run_seed(include_demo_incidents=True)

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()

    def test_pdf_and_excel_generation(self) -> None:
        from utils.report_builder import make_pdf, make_excel, make_csv

        pdf = make_pdf("Monthly Cost Analysis")
        self.assertTrue(pdf.startswith(b"%PDF"))
        excel = make_excel("Safety & Compliance Audit")
        self.assertGreater(len(excel), 100)
        csv = make_csv("Full Site Progress Summary")
        self.assertIn(b"CONSTRUCTION INTELLIGENCE HUB", csv)


class Phase2DashboardTests(unittest.TestCase):
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
        run_seed(include_demo_incidents=True)

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()

    def test_executive_metrics(self) -> None:
        from utils.dashboard_data import get_executive_metrics, get_budget_progress_chart

        metrics = get_executive_metrics()
        self.assertIn("budget_display", metrics)
        self.assertIn("safety_score", metrics)
        df = get_budget_progress_chart()
        self.assertEqual(len(df), 12)


if __name__ == "__main__":
    unittest.main()
