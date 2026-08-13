-- Construction Intelligence Hub — SQLite schema
-- Applied automatically on first run via database/db.py

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Core entities
-- ---------------------------------------------------------------------------

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

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    salt          TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'User',
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS workers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER,
    name        TEXT    NOT NULL,
    role        TEXT,
    site_zone   TEXT,
    ppe_status  TEXT    DEFAULT 'Unknown',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
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

-- ---------------------------------------------------------------------------
-- Safety & incidents
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS incidents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER,
    incident_type   TEXT    NOT NULL,
    severity        TEXT,
    description     TEXT    NOT NULL,
    zone            TEXT,
    reported_by     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS safety_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id       INTEGER,
    project_id      INTEGER,
    ppe_helmet      INTEGER DEFAULT 0,
    ppe_vest        INTEGER DEFAULT 0,
    safety_score    REAL,
    unsafe_behavior TEXT,
    zone            TEXT,
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------------
-- Agent logs (populated in later phases)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS risk_logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER,
    risk_type    TEXT    NOT NULL DEFAULT 'delay',
    score        REAL    NOT NULL,
    priority     TEXT,
    factors_json TEXT,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS compliance_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER,
    standard    TEXT,
    status      TEXT,
    violation   TEXT,
    percentage  REAL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS insurance_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id     INTEGER,
    project_id      INTEGER,
    exposure        REAL,
    severity        TEXT,
    claim_risk_score REAL,
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS material_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER,
    material    TEXT    NOT NULL,
    quantity    REAL,
    unit        TEXT,
    unit_cost   REAL,
    waste_pct   REAL    DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inspections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER,
    inspector       TEXT,
    checklist_json  TEXT,
    result          TEXT,
    inspection_date TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER,
    report_type TEXT    NOT NULL,
    period      TEXT,
    file_path   TEXT,
    generated_at TEXT   NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------------
-- Indexes for common queries
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_incidents_project_id ON incidents(project_id);
CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents(created_at);
CREATE INDEX IF NOT EXISTS idx_risk_logs_type ON risk_logs(risk_type);
CREATE INDEX IF NOT EXISTS idx_safety_logs_project_id ON safety_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_workers_project_id ON workers(project_id);
