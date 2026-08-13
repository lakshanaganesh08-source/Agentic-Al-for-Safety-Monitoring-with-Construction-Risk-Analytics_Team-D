# Construction Intelligence Hub

AI-powered construction management platform built with **Streamlit**, **SQLite**, and **Ollama** (local LLM only — no paid APIs).

## Features

- Executive dashboard with budget, progress, incident heatmaps & KPIs (DB-backed)
- AI cost estimation (ML) with category breakdown
- Schedule delay risk prediction (Random Forest ML + risk history)
- Dual AI chatbots (General + Construction Expert) via Ollama with conversation memory
- Computer vision site inspection (OpenCV PPE & hazard analysis)
- **Material Estimation** — quantities, labour, equipment, BOQ, waste
- Project task management (SQLite-backed)
- Safety incident logging (SQLite-backed)
- Multi-format report export (ReportLab PDF, openpyxl Excel, live DB data)

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) with `llama3.2` pulled locally:

```bash
ollama pull llama3.2
ollama serve
```

## Setup

```bash
# Clone / open project, then:
python -m venv .venv

# Windows
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (optional — app auto-initializes on first run)
python scripts/init_db.py
python scripts/seed_data.py
```

## Run

```bash
streamlit run app.py
```

**Demo login:** `admin` / `admin123` · `user` / `password123` · `demo` / `demo`

## Project structure

```
app.py                 # Streamlit entry point + navigation router
config/settings.py     # Paths, Ollama model, app constants
database/              # SQLite schema, connection, models, seed
modules/               # Feature UI pages (render() pattern)
utils/                 # Styling, ML helpers, Ollama client
scripts/               # init_db.py, seed_data.py
tests/                 # Unit tests
```

## Database

SQLite file: `database/construction_hub.db` (created automatically).

Tables include: `projects`, `tasks`, `incidents`, `workers`, `risk_logs`, `safety_logs`, `compliance_logs`, `insurance_logs`, `material_records`, `reports`, `inspections`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Development phases

See `PROJECT_REQUIREMENTS.md` for the full specification.

| Phase | Status |
|-------|--------|
| 1 — SQLite foundation | ✅ Complete |
| 2 — Upgrade existing modules + Material Estimation | ✅ Complete |
| 3 — Site Risk & Safety Agents | ✅ Complete |
| 4 — Executive dashboard & polish | Pending |

## License

Final-year academic project — Construction Intelligence Hub © 2026
