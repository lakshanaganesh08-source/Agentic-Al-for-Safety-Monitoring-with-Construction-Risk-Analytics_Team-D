"""
Initialize the SQLite database schema.

Usage:
    python scripts/init_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_database  # noqa: E402


def main() -> None:
    db_path = init_database()
    print(f"Database initialized: {db_path}")


if __name__ == "__main__":
    main()
