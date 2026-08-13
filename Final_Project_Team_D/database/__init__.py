"""
Database package for Construction Intelligence Hub.

Public API:
    init_database  — create tables from schema.sql
    get_db         — context-managed connection
    models         — repository CRUD helpers
    seed           — demo data loader
"""

from database.db import database_exists, get_db, init_database

__all__ = ["init_database", "get_db", "database_exists"]
