"""
Central configuration for Construction Intelligence Hub.

All paths and service endpoints are resolved relative to the project root
so the app runs consistently regardless of the working directory.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "construction_hub.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

# ---------------------------------------------------------------------------
# Ollama (local LLM — no paid APIs)
# ---------------------------------------------------------------------------
OLLAMA_MODEL = "llama3.2"
OLLAMA_ROOT_URLS = [
    "http://127.0.0.1:11434",
    "http://localhost:11434",
]
OLLAMA_GENERATE_PATH = "/api/generate"

# Default HTTP timeouts: (connect_seconds, read_seconds)
OLLAMA_DEFAULT_TIMEOUT = (5, 60)
OLLAMA_FAST_TIMEOUT = (3, 15)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
APP_NAME = "Construction Intelligence Hub"
DEFAULT_PROJECT_NAME = "Downtown Tower Phase 1"
