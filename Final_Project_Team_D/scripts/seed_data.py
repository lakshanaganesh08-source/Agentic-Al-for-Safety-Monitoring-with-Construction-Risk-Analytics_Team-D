"""
Load demo projects, tasks, and sample incidents into SQLite.

Usage:
    python scripts/seed_data.py
    python scripts/seed_data.py --no-incidents
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.seed import run_seed  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Construction Intelligence Hub demo data")
    parser.add_argument(
        "--no-incidents",
        action="store_true",
        help="Skip inserting sample incident records",
    )
    args = parser.parse_args()

    summary = run_seed(include_demo_incidents=not args.no_incidents)
    print("Seed complete:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
