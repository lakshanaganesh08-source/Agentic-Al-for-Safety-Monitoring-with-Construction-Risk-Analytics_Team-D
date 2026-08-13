import unittest
import sqlite3
from database import db, models
from utils import report_builder


class TestReportGenerationEngine(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

        schema_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, client_name TEXT, location TEXT, project_type TEXT,
            status TEXT DEFAULT 'In Progress', budget REAL DEFAULT 0, actual_spending REAL DEFAULT 0,
            start_date TEXT, end_date TEXT, actual_start_date TEXT, actual_end_date TEXT,
            progress REAL DEFAULT 0, project_manager TEXT, description TEXT
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, task_name TEXT NOT NULL,
            description TEXT, status TEXT DEFAULT 'In Progress', assignee TEXT, priority TEXT DEFAULT 'Medium',
            start_date TEXT, due_date TEXT, progress REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, milestone_name TEXT NOT NULL,
            target_date TEXT, actual_date TEXT, status TEXT DEFAULT 'Upcoming'
        );
        CREATE TABLE IF NOT EXISTS project_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, title TEXT NOT NULL,
            severity TEXT DEFAULT 'Medium', responsible_person TEXT, status TEXT DEFAULT 'Open'
        );
        """
        self.conn.executescript(schema_sql)

        self.project_id = models.create_project(
            self.conn,
            name="Downtown Tower Phase 1",
            client_name="Apex Realty",
            location="Mumbai, MH",
            budget=50_000_000,
            actual_spending=32_000_000,
            progress=68.0,
        )
        models.create_task(self.conn, task_name="Foundation Concrete", status="Completed", project_id=self.project_id)
        models.create_task(self.conn, task_name="Steel Framing", status="In Progress", project_id=self.project_id)

    def tearDown(self):
        self.conn.close()

    def test_gather_report_data(self):
        data = report_builder._gather_report_data("Monthly Cost Analysis")
        self.assertIsNotNone(data)
        self.assertEqual(data["report_type"], "Monthly Cost Analysis")
        self.assertIn("project_name", data)
        self.assertIn("cost_rows", data)
        self.assertIn("health", data)

    def test_pdf_generation_bytes(self):
        pdf_bytes = report_builder.make_pdf("Executive Report")
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(len(pdf_bytes) > 500)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_csv_json_excel_generation(self):
        csv_bytes = report_builder.make_csv("Monthly Cost Analysis")
        self.assertTrue(b"CONSTRUCTION INTELLIGENCE HUB" in csv_bytes)

        json_bytes = report_builder.make_json("Monthly Cost Analysis")
        self.assertTrue(b"report_type" in json_bytes)

        excel_bytes = report_builder.make_excel("Monthly Cost Analysis")
        self.assertTrue(len(excel_bytes) > 500)


if __name__ == "__main__":
    unittest.main()
