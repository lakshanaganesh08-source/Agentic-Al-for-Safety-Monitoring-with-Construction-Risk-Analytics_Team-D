import unittest
import sqlite3
from database import db, models, seed
from modules import login


class TestAuthenticationRedesign(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for test isolation
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

        # Execute schema
        schema_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            budget REAL, start_date TEXT, end_date TEXT, progress REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'User',
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
        self.conn.executescript(schema_sql)

    def tearDown(self):
        self.conn.close()

    def test_new_user_registration_success(self):
        user, err = models.create_user(
            self.conn,
            full_name="Sarah Architect",
            email="sarah.architect@constructionhub.com",
            password="StrongPass123!",
            role="User",
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "sarah.architect@constructionhub.com")
        self.assertEqual(user["full_name"], "Sarah Architect")
        self.assertEqual(user["role"], "User")
        # Ensure password is not stored in plaintext
        self.assertNotEqual(user["password_hash"], "StrongPass123!")

    def test_duplicate_registration_failure(self):
        models.create_user(
            self.conn,
            full_name="First User",
            email="duplicate@constructionhub.com",
            password="StrongPass123!",
        )
        user, err = models.create_user(
            self.conn,
            full_name="Second User",
            email="duplicate@constructionhub.com",
            password="AnotherPass123!",
        )
        self.assertIsNone(user)
        self.assertEqual(err, "An account with this email already exists.")

    def test_user_login_authentication_success(self):
        models.create_user(
            self.conn,
            full_name="John Engineer",
            email="john.engineer@constructionhub.com",
            password="EngineerPass123!",
            role="Manager",
        )
        user, err = models.authenticate_user(
            self.conn,
            email="john.engineer@constructionhub.com",
            password="EngineerPass123!",
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user)
        self.assertEqual(user["full_name"], "John Engineer")
        self.assertEqual(user["role"], "Manager")

    def test_user_login_wrong_password(self):
        models.create_user(
            self.conn,
            full_name="John Engineer",
            email="john.engineer@constructionhub.com",
            password="EngineerPass123!",
        )
        user, err = models.authenticate_user(
            self.conn,
            email="john.engineer@constructionhub.com",
            password="WrongPassword999",
        )
        self.assertIsNone(user)
        self.assertEqual(err, "Email or password is incorrect.")

    def test_password_strength_validation(self):
        self.assertIn("at least 8 characters", login.validate_password_strength("Short1!"))
        self.assertIn("uppercase letter", login.validate_password_strength("lowercase123!"))
        self.assertIn("lowercase letter", login.validate_password_strength("UPPERCASE123!"))
        self.assertIn("number", login.validate_password_strength("NoNumberPass!"))
        self.assertIsNone(login.validate_password_strength("ValidPass123!"))

    def test_seed_default_users(self):
        seed.seed_users(self.conn)
        admin = models.get_user_by_email(self.conn, "admin@constructionhub.com")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "Admin")

        manager = models.get_user_by_email(self.conn, "manager@constructionhub.com")
        self.assertIsNotNone(manager)
        self.assertEqual(manager["role"], "Manager")


if __name__ == "__main__":
    unittest.main()
