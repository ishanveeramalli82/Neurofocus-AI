PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash   TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    settings_json   TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule_events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title            TEXT NOT NULL,
    subject          TEXT NOT NULL DEFAULT '',
    kind             TEXT NOT NULL DEFAULT 'study',   -- study | class | exam | break | other
    start_at         TEXT NOT NULL,                   -- local ISO datetime, minute precision
    end_at           TEXT NOT NULL,
    notes            TEXT NOT NULL DEFAULT '',
    completed        INTEGER NOT NULL DEFAULT 0,
    recurrence_group TEXT,
    created_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_user_start ON schedule_events(user_id, start_at);

CREATE TABLE IF NOT EXISTS tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title         TEXT NOT NULL,
    subject       TEXT NOT NULL DEFAULT '',
    due_at        TEXT,
    priority      TEXT NOT NULL DEFAULT 'medium',     -- low | medium | high
    estimated_min INTEGER,
    done          INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id, done, due_at);

CREATE TABLE IF NOT EXISTS study_sessions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title             TEXT NOT NULL,
    subject           TEXT NOT NULL DEFAULT '',
    schedule_event_id INTEGER REFERENCES schedule_events(id) ON DELETE SET NULL,
    status            TEXT NOT NULL DEFAULT 'calibrating',  -- calibrating | active | ended
    started_at        TEXT NOT NULL,
    ended_at          TEXT,
    calibrated        INTEGER NOT NULL DEFAULT 0,
    calibration_json  TEXT,
    engine_version    TEXT NOT NULL,
    params_json       TEXT NOT NULL,
    last_t            REAL NOT NULL DEFAULT 0,
    focused_s         REAL NOT NULL DEFAULT 0,
    total_s           REAL NOT NULL DEFAULT 0,
    focus_score       REAL,
    distraction_count INTEGER NOT NULL DEFAULT 0,
    filter_state_json TEXT,
    notes             TEXT NOT NULL DEFAULT '',
    planned_min       INTEGER,
    frames_total      INTEGER NOT NULL DEFAULT 0,   -- feature frames received
    frames_face       INTEGER NOT NULL DEFAULT 0,   -- of those, frames with a detected face
    if_then_plan      TEXT NOT NULL DEFAULT '',     -- optional "if I get distracted, then I will..."
    reflection_json   TEXT                          -- end-of-session reflection answers
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON study_sessions(user_id, started_at);

-- One row per second of session time: the engine state at the end of that second.
CREATE TABLE IF NOT EXISTS session_samples (
    session_id  INTEGER NOT NULL REFERENCES study_sessions(id) ON DELETE CASCADE,
    second      INTEGER NOT NULL,
    state       TEXT NOT NULL,
    live_score  REAL,
    PRIMARY KEY (session_id, second)
);

CREATE TABLE IF NOT EXISTS session_episodes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES study_sessions(id) ON DELETE CASCADE,
    state       TEXT NOT NULL,
    start_t     REAL NOT NULL,
    end_t       REAL
);
CREATE INDEX IF NOT EXISTS idx_episodes_session ON session_episodes(session_id);

-- Onboarding survey answers (product data for personalization only).
CREATE TABLE IF NOT EXISTS study_profiles (
    user_id       INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    answers_json  TEXT NOT NULL DEFAULT '{}',
    completed_at  TEXT,
    skipped       INTEGER NOT NULL DEFAULT 0,
    updated_at    TEXT NOT NULL
);

-- Personal study plans: what the student entered and what the planner produced.
CREATE TABLE IF NOT EXISTS study_plans (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at    TEXT NOT NULL,
    inputs_json   TEXT NOT NULL,
    plan_json     TEXT NOT NULL,
    applied_at    TEXT,
    group_id      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_plans_user ON study_plans(user_id, created_at);

-- Self check-ins during a session ("Was I on task just now?").
CREATE TABLE IF NOT EXISTS session_checkins (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES study_sessions(id) ON DELETE CASCADE,
    t           REAL NOT NULL,
    rating      TEXT NOT NULL               -- on | mostly | off
);
CREATE INDEX IF NOT EXISTS idx_checkins_session ON session_checkins(session_id);
