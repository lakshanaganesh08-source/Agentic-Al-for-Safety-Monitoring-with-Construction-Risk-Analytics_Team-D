import os
import json
import bcrypt
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "construction_db")
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "construction_db.sqlite")

class DBManager:
    """
    Handles user authentication, password hashing with bcrypt,
    parameterized database queries, and user-isolated project persistence.
    Supports MySQL Server primary connection with automatic SQLite fallback.
    """

    @staticmethod
    def get_connection():
        """Attempts MySQL connection; returns (conn, engine_type)."""
        try:
            import mysql.connector
            # Connect to MySQL Server
            try:
                # Try creating database if missing
                root_conn = mysql.connector.connect(
                    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, connect_timeout=3
                )
                cursor = root_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
                cursor.close()
                root_conn.close()

                conn = mysql.connector.connect(
                    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, connect_timeout=3
                )
                return conn, "mysql"
            except Exception as ex:
                pass
        except ImportError:
            pass

        # Fallback to SQLite
        conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        return conn, "sqlite"

    @staticmethod
    def init_db():
        conn, engine = DBManager.get_connection()
        cursor = conn.cursor()
        if engine == "mysql":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    project_name VARCHAR(255) NOT NULL,
                    structure_type VARCHAR(50) NOT NULL,
                    plot_data LONGTEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    structure_type TEXT NOT NULL,
                    plot_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
        conn.commit()
        cursor.close()
        conn.close()
        return engine

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hashes password securely using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies password against stored bcrypt hash."""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    @classmethod
    def register_user(cls, username: str, email: str, password: str, confirm_password: str):
        """Registers a new user with validation and bcrypt hashing."""
        username = username.strip()
        email = email.strip().lower()

        if not username or not email or not password:
            return None, "All fields are required."
        if len(username) < 3:
            return None, "Username must be at least 3 characters long."
        if len(password) < 6:
            return None, "Password must be at least 6 characters long."
        if password != confirm_password:
            return None, "Passwords do not match."
        if "@" not in email or "." not in email:
            return None, "Invalid email address format."

        conn, engine = cls.get_connection()
        cursor = conn.cursor()
        ph = cls.get_placeholder(engine)

        try:
            # Check existing username
            cursor.execute(f"SELECT id FROM users WHERE username = {ph}", (username,))
            if cursor.fetchone():
                return None, "Username is already taken. Please choose another."

            # Check existing email
            cursor.execute(f"SELECT id FROM users WHERE email = {ph}", (email,))
            if cursor.fetchone():
                return None, "Email address is already registered."

            pwd_hash = cls.hash_password(password)
            cursor.execute(
                f"INSERT INTO users (username, email, password_hash) VALUES ({ph}, {ph}, {ph})",
                (username, email, pwd_hash)
            )
            conn.commit()

            # Retrieve inserted ID
            cursor.execute(f"SELECT id FROM users WHERE username = {ph}", (username,))
            user_row = cursor.fetchone()
            user_id = user_row[0] if user_row else cursor.lastrowid
            return {"user_id": user_id, "username": username, "email": email}, None
        except Exception as e:
            return None, f"Database registration error: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def login_user(cls, username_or_email: str, password: str):
        """Authenticates user against stored bcrypt password hash."""
        identifier = username_or_email.strip().lower()
        if not identifier or not password:
            return None, "Please enter your username/email and password."

        conn, engine = cls.get_connection()
        cursor = conn.cursor()
        ph = cls.get_placeholder(engine)

        try:
            cursor.execute(
                f"SELECT id, username, email, password_hash FROM users WHERE LOWER(username) = {ph} OR LOWER(email) = {ph}",
                (identifier, identifier)
            )
            user = cursor.fetchone()
            if not user:
                return None, "Account not found. Please check your credentials or Sign Up."

            user_id, username, email, stored_hash = user[0], user[1], user[2], user[3]
            if not cls.check_password(password, stored_hash):
                return None, "Incorrect password. Please try again."

            return {"user_id": user_id, "username": username, "email": email}, None
        except Exception as e:
            return None, f"Login authentication error: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def save_project(cls, user_id: int, project_name: str, structure_type: str, plot_data: dict):
        """Saves or updates a project for the authenticated user."""
        if not user_id:
            return None, "Authentication required to save projects."

        project_name = project_name.strip() if project_name else "Untitled Project"
        plot_json = json.dumps(plot_data)

        conn, engine = cls.get_connection()
        cursor = conn.cursor()
        ph = cls.get_placeholder(engine)

        try:
            cursor.execute(
                f"INSERT INTO projects (user_id, project_name, structure_type, plot_data) VALUES ({ph}, {ph}, {ph}, {ph})",
                (user_id, project_name, structure_type, plot_json)
            )
            conn.commit()
            return cursor.lastrowid, None
        except Exception as e:
            return None, f"Failed to save project: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_user_projects(cls, user_id: int):
        """Enforces multi-tenant security: returns ONLY projects for the given user_id."""
        if not user_id:
            return []

        conn, engine = cls.get_connection()
        cursor = conn.cursor()
        ph = cls.get_placeholder(engine)

        try:
            cursor.execute(
                f"SELECT id, project_name, structure_type, plot_data, created_at FROM projects WHERE user_id = {ph} ORDER BY id DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            projects = []
            for r in rows:
                pdata = json.loads(r[3]) if isinstance(r[3], str) else r[3]
                projects.append({
                    "id": r[0],
                    "project_name": r[1],
                    "structure_type": r[2],
                    "plot_data": pdata,
                    "created_at": str(r[4])
                })
            return projects
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def delete_user_project(cls, project_id: int, user_id: int):
        """Deletes a project enforcing user_id ownership match."""
        conn, engine = cls.get_connection()
        cursor = conn.cursor()
        ph = cls.get_placeholder(engine)
        try:
            cursor.execute(
                f"DELETE FROM projects WHERE id = {ph} AND user_id = {ph}",
                (project_id, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Delete project error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_placeholder(engine: str) -> str:
        return "%s" if engine == "mysql" else "?"

# Initialize DB on load
active_engine = DBManager.init_db()
print(f"[DBManager] Initialized with active engine: '{active_engine}'")
