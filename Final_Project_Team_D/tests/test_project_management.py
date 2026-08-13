import unittest
import sqlite3
from database import db, models


class TestProjectManagementFunctionality(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

        schema_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            name              TEXT    NOT NULL,
            client_name       TEXT,
            location          TEXT,
            project_type      TEXT    DEFAULT 'Commercial',
            status            TEXT    NOT NULL DEFAULT 'In Progress',
            budget            REAL    DEFAULT 0,
            actual_spending   REAL    DEFAULT 0,
            start_date        TEXT,
            end_date          TEXT,
            actual_start_date TEXT,
            actual_end_date   TEXT,
            project_manager   TEXT,
            description       TEXT,
            progress          REAL    NOT NULL DEFAULT 0,
            created_at        TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at        TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER,
            task_name   TEXT    NOT NULL,
            description TEXT,
            status      TEXT    NOT NULL DEFAULT 'In Progress',
            assignee    TEXT,
            priority    TEXT    NOT NULL DEFAULT 'Medium',
            start_date  TEXT,
            due_date    TEXT,
            progress    REAL    NOT NULL DEFAULT 0,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS milestones (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id     INTEGER NOT NULL,
            milestone_name TEXT    NOT NULL,
            target_date    TEXT,
            actual_date    TEXT,
            status         TEXT    NOT NULL DEFAULT 'Upcoming',
            created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS project_issues (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id         INTEGER NOT NULL,
            title              TEXT    NOT NULL,
            description        TEXT,
            severity           TEXT    NOT NULL DEFAULT 'Medium',
            responsible_person TEXT,
            status             TEXT    NOT NULL DEFAULT 'Open',
            created_at         TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """
        self.conn.executescript(schema_sql)

    def tearDown(self):
        self.conn.close()

    def test_1_create_project(self):
        p_id = models.create_project(
            self.conn,
            name="ABC Commercial Building",
            budget=50_000_000,
            status="In Progress",
        )
        self.assertIsNotNone(p_id)
        projects = models.list_projects(self.conn)
        self.assertTrue(any(p["name"] == "ABC Commercial Building" for p in projects))

    def test_2_open_project_info(self):
        p_id = models.create_project(
            self.conn,
            name="ABC Commercial Building",
            client_name="ABC Corp",
            location="Bengaluru",
            budget=50_000_000,
        )
        project = models.get_project_by_id(self.conn, p_id)
        self.assertEqual(project["name"], "ABC Commercial Building")
        self.assertEqual(project["client_name"], "ABC Corp")
        self.assertEqual(project["budget"], 50_000_000)

    def test_3_task_scoping_per_project(self):
        p1 = models.create_project(self.conn, name="ABC Commercial Building")
        p2 = models.create_project(self.conn, name="XYZ Residential Building")

        t1_id = models.create_task(
            self.conn,
            task_name="Foundation Work",
            status="In Progress",
            progress=50.0,
            project_id=p1,
        )
        t2_id = models.create_task(
            self.conn,
            task_name="Excavation",
            status="In Progress",
            progress=20.0,
            project_id=p2,
        )

        p1_tasks = models.list_tasks(self.conn, p1)
        p2_tasks = models.list_tasks(self.conn, p2)

        self.assertEqual(len(p1_tasks), 1)
        self.assertEqual(p1_tasks[0]["task_name"], "Foundation Work")

        self.assertEqual(len(p2_tasks), 1)
        self.assertEqual(p2_tasks[0]["task_name"], "Excavation")

        # Verify Excavation DOES NOT appear under ABC Commercial Building
        self.assertFalse(any(t["task_name"] == "Excavation" for t in p1_tasks))

    def test_4_budget_calculation(self):
        p_id = models.create_project(
            self.conn,
            name="Budget Test Project",
            budget=50_000_000,
            actual_spending=30_000_000,
        )
        project = models.get_project_by_id(self.conn, p_id)
        est = project["budget"]
        act = project["actual_spending"]
        remaining = est - act
        util = (act / est) * 100

        self.assertEqual(remaining, 20_000_000)
        self.assertEqual(util, 60.0)

    def test_5_progress_and_auto_completion(self):
        p_id = models.create_project(self.conn, name="Progress Test", progress=65.0)
        models.update_project(self.conn, p_id, progress=100.0, status="Completed")
        project = models.get_project_by_id(self.conn, p_id)
        self.assertEqual(project["progress"], 100.0)
        self.assertEqual(project["status"], "Completed")

    def test_6_milestones_and_issues_crud(self):
        p_id = models.create_project(self.conn, name="Milestone Risk Test")
        m_id = models.create_milestone(
            self.conn,
            project_id=p_id,
            milestone_name="Roof Structural Pouring",
            target_date="2025-09-30",
            status="Upcoming",
        )
        r_id = models.create_project_issue(
            self.conn,
            project_id=p_id,
            title="Cement Shortage Delay",
            severity="High",
            status="Open",
        )

        milestones = models.list_milestones(self.conn, p_id)
        issues = models.list_project_issues(self.conn, p_id)

        self.assertEqual(len(milestones), 1)
        self.assertEqual(milestones[0]["milestone_name"], "Roof Structural Pouring")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["title"], "Cement Shortage Delay")


if __name__ == "__main__":
    unittest.main()
