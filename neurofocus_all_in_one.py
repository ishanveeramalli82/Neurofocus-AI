#!/usr/bin/env python3
# =============================================================================
#  NeuroFocus AI - ALL-IN-ONE LAUNCHER
# =============================================================================
#  HOW TO USE (VS Code):
#    1. Make an empty folder, e.g. Documents\NeuroFocusAI, and open it in VS Code
#       (File > Open Folder).
#    2. Create a new file in it called  neurofocus_all_in_one.py  and paste
#       this entire file into it. Save (Ctrl+S).
#    3. Open a terminal (Terminal > New Terminal) and run:
#           python neurofocus_all_in_one.py
#       (on Mac: python3 neurofocus_all_in_one.py)
#    4. Chrome opens http://127.0.0.1:5000 . Create an account, allow the
#       camera, and start a Focus Session. Press Ctrl+C in the terminal to stop.
#
#  WHAT IT DOES ON FIRST RUN:
#    - installs the Python packages it needs (Flask, NumPy, SciPy, Matplotlib, pytest)
#    - unpacks the full, organized project into a folder called  neurofocus\
#      (engine, backend, frontend, research experiment, docs, tests)
#    - downloads the MediaPipe face-tracking files (~22 MB, needs internet once)
#    - starts the app. After the first run it also works offline.
#
#  OTHER COMMANDS (run from the same folder as this file):
#    python neurofocus_all_in_one.py --tests        run the automated tests
#    python neurofocus_all_in_one.py --experiment   run the official experiment
#    python neurofocus_all_in_one.py --unpack-only  only create the project folder
#
#  NeuroFocus estimates where your head and eyes point. It does not measure
#  learning and is not a medical or diagnostic tool.
#  Generated from project commit a25bc6b. Do not edit the embedded files here;
#  edit them in the unpacked neurofocus\ folder instead.
# =============================================================================

import hashlib
import os
import subprocess
import sys
import urllib.request
import webbrowser
from pathlib import Path

VERSION = "a25bc6b"
PROJECT_DIR = Path(__file__).resolve().parent / "neurofocus"
REQUIREMENTS = ["flask>=3.0", "numpy>=1.26", "scipy>=1.11", "matplotlib>=3.8", "pytest>=8.0"]
# Optional override for where the face-tracking files are downloaded from.
MIRROR = os.environ.get("NEUROFOCUS_VENDOR_MIRROR")

VENDOR = [
    ('frontend/vendor/mediapipe/vision_bundle.mjs',
     'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs',
     'e77f281f9619150d937023c355bae170e9120e3b9e43f1e23a2a7bee07197669'),
    ('frontend/vendor/mediapipe/wasm/vision_wasm_internal.js',
     'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_internal.js',
     '9440cf0cc0cea21800e31581ec32aeedcc5fbf9df4509796bbc7d3f99e52ab9c'),
    ('frontend/vendor/mediapipe/wasm/vision_wasm_internal.wasm',
     'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_internal.wasm',
     'f82a8e6c05e08a44cc9f9e7ec5f845935bcbb1b1500ebe8c2f4812fb4e2917dc'),
    ('frontend/vendor/mediapipe/wasm/vision_wasm_nosimd_internal.js',
     'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_nosimd_internal.js',
     'abe9b6fbeaf86fcb53a5edce3926c82ccb0619e18fed4d9d9ce561ee7f55e054'),
    ('frontend/vendor/mediapipe/wasm/vision_wasm_nosimd_internal.wasm',
     'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_nosimd_internal.wasm',
     '38b61feab2fd7934e05cbe9f68baa308978a5e3b7f85c1913bb8ae89b8ef8b97'),
    ('frontend/vendor/models/face_landmarker.task',
     'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
     '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff'),
]

FILES = {}

# ===== .gitignore ============================================================
FILES['.gitignore'] = r'''__pycache__/
*.pyc
instance/
.pytest_cache/
research/data/raw/*
research/data/processed/*
!research/data/raw/.gitkeep
!research/data/processed/.gitkeep
'''

# ===== README.md =============================================================
FILES['README.md'] = r'''# NeuroFocus AI

A webcam-based study-focus tracker with a transparent, testable attention
engine, built as both a working product and a science-fair engineering
research project.

* **Product:** accounts, camera calibration, on-device computer vision, live
  Focus Score, session history, analytics, and a Schedule department (calendar,
  tasks, recurring classes, conflict detection, automatic study-block planning).
* **Research:** a reproducible virtual-student experiment that measures how
  accurately the attention engine detects distraction. See
  [`research/README.md`](research/README.md).

> NeuroFocus estimates where your head and eyes point. It does not measure
> learning, and it is not a medical or diagnostic tool (it does not detect or
> diagnose ADHD or any other condition). Current accuracy figures come from
> simulated students only.

## Quick start

Requires Python 3.10+ and a modern Chromium-based browser, Firefox or Safari.

```bash
pip install -r requirements.txt
python run.py
# open http://127.0.0.1:5000
```

The camera only works on `localhost` or over HTTPS (a browser rule).
Everything, including the MediaPipe face model, is served locally, so the
app works offline once installed.

Environment variables (optional):

| Variable | Purpose |
|---|---|
| `NEUROFOCUS_SECRET_KEY` | session-signing key (otherwise generated into `instance/secret_key`) |
| `NEUROFOCUS_SECURE_COOKIES=1` | set when serving over HTTPS |
| `PORT` | port (default 5000) |

## Tests

```bash
python -m pytest
```

The tests cover the engine rules, calibration and scoring; the API (auth,
CSRF, rate limiting, privacy between users, sessions, schedule, auto-planning,
export/delete); and the research pipeline (ground-truth separation,
reproducibility, metric formulas, statistics).

## How it works

```
Browser                                        Server (Flask + SQLite)
-------                                        -----------------------
webcam -> MediaPipe Face Landmarker            neurofocus_engine
       -> 6 numbers/frame (10 fps) --JSON-->     calibration -> frame rules -> temporal filter
                                                 -> attention state, Focus Score, episodes
live UI <------------------------------------   stored per second; history & analytics
```

Full algorithm: [`research/docs/03_algorithm.md`](research/docs/03_algorithm.md).

## Project structure

```
neurofocus_engine/   attention engine shared by the app and the experiment
backend/             Flask API: auth, sessions, schedule, analytics, research results
frontend/            HTML/CSS/JS pages; vendor/ holds MediaPipe + the face model
research/            experiment: simulator, pipeline, analysis, docs, results
tests/               automated tests
run.py               starts the web app
```

## Security & privacy

* Video never leaves the browser; only numeric features are sent.
* Passwords hashed with scrypt; HttpOnly SameSite cookies; CSRF tokens on all
  state-changing requests; login rate limiting; strict Content-Security-Policy
  (no third-party scripts); per-user data isolation; data export and account
  deletion.
* The development server (`python run.py`) is for local use. For anything
  public, run behind HTTPS with a production WSGI server.
'''

# ===== backend/__init__.py ===================================================
FILES['backend/__init__.py'] = r''''''

# ===== backend/analytics_api.py ==============================================
FILES['backend/analytics_api.py'] = r'''import datetime as dt
import json

from flask import Blueprint, jsonify, request, session

from .db import get_db
from .security import login_required
from . import validation as v

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def _weighted(items):
    tot = sum(i["total_s"] for i in items)
    foc = sum(i["focused_s"] for i in items)
    return (100 * foc / tot) if tot > 0 else None


@bp.get("/summary")
@login_required
def summary():
    days = v.integer(request.args, "days", lo=1, hi=365, default=30)
    # minutes to ADD to UTC to get the user's local time (JS: -new Date().getTimezoneOffset())
    tz = dt.timedelta(minutes=v.integer(request.args, "tz_offset_min", lo=-840, hi=840, default=0))
    today = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + tz
    since_local = (today - dt.timedelta(days=days - 1)).date()
    db = get_db()
    rows = db.execute(
        "SELECT * FROM study_sessions WHERE user_id = ? AND status = 'ended' AND total_s > 0 ORDER BY started_at",
        (session["user_id"],)).fetchall()
    sessions = []
    for r in rows:
        local = dt.datetime.fromisoformat(r["started_at"]).replace(tzinfo=None) + tz
        if local.date() >= since_local:
            sessions.append({**dict(r), "local": local})

    daily = {}
    for i in range(days):
        d = (since_local + dt.timedelta(days=i)).isoformat()
        daily[d] = {"date": d, "focused_s": 0.0, "total_s": 0.0, "sessions": 0}
    by_hour, by_subject = {}, {}
    for s in sessions:
        dd = daily[s["local"].date().isoformat()]
        dd["focused_s"] += s["focused_s"]
        dd["total_s"] += s["total_s"]
        dd["sessions"] += 1
        by_hour.setdefault(s["local"].hour, []).append(s)
        by_subject.setdefault(s["subject"] or "(no subject)", []).append(s)
    for dd in daily.values():
        dd["score"] = 100 * dd["focused_s"] / dd["total_s"] if dd["total_s"] else None

    ids = [s["id"] for s in sessions]
    breakdown = {}
    if ids:
        marks = ",".join("?" * len(ids))
        for e in db.execute(
                f"SELECT state, COUNT(*) AS n, SUM(COALESCE(end_t, start_t) - start_t) AS secs "
                f"FROM session_episodes WHERE session_id IN ({marks}) GROUP BY state", ids):
            breakdown[e["state"]] = {"count": e["n"], "seconds": e["secs"] or 0}

    # streak of consecutive days (ending today or yesterday) with at least one session
    active_days = {dt.date.fromisoformat(k) for k, d in daily.items() if d["sessions"]}
    streak, cursor = 0, today.date()
    if cursor not in active_days:
        cursor -= dt.timedelta(days=1)
    while cursor in active_days:
        streak += 1
        cursor -= dt.timedelta(days=1)

    user = db.execute("SELECT settings_json FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    goal = json.loads(user["settings_json"] or "{}").get("daily_goal_min", 120)
    today_d = daily.get(today.date().isoformat(), {"focused_s": 0})
    return jsonify(
        range_days=days,
        totals={"sessions": len(sessions),
                "total_hours": sum(s["total_s"] for s in sessions) / 3600,
                "focused_hours": sum(s["focused_s"] for s in sessions) / 3600,
                "focus_score": _weighted(sessions),
                "distractions": sum(s["distraction_count"] for s in sessions)},
        daily=list(daily.values()),
        by_hour=[{"hour": h, "score": _weighted(v_), "sessions": len(v_)} for h, v_ in sorted(by_hour.items())],
        by_subject=sorted(
            [{"subject": k, "score": _weighted(v_), "hours": sum(x["total_s"] for x in v_) / 3600,
              "sessions": len(v_)} for k, v_ in by_subject.items()], key=lambda x: -x["hours"]),
        distraction_breakdown=breakdown,
        streak_days=streak,
        today={"focused_min": today_d["focused_s"] / 60, "goal_min": goal},
        note="Focus Score measures camera-visible attention behaviour (where your head and eyes point). "
             "It does not measure learning, comprehension, or any medical condition.",
    )
'''

# ===== backend/app.py ========================================================
FILES['backend/app.py'] = r'''import datetime as dt
import os
import secrets
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory

from .db import close_db, init_db
from .security import apply_security_headers, check_csrf
from .validation import ValidationError

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PAGES = {"", "login", "register", "dashboard", "session", "history", "analytics",
         "schedule", "research", "settings"}


def _secret_key(instance):
    env = os.environ.get("NEUROFOCUS_SECRET_KEY")
    if env:
        return env
    path = instance / "secret_key"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_hex(32))
        path.chmod(0o600)
    return path.read_text().strip()


def create_app(test_config=None):
    instance = ROOT / "instance"
    app = Flask(__name__, static_folder=None)
    app.config.update(
        DATABASE=str(instance / "neurofocus.sqlite3"),
        SECRET_KEY=None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("NEUROFOCUS_SECURE_COOKIES") == "1",
        PERMANENT_SESSION_LIFETIME=dt.timedelta(days=14),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"]:
        app.config["SECRET_KEY"] = _secret_key(instance)
    init_db(app.config["DATABASE"])

    from . import auth, sessions_api, schedule_api, analytics_api, research_api
    for mod in (auth, sessions_api, schedule_api, analytics_api, research_api):
        app.register_blueprint(mod.bp)

    app.before_request(check_csrf)
    app.after_request(apply_security_headers)
    app.teardown_appcontext(close_db)

    @app.errorhandler(ValidationError)
    def _bad(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(404)
    def _nf(e):
        return jsonify(error="Not found."), 404

    @app.errorhandler(413)
    def _big(e):
        return jsonify(error="Request too large."), 413

    @app.get("/api/health")
    def health():
        return jsonify(ok=True)

    @app.get("/")
    @app.get("/<page>")
    def page(page=""):
        if page not in PAGES:
            abort(404)
        return send_from_directory(FRONTEND, f"{page or 'index'}.html")

    @app.get("/static/<path:path>")
    def static_files(path):
        return send_from_directory(FRONTEND, path)

    return app
'''

# ===== backend/auth.py =======================================================
FILES['backend/auth.py'] = r'''import json

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, now_iso
from .security import csrf_token, login_limiter, login_required
from . import validation as v

bp = Blueprint("auth", __name__, url_prefix="/api")

DEFAULT_SETTINGS = {
    "daily_goal_min": 120,
    "alert_after_s": 20,
    "alert_sound": True,
    "default_session_min": 50,
    "break_min": 10,
    "show_camera_preview": True,
}
# A real hash of a random string so failed logins for unknown emails take as
# long as for known ones (prevents account enumeration by timing).
_DUMMY_HASH = generate_password_hash("not-a-real-password-0f9a")


def _user_payload(row):
    settings = {**DEFAULT_SETTINGS, **json.loads(row["settings_json"] or "{}")}
    return {"id": row["id"], "email": row["email"], "display_name": row["display_name"],
            "settings": settings, "created_at": row["created_at"]}


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def _start_session(user_id):
    session.clear()
    session.permanent = True
    session["user_id"] = user_id
    return csrf_token()


@bp.get("/auth/csrf")
def get_csrf():
    return jsonify(csrf=csrf_token())


@bp.get("/auth/status")
def status():
    """Public check used by public pages (no 401 noise in the console)."""
    return jsonify(signed_in=current_user() is not None)


@bp.post("/auth/register")
def register():
    d = request.get_json(silent=True) or {}
    email = v.email(d)
    pw = v.password(d)
    name = v.text(d, "display_name", required=True, max_len=60)
    db = get_db()
    if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
        return jsonify(error="An account with that email already exists."), 409
    cur = db.execute(
        "INSERT INTO users (email, password_hash, display_name, settings_json, created_at) VALUES (?,?,?,?,?)",
        (email, generate_password_hash(pw), name, json.dumps(DEFAULT_SETTINGS), now_iso()))
    db.commit()
    token = _start_session(cur.lastrowid)
    row = db.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(user=_user_payload(row), csrf=token), 201


@bp.post("/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    email = str(d.get("email", "")).strip().lower()
    pw = str(d.get("password", ""))
    key = f"{request.remote_addr}|{email}"
    if login_limiter.blocked(key):
        return jsonify(error="Too many failed attempts. Try again in 15 minutes."), 429
    row = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not check_password_hash(row["password_hash"] if row else _DUMMY_HASH, pw) or not row:
        login_limiter.fail(key)
        return jsonify(error="Incorrect email or password."), 401
    login_limiter.reset(key)
    token = _start_session(row["id"])
    return jsonify(user=_user_payload(row), csrf=token)


@bp.post("/auth/logout")
def logout():
    session.clear()
    return jsonify(ok=True, csrf=csrf_token())


@bp.get("/auth/me")
@login_required
def me():
    row = current_user()
    if row is None:
        session.clear()
        return jsonify(error="Please sign in."), 401
    return jsonify(user=_user_payload(row), csrf=csrf_token())


@bp.put("/account/profile")
@login_required
def update_profile():
    d = request.get_json(silent=True) or {}
    row = current_user()
    settings = {**DEFAULT_SETTINGS, **json.loads(row["settings_json"] or "{}")}
    s = d.get("settings") or {}
    if s:
        settings["daily_goal_min"] = v.integer(s, "daily_goal_min", lo=10, hi=900, default=settings["daily_goal_min"])
        settings["alert_after_s"] = v.integer(s, "alert_after_s", lo=5, hi=600, default=settings["alert_after_s"])
        settings["default_session_min"] = v.integer(s, "default_session_min", lo=5, hi=240, default=settings["default_session_min"])
        settings["break_min"] = v.integer(s, "break_min", lo=1, hi=60, default=settings["break_min"])
        for flag in ("alert_sound", "show_camera_preview"):
            if flag in s:
                settings[flag] = bool(s[flag])
    name = v.text(d, "display_name", max_len=60, default=row["display_name"]) or row["display_name"]
    db = get_db()
    db.execute("UPDATE users SET display_name = ?, settings_json = ? WHERE id = ?",
               (name, json.dumps(settings), row["id"]))
    db.commit()
    return jsonify(user=_user_payload(current_user()))


@bp.put("/account/password")
@login_required
def change_password():
    d = request.get_json(silent=True) or {}
    row = current_user()
    if not check_password_hash(row["password_hash"], str(d.get("current_password", ""))):
        return jsonify(error="Current password is incorrect."), 400
    new = v.password(d, "new_password")
    db = get_db()
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(new), row["id"]))
    db.commit()
    token = _start_session(row["id"])
    return jsonify(ok=True, csrf=token)


@bp.get("/account/export")
@login_required
def export_data():
    uid = session["user_id"]
    db = get_db()
    rows = lambda q, *a: [dict(r) for r in db.execute(q, a).fetchall()]
    user = _user_payload(current_user())
    sessions = rows("SELECT * FROM study_sessions WHERE user_id = ? ORDER BY started_at", uid)
    for s in sessions:
        s["samples"] = rows("SELECT second, state, live_score FROM session_samples WHERE session_id = ? ORDER BY second", s["id"])
        s["episodes"] = rows("SELECT state, start_t, end_t FROM session_episodes WHERE session_id = ? ORDER BY start_t", s["id"])
    data = {"exported_at": now_iso(), "user": user, "study_sessions": sessions,
            "schedule_events": rows("SELECT * FROM schedule_events WHERE user_id = ?", uid),
            "tasks": rows("SELECT * FROM tasks WHERE user_id = ?", uid)}
    resp = jsonify(data)
    resp.headers["Content-Disposition"] = "attachment; filename=neurofocus-export.json"
    return resp


@bp.delete("/account")
@login_required
def delete_account():
    d = request.get_json(silent=True) or {}
    row = current_user()
    if not check_password_hash(row["password_hash"], str(d.get("password", ""))):
        return jsonify(error="Password is incorrect."), 400
    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (row["id"],))
    db.commit()
    session.clear()
    return jsonify(ok=True)
'''

# ===== backend/db.py =========================================================
FILES['backend/db.py'] = r'''import datetime as dt
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = Path(__file__).with_name("schema.sql")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA.read_text())
    con.execute("PRAGMA journal_mode = WAL")
    con.close()


def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def row_dict(row):
    return dict(row) if row is not None else None
'''

# ===== backend/research_api.py ===============================================
FILES['backend/research_api.py'] = r'''"""Read-only access to the engine's parameters and to finished experiment
results, so the Research & Method page always shows the real, current values
rather than numbers copied by hand."""

import json
from pathlib import Path

from flask import Blueprint, abort, jsonify, send_from_directory

from neurofocus_engine import DEFAULT_PARAMS, ENGINE_VERSION

bp = Blueprint("research", __name__)
RESULTS = Path(__file__).resolve().parents[1] / "research" / "results"
ALLOWED = {".png", ".csv", ".json", ".md"}


@bp.get("/api/engine/params")
def engine_params():
    return jsonify(version=ENGINE_VERSION, params=DEFAULT_PARAMS.to_dict())


@bp.get("/api/research/runs")
def runs():
    out = []
    if RESULTS.exists():
        for d in sorted(RESULTS.iterdir(), reverse=True):
            man, st = d / "manifest.json", d / "statistics.json"
            if not (man.exists() and st.exists()):
                continue
            manifest = json.loads(man.read_text())
            out.append({
                "run_id": d.name,
                "smoke_test": manifest.get("smoke_test", False),
                "created": manifest.get("created"),
                "experiment_id": manifest["effective_config"]["experiment_id"],
                "n_students": manifest["effective_config"]["n_students"],
                "session_duration_s": manifest["effective_config"]["session_duration_s"],
                "engine_version": manifest.get("engine_version"),
                "statistics": json.loads(st.read_text()),
                "figures": sorted(p.name for p in (d / "figures").glob("*.png")) if (d / "figures").exists() else [],
            })
    return jsonify(runs=out)


@bp.get("/research-files/<run_id>/<path:name>")
def research_file(run_id, name):
    if Path(name).suffix not in ALLOWED or ".." in run_id:
        abort(404)
    return send_from_directory(RESULTS / run_id, name)
'''

# ===== backend/schedule_api.py ===============================================
FILES['backend/schedule_api.py'] = r'''"""Schedule department: study blocks / classes / exams (calendar events),
tasks and assignments, conflict detection, and automatic study planning.

Times are stored as local wall-clock ISO strings ('YYYY-MM-DDTHH:MM') because
a study plan is about the student's own day, not a global instant. The browser
supplies 'now' when an operation depends on the current time.
"""

import datetime as dt
import uuid

from flask import Blueprint, jsonify, request, session

from .db import get_db, now_iso, row_dict
from .security import login_required
from . import validation as v

bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")

KINDS = ("study", "class", "exam", "break", "other")
PRIORITIES = ("low", "medium", "high")


def _uid():
    return session["user_id"]


def _parse(s):
    return dt.datetime.fromisoformat(s)


def _iso(d):
    return d.isoformat(timespec="minutes")


def _conflicts(db, start, end, exclude_ids=()):
    rows = db.execute(
        "SELECT * FROM schedule_events WHERE user_id = ? AND start_at < ? AND end_at > ?",
        (_uid(), end, start)).fetchall()
    return [row_dict(r) for r in rows if r["id"] not in exclude_ids]


def _event_fields(d, existing=None):
    existing = existing or {}
    merged = {**existing, **d}
    title = v.text(merged, "title", required=True, max_len=120)
    subject = v.text(merged, "subject", max_len=60)
    kind = v.choice(merged, "kind", KINDS, "study")
    start = v.local_datetime(merged, "start_at", required=True)
    end = v.local_datetime(merged, "end_at", required=True)
    if end <= start:
        raise v.ValidationError("End time must be after start time")
    if _parse(end) - _parse(start) > dt.timedelta(hours=16):
        raise v.ValidationError("An event can be at most 16 hours long")
    notes = v.text(merged, "notes", max_len=2000)
    completed = int(bool(merged.get("completed", 0)))
    return dict(title=title, subject=subject, kind=kind, start_at=start, end_at=end,
                notes=notes, completed=completed)


def _with_focus(db, events):
    """Attach the Focus Score of sessions run for each event."""
    ids = [e["id"] for e in events]
    if not ids:
        return events
    marks = ",".join("?" * len(ids))
    rows = db.execute(
        f"""SELECT schedule_event_id AS eid, AVG(focus_score) AS score, SUM(total_s) AS secs, COUNT(*) AS n
            FROM study_sessions WHERE user_id = ? AND status = 'ended' AND schedule_event_id IN ({marks})
            GROUP BY schedule_event_id""", (_uid(), *ids)).fetchall()
    by = {r["eid"]: dict(r) for r in rows}
    for e in events:
        s = by.get(e["id"])
        e["focus"] = {"score": s["score"], "seconds": s["secs"], "sessions": s["n"]} if s else None
    return events


@bp.get("/events")
@login_required
def list_events():
    start = request.args.get("start", "0000")
    end = request.args.get("end", "9999")
    db = get_db()
    rows = db.execute(
        "SELECT * FROM schedule_events WHERE user_id = ? AND start_at < ? AND end_at > ? ORDER BY start_at",
        (_uid(), end, start)).fetchall()
    return jsonify(events=_with_focus(db, [row_dict(r) for r in rows]))


@bp.post("/events")
@login_required
def create_event():
    d = request.get_json(silent=True) or {}
    f = _event_fields(d)
    repeat = v.integer(d, "repeat_weekly", lo=0, hi=26, default=0)
    db = get_db()
    group = uuid.uuid4().hex if repeat else None
    created, conflicts = [], []
    for week in range(repeat + 1):
        shift = dt.timedelta(weeks=week)
        s, e = _iso(_parse(f["start_at"]) + shift), _iso(_parse(f["end_at"]) + shift)
        conflicts += _conflicts(db, s, e)
        cur = db.execute(
            """INSERT INTO schedule_events (user_id, title, subject, kind, start_at, end_at, notes,
               completed, recurrence_group, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (_uid(), f["title"], f["subject"], f["kind"], s, e, f["notes"], 0, group, now_iso()))
        created.append(cur.lastrowid)
    db.commit()
    rows = [row_dict(db.execute("SELECT * FROM schedule_events WHERE id = ?", (i,)).fetchone()) for i in created]
    return jsonify(events=rows, conflicts=conflicts), 201


def _own_event(eid):
    return get_db().execute("SELECT * FROM schedule_events WHERE id = ? AND user_id = ?",
                            (eid, _uid())).fetchone()


@bp.put("/events/<int:eid>")
@login_required
def update_event(eid):
    row = _own_event(eid)
    if not row:
        return jsonify(error="Event not found."), 404
    f = _event_fields(request.get_json(silent=True) or {}, row_dict(row))
    db = get_db()
    db.execute("""UPDATE schedule_events SET title=?, subject=?, kind=?, start_at=?, end_at=?, notes=?,
                  completed=? WHERE id = ?""",
               (f["title"], f["subject"], f["kind"], f["start_at"], f["end_at"], f["notes"], f["completed"], eid))
    db.commit()
    return jsonify(event=row_dict(_own_event(eid)),
                   conflicts=_conflicts(db, f["start_at"], f["end_at"], exclude_ids=(eid,)))


@bp.delete("/events/<int:eid>")
@login_required
def delete_event(eid):
    row = _own_event(eid)
    if not row:
        return jsonify(error="Event not found."), 404
    db = get_db()
    if request.args.get("scope") == "series" and row["recurrence_group"]:
        n = db.execute("DELETE FROM schedule_events WHERE user_id = ? AND recurrence_group = ? AND start_at >= ?",
                       (_uid(), row["recurrence_group"], row["start_at"])).rowcount
    else:
        n = db.execute("DELETE FROM schedule_events WHERE id = ?", (eid,)).rowcount
    db.commit()
    return jsonify(deleted=n)


# ---------------------------------------------------------------- tasks

def _task_fields(d, existing=None):
    merged = {**(existing or {}), **d}
    return dict(
        title=v.text(merged, "title", required=True, max_len=160),
        subject=v.text(merged, "subject", max_len=60),
        due_at=v.local_datetime(merged, "due_at"),
        priority=v.choice(merged, "priority", PRIORITIES, "medium"),
        estimated_min=v.integer(merged, "estimated_min", lo=5, hi=6000),
        done=int(bool(merged.get("done", 0))),
    )


def _own_task(tid):
    return get_db().execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (tid, _uid())).fetchone()


@bp.get("/tasks")
@login_required
def list_tasks():
    rows = get_db().execute(
        """SELECT * FROM tasks WHERE user_id = ?
           ORDER BY done, CASE WHEN due_at IS NULL THEN 1 ELSE 0 END, due_at,
           CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END""", (_uid(),)).fetchall()
    return jsonify(tasks=[row_dict(r) for r in rows])


@bp.post("/tasks")
@login_required
def create_task():
    f = _task_fields(request.get_json(silent=True) or {})
    db = get_db()
    cur = db.execute(
        "INSERT INTO tasks (user_id, title, subject, due_at, priority, estimated_min, done, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (_uid(), f["title"], f["subject"], f["due_at"], f["priority"], f["estimated_min"], 0, now_iso()))
    db.commit()
    return jsonify(task=row_dict(_own_task(cur.lastrowid))), 201


@bp.put("/tasks/<int:tid>")
@login_required
def update_task(tid):
    row = _own_task(tid)
    if not row:
        return jsonify(error="Task not found."), 404
    f = _task_fields(request.get_json(silent=True) or {}, row_dict(row))
    db = get_db()
    db.execute("UPDATE tasks SET title=?, subject=?, due_at=?, priority=?, estimated_min=?, done=? WHERE id=?",
               (f["title"], f["subject"], f["due_at"], f["priority"], f["estimated_min"], f["done"], tid))
    db.commit()
    return jsonify(task=row_dict(_own_task(tid)))


@bp.delete("/tasks/<int:tid>")
@login_required
def delete_task(tid):
    if not _own_task(tid):
        return jsonify(error="Task not found."), 404
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (tid,))
    db.commit()
    return jsonify(ok=True)


def _hhmm(d, key, default):
    s = d.get(key, default)
    try:
        h, m = map(int, str(s).split(":"))
        return dt.time(h, m)
    except (ValueError, TypeError):
        raise v.ValidationError(f"{key} must look like 16:00")


def find_free_slots(busy, now, until, block, day_start, day_end, max_per_day):
    """Greedy planner. busy: list of (start, end) datetimes. Returns slots."""
    slots, day = [], now.date()
    while day <= until.date():
        window_s = max(dt.datetime.combine(day, day_start), now)
        window_e = min(dt.datetime.combine(day, day_end), until)
        cursor, per_day = window_s, 0
        # round up to the next quarter hour
        if cursor.minute % 15 or cursor.second:
            cursor = cursor.replace(second=0, microsecond=0) + dt.timedelta(minutes=15 - cursor.minute % 15)
        while cursor + block <= window_e and per_day < max_per_day:
            clash = [b for b in busy if b[0] < cursor + block and b[1] > cursor]
            if clash:
                cursor = max(b[1] for b in clash)
                continue
            slots.append((cursor, cursor + block))
            busy.append((cursor, cursor + block))
            per_day += 1
            cursor += block + dt.timedelta(minutes=15)  # breathing room between blocks
        day += dt.timedelta(days=1)
    return slots


@bp.post("/tasks/<int:tid>/plan")
@login_required
def plan_task(tid):
    """Split a task's estimated time into study blocks placed in free time before it is due."""
    row = _own_task(tid)
    if not row:
        return jsonify(error="Task not found."), 404
    if not row["estimated_min"]:
        return jsonify(error="Add an estimated time to this task first."), 400
    d = request.get_json(silent=True) or {}
    now = _parse(v.local_datetime(d, "now", required=True))
    block_min = v.integer(d, "block_min", lo=15, hi=180, default=50)
    max_per_day = v.integer(d, "max_per_day", lo=1, hi=6, default=2)
    day_start, day_end = _hhmm(d, "day_start", "16:00"), _hhmm(d, "day_end", "21:00")
    if day_end <= day_start:
        raise v.ValidationError("day_end must be after day_start")
    until = _parse(row["due_at"]) if row["due_at"] else now + dt.timedelta(days=7)
    if until <= now:
        return jsonify(error="This task is already past its due time."), 400
    db = get_db()
    busy = [(_parse(r["start_at"]), _parse(r["end_at"])) for r in db.execute(
        "SELECT start_at, end_at FROM schedule_events WHERE user_id = ? AND end_at > ? AND start_at < ?",
        (_uid(), _iso(now), _iso(until)))]
    n_blocks = -(-row["estimated_min"] // block_min)
    slots = find_free_slots(busy, now, until, dt.timedelta(minutes=block_min),
                            day_start, day_end, max_per_day)[:n_blocks]
    group = uuid.uuid4().hex
    created = []
    for i, (s, e) in enumerate(slots, 1):
        cur = db.execute(
            """INSERT INTO schedule_events (user_id, title, subject, kind, start_at, end_at, notes,
               completed, recurrence_group, created_at) VALUES (?,?,?,?,?,?,?,0,?,?)""",
            (_uid(), f"{row['title']} ({i}/{n_blocks})", row["subject"], "study", _iso(s), _iso(e),
             f"Auto-planned for task #{tid}", group, now_iso()))
        created.append(row_dict(db.execute("SELECT * FROM schedule_events WHERE id = ?", (cur.lastrowid,)).fetchone()))
    db.commit()
    return jsonify(events=created, requested_blocks=n_blocks, placed_blocks=len(created),
                   warning=None if len(created) == n_blocks else
                   f"Only found room for {len(created)} of {n_blocks} blocks before the due date."), 201


@bp.get("/overview")
@login_required
def overview():
    """Today's agenda, next block, and this week's planned vs completed study time."""
    today = request.args.get("date") or dt.date.today().isoformat()
    try:
        day = dt.date.fromisoformat(today)
    except ValueError:
        raise v.ValidationError("date must be YYYY-MM-DD")
    week_start = day - dt.timedelta(days=day.weekday())
    week_end = week_start + dt.timedelta(days=7)
    db = get_db()
    todays = [row_dict(r) for r in db.execute(
        "SELECT * FROM schedule_events WHERE user_id = ? AND start_at < ? AND end_at > ? ORDER BY start_at",
        (_uid(), (day + dt.timedelta(days=1)).isoformat(), day.isoformat()))]
    week = db.execute(
        "SELECT start_at, end_at, completed FROM schedule_events WHERE user_id = ? AND kind = 'study' AND start_at >= ? AND start_at < ?",
        (_uid(), week_start.isoformat(), week_end.isoformat())).fetchall()
    planned = sum((_parse(r["end_at"]) - _parse(r["start_at"])).seconds / 60 for r in week)
    done = sum((_parse(r["end_at"]) - _parse(r["start_at"])).seconds / 60 for r in week if r["completed"])
    due = [row_dict(r) for r in db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND done = 0 AND due_at IS NOT NULL AND due_at < ? ORDER BY due_at LIMIT 10",
        (_uid(), (day + dt.timedelta(days=7)).isoformat()))]
    return jsonify(today=_with_focus(db, todays), due_soon=due,
                   week={"start": week_start.isoformat(), "planned_study_min": planned,
                         "completed_study_min": done})
'''

# ===== backend/schema.sql ====================================================
FILES['backend/schema.sql'] = r'''PRAGMA foreign_keys = ON;

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
    notes             TEXT NOT NULL DEFAULT ''
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
'''

# ===== backend/security.py ===================================================
FILES['backend/security.py'] = r'''"""Security helpers: CSRF protection, login rate limiting, auth decorator, headers."""

import functools
import hmac
import secrets
import threading
import time

from flask import jsonify, request, session

CSRF_HEADER = "X-CSRF-Token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def check_csrf():
    """Called before every API request. State-changing requests must echo the
    per-session token in a header (double-submit pattern)."""
    if request.method in SAFE_METHODS or not request.path.startswith("/api/"):
        return None
    sent = request.headers.get(CSRF_HEADER, "")
    expected = session.get("csrf", "")
    if not expected or not hmac.compare_digest(sent, expected):
        return jsonify(error="Missing or invalid CSRF token. Reload the page and try again."), 403
    return None


class RateLimiter:
    """Counts failures per key in a sliding window (in-memory, single process)."""

    def __init__(self, max_failures=5, window_s=900):
        self.max, self.window = max_failures, window_s
        self._hits = {}
        self._lock = threading.Lock()

    def _prune(self, key, now):
        self._hits[key] = [t for t in self._hits.get(key, []) if now - t < self.window]

    def blocked(self, key):
        with self._lock:
            now = time.time()
            self._prune(key, now)
            return len(self._hits[key]) >= self.max

    def fail(self, key):
        with self._lock:
            now = time.time()
            self._prune(key, now)
            self._hits[key].append(now)

    def reset(self, key):
        with self._lock:
            self._hits.pop(key, None)


login_limiter = RateLimiter()


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(error="Please sign in."), 401
        return view(*args, **kwargs)
    return wrapped


CSP = "; ".join([
    "default-src 'self'",
    # MediaPipe is served locally (frontend/vendor); WebAssembly needs wasm-unsafe-eval.
    "script-src 'self' 'wasm-unsafe-eval'",
    "connect-src 'self'",
    "img-src 'self' data: blob:",
    "media-src 'self' blob:",
    "style-src 'self'",
    "font-src 'self'",
    "worker-src 'self' blob:",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
])


def apply_security_headers(resp):
    resp.headers.setdefault("Content-Security-Policy", CSP)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    resp.headers.setdefault("Permissions-Policy", "camera=(self), microphone=(), geolocation=()")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp
'''

# ===== backend/sessions_api.py ===============================================
FILES['backend/sessions_api.py'] = r'''"""Study sessions: calibration, streaming feature frames through the engine,
history. The browser sends only numeric face features (never video)."""

import json
import threading

from flask import Blueprint, jsonify, request, session

from neurofocus_engine import (AttentionEngine, Calibration, DEFAULT_PARAMS, ENGINE_VERSION,
                               FOCUSED, FeatureFrame, LiveScore, calibrate,
                               default_calibration)
from neurofocus_engine.scoring import MAX_FRAME_GAP_S

from .db import get_db, now_iso, row_dict
from .security import login_required
from . import validation as v

bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

MAX_FRAMES_PER_BATCH = 600
MAX_CAL_FRAMES = 1200

# Live engine objects, keyed by session id. Rebuilt from the database if the
# server restarts mid-session, so the database stays the source of truth.
_runtime = {}
_runtime_lock = threading.Lock()


class _Runtime:
    def __init__(self, cal, params):
        self.engine = AttentionEngine(cal, params)
        self.live = LiveScore(params)
        self.lock = threading.Lock()


def _own_session(sid):
    row = get_db().execute("SELECT * FROM study_sessions WHERE id = ? AND user_id = ?",
                           (sid, session["user_id"])).fetchone()
    return row


def _not_found():
    return jsonify(error="Session not found."), 404


def _session_payload(row):
    d = row_dict(row)
    d["calibration"] = json.loads(d.pop("calibration_json") or "null")
    d.pop("params_json", None)
    d.pop("filter_state_json", None)
    return d


def _get_runtime(row):
    with _runtime_lock:
        rt = _runtime.get(row["id"])
        if rt is None:
            cal_d = json.loads(row["calibration_json"] or "null")
            cal = Calibration.from_dict(cal_d) if cal_d else default_calibration()
            rt = _Runtime(cal, DEFAULT_PARAMS)
            fs = json.loads(row["filter_state_json"] or "null")
            if fs:
                f = rt.engine.filter
                f.state, f._cand, f._cand_since = fs["state"], fs["cand"], fs["cand_since"]
            for s in get_db().execute(
                    "SELECT second, state FROM session_samples WHERE session_id = ? AND second >= ? ORDER BY second",
                    (row["id"], int(row["last_t"]) - int(DEFAULT_PARAMS.live_window_s))):
                rt.live.add(float(s["second"]), s["state"])
            _runtime[row["id"]] = rt
        return rt


@bp.post("")
@login_required
def create():
    d = request.get_json(silent=True) or {}
    title = v.text(d, "title", max_len=120) or "Study session"
    subject = v.text(d, "subject", max_len=60)
    event_id = d.get("schedule_event_id")
    db = get_db()
    if event_id is not None:
        ev = db.execute("SELECT id FROM schedule_events WHERE id = ? AND user_id = ?",
                        (event_id, session["user_id"])).fetchone()
        if not ev:
            return jsonify(error="Schedule block not found."), 404
    cur = db.execute(
        """INSERT INTO study_sessions (user_id, title, subject, schedule_event_id, status, started_at,
           engine_version, params_json) VALUES (?,?,?,?, 'calibrating', ?, ?, ?)""",
        (session["user_id"], title, subject, event_id, now_iso(), ENGINE_VERSION,
         json.dumps(DEFAULT_PARAMS.to_dict())))
    db.commit()
    return jsonify(session=_session_payload(_own_session(cur.lastrowid))), 201


def _parse_frames(raw, limit):
    if not isinstance(raw, list):
        raise v.ValidationError("frames must be a list")
    if len(raw) > limit:
        raise v.ValidationError(f"at most {limit} frames per request")
    frames = []
    for item in raw:
        if not isinstance(item, dict):
            raise v.ValidationError("each frame must be an object")
        try:
            fr = FeatureFrame.from_dict(item)
        except ValueError as e:
            raise v.ValidationError(str(e))
        if not (0 <= fr.t < 24 * 3600):
            raise v.ValidationError("frame time out of range")
        frames.append(fr)
    frames.sort(key=lambda f: f.t)
    return frames


@bp.post("/<int:sid>/calibration")
@login_required
def submit_calibration(sid):
    row = _own_session(sid)
    if not row:
        return _not_found()
    if row["status"] == "ended":
        return jsonify(error="Session already ended."), 409
    d = request.get_json(silent=True) or {}
    if d.get("skip"):
        cal, ok = default_calibration(), True
    else:
        phases = d.get("phases")
        if not isinstance(phases, dict):
            raise v.ValidationError("phases is required (or skip: true)")
        by_phase = {}
        for name in ("center", "corners", "down"):
            by_phase[name] = _parse_frames(phases.get(name, []), MAX_CAL_FRAMES)
        cal, ok = calibrate(by_phase)
        if not ok and not d.get("accept_anyway"):
            return jsonify(ok=False, calibration=cal.to_dict()), 200
    db = get_db()
    db.execute("UPDATE study_sessions SET calibration_json = ?, calibrated = ?, status = 'active' WHERE id = ?",
               (json.dumps(cal.to_dict()), int(cal.calibrated), sid))
    db.commit()
    with _runtime_lock:
        _runtime.pop(sid, None)
    return jsonify(ok=True, calibration=cal.to_dict())


@bp.post("/<int:sid>/frames")
@login_required
def push_frames(sid):
    row = _own_session(sid)
    if not row:
        return _not_found()
    if row["status"] != "active":
        return jsonify(error="Session is not active (calibrate first, or it has ended)."), 409
    d = request.get_json(silent=True) or {}
    frames = _parse_frames(d.get("frames", []), MAX_FRAMES_PER_BATCH)
    rt = _get_runtime(row)
    db = get_db()
    with rt.lock:
        row = _own_session(sid)  # re-read counters under the lock
        last_t, focused_s, total_s = row["last_t"], row["focused_s"], row["total_s"]
        distractions = row["distraction_count"]
        fs = json.loads(row["filter_state_json"] or "null") or {}
        prev_state = fs.get("last_state")
        has_prev = prev_state is not None
        raw_s = state = prev_state or FOCUSED
        live = None
        samples = {}
        for fr in frames:
            if has_prev and fr.t <= last_t:
                continue  # duplicate or out-of-order frame
            raw_s, state = rt.engine.process(fr)
            if has_prev:
                gap = min(fr.t - last_t, MAX_FRAME_GAP_S)
                total_s += gap
                if prev_state == FOCUSED:
                    focused_s += gap
            if state != prev_state:
                if prev_state not in (None, FOCUSED):
                    db.execute("UPDATE session_episodes SET end_t = ? WHERE session_id = ? AND end_t IS NULL",
                               (fr.t, sid))
                if state != FOCUSED:
                    db.execute("INSERT INTO session_episodes (session_id, state, start_t) VALUES (?,?,?)",
                               (sid, state, fr.t))
                    if prev_state in (None, FOCUSED):
                        distractions += 1
            live = rt.live.add(fr.t, state)
            samples[int(fr.t)] = (state, live)
            prev_state, last_t, has_prev = state, fr.t, True
        db.executemany(
            """INSERT INTO session_samples (session_id, second, state, live_score) VALUES (?,?,?,?)
               ON CONFLICT(session_id, second) DO UPDATE SET state = excluded.state, live_score = excluded.live_score""",
            [(sid, sec, st, sc) for sec, (st, sc) in samples.items()])
        f = rt.engine.filter
        fs = {"state": f.state, "cand": f._cand, "cand_since": f._cand_since, "last_state": prev_state}
        score = 100 * focused_s / total_s if total_s > 0 else None
        db.execute("""UPDATE study_sessions SET last_t = ?, focused_s = ?, total_s = ?, focus_score = ?,
                      distraction_count = ?, filter_state_json = ? WHERE id = ?""",
                   (last_t, focused_s, total_s, score, distractions, json.dumps(fs), sid))
        db.commit()
        ep = db.execute("SELECT state, start_t FROM session_episodes WHERE session_id = ? AND end_t IS NULL",
                        (sid,)).fetchone()
    return jsonify(state=state, raw_state=raw_s, live_score=live, session_score=score,
                   focused_s=focused_s, total_s=total_s, distraction_count=distractions,
                   current_episode=row_dict(ep), t=last_t)


@bp.post("/<int:sid>/end")
@login_required
def end(sid):
    row = _own_session(sid)
    if not row:
        return _not_found()
    d = request.get_json(silent=True) or {}
    notes = v.text(d, "notes", max_len=2000, default=row["notes"])
    db = get_db()
    db.execute("UPDATE session_episodes SET end_t = ? WHERE session_id = ? AND end_t IS NULL",
               (row["last_t"], sid))
    score = 100 * row["focused_s"] / row["total_s"] if row["total_s"] > 0 else None
    db.execute("UPDATE study_sessions SET status = 'ended', ended_at = ?, focus_score = ?, notes = ? WHERE id = ?",
               (row["ended_at"] or now_iso(), score, notes, sid))
    if d.get("complete_event") and row["schedule_event_id"]:
        db.execute("UPDATE schedule_events SET completed = 1 WHERE id = ? AND user_id = ?",
                   (row["schedule_event_id"], session["user_id"]))
    db.commit()
    with _runtime_lock:
        _runtime.pop(sid, None)
    return jsonify(session=_session_payload(_own_session(sid)))


@bp.get("")
@login_required
def list_sessions():
    limit = min(max(int(request.args.get("limit", 50)), 1), 200)
    offset = max(int(request.args.get("offset", 0)), 0)
    rows = get_db().execute(
        "SELECT * FROM study_sessions WHERE user_id = ? ORDER BY started_at DESC LIMIT ? OFFSET ?",
        (session["user_id"], limit, offset)).fetchall()
    total = get_db().execute("SELECT COUNT(*) FROM study_sessions WHERE user_id = ?",
                             (session["user_id"],)).fetchone()[0]
    return jsonify(sessions=[_session_payload(r) for r in rows], total=total)


@bp.get("/<int:sid>")
@login_required
def detail(sid):
    row = _own_session(sid)
    if not row:
        return _not_found()
    db = get_db()
    samples = [dict(r) for r in db.execute(
        "SELECT second, state, live_score FROM session_samples WHERE session_id = ? ORDER BY second", (sid,))]
    episodes = [dict(r) for r in db.execute(
        "SELECT state, start_t, end_t FROM session_episodes WHERE session_id = ? ORDER BY start_t", (sid,))]
    by_state = {}
    for e in episodes:
        dur = (e["end_t"] if e["end_t"] is not None else row["last_t"]) - e["start_t"]
        b = by_state.setdefault(e["state"], {"count": 0, "seconds": 0.0})
        b["count"] += 1
        b["seconds"] += max(dur, 0)
    return jsonify(session=_session_payload(row), samples=samples, episodes=episodes,
                   distraction_breakdown=by_state)


@bp.patch("/<int:sid>")
@login_required
def update(sid):
    row = _own_session(sid)
    if not row:
        return _not_found()
    d = request.get_json(silent=True) or {}
    title = v.text(d, "title", max_len=120, default=row["title"]) or row["title"]
    subject = v.text(d, "subject", max_len=60, default=row["subject"])
    notes = v.text(d, "notes", max_len=2000, default=row["notes"])
    db = get_db()
    db.execute("UPDATE study_sessions SET title = ?, subject = ?, notes = ? WHERE id = ?",
               (title, subject, notes, sid))
    db.commit()
    return jsonify(session=_session_payload(_own_session(sid)))


@bp.delete("/<int:sid>")
@login_required
def delete(sid):
    row = _own_session(sid)
    if not row:
        return _not_found()
    db = get_db()
    db.execute("DELETE FROM study_sessions WHERE id = ?", (sid,))
    db.commit()
    with _runtime_lock:
        _runtime.pop(sid, None)
    return jsonify(ok=True)
'''

# ===== backend/validation.py =================================================
FILES['backend/validation.py'] = r'''import datetime as dt
import re


class ValidationError(ValueError):
    pass


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def text(d, key, *, required=False, max_len=200, default=""):
    v = d.get(key, default)
    if v is None:
        v = default
    if not isinstance(v, str):
        raise ValidationError(f"{key} must be text")
    v = v.strip()
    if required and not v:
        raise ValidationError(f"{key} is required")
    if len(v) > max_len:
        raise ValidationError(f"{key} must be at most {max_len} characters")
    return v


def choice(d, key, options, default):
    v = d.get(key, default)
    if v not in options:
        raise ValidationError(f"{key} must be one of: {', '.join(options)}")
    return v


def integer(d, key, *, lo, hi, default=None, required=False):
    v = d.get(key, default)
    if v is None or v == "":
        if required:
            raise ValidationError(f"{key} is required")
        return default
    try:
        v = int(v)
    except (TypeError, ValueError):
        raise ValidationError(f"{key} must be a whole number")
    if not lo <= v <= hi:
        raise ValidationError(f"{key} must be between {lo} and {hi}")
    return v


def local_datetime(d, key, *, required=False):
    """Accepts 'YYYY-MM-DDTHH:MM' (local wall-clock time, as from <input type=datetime-local>)."""
    v = d.get(key)
    if not v:
        if required:
            raise ValidationError(f"{key} is required")
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(v))
    except ValueError:
        raise ValidationError(f"{key} must be a date and time")
    return parsed.replace(tzinfo=None, second=0, microsecond=0).isoformat(timespec="minutes")


def email(d, key="email"):
    v = text(d, key, required=True, max_len=254).lower()
    if not EMAIL_RE.match(v):
        raise ValidationError("Enter a valid email address")
    return v


def password(d, key="password"):
    v = d.get(key)
    if not isinstance(v, str) or len(v) < 10:
        raise ValidationError("Password must be at least 10 characters")
    if len(v) > 200:
        raise ValidationError("Password is too long")
    if v.isalpha() or v.isdigit():
        raise ValidationError("Password must mix letters with numbers or symbols")
    return v
'''

# ===== frontend/analytics.html ===============================================
FILES['frontend/analytics.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Analytics · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/analytics.js"></script>
</head>
<body>
<div class="shell">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="main">
    <div class="page-head">
      <div>
        <button class="btn ghost small menu-btn" id="menuBtn" aria-label="Menu"></button>
        <h1>Analytics</h1>
        <p id="note"></p>
      </div>
      <div class="tabs" id="rangeTabs" role="tablist">
        <button data-days="7">7 days</button><button data-days="30" class="active">30 days</button><button data-days="90">90 days</button>
      </div>
    </div>
    <div class="grid cols-4">
      <div class="card stat"><div class="label">Focus Score</div><div class="value" id="tScore">–</div><div class="sub">time-weighted</div></div>
      <div class="card stat"><div class="label">Focused time</div><div class="value" id="tFocused">–</div><div class="sub" id="tTotal"></div></div>
      <div class="card stat"><div class="label">Sessions</div><div class="value" id="tSessions">–</div></div>
      <div class="card stat"><div class="label">Distractions / hour</div><div class="value" id="tRate">–</div></div>
    </div>
    <div class="grid cols-2">
      <div class="card span-2"><div class="card-head"><h2>Daily Focus Score</h2></div><div id="dailyScore"></div></div>
      <div class="card"><div class="card-head"><h2>Focused minutes per day</h2></div><div id="dailyMin"></div></div>
      <div class="card"><div class="card-head"><h2>Focus Score by start hour</h2></div><div id="byHour"></div></div>
      <div class="card"><div class="card-head"><h2>By subject</h2></div><div class="table-wrap"><table><thead><tr><th>Subject</th><th>Sessions</th><th>Hours</th><th>Score</th></tr></thead><tbody id="bySubject"></tbody></table></div></div>
      <div class="card"><div class="card-head"><h2>Distraction types</h2></div><div id="breakdown"></div></div>
    </div>
  </main>
</div>
</body>
</html>
'''

# ===== frontend/css/app.css ==================================================
FILES['frontend/css/app.css'] = r'''/* NeuroFocus AI — design tokens and components. No inline styles are used
   anywhere (the Content-Security-Policy forbids them). */

:root {
  --bg: #f6f7fb;
  --surface: #ffffff;
  --surface-2: #f0f2f8;
  --border: #e2e6ef;
  --text: #141a2a;
  --text-2: #4f5a72;
  --text-3: #7c869c;
  --brand: #4f46e5;
  --brand-2: #6366f1;
  --brand-soft: #eef0ff;
  --focus: #16a34a;
  --away: #ea580c;
  --down: #d97706;
  --closed: #9333ea;
  --absent: #64748b;
  --danger: #dc2626;
  --danger-soft: #fee2e2;
  --warn-soft: #fff7e6;
  --ok-soft: #e8f8ee;
  --radius: 14px;
  --radius-sm: 9px;
  --shadow: 0 1px 2px rgba(16, 24, 40, .05), 0 4px 16px rgba(16, 24, 40, .06);
  --font: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  color-scheme: light;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0d111b;
    --surface: #151b29;
    --surface-2: #1c2435;
    --border: #2a3448;
    --text: #e8ecf5;
    --text-2: #aab3c7;
    --text-3: #7d879d;
    --brand: #818cf8;
    --brand-2: #a5b4fc;
    --brand-soft: #23284a;
    --focus: #4ade80;
    --away: #fb923c;
    --down: #fbbf24;
    --closed: #c084fc;
    --absent: #94a3b8;
    --danger: #f87171;
    --danger-soft: #3b1d22;
    --warn-soft: #3a2f17;
    --ok-soft: #173326;
    --shadow: 0 1px 2px rgba(0, 0, 0, .3), 0 4px 16px rgba(0, 0, 0, .25);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0d111b; --surface: #151b29; --surface-2: #1c2435; --border: #2a3448;
  --text: #e8ecf5; --text-2: #aab3c7; --text-3: #7d879d; --brand: #818cf8; --brand-2: #a5b4fc;
  --brand-soft: #23284a; --focus: #4ade80; --away: #fb923c; --down: #fbbf24; --closed: #c084fc;
  --absent: #94a3b8; --danger: #f87171; --danger-soft: #3b1d22; --warn-soft: #3a2f17; --ok-soft: #173326;
  --shadow: 0 1px 2px rgba(0, 0, 0, .3), 0 4px 16px rgba(0, 0, 0, .25);
  color-scheme: dark;
}

* { box-sizing: border-box; }
html, body { margin: 0; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--brand); text-decoration: none; }
a:hover { text-decoration: underline; }
h1, h2, h3, h4 { margin: 0 0 .4em; line-height: 1.25; letter-spacing: -.01em; }
h1 { font-size: 1.6rem; }
h2 { font-size: 1.2rem; }
h3 { font-size: 1.02rem; }
p { margin: 0 0 .8em; }
code, .mono { font-family: var(--mono); font-size: .9em; }
.hidden { display: none !important; }
.muted { color: var(--text-2); }
.small { font-size: .86rem; }
.tiny { font-size: .76rem; color: var(--text-3); }
.center { text-align: center; }
.row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.row.between { justify-content: space-between; }
.stack > * + * { margin-top: 12px; }
.grow { flex: 1; }

/* ---------- App shell ---------- */
.shell { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }
.sidebar {
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 20px 14px;
  position: sticky; top: 0; height: 100vh;
  display: flex; flex-direction: column; gap: 4px;
}
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1.08rem; padding: 4px 10px 18px; color: var(--text); }
.brand:hover { text-decoration: none; }
.brand-mark {
  width: 32px; height: 32px; border-radius: 10px;
  background: linear-gradient(135deg, var(--brand), #22c55e);
  display: grid; place-items: center; color: #fff; font-size: 16px;
}
.nav a {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px; border-radius: var(--radius-sm);
  color: var(--text-2); font-weight: 500;
}
.nav a:hover { background: var(--surface-2); text-decoration: none; color: var(--text); }
.nav a.active { background: var(--brand-soft); color: var(--brand); }
.nav svg { width: 18px; height: 18px; flex: none; }
.nav-section { font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; color: var(--text-3); padding: 14px 12px 4px; }
.sidebar-foot { margin-top: auto; padding: 12px; border-top: 1px solid var(--border); }
.main { padding: 28px 36px 60px; max-width: 1240px; width: 100%; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 22px; flex-wrap: wrap; }
.page-head p { margin: 0; color: var(--text-2); }
.menu-btn { display: none; }

@media (max-width: 860px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar { position: fixed; z-index: 30; left: 0; width: 260px; transform: translateX(-100%); transition: transform .2s; }
  .sidebar.open { transform: none; box-shadow: var(--shadow); }
  .main { padding: 16px 16px 60px; }
  .menu-btn { display: inline-flex; }
}

/* ---------- Cards & grid ---------- */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow);
  min-width: 0;
}
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; gap: 10px; }
.card-head h2, .card-head h3 { margin: 0; }
.grid { display: grid; gap: 16px; }
.grid.cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid.cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid.cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.span-2 { grid-column: span 2; }
@media (max-width: 1000px) { .grid.cols-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .grid.cols-3 { grid-template-columns: 1fr 1fr; } }
@media (max-width: 680px) { .grid.cols-2, .grid.cols-3, .grid.cols-4 { grid-template-columns: 1fr; } .span-2 { grid-column: auto; } }

.stat .label { color: var(--text-2); font-size: .82rem; font-weight: 500; }
.stat .value { font-size: 1.75rem; font-weight: 700; letter-spacing: -.02em; margin-top: 2px; }
.stat .sub { color: var(--text-3); font-size: .8rem; }

/* ---------- Buttons & forms ---------- */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  border: 1px solid var(--border); background: var(--surface); color: var(--text);
  padding: 9px 16px; border-radius: var(--radius-sm); font: inherit; font-weight: 600;
  cursor: pointer; transition: background .15s, border-color .15s, transform .05s;
  text-decoration: none;
}
.btn:hover { background: var(--surface-2); text-decoration: none; }
.btn:active { transform: translateY(1px); }
.btn:disabled { opacity: .55; cursor: not-allowed; }
.btn.primary { background: var(--brand); border-color: var(--brand); color: #fff; }
.btn.primary:hover { background: var(--brand-2); }
.btn.danger { color: var(--danger); border-color: var(--danger); }
.btn.danger:hover { background: var(--danger-soft); }
.btn.ghost { border-color: transparent; background: transparent; }
.btn.small { padding: 5px 10px; font-size: .84rem; }
.btn.big { padding: 13px 24px; font-size: 1.02rem; }
:focus-visible { outline: 3px solid color-mix(in srgb, var(--brand) 50%, transparent); outline-offset: 2px; }

label { display: block; font-weight: 600; font-size: .86rem; margin-bottom: 5px; color: var(--text-2); }
input, select, textarea {
  width: 100%; padding: 9px 12px; border-radius: var(--radius-sm);
  border: 1px solid var(--border); background: var(--surface); color: var(--text); font: inherit;
}
textarea { min-height: 80px; resize: vertical; }
input:focus, select:focus, textarea:focus { border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--brand-soft); }
input[type="checkbox"] { width: auto; }
.field { margin-bottom: 14px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 560px) { .field-row { grid-template-columns: 1fr; } }
.check { display: flex; gap: 8px; align-items: center; font-weight: 500; color: var(--text); }

.alert { padding: 10px 14px; border-radius: var(--radius-sm); font-size: .9rem; margin-bottom: 12px; border: 1px solid transparent; }
.alert.error { background: var(--danger-soft); color: var(--danger); border-color: color-mix(in srgb, var(--danger) 30%, transparent); }
.alert.warn { background: var(--warn-soft); border-color: color-mix(in srgb, var(--down) 35%, transparent); }
.alert.ok { background: var(--ok-soft); border-color: color-mix(in srgb, var(--focus) 35%, transparent); }
.alert.info { background: var(--brand-soft); border-color: color-mix(in srgb, var(--brand) 25%, transparent); }

.badge { display: inline-flex; align-items: center; gap: 6px; padding: 2px 9px; border-radius: 999px; font-size: .76rem; font-weight: 600; background: var(--surface-2); color: var(--text-2); white-space: nowrap; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; background: currentColor; }
.s-FOCUSED { color: var(--focus); }
.s-LOOKING_AWAY { color: var(--away); }
.s-LOOKING_DOWN { color: var(--down); }
.s-EYES_CLOSED { color: var(--closed); }
.s-ABSENT { color: var(--absent); }
.bg-FOCUSED { background: var(--focus); }
.bg-LOOKING_AWAY { background: var(--away); }
.bg-LOOKING_DOWN { background: var(--down); }
.bg-EYES_CLOSED { background: var(--closed); }
.bg-ABSENT { background: var(--absent); }
.k-study { --k: var(--brand); }
.k-class { --k: #0891b2; }
.k-exam { --k: var(--danger); }
.k-break { --k: var(--focus); }
.k-other { --k: var(--absent); }

/* ---------- Tables / lists ---------- */
table { width: 100%; border-collapse: collapse; font-size: .9rem; }
th { text-align: left; color: var(--text-3); font-weight: 600; font-size: .76rem; text-transform: uppercase; letter-spacing: .04em; padding: 8px 10px; border-bottom: 1px solid var(--border); }
td { padding: 10px; border-bottom: 1px solid var(--border); vertical-align: middle; }
tr:last-child td { border-bottom: 0; }
tr.clickable { cursor: pointer; }
tr.clickable:hover td { background: var(--surface-2); }
.table-wrap { overflow-x: auto; }
.list { list-style: none; margin: 0; padding: 0; }
.list li { padding: 10px 0; border-bottom: 1px solid var(--border); display: flex; gap: 10px; align-items: center; }
.list li:last-child { border-bottom: 0; }
.empty { text-align: center; color: var(--text-3); padding: 26px 10px; }

/* ---------- Toast & modal ---------- */
.toast-host { position: fixed; bottom: 20px; right: 20px; z-index: 100; display: flex; flex-direction: column; gap: 8px; }
.toast { background: var(--text); color: var(--bg); padding: 10px 16px; border-radius: var(--radius-sm); box-shadow: var(--shadow); font-size: .9rem; max-width: 360px; }
.toast.error { background: var(--danger); color: #fff; }
dialog { border: 1px solid var(--border); border-radius: var(--radius); padding: 0; background: var(--surface); color: var(--text); width: min(560px, calc(100vw - 32px)); box-shadow: var(--shadow); }
dialog::backdrop { background: rgba(10, 14, 25, .5); }
.dialog-body { padding: 20px 22px; }
.dialog-foot { padding: 14px 22px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }

/* ---------- Charts ---------- */
.chart { width: 100%; display: block; overflow: visible; }
.chart text { fill: var(--text-3); font-size: 11px; font-family: var(--font); }
.chart .grid-line { stroke: var(--border); stroke-width: 1; }
.chart .axis { stroke: var(--border); }
.chart .line { fill: none; stroke: var(--brand); stroke-width: 2.2; stroke-linejoin: round; stroke-linecap: round; }
.chart .area { fill: var(--brand); opacity: .12; }
.chart .bar { fill: var(--brand); }
.chart .bar.alt { fill: var(--focus); }
.chart .bar-bg { fill: var(--surface-2); }
.chart .pt { fill: var(--brand); }
.legend { display: flex; flex-wrap: wrap; gap: 14px; font-size: .8rem; color: var(--text-2); margin-top: 8px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.timeline { display: flex; height: 26px; border-radius: 6px; overflow: hidden; background: var(--surface-2); }
.timeline div { height: 100%; }
.meter { height: 8px; background: var(--surface-2); border-radius: 99px; overflow: hidden; }
.meter > div { height: 100%; background: var(--brand); border-radius: 99px; width: 0; transition: width .4s; }

/* ---------- Auth & landing ---------- */
.auth-wrap { min-height: 100vh; display: grid; place-items: center; padding: 24px 16px; }
.auth-card { width: min(420px, 100%); }
.auth-card .brand { justify-content: center; padding-bottom: 8px; }
.landing { max-width: 1080px; margin: 0 auto; padding: 22px 20px 60px; }
.landing-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 50px; }
.hero { display: grid; grid-template-columns: 1.1fr .9fr; gap: 40px; align-items: center; margin-bottom: 60px; }
.hero h1 { font-size: clamp(2rem, 4.4vw, 3.1rem); letter-spacing: -.03em; }
.hero .lead { font-size: 1.12rem; color: var(--text-2); }
.hero-visual { aspect-ratio: 1 / 1; border-radius: 24px; background: radial-gradient(circle at 30% 30%, var(--brand-soft), transparent 60%), var(--surface); border: 1px solid var(--border); display: grid; place-items: center; box-shadow: var(--shadow); }
@media (max-width: 800px) { .hero { grid-template-columns: 1fr; } .hero-visual { max-width: 340px; margin: 0 auto; width: 100%; } }
.feature-icon { width: 38px; height: 38px; border-radius: 10px; background: var(--brand-soft); color: var(--brand); display: grid; place-items: center; margin-bottom: 10px; }
.feature-icon svg { width: 20px; height: 20px; }
.disclaimer { border-left: 4px solid var(--down); background: var(--warn-soft); padding: 14px 18px; border-radius: var(--radius-sm); font-size: .92rem; }

/* ---------- Session page ---------- */
.session-grid { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 16px; }
@media (max-width: 980px) { .session-grid { grid-template-columns: 1fr; } }
.video-box { position: relative; border-radius: var(--radius); overflow: hidden; background: #0b0f19; aspect-ratio: 4 / 3; }
.video-box video, .video-box canvas { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
.video-box .overlay-msg { position: absolute; inset: 0; display: grid; place-items: center; color: #cbd5e1; text-align: center; padding: 20px; }
.video-box.privacy video { filter: blur(18px) brightness(.7); }
.cal-target { position: absolute; width: 34px; height: 34px; border-radius: 50%; border: 3px solid #fff; background: var(--brand); box-shadow: 0 0 0 6px rgba(79, 70, 229, .35); transform: translate(-50%, -50%); transition: left .35s, top .35s; z-index: 5; }
.cal-stage { position: fixed; inset: 0; z-index: 50; background: var(--bg); display: grid; place-items: center; }
.cal-stage .cal-instructions { max-width: 520px; text-align: center; padding: 20px; }
.cal-progress { width: 260px; margin: 16px auto 0; }
.state-pill { display: inline-flex; align-items: center; gap: 10px; padding: 10px 18px; border-radius: 999px; font-weight: 700; font-size: 1.05rem; background: var(--surface-2); }
.state-pill .dot { width: 12px; height: 12px; }
.ring { width: 170px; height: 170px; display: block; margin: 0 auto; }
.ring .track { stroke: var(--surface-2); }
.ring .val { stroke: var(--focus); transition: stroke-dashoffset .5s; }
.ring text { fill: var(--text); font-weight: 700; font-family: var(--font); }
.ring .ring-sub { fill: var(--text-3); font-weight: 500; font-size: 11px; }
.feature-readout { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; font-family: var(--mono); font-size: .8rem; }
.feature-readout div { background: var(--surface-2); padding: 6px 8px; border-radius: 6px; }

/* ---------- Schedule ---------- */
.week { display: grid; grid-template-columns: 52px repeat(7, minmax(0, 1fr)); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: var(--surface); }
.week-scroll { overflow-x: auto; }
.week-inner { min-width: 760px; }
.week-head { display: contents; }
.week-head div { padding: 8px 6px; text-align: center; font-size: .8rem; font-weight: 600; border-bottom: 1px solid var(--border); background: var(--surface-2); }
.week-head .today { color: var(--brand); }
.hours { position: relative; }
.hours div { height: 44px; font-size: .7rem; color: var(--text-3); text-align: right; padding-right: 6px; transform: translateY(-7px); }
.day-col { position: relative; border-left: 1px solid var(--border); cursor: crosshair; }
.day-col .slot { height: 44px; border-bottom: 1px dashed var(--border); }
.day-col.today { background: color-mix(in srgb, var(--brand-soft) 45%, transparent); }
.ev { position: absolute; left: 3px; right: 3px; border-radius: 7px; padding: 3px 6px; font-size: .74rem; overflow: hidden; cursor: pointer; background: color-mix(in srgb, var(--k) 16%, var(--surface)); border-left: 3px solid var(--k); color: var(--text); line-height: 1.25; }
.ev:hover { filter: brightness(1.05); box-shadow: var(--shadow); }
.ev.done { opacity: .6; }
.ev.done .ev-title { text-decoration: line-through; }
.ev-title { font-weight: 600; }
.now-line { position: absolute; left: 0; right: 0; height: 2px; background: var(--danger); z-index: 3; }
.task-item { display: flex; gap: 10px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid var(--border); }
.task-item:last-child { border-bottom: 0; }
.task-item.done .task-title { text-decoration: line-through; color: var(--text-3); }
.prio-high { color: var(--danger); }
.prio-medium { color: var(--down); }
.prio-low { color: var(--text-3); }
.tabs { display: inline-flex; background: var(--surface-2); border-radius: var(--radius-sm); padding: 3px; gap: 2px; }
.tabs button { border: 0; background: transparent; padding: 6px 14px; border-radius: 7px; font: inherit; font-weight: 600; color: var(--text-2); cursor: pointer; }
.tabs button.active { background: var(--surface); color: var(--text); box-shadow: var(--shadow); }

/* ---------- Research page ---------- */
.prose { max-width: 820px; }
.prose h2 { margin-top: 1.6em; }
.prose li { margin-bottom: .35em; }
.formula { font-family: var(--mono); background: var(--surface-2); padding: 12px 14px; border-radius: var(--radius-sm); overflow-x: auto; font-size: .88rem; }
.compare { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 700px) { .compare { grid-template-columns: 1fr; } }
.row.centered { justify-content: center; }
.cal-stage.running .cal-instructions { transform: translateY(130px); }
.kdot { color: var(--k); flex: none; }
.btn svg { width: 18px; height: 18px; flex: none; }
.grid + .grid, .grid + .card, .card + .grid { margin-top: 16px; }
.schedule-layout { display: grid; grid-template-columns: minmax(0, 1fr) 330px; gap: 16px; align-items: start; }
@media (max-width: 1100px) { .schedule-layout { grid-template-columns: 1fr; } }
.week-inner { min-width: 640px; }
.btn.menu-btn { display: none; }
@media (max-width: 860px) { .btn.menu-btn { display: inline-flex; } }
.card > h2:first-child, .card > h3:first-child { margin-top: 0; }
'''

# ===== frontend/dashboard.html ===============================================
FILES['frontend/dashboard.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/dashboard.js"></script>
</head>
<body>
<div class="shell">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="main">
    <div class="page-head">
      <div>
        <button class="btn ghost small menu-btn" id="menuBtn" aria-label="Menu"></button>
        <h1 id="greeting">Dashboard</h1>
        <p id="dateLabel"></p>
      </div>
      <a class="btn primary big" href="/session">Start focus session</a>
    </div>
    <div class="grid cols-4">
      <div class="card stat"><div class="label">Focused today</div><div class="value" id="todayMin">–</div>
        <div class="meter" id="goalMeter"><div></div></div><div class="sub" id="goalLabel"></div></div>
      <div class="card stat"><div class="label">Focus Score (7 days)</div><div class="value" id="weekScore">–</div><div class="sub">time-weighted across sessions</div></div>
      <div class="card stat"><div class="label">Study streak</div><div class="value" id="streak">–</div><div class="sub">days in a row</div></div>
      <div class="card stat"><div class="label">Study blocks this week</div><div class="value" id="weekPlan">–</div><div class="sub" id="weekPlanSub"></div></div>
    </div>
    <div class="grid cols-3" id="dashMain">
      <div class="card span-2">
        <div class="card-head"><h2>Focus Score, last 14 days</h2><a class="small" href="/analytics">Analytics →</a></div>
        <div id="trend"></div>
      </div>
      <div class="card">
        <div class="card-head"><h2>Today</h2><a class="small" href="/schedule">Schedule →</a></div>
        <ul class="list" id="todayList"></ul>
      </div>
      <div class="card span-2">
        <div class="card-head"><h2>Recent sessions</h2><a class="small" href="/history">All →</a></div>
        <div class="table-wrap"><table><thead><tr><th>Session</th><th>When</th><th>Length</th><th>Score</th></tr></thead><tbody id="recent"></tbody></table></div>
      </div>
      <div class="card">
        <div class="card-head"><h2>Due soon</h2></div>
        <ul class="list" id="dueList"></ul>
      </div>
    </div>
  </main>
</div>
</body>
</html>
'''

# ===== frontend/history.html =================================================
FILES['frontend/history.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>History · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/history.js"></script>
</head>
<body>
<div class="shell">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="main">
    <div class="page-head">
      <div>
        <button class="btn ghost small menu-btn" id="menuBtn" aria-label="Menu"></button>
        <h1>Session history</h1>
        <p>Every session you have recorded. Select one for its full timeline.</p>
      </div>
    </div>
    <section id="listView" class="card">
      <div class="table-wrap"><table>
        <thead><tr><th>Session</th><th>Subject</th><th>Started</th><th>Length</th><th>Calibrated</th><th>Distractions</th><th>Score</th></tr></thead>
        <tbody id="rows"></tbody>
      </table></div>
      <div class="row between"><span class="tiny" id="pageLabel"></span>
        <div class="row"><button class="btn small" id="prevBtn">Previous</button><button class="btn small" id="nextBtn">Next</button></div></div>
    </section>
    <section id="detailView" class="hidden stack">
      <a href="/history" class="small">← All sessions</a>
      <div class="grid cols-3">
        <div class="card center"><div id="detailRing"></div></div>
        <div class="card span-2">
          <div class="card-head"><h2 id="dTitle"></h2><span class="badge" id="dStatus"></span></div>
          <div class="grid cols-3">
            <div class="stat"><div class="label">Length</div><div class="value" id="dLen"></div></div>
            <div class="stat"><div class="label">Focused</div><div class="value" id="dFocused"></div></div>
            <div class="stat"><div class="label">Distractions</div><div class="value" id="dDis"></div></div>
          </div>
          <p class="small muted" id="dMeta"></p>
          <p class="small muted" id="dCal"></p>
        </div>
      </div>
      <div class="card">
        <div class="card-head"><h3>Attention timeline</h3><span class="tiny" id="dTimeLabel"></span></div>
        <div id="dTimeline"></div>
        <div class="legend" id="dLegend"></div>
      </div>
      <div class="grid cols-2">
        <div class="card"><div class="card-head"><h3>Rolling Focus Score (60 s window)</h3></div><div id="dLive"></div></div>
        <div class="card"><div class="card-head"><h3>Time by distraction type</h3></div><div id="dBreakdown"></div></div>
      </div>
      <div class="card">
        <div class="card-head"><h3>Notes</h3></div>
        <div class="field"><label for="dTitleInput">Title</label><input id="dTitleInput" maxlength="120"></div>
        <div class="field"><label for="dSubjectInput">Subject</label><input id="dSubjectInput" maxlength="60"></div>
        <textarea id="dNotes" maxlength="2000"></textarea>
        <div class="row between"><button class="btn primary small" id="saveNotes">Save</button><button class="btn danger small" id="deleteBtn">Delete session</button></div>
      </div>
    </section>
  </main>
</div>
</body>
</html>
'''

# ===== frontend/index.html ===================================================
FILES['frontend/index.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NeuroFocus AI</title>
  <meta name="description" content="A webcam-based study-focus tracker with a transparent, testable attention engine.">
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/landing.js"></script>
</head>
<body>
<div class="landing">
  <nav class="landing-nav">
    <a class="brand" href="/"><span class="brand-mark">◎</span>NeuroFocus AI</a>
    <div class="row" id="navActions">
      <a class="btn ghost" href="/login">Sign in</a>
      <a class="btn primary" href="/register">Create account</a>
    </div>
  </nav>

  <section class="hero">
    <div>
      <span class="badge">Science-fair engineering project</span>
      <h1>See how focused your study time really is.</h1>
      <p class="lead">NeuroFocus AI uses your webcam and on-device computer vision to estimate when you are looking at your work, then turns it into a transparent Focus Score, session history and a study schedule that adapts to you.</p>
      <div class="row">
        <a class="btn primary big" href="/register">Get started</a>
        <a class="btn big" href="/research">How it is tested</a>
      </div>
    </div>
    <div class="hero-visual" aria-hidden="true">
      <svg viewBox="0 0 200 200" width="70%">
        <circle cx="100" cy="100" r="78" fill="none" stroke="currentColor" stroke-opacity=".12" stroke-width="14"/>
        <circle cx="100" cy="100" r="78" fill="none" stroke="#16a34a" stroke-width="14" stroke-linecap="round" stroke-dasharray="490" stroke-dashoffset="98" transform="rotate(-90 100 100)"/>
        <text x="100" y="108" text-anchor="middle" font-size="40" font-weight="700" fill="currentColor">80</text>
        <text x="100" y="130" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".6">example score</text>
      </svg>
    </div>
  </section>

  <section class="grid cols-3">
    <div class="card"><div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.5"/></svg></div>
      <h3>Private by design</h3><p class="muted small">Face landmarks are computed in your browser. The server receives six numbers per frame (head angles, eye openness, iris position), never images or video.</p></div>
    <div class="card"><div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg></div>
      <h3>Personal calibration</h3><p class="muted small">A 30-second calibration learns where your screen is relative to your camera, so a laptop off to the side does not look like "looking away".</p></div>
    <div class="card"><div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg></div>
      <h3>Schedule that plans for you</h3><p class="muted small">Add classes, exams and assignments. NeuroFocus finds free time before each deadline and books study blocks, then links each block to the Focus Score you achieved.</p></div>
  </section>

  <section class="card" id="honest">
    <h2>What the Focus Score is, and what it is not</h2>
    <div class="compare">
      <div>
        <h3 class="s-FOCUSED">It is</h3>
        <ul class="small">
          <li>The percentage of session time your head and eyes were classified as pointing at your screen.</li>
          <li>Computed by a documented, rule-based algorithm whose accuracy is measured in a reproducible simulation experiment.</li>
          <li>A study aid that helps you notice patterns (time of day, subject, distraction type).</li>
        </ul>
      </div>
      <div>
        <h3 class="s-LOOKING_AWAY">It is not</h3>
        <ul class="small">
          <li>A measure of learning, understanding or effort.</li>
          <li>A medical device. It does not diagnose or screen for ADHD or any other condition.</li>
          <li>Validated on real students yet. Current accuracy figures come from simulated "virtual students" (see Research &amp; Method).</li>
        </ul>
      </div>
    </div>
  </section>
  <p class="tiny center">NeuroFocus AI · student engineering research project</p>
</div>
</body>
</html>
'''

# ===== frontend/js/analytics.js ==============================================
FILES['frontend/js/analytics.js'] = r'''import { api } from "./api.js";
import { lineChart, barChart } from "./charts.js";
import { $, $$, esc, mountShell, fmtScore, scoreClass, STATE_LABEL, tzOffsetMin } from "./ui.js";

await mountShell("analytics");

async function load(days) {
  const a = await api(`/api/analytics/summary?days=${days}&tz_offset_min=${tzOffsetMin()}`);
  $("#note").textContent = a.note;
  $("#tScore").textContent = fmtScore(a.totals.focus_score);
  $("#tScore").className = `value ${scoreClass(a.totals.focus_score)}`;
  $("#tFocused").textContent = `${a.totals.focused_hours.toFixed(1)} h`;
  $("#tTotal").textContent = `of ${a.totals.total_hours.toFixed(1)} h tracked`;
  $("#tSessions").textContent = a.totals.sessions;
  $("#tRate").textContent = a.totals.total_hours ? (a.totals.distractions / a.totals.total_hours).toFixed(1) : "–";
  const label = (d) => new Date(d + "T12:00").toLocaleDateString(undefined, { month: "short", day: "numeric" });
  lineChart($("#dailyScore"), a.daily.map((d) => ({ label: label(d.date), value: d.score })));
  barChart($("#dailyMin"), a.daily.map((d) => ({ label: label(d.date), value: d.focused_s / 60 })), { unit: "", alt: true });
  const hours = Array.from({ length: 24 }, (_, h) => a.by_hour.find((x) => x.hour === h));
  const first = hours.findIndex(Boolean), last = 23 - [...hours].reverse().findIndex(Boolean);
  barChart($("#byHour"), first < 0 ? [] : hours.slice(first, last + 1).map((x, i) => ({
    label: `${first + i}:00`, value: x?.score || 0,
    title: x ? `${first + i}:00 · score ${Math.round(x.score)} · ${x.sessions} sessions` : "no sessions",
  })), { yMax: 100 });
  $("#bySubject").innerHTML = a.by_subject.length ? a.by_subject.map((s) => `
    <tr><td>${esc(s.subject)}</td><td>${s.sessions}</td><td>${s.hours.toFixed(1)}</td>
    <td><strong class="${scoreClass(s.score)}">${fmtScore(s.score)}</strong></td></tr>`).join("")
    : '<tr><td colspan="4" class="empty">No sessions in this range.</td></tr>';
  const br = a.distraction_breakdown;
  barChart($("#breakdown"), ["LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT"].map((k) => ({
    label: STATE_LABEL[k], value: (br[k]?.seconds || 0) / 60, title: `${STATE_LABEL[k]}: ${br[k]?.count || 0} episodes`,
  })), { unit: "m" });
}

$("#rangeTabs").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  $$("#rangeTabs button").forEach((x) => x.classList.toggle("active", x === b));
  load(Number(b.dataset.days));
});
load(30);
'''

# ===== frontend/js/api.js ====================================================
FILES['frontend/js/api.js'] = r'''// Fetch wrapper: JSON in/out, CSRF header on state-changing requests, auth guard.

let csrf = null;

async function ensureCsrf() {
  if (!csrf) {
    const r = await fetch("/api/auth/csrf", { credentials: "same-origin" });
    csrf = (await r.json()).csrf;
  }
  return csrf;
}

export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

export async function api(path, { method = "GET", body } = {}) {
  const headers = { Accept: "application/json" };
  if (method !== "GET") {
    headers["X-CSRF-Token"] = await ensureCsrf();
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(path, {
    method,
    headers,
    credentials: "same-origin",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  let data = {};
  try { data = await res.json(); } catch { /* empty body */ }
  if (data && data.csrf) csrf = data.csrf;
  if (!res.ok) {
    if (res.status === 401 && !location.pathname.match(/^\/(login|register)?$/)) {
      location.href = `/login?next=${encodeURIComponent(location.pathname + location.search)}`;
    }
    throw new ApiError(data.error || `Request failed (${res.status})`, res.status, data);
  }
  return data;
}

let userPromise = null;
export function requireUser() {
  if (!userPromise) userPromise = api("/api/auth/me").then((d) => d.user);
  return userPromise;
}

export async function logout() {
  await api("/api/auth/logout", { method: "POST" });
  location.href = "/";
}
'''

# ===== frontend/js/auth.js ===================================================
FILES['frontend/js/auth.js'] = r'''import { api } from "./api.js";
import { $, showError } from "./ui.js";

const next = new URLSearchParams(location.search).get("next");
const dest = next && next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard";

async function submit(form, path, body) {
  $("#error").classList.add("hidden");
  $("#submitBtn").disabled = true;
  try {
    await api(path, { method: "POST", body });
    location.href = dest;
  } catch (e) {
    showError($("#error"), e);
  } finally {
    $("#submitBtn").disabled = false;
  }
}

$("#loginForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  submit(e.target, "/api/auth/login", { email: $("#email").value, password: $("#password").value });
});

$("#registerForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!$("#agree").checked) return showError($("#error"), { message: "Please confirm you understand NeuroFocus is not a diagnostic tool." });
  submit(e.target, "/api/auth/register", {
    display_name: $("#name").value, email: $("#email").value, password: $("#password").value,
  });
});
'''

# ===== frontend/js/charts.js =================================================
FILES['frontend/js/charts.js'] = r'''// Small dependency-free SVG charts. Rendered at the container's pixel width
// and re-rendered on resize. Colours come from CSS classes (theme-aware).

import { esc, STATE_LABEL } from "./ui.js";

const PAD = { l: 34, r: 10, t: 10, b: 26 };
const renderers = new Map();
window.addEventListener("resize", () => renderers.forEach((fn) => fn()));

function mount(el, draw) {
  const fn = () => { el.innerHTML = draw(Math.max(el.clientWidth, 260)); };
  renderers.set(el, fn);
  fn();
}

function yTicks(max) {
  const step = max <= 10 ? 2 : max <= 50 ? 10 : max <= 100 ? 25 : Math.ceil(max / 4 / 10) * 10;
  const out = [];
  for (let v = 0; v <= max + 1e-9; v += step) out.push(v);
  return out;
}

/** points: [{label, value|null}] */
export function lineChart(el, points, { height = 220, yMax = 100, unit = "" } = {}) {
  if (!points.some((p) => p.value != null)) {
    el.innerHTML = '<div class="empty">No data yet</div>';
    renderers.delete(el);
    return;
  }
  mount(el, (W) => {
    const iw = W - PAD.l - PAD.r, ih = height - PAD.t - PAD.b;
    const x = (i) => PAD.l + (points.length === 1 ? iw / 2 : (i * iw) / (points.length - 1));
    const y = (v) => PAD.t + ih - (v / yMax) * ih;
    const grid = yTicks(yMax).map((v) =>
      `<line class="grid-line" x1="${PAD.l}" x2="${W - PAD.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${PAD.l - 6}" y="${y(v) + 4}" text-anchor="end">${v}${unit}</text>`).join("");
    const every = Math.ceil(points.length / Math.max(2, Math.floor(iw / 60)));
    const xl = points.map((p, i) => (i % every === 0 || (i === points.length - 1 && i % every >= every * 0.75))
      ? `<text x="${x(i)}" y="${height - 6}" text-anchor="middle">${esc(p.label)}</text>` : "").join("");
    // break the line where values are missing
    let d = "", area = "", seg = [];
    const flush = () => {
      if (!seg.length) return;
      d += "M" + seg.map(([i, v]) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("L");
      area += `M${x(seg[0][0])},${y(0)}L` + seg.map(([i, v]) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("L") + `L${x(seg[seg.length - 1][0])},${y(0)}Z`;
      seg = [];
    };
    points.forEach((p, i) => (p.value == null ? flush() : seg.push([i, Math.min(p.value, yMax)])));
    flush();
    const dots = points.length <= 40 ? points.map((p, i) => p.value == null ? "" :
      `<circle class="pt" cx="${x(i)}" cy="${y(Math.min(p.value, yMax))}" r="3"><title>${esc(p.label)}: ${Math.round(p.value)}${unit}</title></circle>`).join("") : "";
    return `<svg class="chart" width="${W}" height="${height}" role="img">${grid}<path class="area" d="${area}"/><path class="line" d="${d}"/>${dots}${xl}</svg>`;
  });
}

/** items: [{label, value, title?}] */
export function barChart(el, items, { height = 200, yMax, unit = "", alt = false } = {}) {
  if (!items.length || !items.some((i) => i.value)) {
    el.innerHTML = '<div class="empty">No data yet</div>';
    renderers.delete(el);
    return;
  }
  const max = yMax ?? (Math.max(...items.map((i) => i.value || 0)) * 1.15 || 1);
  mount(el, (W) => {
    const iw = W - PAD.l - PAD.r, ih = height - PAD.t - PAD.b;
    const bw = iw / items.length;
    const y = (v) => PAD.t + ih - (v / max) * ih;
    const grid = yTicks(max).filter((v) => v <= max).map((v) =>
      `<line class="grid-line" x1="${PAD.l}" x2="${W - PAD.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${PAD.l - 6}" y="${y(v) + 4}" text-anchor="end">${Math.round(v)}${unit}</text>`).join("");
    const every = Math.ceil(items.length / Math.max(2, Math.floor(iw / 44)));
    const bars = items.map((it, i) => {
      const v = it.value || 0, bx = PAD.l + i * bw + bw * 0.18, w = bw * 0.64;
      const label = i % every === 0 ? `<text x="${PAD.l + i * bw + bw / 2}" y="${height - 6}" text-anchor="middle">${esc(it.label)}</text>` : "";
      return `<rect class="bar ${alt ? "alt" : ""}" x="${bx}" y="${y(v)}" width="${w}" height="${Math.max(0, y(0) - y(v))}" rx="3"><title>${esc(it.title || `${it.label}: ${Math.round(v)}${unit}`)}</title></rect>${label}`;
    }).join("");
    return `<svg class="chart" width="${W}" height="${height}" role="img">${grid}${bars}</svg>`;
  });
}

/** Coloured strip of attention states. samples: [{second, state}] */
export function timeline(el, samples) {
  el.className = "timeline";
  el.innerHTML = "";
  if (!samples.length) return;
  const total = samples[samples.length - 1].second - samples[0].second + 1;
  let runStart = 0;
  for (let i = 1; i <= samples.length; i++) {
    if (i === samples.length || samples[i].state !== samples[runStart].state) {
      const end = i === samples.length ? samples[i - 1].second + 1 : samples[i].second;
      const div = document.createElement("div");
      div.className = `bg-${samples[runStart].state}`;
      div.style.width = `${(100 * (end - samples[runStart].second)) / total}%`;
      div.title = `${STATE_LABEL[samples[runStart].state]} · ${end - samples[runStart].second}s`;
      el.append(div);
      runStart = i;
    }
  }
}

/** Circular score gauge (0-100). */
export function ring(el, value, sub = "Focus Score") {
  const r = 70, c = 2 * Math.PI * r;
  const v = value == null ? 0 : Math.max(0, Math.min(100, value));
  el.innerHTML = `<svg class="ring" viewBox="0 0 170 170" role="img" aria-label="${sub} ${value == null ? "not available" : Math.round(v)}">
    <circle class="track" cx="85" cy="85" r="${r}" fill="none" stroke-width="13"/>
    <circle class="val" cx="85" cy="85" r="${r}" fill="none" stroke-width="13" stroke-linecap="round"
      stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - v / 100)}" transform="rotate(-90 85 85)"/>
    <text x="85" y="90" text-anchor="middle" font-size="38">${value == null ? "–" : Math.round(v)}</text>
    <text class="ring-sub" x="85" y="114" text-anchor="middle">${esc(sub)}</text></svg>`;
}
'''

# ===== frontend/js/dashboard.js ==============================================
FILES['frontend/js/dashboard.js'] = r'''import { api } from "./api.js";
import { lineChart } from "./charts.js";
import { $, esc, mountShell, fmtDuration, fmtScore, fmtDateTime, fmtTime, scoreClass, localDate, tzOffsetMin } from "./ui.js";

const user = await mountShell("dashboard");
const hour = new Date().getHours();
$("#greeting").textContent = `${hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening"}, ${user.display_name.split(" ")[0]}`;
$("#dateLabel").textContent = new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });

const [week, two, overview, recent] = await Promise.all([
  api(`/api/analytics/summary?days=7&tz_offset_min=${tzOffsetMin()}`),
  api(`/api/analytics/summary?days=14&tz_offset_min=${tzOffsetMin()}`),
  api(`/api/schedule/overview?date=${localDate()}`),
  api("/api/sessions?limit=6"),
]);

const t = week.today;
$("#todayMin").textContent = `${Math.round(t.focused_min)} min`;
$("#goalMeter").firstElementChild.style.width = `${Math.min(100, (100 * t.focused_min) / t.goal_min)}%`;
$("#goalLabel").textContent = `goal ${t.goal_min} min`;
$("#weekScore").textContent = fmtScore(week.totals.focus_score);
$("#weekScore").className = `value ${scoreClass(week.totals.focus_score)}`;
$("#streak").textContent = week.streak_days;
$("#weekPlan").textContent = `${Math.round(overview.week.completed_study_min / 60 * 10) / 10}h`;
$("#weekPlanSub").textContent = `done of ${Math.round(overview.week.planned_study_min / 60 * 10) / 10}h planned`;

lineChart($("#trend"), two.daily.map((d) => ({
  label: new Date(d.date + "T12:00").toLocaleDateString(undefined, { month: "short", day: "numeric" }),
  value: d.score,
})));

const tl = $("#todayList");
tl.innerHTML = overview.today.length ? overview.today.map((e) => `
  <li class="k-${e.kind}"><span class="dot kdot"></span>
    <div class="grow"><div class="small"><strong>${esc(e.title)}</strong></div>
    <div class="tiny">${fmtTime(e.start_at)}–${fmtTime(e.end_at)} · ${esc(e.kind)}${e.focus ? ` · score ${fmtScore(e.focus.score)}` : ""}</div></div>
    ${e.kind === "study" && !e.completed ? `<a class="btn small" href="/session?event=${e.id}">Start</a>` : e.completed ? '<span class="badge s-FOCUSED">done</span>' : ""}
  </li>`).join("") : '<li class="empty">Nothing scheduled today. <a href="/schedule">Plan a study block</a></li>';

$("#dueList").innerHTML = overview.due_soon.length ? overview.due_soon.map((task) => `
  <li><div class="grow"><div class="small"><strong>${esc(task.title)}</strong></div>
  <div class="tiny">due ${fmtDateTime(task.due_at)}${task.subject ? ` · ${esc(task.subject)}` : ""}</div></div>
  <span class="badge prio-${task.priority}">${task.priority}</span></li>`).join("") : '<li class="empty">No deadlines in the next 7 days.</li>';

$("#recent").innerHTML = recent.sessions.length ? recent.sessions.map((s) => `
  <tr class="clickable" data-id="${s.id}"><td><strong>${esc(s.title)}</strong><div class="tiny">${esc(s.subject)}</div></td>
  <td class="small">${fmtDateTime(s.started_at)}</td><td class="small">${fmtDuration(s.total_s)}</td>
  <td><strong class="${scoreClass(s.focus_score)}">${fmtScore(s.focus_score)}</strong></td></tr>`).join("")
  : '<tr><td colspan="4" class="empty">No sessions yet. <a href="/session">Start your first one</a></td></tr>';
$("#recent").addEventListener("click", (e) => {
  const tr = e.target.closest("tr[data-id]");
  if (tr) location.href = `/history?id=${tr.dataset.id}`;
});
'''

# ===== frontend/js/history.js ================================================
FILES['frontend/js/history.js'] = r'''import { api } from "./api.js";
import { lineChart, barChart, ring, timeline } from "./charts.js";
import { $, esc, mountShell, fmtClock, fmtDuration, fmtScore, fmtDateTime, scoreClass, STATE_LABEL, toast, confirmDialog } from "./ui.js";

await mountShell("history");
const id = new URLSearchParams(location.search).get("id");
const PAGE = 20;
let offset = 0;

async function loadList() {
  const { sessions, total } = await api(`/api/sessions?limit=${PAGE}&offset=${offset}`);
  $("#rows").innerHTML = sessions.length ? sessions.map((s) => `
    <tr class="clickable" data-id="${s.id}">
      <td><strong>${esc(s.title)}</strong>${s.status !== "ended" ? ' <span class="badge">unfinished</span>' : ""}</td>
      <td class="small">${esc(s.subject) || "–"}</td>
      <td class="small">${fmtDateTime(s.started_at)}</td>
      <td class="small">${fmtDuration(s.total_s)}</td>
      <td class="small">${s.calibrated ? "yes" : "no"}</td>
      <td class="small">${s.distraction_count}</td>
      <td><strong class="${scoreClass(s.focus_score)}">${fmtScore(s.focus_score)}</strong></td>
    </tr>`).join("") : '<tr><td colspan="7" class="empty">No sessions recorded yet.</td></tr>';
  $("#pageLabel").textContent = total ? `${offset + 1}–${Math.min(offset + PAGE, total)} of ${total}` : "";
  $("#prevBtn").disabled = offset === 0;
  $("#nextBtn").disabled = offset + PAGE >= total;
}

$("#rows").addEventListener("click", (e) => {
  const tr = e.target.closest("tr[data-id]");
  if (tr) location.href = `/history?id=${tr.dataset.id}`;
});
$("#prevBtn").addEventListener("click", () => { offset = Math.max(0, offset - PAGE); loadList(); });
$("#nextBtn").addEventListener("click", () => { offset += PAGE; loadList(); });

async function loadDetail() {
  $("#listView").classList.add("hidden");
  $("#detailView").classList.remove("hidden");
  const d = await api(`/api/sessions/${id}`);
  const s = d.session;
  ring($("#detailRing"), s.focus_score, "Focus Score");
  $("#dTitle").textContent = s.title;
  $("#dStatus").textContent = s.status;
  $("#dLen").textContent = fmtDuration(s.total_s);
  $("#dFocused").textContent = fmtDuration(s.focused_s);
  $("#dDis").textContent = s.distraction_count;
  $("#dMeta").textContent = `${fmtDateTime(s.started_at)}${s.subject ? ` · ${s.subject}` : ""} · engine v${s.engine_version}`;
  const c = s.calibration;
  $("#dCal").textContent = !c ? "Not calibrated." : c.calibrated
    ? `Calibrated (${c.quality}): away beyond ±${c.yaw_threshold.toFixed(0)}°, down beyond ${c.pitch_down_threshold.toFixed(0)}°.`
    : "Ran with population-default thresholds (no personal calibration).";
  timeline($("#dTimeline"), d.samples);
  $("#dTimeLabel").textContent = `${d.samples.length} s`;
  $("#dLegend").innerHTML = Object.entries(STATE_LABEL).map(([k, v]) => `<span><i class="dot s-${k}"></i>${v}</span>`).join("");
  const step = Math.max(1, Math.floor(d.samples.length / 300));
  lineChart($("#dLive"), d.samples.filter((_, i) => i % step === 0).map((x) => ({
    label: fmtClock(x.second), value: x.live_score,
  })));
  const br = d.distraction_breakdown;
  barChart($("#dBreakdown"), ["LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT"].map((k) => ({
    label: STATE_LABEL[k], value: (br[k]?.seconds || 0) / 60,
    title: `${STATE_LABEL[k]}: ${br[k]?.count || 0} times, ${fmtDuration(br[k]?.seconds || 0)}`,
  })), { unit: "m" });
  $("#dTitleInput").value = s.title;
  $("#dSubjectInput").value = s.subject;
  $("#dNotes").value = s.notes;
}

$("#saveNotes").addEventListener("click", async () => {
  try {
    await api(`/api/sessions/${id}`, { method: "PATCH", body: { title: $("#dTitleInput").value, subject: $("#dSubjectInput").value, notes: $("#dNotes").value } });
    toast("Saved");
    $("#dTitle").textContent = $("#dTitleInput").value;
  } catch (e) { toast(e.message, "error"); }
});
$("#deleteBtn").addEventListener("click", async () => {
  if (!(await confirmDialog("Delete this session and all of its data? This cannot be undone."))) return;
  await api(`/api/sessions/${id}`, { method: "DELETE" });
  location.href = "/history";
});

if (id) loadDetail().catch((e) => { toast(e.message, "error"); });
else loadList();
'''

# ===== frontend/js/landing.js ================================================
FILES['frontend/js/landing.js'] = r'''// If already signed in, swap the landing-page buttons for a dashboard link.
try {
  const r = await fetch("/api/auth/status", { credentials: "same-origin" });
  if ((await r.json()).signed_in) document.getElementById("navActions").innerHTML = '<a class="btn primary" href="/dashboard">Open dashboard</a>';
} catch { /* offline: keep defaults */ }
'''

# ===== frontend/js/research.js ===============================================
FILES['frontend/js/research.js'] = r'''import { $, esc, mountShell } from "./ui.js";

// Public page: use the app shell when signed in, otherwise a simple layout.
const status = await (await fetch("/api/auth/status", { credentials: "same-origin" })).json();
if (status.signed_in) await mountShell("research");
else {
  $("#sidebar").remove();
  $("#shell").classList.remove("shell");
  $("#publicHome").classList.remove("hidden");
}

const fmt = (x, n = 3) => (x == null || Number.isNaN(x) ? "n/a" : Number(x).toFixed(n));

const { version, params } = await (await fetch("/api/engine/params")).json();
const rows = [
  ["Engine version", version],
  ["Default 'looking away' threshold (no calibration)", `±${params.default_yaw_threshold_deg}°`],
  ["Default 'looking down' threshold (no calibration)", `${params.default_pitch_down_threshold_deg}°`],
  ["Calibrated away threshold", `widest corner look + ${params.yaw_margin_deg}°, limited to ${params.yaw_threshold_bounds.join("–")}°`],
  ["Calibrated down threshold", `lowest corner look + ${params.pitch_margin_deg}°, limited to ${params.pitch_threshold_bounds.join("–")}°`],
  ["Eyes-closed threshold", `EAR < ${params.ear_closed_ratio} × personal open-eye EAR`],
  ["Iris offset to degrees", `${params.gaze_to_deg}° per unit`],
  ["Onset times", Object.entries(params.onset_s).map(([k, v]) => `${k.replace("_", " ").toLowerCase()} ${v} s`).join(", ")],
  ["Recovery time", `${params.recovery_s} s`],
  ["Live score window", `${params.live_window_s} s`],
];
$("#paramsTable").innerHTML = rows.map(([k, v]) => `<tr><td class="small">${esc(k)}</td><td class="small mono">${esc(v)}</td></tr>`).join("");

const { runs } = await (await fetch("/api/research/runs")).json();
const official = runs.filter((r) => !r.smoke_test);
const box = $("#results");
if (!official.length) {
  box.innerHTML = `<p class="small">No official experiment run has been recorded yet. Run
    <code>python -m research.pipeline.run_experiment --config research/config/experiment_v1.json</code>
    and the results will appear here automatically.</p>`;
} else {
  box.innerHTML = official.map((r) => {
    const p = r.statistics.primary;
    const table = p ? `
      <p class="small">Primary comparison: <strong>${esc(p.comparison.treatment)}</strong> vs <strong>${esc(p.comparison.control)}</strong> on <code>${esc(p.comparison.metric)}</code>
        (${r.n_students} virtual students, ${Math.round(r.session_duration_s / 60)}-minute sessions)</p>
      <div class="table-wrap"><table>
        <thead><tr><th>Noise</th><th>Treatment</th><th>Control</th><th>Mean difference [95% CI]</th><th>p (Holm)</th><th>Effect r</th></tr></thead>
        <tbody>${Object.entries(p.by_noise).map(([lv, t]) => `<tr><td>${esc(lv)}</td><td>${fmt(t.mean_a)}</td><td>${fmt(t.mean_b)}</td>
          <td>${fmt(t.mean_diff)} [${fmt(t.ci95_mean_diff[0])}, ${fmt(t.ci95_mean_diff[1])}]</td><td>${fmt(t.p_holm, 4)}</td><td>${fmt(t.rank_biserial, 2)}</td></tr>`).join("")}</tbody>
      </table></div>` : "<p class='small'>Exploratory run (no primary hypothesis test).</p>";
    const figs = r.figures.filter((f) => !f.startsWith("confusion_behaviors")).slice(0, 8).map((f) =>
      `<a href="/research-files/${encodeURIComponent(r.run_id)}/figures/${encodeURIComponent(f)}" target="_blank" rel="noopener">${esc(f)}</a>`).join(" · ");
    return `<div class="stack"><h3>${esc(r.experiment_id)} <span class="tiny">run ${esc(r.run_id)} · engine v${esc(r.engine_version)}</span></h3>${table}
      <p class="tiny">Full report: <a href="/research-files/${encodeURIComponent(r.run_id)}/statistics_report.md" target="_blank" rel="noopener">statistics_report.md</a>${figs ? ` · Figures: ${figs}` : ""}</p></div>`;
  }).join("<hr>");
}
'''

# ===== frontend/js/schedule.js ===============================================
FILES['frontend/js/schedule.js'] = r'''import { api } from "./api.js";
import { $, $$, esc, mountShell, fmtTime, fmtDateTime, fmtScore, scoreClass, localIso, localDate, toast, confirmDialog } from "./ui.js";

const user = await mountShell("schedule");
const H0 = 6, H1 = 24, ROW = 44; // visible hours and pixel height per hour
let weekStart = mondayOf(new Date());
let view = "week";
let events = [];
let editing = null;
let planningTask = null;

function mondayOf(d) {
  const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
  return x;
}
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };

async function load() {
  const start = localDate(weekStart);
  const end = localDate(addDays(weekStart, view === "week" ? 7 : 14));
  const [{ events: evs }, overview] = await Promise.all([
    api(`/api/schedule/events?start=${start}&end=${end}`),
    api(`/api/schedule/overview?date=${start}`),
  ]);
  events = evs;
  const endLabel = addDays(weekStart, view === "week" ? 6 : 13);
  $("#weekLabel").textContent = `${weekStart.toLocaleDateString(undefined, { month: "short", day: "numeric" })} – ${endLabel.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}`;
  view === "week" ? renderWeek() : renderAgenda();
  const w = overview.week;
  $("#weekStudy").textContent = `${(w.completed_study_min / 60).toFixed(1)} h done`;
  $("#weekStudySub").textContent = `of ${(w.planned_study_min / 60).toFixed(1)} h of study blocks planned`;
  $("#weekMeter").firstElementChild.style.width = `${w.planned_study_min ? Math.min(100, (100 * w.completed_study_min) / w.planned_study_min) : 0}%`;
  const scored = events.filter((e) => e.focus);
  $("#weekFocus").textContent = scored.length
    ? `Average Focus Score in scheduled blocks: ${fmtScore(scored.reduce((a, e) => a + e.focus.score, 0) / scored.length)}` : "";
}

// ---------------------------------------------------------------- week grid
function renderWeek() {
  const wk = $("#week");
  const todayStr = localDate();
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  wk.innerHTML = `<div class="week-head"><div></div>${days.map((d) =>
    `<div class="${localDate(d) === todayStr ? "today" : ""}">${d.toLocaleDateString(undefined, { weekday: "short" })} ${d.getDate()}</div>`).join("")}</div>
    <div class="hours">${Array.from({ length: H1 - H0 }, (_, i) => `<div>${i ? `${(H0 + i) % 12 || 12}${H0 + i < 12 ? "a" : "p"}` : ""}</div>`).join("")}</div>
    ${days.map((d) => `<div class="day-col ${localDate(d) === todayStr ? "today" : ""}" data-date="${localDate(d)}">${"<div class='slot'></div>".repeat(H1 - H0)}</div>`).join("")}`;
  for (const col of $$(".day-col", wk)) {
    const date = col.dataset.date;
    const dayEvents = events.filter((e) => e.start_at.slice(0, 10) <= date && e.end_at.slice(0, 10) >= date)
      .map((e) => clipToDay(e, date)).filter(Boolean);
    layoutLanes(dayEvents);
    for (const e of dayEvents) {
      const el = document.createElement("div");
      el.className = `ev k-${e.ev.kind} ${e.ev.completed ? "done" : ""}`;
      el.style.top = `${(e.startMin / 60 - H0) * ROW}px`;
      el.style.height = `${Math.max(18, ((e.endMin - e.startMin) / 60) * ROW - 2)}px`;
      el.style.left = `calc(${(100 * e.lane) / e.lanes}% + 3px)`;
      el.style.width = `calc(${100 / e.lanes}% - 6px)`;
      el.style.right = "auto";
      el.innerHTML = `<div class="ev-title">${esc(e.ev.title)}</div><div>${fmtTime(e.ev.start_at)}${e.ev.focus ? ` · ${fmtScore(e.ev.focus.score)}` : ""}</div>`;
      el.title = `${e.ev.title} (${fmtTime(e.ev.start_at)}–${fmtTime(e.ev.end_at)})`;
      el.addEventListener("click", (ev) => { ev.stopPropagation(); openEvent(e.ev); });
      col.append(el);
    }
    if (date === todayStr) {
      const now = new Date();
      const mins = now.getHours() * 60 + now.getMinutes();
      if (mins >= H0 * 60) {
        const line = document.createElement("div");
        line.className = "now-line";
        line.style.top = `${(mins / 60 - H0) * ROW}px`;
        col.append(line);
      }
    }
    col.addEventListener("click", (ev) => {
      if (ev.target.closest(".ev")) return;
      const rect = col.getBoundingClientRect();
      const mins = Math.floor((((ev.clientY - rect.top) / ROW) * 60 + H0 * 60) / 30) * 30;
      openEvent(null, date, mins);
    });
  }
}

function clipToDay(ev, date) {
  const toMin = (iso) => Number(iso.slice(11, 13)) * 60 + Number(iso.slice(14, 16));
  const startMin = ev.start_at.slice(0, 10) < date ? 0 : toMin(ev.start_at);
  const endMin = ev.end_at.slice(0, 10) > date ? 24 * 60 : toMin(ev.end_at);
  const s = Math.max(startMin, H0 * 60), e = Math.min(endMin, H1 * 60);
  return e > s ? { ev, startMin: s, endMin: e } : null;
}

function layoutLanes(items) {
  items.sort((a, b) => a.startMin - b.startMin || b.endMin - a.endMin);
  let cluster = [], clusterEnd = -1;
  const close = () => { const n = Math.max(...cluster.map((c) => c.lane)) + 1; cluster.forEach((c) => (c.lanes = n)); cluster = []; };
  for (const it of items) {
    if (it.startMin >= clusterEnd && cluster.length) close();
    const used = new Set(cluster.filter((c) => c.endMin > it.startMin).map((c) => c.lane));
    let lane = 0;
    while (used.has(lane)) lane++;
    it.lane = lane;
    cluster.push(it);
    clusterEnd = Math.max(clusterEnd, it.endMin);
  }
  if (cluster.length) close();
}

function renderAgenda() {
  const byDay = {};
  for (const e of events) (byDay[e.start_at.slice(0, 10)] ||= []).push(e);
  const keys = Object.keys(byDay).sort();
  $("#agenda").innerHTML = keys.length ? keys.map((k) => `
    <h3>${new Date(k + "T12:00").toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })}</h3>
    <ul class="list">${byDay[k].map((e) => `
      <li class="k-${e.kind}" data-id="${e.id}"><i class="dot kdot"></i>
        <div class="grow"><strong class="small">${esc(e.title)}</strong>${e.completed ? ' <span class="badge s-FOCUSED">done</span>' : ""}
          <div class="tiny">${fmtTime(e.start_at)}–${fmtTime(e.end_at)} · ${e.kind}${e.subject ? ` · ${esc(e.subject)}` : ""}${e.focus ? ` · Focus ${fmtScore(e.focus.score)}` : ""}</div></div>
        <button class="btn small" data-open="${e.id}">Open</button></li>`).join("")}</ul>`).join("")
    : '<div class="empty">Nothing scheduled in the next two weeks.</div>';
}
$("#agenda").addEventListener("click", (e) => {
  const b = e.target.closest("[data-open]");
  if (b) openEvent(events.find((x) => x.id === Number(b.dataset.open)));
});

// ---------------------------------------------------------------- event dialog
const pad = (n) => String(n).padStart(2, "0");
function openEvent(ev, date, mins) {
  editing = ev;
  $("#evError").classList.add("hidden");
  $("#evDialogTitle").textContent = ev ? "Edit event" : "New event";
  $("#evTitle").value = ev?.title ?? "";
  $("#evKind").value = ev?.kind ?? "study";
  $("#evSubject").value = ev?.subject ?? "";
  $("#evNotes").value = ev?.notes ?? "";
  if (ev) {
    $("#evDate").value = ev.start_at.slice(0, 10);
    $("#evStart").value = ev.start_at.slice(11, 16);
    $("#evEnd").value = ev.end_at.slice(11, 16);
  } else {
    const m = mins ?? Math.ceil((new Date().getHours() * 60 + new Date().getMinutes()) / 30) * 30;
    const end = Math.min(m + user.settings.default_session_min, 23 * 60 + 59);
    $("#evDate").value = date ?? localDate();
    $("#evStart").value = `${pad(Math.floor(m / 60) % 24)}:${pad(m % 60)}`;
    $("#evEnd").value = `${pad(Math.floor(end / 60))}:${pad(end % 60)}`;
  }
  $("#repeatField").classList.toggle("hidden", !!ev);
  $("#evRepeat").value = "0";
  $("#evDoneWrap").classList.toggle("hidden", !ev);
  $("#evDone").checked = !!ev?.completed;
  $("#evDelete").classList.toggle("hidden", !ev);
  const startable = ev && ev.kind === "study" && !ev.completed;
  $("#evStartSession").classList.toggle("hidden", !startable);
  if (startable) $("#evStartSession").href = `/session?event=${ev.id}`;
  $("#evFocus").textContent = ev?.focus ? `Focus Score in this block: ${fmtScore(ev.focus.score)} over ${Math.round(ev.focus.seconds / 60)} min (${ev.focus.sessions} session${ev.focus.sessions > 1 ? "s" : ""}).` : "";
  $("#eventDialog").showModal();
  $("#evTitle").focus();
}

$("#evCancel").addEventListener("click", () => $("#eventDialog").close());
$("#eventForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const date = $("#evDate").value;
  let endDate = date;
  if ($("#evEnd").value <= $("#evStart").value) endDate = localDate(addDays(new Date(date + "T12:00"), 1)); // crosses midnight
  const body = {
    title: $("#evTitle").value, kind: $("#evKind").value, subject: $("#evSubject").value, notes: $("#evNotes").value,
    start_at: `${date}T${$("#evStart").value}`, end_at: `${endDate}T${$("#evEnd").value}`,
  };
  try {
    let r;
    if (editing) r = await api(`/api/schedule/events/${editing.id}`, { method: "PUT", body: { ...body, completed: $("#evDone").checked } });
    else r = await api("/api/schedule/events", { method: "POST", body: { ...body, repeat_weekly: Number($("#evRepeat").value) } });
    $("#eventDialog").close();
    if (r.conflicts?.length) toast(`Saved, but it overlaps: ${[...new Set(r.conflicts.map((c) => c.title))].join(", ")}`);
    else toast("Saved");
    load();
  } catch (err) {
    $("#evError").textContent = err.message;
    $("#evError").classList.remove("hidden");
  }
});

$("#evDelete").addEventListener("click", async () => {
  const ev = editing;
  let scope = "one";
  if (ev.recurrence_group) {
    const series = await confirmDialog("Delete this and all following events in the series? Choose Cancel to delete only this one.", "Delete series");
    scope = series ? "series" : "one";
  } else if (!(await confirmDialog(`Delete "${ev.title}"?`))) return;
  await api(`/api/schedule/events/${ev.id}?scope=${scope}`, { method: "DELETE" });
  $("#eventDialog").close();
  load();
});

// ---------------------------------------------------------------- tasks
async function loadTasks() {
  const { tasks } = await api("/api/schedule/tasks");
  const now = localIso();
  $("#tasks").innerHTML = tasks.length ? tasks.map((t) => `
    <div class="task-item ${t.done ? "done" : ""}" data-id="${t.id}">
      <input type="checkbox" data-act="toggle" ${t.done ? "checked" : ""} aria-label="Mark done">
      <div class="grow">
        <div class="task-title small"><strong>${esc(t.title)}</strong> <span class="badge prio-${t.priority}">${t.priority}</span></div>
        <div class="tiny">${t.due_at ? `<span class="${!t.done && t.due_at < now ? "s-LOOKING_AWAY" : ""}">due ${fmtDateTime(t.due_at)}</span>` : "no due date"}
          ${t.estimated_min ? ` · ~${t.estimated_min} min` : ""}${t.subject ? ` · ${esc(t.subject)}` : ""}</div>
        ${t.done ? "" : `<div class="row"><button class="btn small" data-act="plan">Auto-plan</button><button class="btn small ghost" data-act="delete">Delete</button></div>`}
      </div>
    </div>`).join("") : '<div class="empty">No tasks yet.</div>';
  window._tasks = tasks;
}

$("#taskForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/schedule/tasks", { method: "POST", body: {
      title: $("#tTitle").value, subject: $("#tSubject").value, priority: $("#tPrio").value,
      due_at: $("#tDue").value || null, estimated_min: $("#tEst").value || null,
    } });
    e.target.reset();
    loadTasks();
  } catch (err) { toast(err.message, "error"); }
});

$("#tasks").addEventListener("click", async (e) => {
  const act = e.target.dataset.act;
  const item = e.target.closest(".task-item");
  if (!act || !item) return;
  const id = Number(item.dataset.id);
  const task = window._tasks.find((t) => t.id === id);
  if (act === "toggle") {
    await api(`/api/schedule/tasks/${id}`, { method: "PUT", body: { done: e.target.checked } });
    loadTasks();
  } else if (act === "delete") {
    if (await confirmDialog(`Delete task "${task.title}"?`)) { await api(`/api/schedule/tasks/${id}`, { method: "DELETE" }); loadTasks(); }
  } else if (act === "plan") {
    planningTask = task;
    $("#pEst").value = task.estimated_min || "";
    $("#pBlock").value = user.settings.default_session_min;
    $("#planInfo").textContent = `Plan "${task.title}"${task.due_at ? `, due ${fmtDateTime(task.due_at)}` : ""}.`;
    $("#planDialog").showModal();
  }
});

$("#planCancel").addEventListener("click", () => $("#planDialog").close());
$("#planForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    if (Number($("#pEst").value) !== planningTask.estimated_min) {
      await api(`/api/schedule/tasks/${planningTask.id}`, { method: "PUT", body: { estimated_min: Number($("#pEst").value) } });
      loadTasks();
    }
    const r = await api(`/api/schedule/tasks/${planningTask.id}/plan`, { method: "POST", body: {
      now: localIso(), block_min: Number($("#pBlock").value), max_per_day: Number($("#pMax").value),
      day_start: $("#pStart").value, day_end: $("#pEnd").value,
    } });
    $("#planDialog").close();
    toast(r.warning || `Planned ${r.placed_blocks} study block${r.placed_blocks === 1 ? "" : "s"}.`, r.warning ? "error" : "");
    if (r.events[0]) weekStart = mondayOf(new Date(r.events[0].start_at));
    load();
  } catch (err) { toast(err.message, "error"); }
});

// ---------------------------------------------------------------- navigation
$("#prevWeek").addEventListener("click", () => { weekStart = addDays(weekStart, -7); load(); });
$("#nextWeek").addEventListener("click", () => { weekStart = addDays(weekStart, 7); load(); });
$("#thisWeek").addEventListener("click", () => { weekStart = mondayOf(new Date()); load(); });
$("#newEventBtn").addEventListener("click", () => openEvent(null));
$("#viewTabs").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  view = b.dataset.view;
  $$("#viewTabs button").forEach((x) => x.classList.toggle("active", x === b));
  $("#weekView").classList.toggle("hidden", view !== "week");
  $("#agendaView").classList.toggle("hidden", view !== "agenda");
  load();
});

load();
loadTasks();
'''

# ===== frontend/js/session.js ================================================
FILES['frontend/js/session.js'] = r'''import { api } from "./api.js";
import { VisionTracker, FRAME_HZ } from "./vision.js";
import { ring, timeline } from "./charts.js";
import { $, esc, mountShell, STATE_LABEL, fmtClock, fmtScore, fmtTime, toast, showError, localDate } from "./ui.js";

const user = await mountShell("session");
const settings = user.settings;
$("#planned").value = settings.default_session_min;

let tracker = null;
let sessionId = null;
let linkedEvent = null;
let running = false, paused = false;
let buffer = [];
let samples = [];            // [{second, state}] for the local timeline
let lastState = null, episodeStart = null, alerted = false;
let t0 = 0, pausedAt = 0, pausedTotal = 0;
let sendTimer = null, clockTimer = null;
let lastFeature = null;

// ---------------------------------------------------------- setup form
const today = localDate();
const params = new URLSearchParams(location.search);
try {
  const [{ events }, { sessions }] = await Promise.all([
    api(`/api/schedule/events?start=${today}&end=${today}T23:59`),
    api("/api/sessions?limit=50"),
  ]);
  for (const ev of events.filter((e) => e.kind === "study" || e.kind === "exam" || e.kind === "other")) {
    const o = document.createElement("option");
    o.value = ev.id;
    o.textContent = `${fmtTime(ev.start_at)}–${fmtTime(ev.end_at)} · ${ev.title}`;
    o.dataset.title = ev.title;
    o.dataset.subject = ev.subject;
    o.dataset.minutes = Math.round((new Date(ev.end_at) - new Date(ev.start_at)) / 60000);
    $("#eventSel").append(o);
  }
  const subjects = [...new Set(sessions.map((s) => s.subject).filter(Boolean))];
  $("#subjectList").innerHTML = subjects.map((s) => `<option value="${esc(s)}">`).join("");
  if (params.get("event")) {
    $("#eventSel").value = params.get("event");
    $("#eventSel").dispatchEvent(new Event("change"));
  }
} catch (e) { /* the form still works without these */ }

$("#eventSel").addEventListener("change", (e) => {
  const o = e.target.selectedOptions[0];
  if (o?.value) {
    if (!$("#title").value) $("#title").value = o.dataset.title;
    if (!$("#subject").value) $("#subject").value = o.dataset.subject;
    $("#planned").value = o.dataset.minutes;
  }
});
if (params.get("event")) $("#eventSel").dispatchEvent(new Event("change"));

$("#setupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("#setupError").classList.add("hidden");
  $("#startBtn").disabled = true;
  try {
    const eventId = $("#eventSel").value ? Number($("#eventSel").value) : null;
    const { session } = await api("/api/sessions", {
      method: "POST",
      body: { title: $("#title").value, subject: $("#subject").value, schedule_event_id: eventId },
    });
    sessionId = session.id;
    linkedEvent = eventId;
    $("#completeWrap").classList.toggle("hidden", !eventId);
    $("#setup").classList.add("hidden");
    $("#live").classList.remove("hidden");
    tracker = new VisionTracker($("#video"), $("#overlay"));
    await tracker.init((msg) => { $("#videoMsg").textContent = msg; $("#videoMsg").classList.toggle("hidden", !msg); });
    if ($("#doCal").checked) await runCalibration();
    else await skipCalibration();
  } catch (err) {
    console.error(err);
    tracker?.stop();
    $("#live").classList.add("hidden");
    $("#setup").classList.remove("hidden");
    const msg = err.name === "NotAllowedError" ? "Camera permission was denied. Allow camera access in your browser and try again."
      : err.name === "NotFoundError" ? "No camera was found on this device." : err.message;
    showError($("#setupError"), { message: msg });
    if (sessionId) await api(`/api/sessions/${sessionId}`, { method: "DELETE" }).catch(() => {});
    sessionId = null;
  } finally {
    $("#startBtn").disabled = false;
  }
});

// ---------------------------------------------------------- calibration
const PHASES = [
  { name: "center", title: "Look at the dot", text: "Look at the dot in the middle of your screen, as if you were reading. Keep still.", targets: [[50, 50]], each: 10 },
  { name: "corners", title: "Follow the dot", text: "Follow the dot to each corner of your screen with your eyes and head, as you naturally would.", targets: [[4, 6], [96, 6], [96, 94], [4, 94]], each: 3 },
  { name: "down", title: "Look at your desk", text: "Look down at your desk or keyboard, as if writing notes.", targets: [null], each: 4 },
];
const LEAD_IN = 1.2; // seconds to move your eyes before recording starts
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function collectPhase(phase, frames) {
  const target = $("#calTarget");
  for (const tgt of phase.targets) {
    if (tgt) {
      target.classList.remove("hidden");
      target.style.left = `${tgt[0]}%`;
      target.style.top = `${tgt[1]}%`;
    } else target.classList.add("hidden");
    await sleep(LEAD_IN * 1000);
    const start = performance.now();
    await new Promise((resolve) => {
      tracker.start((f) => {
        frames.push(f);
        const p = (performance.now() - start) / (phase.each * 1000);
        $("#calBar").style.width = `${Math.min(100, p * 100)}%`;
        if (p >= 1) { tracker.pause(); resolve(); }
      }, calT0);
    });
  }
}

let calT0 = 0;
async function runCalibration() {
  const stage = $("#calStage");
  stage.classList.remove("hidden");
  stage.classList.add("running");
  $("#calResult").classList.add("hidden");
  $("#calCancel").classList.remove("hidden");
  calT0 = performance.now();
  const phases = {};
  let cancelled = false;
  $("#calCancel").onclick = () => { cancelled = true; };
  for (const ph of PHASES) {
    $("#calTitle").textContent = ph.title;
    $("#calText").textContent = ph.text;
    $("#calBar").style.width = "0%";
    phases[ph.name] = [];
    await collectPhase(ph, phases[ph.name]);
    if (cancelled) break;
  }
  $("#calTarget").classList.add("hidden");
  stage.classList.remove("running");
  if (cancelled) { stage.classList.add("hidden"); return skipCalibration(); }
  $("#calTitle").textContent = "Checking calibration…";
  $("#calText").textContent = "";
  const res = await api(`/api/sessions/${sessionId}/calibration`, { method: "POST", body: { phases } });
  showCalResult(res, phases);
}

function calSummary(c) {
  return `Neutral head pose: yaw ${c.yaw0.toFixed(1)}°, pitch ${c.pitch0.toFixed(1)}° · ` +
    `"looking away" beyond ±${c.yaw_threshold.toFixed(0)}° · "looking down" beyond ${c.pitch_down_threshold.toFixed(0)}° · ` +
    `eyes closed below EAR ${c.ear_closed_threshold.toFixed(3)}`;
}

function showCalResult(res, phases) {
  const box = $("#calResult");
  const c = res.calibration;
  box.classList.remove("hidden");
  $("#calCancel").classList.add("hidden");
  $("#calTitle").textContent = res.ok ? "Calibration complete" : "Calibration needs another try";
  $("#calText").textContent = res.ok ? calSummary(c) : "";
  box.innerHTML = `
    ${c.warnings.length ? `<div class="alert ${res.ok ? "warn" : "error"} small">${c.warnings.map(esc).join("<br>")}</div>` : ""}
    <div class="row centered"></div>`;
  const row = box.querySelector(".row");
  const btn = (label, cls, fn) => { const b = document.createElement("button"); b.className = `btn ${cls}`; b.textContent = label; b.onclick = fn; row.append(b); };
  if (res.ok) btn("Start studying", "primary", () => { $("#calStage").classList.add("hidden"); beginTracking(c); });
  btn("Redo calibration", res.ok ? "" : "primary", () => runCalibration());
  if (!res.ok) {
    if (c.quality !== "failed") btn("Use it anyway", "", async () => {
      const r = await api(`/api/sessions/${sessionId}/calibration`, { method: "POST", body: { phases, accept_anyway: true } });
      $("#calStage").classList.add("hidden");
      beginTracking(r.calibration);
    });
    btn("Skip calibration", "ghost", () => { $("#calStage").classList.add("hidden"); skipCalibration(); });
  }
}

async function skipCalibration() {
  const r = await api(`/api/sessions/${sessionId}/calibration`, { method: "POST", body: { skip: true } });
  beginTracking(r.calibration);
}

// ---------------------------------------------------------- live tracking
const legend = Object.entries(STATE_LABEL).map(([k, v]) => `<span><i class="dot s-${k}"></i>${v}</span>`).join("");
$("#legend").innerHTML = legend;
ring($("#ringLive"), null, "Last 60 s");

function beginTracking(cal) {
  $("#calInfo").textContent = cal.calibrated
    ? `Calibrated. ${calSummary(cal)}`
    : "Running without personal calibration (population-default thresholds). Accuracy may be lower if your camera is off to the side.";
  running = true;
  t0 = performance.now();
  tracker.start(onFrame, t0);
  sendTimer = setInterval(flush, 1000);
  clockTimer = setInterval(tick, 500);
  window.addEventListener("beforeunload", warnUnload);
}

function onFrame(f) {
  if (paused) return;
  f.t = Math.round((f.t - pausedTotal) * 1000) / 1000;
  buffer.push(f);
  lastFeature = f;
  if ($("#showSensors").checked) renderSensors(f);
}

function renderSensors(f) {
  const cell = (k, v) => `<div>${k}: ${v}</div>`;
  $("#sensorBox").innerHTML = f.face_present
    ? cell("yaw", `${f.yaw.toFixed(1)}°`) + cell("pitch", `${f.pitch.toFixed(1)}°`) + cell("EAR", f.ear.toFixed(3)) +
      cell("gaze_h", f.gaze_h.toFixed(2)) + cell("gaze_v", f.gaze_v.toFixed(2)) + cell("t", f.t.toFixed(1))
    : cell("face", "not detected") + cell("t", f.t.toFixed(1));
}

let flushing = false;
async function flush() {
  if (flushing || !buffer.length || !sessionId) return;
  flushing = true;
  const batch = buffer.splice(0, 600);
  try {
    const r = await api(`/api/sessions/${sessionId}/frames`, { method: "POST", body: { frames: batch } });
    update(r);
  } catch (e) {
    if (e.status >= 500 || !e.status) buffer.unshift(...batch); // network problem: retry later
    if (buffer.length > 3000) buffer.splice(0, buffer.length - 3000);
  } finally { flushing = false; }
}

function update(r) {
  const s = r.state;
  $("#statePill").innerHTML = `<span class="dot s-${s}"></span><span class="s-${s}">${STATE_LABEL[s]}</span>`;
  ring($("#ringLive"), r.live_score, "Last 60 s");
  $("#sessScore").textContent = fmtScore(r.session_score);
  $("#distractions").textContent = r.distraction_count;
  const sec = Math.floor(r.t);
  if (!samples.length || samples[samples.length - 1].second < sec) samples.push({ second: sec, state: s });
  timeline($("#liveTimeline"), samples);
  if (tracker) $("#fps").textContent = `${tracker.fps.toFixed(1)} frames/s`;

  if (s !== lastState) { episodeStart = r.t; alerted = false; lastState = s; }
  const away = s !== "FOCUSED" ? r.t - (r.current_episode?.start_t ?? episodeStart) : 0;
  const alertBox = $("#liveAlert");
  if (s !== "FOCUSED" && away >= settings.alert_after_s) {
    alertBox.textContent = `${STATE_LABEL[s]} for ${Math.round(away)} s. Ready to get back to it?`;
    alertBox.classList.remove("hidden");
    if (!alerted) { alerted = true; chime(); }
  } else alertBox.classList.add("hidden");
}

function chime() {
  if (!settings.alert_sound) return;
  try {
    const ctx = new AudioContext();
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.value = 660;
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.15, ctx.currentTime + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.6);
    o.connect(g).connect(ctx.destination);
    o.start(); o.stop(ctx.currentTime + 0.65);
  } catch { /* audio not available */ }
}

let goalNotified = false;
function tick() {
  if (!running) return;
  const now = paused ? pausedAt : performance.now();
  const el = (now - t0) / 1000 - pausedTotal;
  $("#elapsed").textContent = fmtClock(el);
  const planned = Number($("#planned").value) * 60;
  $("#planMeter").firstElementChild.style.width = `${Math.min(100, (100 * el) / planned)}%`;
  $("#planLabel").textContent = el < planned ? `${fmtClock(planned - el)} left of ${planned / 60} min plan`
    : `Plan complete. Time for a ${settings.break_min}-minute break.`;
  if (el >= planned && !goalNotified) { goalNotified = true; toast(`You reached your ${planned / 60}-minute goal. Take a ${settings.break_min}-minute break!`); chime(); }
  $("#timeLabel").textContent = `${samples.length}s recorded`;
}

$("#pauseBtn").addEventListener("click", () => {
  paused = !paused;
  if (paused) { pausedAt = performance.now(); tracker.pause(); $("#pauseBtn").textContent = "Resume"; }
  else {
    pausedTotal += (performance.now() - pausedAt) / 1000;
    tracker.start(onFrame, t0);
    $("#pauseBtn").textContent = "Pause";
  }
});

$("#privacyBlur").addEventListener("change", (e) => $("#videoBox").classList.toggle("privacy", e.target.checked));
$("#showSensors").addEventListener("change", (e) => $("#sensorBox").classList.toggle("hidden", !e.target.checked));

function warnUnload(e) { e.preventDefault(); e.returnValue = ""; }

$("#endBtn").addEventListener("click", async () => {
  $("#endBtn").disabled = true;
  running = false;
  clearInterval(sendTimer); clearInterval(clockTimer);
  tracker?.stop();
  await flush();
  const { session } = await api(`/api/sessions/${sessionId}/end`, {
    method: "POST",
    body: { notes: $("#notes").value, complete_event: linkedEvent && $("#completeEvent").checked },
  });
  window.removeEventListener("beforeunload", warnUnload);
  location.href = `/history?id=${session.id}`;
});
'''

# ===== frontend/js/settings.js ===============================================
FILES['frontend/js/settings.js'] = r'''import { api } from "./api.js";
import { $, mountShell, toast, confirmDialog } from "./ui.js";

const user = await mountShell("settings");
const s = user.settings;
$("#name").value = user.display_name;
$("#goal").value = s.daily_goal_min;
$("#sessionLen").value = s.default_session_min;
$("#breakLen").value = s.break_min;
$("#alertAfter").value = s.alert_after_s;
$("#sound").checked = s.alert_sound;
try { $("#theme").value = localStorage.getItem("nf-theme") || ""; } catch { /* storage blocked */ }

$("#profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/account/profile", { method: "PUT", body: {
      display_name: $("#name").value,
      settings: { daily_goal_min: $("#goal").value, default_session_min: $("#sessionLen").value,
        break_min: $("#breakLen").value, alert_after_s: $("#alertAfter").value, alert_sound: $("#sound").checked },
    } });
    try { localStorage.setItem("nf-theme", $("#theme").value); } catch { /* ignore */ }
    applyTheme();
    toast("Settings saved");
  } catch (err) { toast(err.message, "error"); }
});

$("#pwForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/account/password", { method: "PUT", body: { current_password: $("#curPw").value, new_password: $("#newPw").value } });
    e.target.reset();
    toast("Password updated");
  } catch (err) { toast(err.message, "error"); }
});

$("#deleteForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!(await confirmDialog("Permanently delete your account and all data?", "Delete everything"))) return;
  try {
    await api("/api/account", { method: "DELETE", body: { password: $("#delPw").value } });
    location.href = "/";
  } catch (err) { toast(err.message, "error"); }
});

function applyTheme() {
  let t = "";
  try { t = localStorage.getItem("nf-theme") || ""; } catch { /* ignore */ }
  if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
}
'''

# ===== frontend/js/ui.js =====================================================
FILES['frontend/js/ui.js'] = r'''// Shared UI: app shell, escaping, formatting, toasts, dialogs.

import { requireUser, logout } from "./api.js";

export const STATE_LABEL = {
  FOCUSED: "Focused",
  LOOKING_AWAY: "Looking away",
  LOOKING_DOWN: "Looking down",
  EYES_CLOSED: "Eyes closed",
  ABSENT: "Not detected",
};
export const DISTRACTION_STATES = ["LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT"];

export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const ICONS = {
  dashboard: '<path d="M3 13h8V3H3zM13 21h8V11h-8zM3 21h8v-6H3zM13 3v6h8V3z"/>',
  session: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.5"/>',
  schedule: '<rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
  analytics: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  research: '<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9V3"/><path d="M7 15h10"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
  menu: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
};

export function icon(name) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;
}

const NAV = [
  ["dashboard", "Dashboard", "/dashboard"],
  ["session", "Focus Session", "/session"],
  ["schedule", "Schedule", "/schedule"],
  ["history", "History", "/history"],
  ["analytics", "Analytics", "/analytics"],
];

export async function mountShell(active) {
  const user = await requireUser();
  const side = $("#sidebar");
  const link = ([key, label, href]) =>
    `<a href="${href}" class="${key === active ? "active" : ""}" ${key === active ? 'aria-current="page"' : ""}>${icon(key)}${label}</a>`;
  side.innerHTML = `
    <a class="brand" href="/dashboard"><span class="brand-mark">◎</span>NeuroFocus AI</a>
    <nav class="nav" aria-label="Main">
      ${NAV.map(link).join("")}
      <div class="nav-section">Project</div>
      ${link(["research", "Research & Method", "/research"])}
      ${link(["settings", "Settings", "/settings"])}
    </nav>
    <div class="sidebar-foot">
      <div class="small"><strong>${esc(user.display_name)}</strong></div>
      <div class="tiny">${esc(user.email)}</div>
      <button class="btn ghost small" id="logoutBtn">${icon("logout")}<span>Sign out</span></button>
    </div>`;
  $("#logoutBtn").addEventListener("click", logout);
  const menu = $("#menuBtn");
  if (menu) {
    menu.innerHTML = icon("menu");
    menu.addEventListener("click", () => side.classList.toggle("open"));
  }
  return user;
}

let toastHost;
export function toast(msg, kind = "") {
  if (!toastHost) {
    toastHost = document.createElement("div");
    toastHost.className = "toast-host";
    toastHost.setAttribute("role", "status");
    document.body.append(toastHost);
  }
  const t = document.createElement("div");
  t.className = `toast ${kind}`;
  t.textContent = msg;
  toastHost.append(t);
  setTimeout(() => t.remove(), 4200);
}

export function showError(el, err) {
  el.textContent = err?.message || String(err);
  el.classList.remove("hidden");
}

export function confirmDialog(message, okLabel = "Delete") {
  return new Promise((resolve) => {
    const d = document.createElement("dialog");
    d.innerHTML = `<div class="dialog-body"><p></p></div>
      <div class="dialog-foot"><button class="btn" value="no">Cancel</button><button class="btn danger" value="yes"></button></div>`;
    d.querySelector("p").textContent = message;
    d.querySelector('[value="yes"]').textContent = okLabel;
    d.addEventListener("click", (e) => {
      if (e.target.value) { d.close(); resolve(e.target.value === "yes"); d.remove(); }
    });
    d.addEventListener("cancel", () => { resolve(false); d.remove(); });
    document.body.append(d);
    d.showModal();
  });
}

// ---------- formatting ----------
export function fmtScore(x) { return x == null ? "–" : Math.round(x).toString(); }
export function fmtDuration(sec) {
  if (sec == null) return "–";
  sec = Math.round(sec);
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  if (h) return `${h}h ${m}m`;
  if (m) return `${m}m ${s.toString().padStart(2, "0")}s`;
  return `${s}s`;
}
export function fmtClock(sec) {
  sec = Math.max(0, Math.floor(sec));
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  return (h ? `${h}:` : "") + `${String(m).padStart(h ? 2 : 1, "0")}:${String(s).padStart(2, "0")}`;
}
export function fmtDateTime(iso) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}
export function fmtTime(localIso) {
  return new Date(localIso).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
}
export function scoreClass(x) {
  if (x == null) return "";
  return x >= 75 ? "s-FOCUSED" : x >= 50 ? "s-LOOKING_DOWN" : "s-LOOKING_AWAY";
}
// Local wall-clock ISO 'YYYY-MM-DDTHH:MM' (what the schedule API stores).
export function localIso(d = new Date()) {
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}
export function localDate(d = new Date()) { return localIso(d).slice(0, 10); }
export const tzOffsetMin = () => -new Date().getTimezoneOffset();

// Apply the saved theme preference (per-device convenience only).
try {
  const t = localStorage.getItem("nf-theme");
  if (t) document.documentElement.dataset.theme = t;
} catch { /* storage blocked */ }
'''

# ===== frontend/js/vision.js =================================================
FILES['frontend/js/vision.js'] = r'''// Computer-vision front end. Runs entirely in the browser:
//   webcam frame -> MediaPipe Face Landmarker (478 landmarks + head transform)
//   -> 6 numeric features (face_present, yaw, pitch, ear, gaze_h, gaze_v)
// Only those numbers are sent to the server. Video never leaves the device.
// Feature definitions are documented in research/docs/03_algorithm.md.

// MediaPipe Tasks Vision 0.10.14 and the Face Landmarker model are bundled in
// frontend/vendor (see vendor/README.md), so no third-party server is contacted.
const MP_BASE = "/static/vendor/mediapipe";
const MODEL_URL = "/static/vendor/models/face_landmarker.task";
export const FRAME_HZ = 10;

// Landmark indices in the MediaPipe 478-point face mesh.
const EYE_R = { left: 33, right: 133, top: [160, 158], bottom: [144, 153], lid: [159, 145], iris: 468 };
const EYE_L = { left: 362, right: 263, top: [385, 387], bottom: [380, 373], lid: [386, 374], iris: 473 };
// EAR pairs follow Soukupová & Čech (2016): p2-p6 and p3-p5 over p1-p4.

function dist(a, b, W, H) { return Math.hypot((a.x - b.x) * W, (a.y - b.y) * H); }

function eyeFeatures(lm, e, W, H) {
  const p1 = lm[e.left], p4 = lm[e.right];
  const width = dist(p1, p4, W, H);
  const ear = (dist(lm[e.top[0]], lm[e.bottom[0]], W, H) + dist(lm[e.top[1]], lm[e.bottom[1]], W, H)) / (2 * width);
  const iris = lm[e.iris];
  // position of the iris along the corner-to-corner axis, 0 (image-left) .. 1 (image-right)
  const ax = (p4.x - p1.x) * W, ay = (p4.y - p1.y) * H;
  const u = (((iris.x - p1.x) * W) * ax + ((iris.y - p1.y) * H) * ay) / (ax * ax + ay * ay);
  const lidMidY = (lm[e.lid[0]].y + lm[e.lid[1]].y) / 2;
  const v = ((iris.y - lidMidY) * H) / width;
  return { ear, u, v };
}

const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

/** Rotation -> yaw/pitch of the face's forward axis, in degrees.
 * MediaPipe returns a 4x4 matrix; its storage order is detected from where the
 * translation (face ~30-80 cm in front of camera) sits. */
function headPose(m) {
  const colMajor = Math.abs(m[14]) >= Math.abs(m[11]);
  const R = (r, c) => (colMajor ? m[c * 4 + r] : m[r * 4 + c]);
  const fx = R(0, 2), fy = R(1, 2), fz = R(2, 2); // forward axis = third column
  const yaw = (Math.atan2(fx, fz) * 180) / Math.PI;
  const pitch = (Math.atan2(fy, Math.hypot(fx, fz)) * 180) / Math.PI; // +up (verified in calibration)
  return { yaw, pitch };
}

export function computeFeatures(result, t, W, H) {
  const lm = result?.faceLandmarks?.[0];
  const mat = result?.facialTransformationMatrixes?.[0]?.data;
  if (!lm || lm.length < 478 || !mat) return { t, face_present: false };
  const { yaw, pitch } = headPose(mat);
  const r = eyeFeatures(lm, EYE_R, W, H), l = eyeFeatures(lm, EYE_L, W, H);
  const round = (x, n = 3) => Math.round(x * 10 ** n) / 10 ** n;
  return {
    t: round(t, 3),
    face_present: true,
    yaw: round(yaw, 2),
    pitch: round(pitch, 2),
    ear: round((r.ear + l.ear) / 2, 4),
    // centred iris offset scaled so +-1 is roughly the comfortable limit of eye rotation
    gaze_h: round(clamp(((r.u + l.u) / 2 - 0.5) * 4, -1, 1), 4),
    gaze_v: round(clamp(((r.v + l.v) / 2) * 4, -1, 1), 4),
  };
}

// A worker-based ticker keeps sampling at ~10 Hz even when this tab is in the
// background (plain timers get throttled to 1 Hz or less there).
function makeTicker(hz, fn) {
  const src = `let id=setInterval(()=>postMessage(0),${Math.round(1000 / hz)});onmessage=()=>clearInterval(id);`;
  try {
    const url = URL.createObjectURL(new Blob([src], { type: "text/javascript" }));
    const w = new Worker(url);
    w.onmessage = fn;
    return () => { w.postMessage(0); w.terminate(); URL.revokeObjectURL(url); };
  } catch {
    const id = setInterval(fn, 1000 / hz);
    return () => clearInterval(id);
  }
}

export class VisionTracker {
  constructor(video, canvas) {
    this.video = video;
    this.canvas = canvas;
    this.landmarker = null;
    this.stream = null;
    this.stopTick = null;
    this.t0 = null;
    this.drawOverlay = true;
    this.fps = 0;
  }

  async init(onStatus = () => {}) {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error("This browser cannot access a camera.");
    onStatus("Requesting camera permission…");
    this.stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" }, audio: false,
    });
    this.video.srcObject = this.stream;
    this.video.muted = true;
    this.video.playsInline = true;
    await this.video.play();
    onStatus("Loading face-landmark model (first time can take a few seconds)…");
    const vision = await import(`${MP_BASE}/vision_bundle.mjs`);
    const files = await vision.FilesetResolver.forVisionTasks(`${MP_BASE}/wasm`);
    const opts = (delegate) => ({
      baseOptions: { modelAssetPath: MODEL_URL, delegate },
      runningMode: "VIDEO",
      numFaces: 1,
      outputFacialTransformationMatrixes: true,
      outputFaceBlendshapes: false,
    });
    try {
      this.landmarker = await vision.FaceLandmarker.createFromOptions(files, opts("GPU"));
    } catch {
      this.landmarker = await vision.FaceLandmarker.createFromOptions(files, opts("CPU"));
    }
    onStatus("");
  }

  /** Start sampling. onFrame(features) is called ~10 times per second. */
  start(onFrame, t0 = performance.now()) {
    this.t0 = t0;
    let last = -1, count = 0, fpsT = performance.now();
    this.stopTick = makeTicker(FRAME_HZ, () => {
      if (!this.landmarker || this.video.readyState < 2) return;
      const now = performance.now();
      if (now <= last) return;
      last = now;
      let result;
      try { result = this.landmarker.detectForVideo(this.video, now); } catch { return; }
      const W = this.video.videoWidth, H = this.video.videoHeight;
      const f = computeFeatures(result, (now - this.t0) / 1000, W, H);
      if (this.drawOverlay) this.draw(result, W, H);
      count++;
      if (now - fpsT > 2000) { this.fps = (count * 1000) / (now - fpsT); count = 0; fpsT = now; }
      onFrame(f);
    });
  }

  pause() { if (this.stopTick) { this.stopTick(); this.stopTick = null; } }

  draw(result, W, H) {
    const c = this.canvas;
    if (!c) return;
    if (c.width !== W) { c.width = W; c.height = H; }
    const ctx = c.getContext("2d");
    ctx.clearRect(0, 0, W, H);
    const lm = result?.faceLandmarks?.[0];
    if (!lm) return;
    ctx.fillStyle = "rgba(129,140,248,.85)";
    for (const i of [33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373, 380, 1, 152, 10, 234, 454]) {
      ctx.beginPath(); ctx.arc(lm[i].x * W, lm[i].y * H, 2.2, 0, 2 * Math.PI); ctx.fill();
    }
    ctx.fillStyle = "rgba(74,222,128,.95)";
    for (const i of [468, 473]) {
      ctx.beginPath(); ctx.arc(lm[i].x * W, lm[i].y * H, 3.5, 0, 2 * Math.PI); ctx.fill();
    }
  }

  stop() {
    this.pause();
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
    this.landmarker?.close?.();
    this.landmarker = null;
    if (this.canvas) this.canvas.getContext("2d").clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}
'''

# ===== frontend/login.html ===================================================
FILES['frontend/login.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sign in · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/auth.js"></script>
</head>
<body>
<div class="auth-wrap">
  <div class="card auth-card">
    <a class="brand" href="/"><span class="brand-mark">◎</span>NeuroFocus AI</a>
    <h1 class="center">Welcome back</h1>
    <p class="muted center small">Sign in to continue your study sessions.</p>
    <div id="error" class="alert error hidden" role="alert"></div>
    <form id="loginForm" novalidate>
      <div class="field"><label for="email">Email</label><input id="email" type="email" autocomplete="email" required></div>
      <div class="field"><label for="password">Password</label><input id="password" type="password" autocomplete="current-password" required></div>
      <button class="btn primary big" type="submit" id="submitBtn">Sign in</button>
    </form>
    <p class="small center">New here? <a href="/register">Create an account</a></p>
  </div>
</div>
</body>
</html>
'''

# ===== frontend/register.html ================================================
FILES['frontend/register.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Create account · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/auth.js"></script>
</head>
<body>
<div class="auth-wrap">
  <div class="card auth-card">
    <a class="brand" href="/"><span class="brand-mark">◎</span>NeuroFocus AI</a>
    <h1 class="center">Create your account</h1>
    <div id="error" class="alert error hidden" role="alert"></div>
    <form id="registerForm" novalidate>
      <div class="field"><label for="name">Name</label><input id="name" autocomplete="name" maxlength="60" required></div>
      <div class="field"><label for="email">Email</label><input id="email" type="email" autocomplete="email" required></div>
      <div class="field"><label for="password">Password</label><input id="password" type="password" autocomplete="new-password" minlength="10" required>
        <div class="tiny">At least 10 characters, mixing letters with numbers or symbols.</div></div>
      <div class="field"><label class="check small"><input type="checkbox" id="agree" required> I understand NeuroFocus is a study aid, not a medical or diagnostic tool.</label></div>
      <button class="btn primary big" type="submit" id="submitBtn">Create account</button>
    </form>
    <p class="small center">Already have an account? <a href="/login">Sign in</a></p>
  </div>
</div>
</body>
</html>
'''

# ===== frontend/research.html ================================================
FILES['frontend/research.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research &amp; Method · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/research.js"></script>
</head>
<body>
<div class="shell" id="shell">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="main">
    <div class="page-head">
      <div>
        <button class="btn ghost small menu-btn" id="menuBtn" aria-label="Menu"></button>
        <h1>Research &amp; Method</h1>
        <p>How NeuroFocus AI works, and how its accuracy is measured.</p>
      </div>
      <a class="btn hidden" id="publicHome" href="/">← Home</a>
    </div>

    <div class="prose stack">
      <div class="card">
        <h2>Product vs. experiment</h2>
        <div class="compare">
          <div>
            <h3>The product</h3>
            <p class="small">Accounts, camera calibration, live tracking, Focus Score, history, analytics and the Schedule department. These features are <em>software-tested</em> (automated tests check they behave as specified).</p>
          </div>
          <div>
            <h3>The experiment</h3>
            <p class="small">Measures one engineering question about the attention engine only: <strong>how accurately does it detect distraction, and does personal calibration improve that accuracy across different camera placements and sensor-noise levels?</strong></p>
          </div>
        </div>
        <div class="disclaimer small">A passing software test shows the code does what it was designed to do. It is <strong>not</strong> evidence that the system measures real students' attention reliably. The current experiment uses simulated "virtual students"; no human participants were involved.</div>
      </div>

      <div class="card">
        <h2>Engineering question &amp; variables</h2>
        <ul class="small">
          <li><strong>Independent variable 1:</strong> calibration mode (personal calibration vs. population-default thresholds).</li>
          <li><strong>Independent variable 2:</strong> sensor-noise level (low / medium / high landmark jitter and detection dropouts).</li>
          <li><strong>Dependent variables:</strong> frame-level F1, precision, recall, specificity and accuracy for "distracted"; 5×5 confusion matrix; episode detection rate; detection latency (s); false alarms per on-task hour; Focus Score absolute error (percentage points).</li>
          <li><strong>Controls:</strong> identical virtual students, behaviour timelines and random seeds across conditions (paired design); 10 frames/s; 20-minute sessions; fixed engine version and parameters.</li>
          <li><strong>Pre-specified analysis:</strong> Wilcoxon signed-rank test on paired per-student F1 at each noise level, Holm-corrected, with bootstrap 95% confidence intervals and effect sizes.</li>
        </ul>
      </div>

      <div class="card">
        <h2>The algorithm</h2>
        <ol class="small">
          <li><strong>Features (in the browser).</strong> MediaPipe Face Landmarker gives 478 face landmarks and a head-pose matrix. From these: head yaw and pitch (degrees), eye aspect ratio (EAR), and horizontal/vertical iris offset.</li>
          <li><strong>Calibration.</strong> Centre look (10 s) sets your neutral pose and open-eye EAR; four corner looks (3 s each) set how far you turn to see your screen; a desk look (4 s) checks the direction of "down".</li>
          <li><strong>Frame rules</strong> (first match wins): no face → <span class="s-ABSENT">Not detected</span>; EAR &lt; 0.65 × your open-eye EAR → <span class="s-EYES_CLOSED">Eyes closed</span>; pitch below your neutral by more than the down threshold → <span class="s-LOOKING_DOWN">Looking down</span>; |yaw deviation + 30° × iris offset| above the away threshold → <span class="s-LOOKING_AWAY">Looking away</span>; otherwise <span class="s-FOCUSED">Focused</span>.</li>
          <li><strong>Temporal filter.</strong> A non-focused state is reported only after it lasts its onset time; return to focused needs 0.5 s.</li>
        </ol>
        <div class="formula">Focus Score = 100 × (time reported FOCUSED) ÷ (session time)</div>
        <h3>Current parameters</h3>
        <div class="table-wrap"><table><tbody id="paramsTable"></tbody></table></div>
      </div>

      <div class="card">
        <h2>Experiment results</h2>
        <div id="results"><p class="muted small">Loading…</p></div>
      </div>

      <div class="card">
        <h2>Known limitations</h2>
        <ul class="small">
          <li>The virtual-student model is a set of assumptions (behaviour durations, head/eye movement, noise). Results describe performance on that model, not on real people.</li>
          <li>Head and eye direction show where someone is looking, not whether they are thinking about the work. Looking down to write notes, or reading a phone held near the screen, can be misclassified.</li>
          <li>The iris-offset scale (±1 ≈ ±30°) and pitch sign are not yet validated against measured ground truth on real cameras.</li>
          <li>Lighting, glasses, camera quality and skin tone can affect landmark detection; these have not been tested.</li>
          <li>Any future testing with people requires approval under school and ISEF human-participant rules (IRB/SRC) before data collection.</li>
        </ul>
      </div>
    </div>
  </main>
</div>
</body>
</html>
'''

# ===== frontend/schedule.html ================================================
FILES['frontend/schedule.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Schedule · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/schedule.js"></script>
</head>
<body>
<div class="shell">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="main">
    <div class="page-head">
      <div>
        <button class="btn ghost small menu-btn" id="menuBtn" aria-label="Menu"></button>
        <h1>Schedule</h1>
        <p id="weekLabel"></p>
      </div>
      <div class="row">
        <div class="tabs" id="viewTabs"><button data-view="week" class="active">Week</button><button data-view="agenda">Agenda</button></div>
        <button class="btn small" id="prevWeek" aria-label="Previous week">←</button>
        <button class="btn small" id="thisWeek">Today</button>
        <button class="btn small" id="nextWeek" aria-label="Next week">→</button>
        <button class="btn primary" id="newEventBtn">+ New event</button>
      </div>
    </div>

    <div class="schedule-layout">
      <div class="stack">
        <div id="weekView" class="week-scroll"><div class="week-inner"><div class="week" id="week"></div></div></div>
        <div id="agendaView" class="card hidden"><div id="agenda"></div></div>
        <div class="legend">
          <span class="k-study"><i class="dot kdot"></i>Study block</span>
          <span class="k-class"><i class="dot kdot"></i>Class</span>
          <span class="k-exam"><i class="dot kdot"></i>Exam</span>
          <span class="k-break"><i class="dot kdot"></i>Break</span>
          <span class="k-other"><i class="dot kdot"></i>Other</span>
          <span class="tiny">Click an empty slot to add an event.</span>
        </div>
      </div>
      <div class="stack">
        <div class="card">
          <div class="card-head"><h2>This week</h2></div>
          <div class="stat"><div class="value" id="weekStudy">–</div><div class="sub" id="weekStudySub"></div></div>
          <div class="meter" id="weekMeter"><div></div></div>
          <p class="tiny" id="weekFocus"></p>
        </div>
        <div class="card">
          <div class="card-head"><h2>Tasks &amp; assignments</h2></div>
          <form id="taskForm">
            <div class="field"><input id="tTitle" maxlength="160" placeholder="Add a task, e.g. History essay" required aria-label="Task title"></div>
            <div class="field"><label for="tDue">Due</label><input id="tDue" type="datetime-local"></div>
            <div class="field-row">
              <div class="field"><label for="tEst">Minutes needed</label><input id="tEst" type="number" min="5" max="6000" placeholder="e.g. 120"></div>
              <div class="field"><label for="tPrio">Priority</label><select id="tPrio"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></div>
            </div>
            <div class="field"><label for="tSubject">Subject</label><input id="tSubject" maxlength="60"></div>
            <button class="btn primary small" type="submit">Add task</button>
          </form>
          <div id="tasks"></div>
        </div>
      </div>
    </div>

    <dialog id="eventDialog">
      <form id="eventForm" method="dialog">
        <div class="dialog-body">
          <h2 id="evDialogTitle">New event</h2>
          <div id="evError" class="alert error hidden" role="alert"></div>
          <div class="field"><label for="evTitle">Title</label><input id="evTitle" maxlength="120" required></div>
          <div class="field-row">
            <div class="field"><label for="evKind">Type</label>
              <select id="evKind"><option value="study">Study block</option><option value="class">Class</option><option value="exam">Exam</option><option value="break">Break</option><option value="other">Other</option></select></div>
            <div class="field"><label for="evSubject">Subject</label><input id="evSubject" maxlength="60"></div>
          </div>
          <div class="field-row">
            <div class="field"><label for="evDate">Date</label><input id="evDate" type="date" required></div>
            <div class="field-row">
              <div class="field"><label for="evStart">Start</label><input id="evStart" type="time" required></div>
              <div class="field"><label for="evEnd">End</label><input id="evEnd" type="time" required></div>
            </div>
          </div>
          <div class="field" id="repeatField"><label for="evRepeat">Repeat weekly for</label>
            <select id="evRepeat"><option value="0">Does not repeat</option><option value="3">3 more weeks</option><option value="7">7 more weeks</option><option value="11">11 more weeks</option><option value="15">15 more weeks</option></select></div>
          <div class="field"><label for="evNotes">Notes</label><textarea id="evNotes" maxlength="2000"></textarea></div>
          <label class="check small hidden" id="evDoneWrap"><input type="checkbox" id="evDone"> Completed</label>
          <p class="tiny" id="evFocus"></p>
        </div>
        <div class="dialog-foot">
          <button type="button" class="btn danger hidden" id="evDelete">Delete</button>
          <a class="btn hidden" id="evStartSession">Start session</a>
          <span class="grow"></span>
          <button type="button" class="btn" id="evCancel">Cancel</button>
          <button type="submit" class="btn primary" id="evSave">Save</button>
        </div>
      </form>
    </dialog>

    <dialog id="planDialog">
      <form id="planForm" method="dialog">
        <div class="dialog-body">
          <h2>Auto-plan study blocks</h2>
          <p class="small muted" id="planInfo"></p>
          <div class="field"><label for="pEst">Total time needed (minutes)</label><input id="pEst" type="number" min="5" max="6000" required></div>
          <div class="field-row">
            <div class="field"><label for="pBlock">Block length (min)</label><input id="pBlock" type="number" min="15" max="180" value="50"></div>
            <div class="field"><label for="pMax">Max blocks per day</label><input id="pMax" type="number" min="1" max="6" value="2"></div>
          </div>
          <div class="field-row">
            <div class="field"><label for="pStart">Earliest start</label><input id="pStart" type="time" value="16:00"></div>
            <div class="field"><label for="pEnd">Latest end</label><input id="pEnd" type="time" value="21:00"></div>
          </div>
          <p class="tiny">Blocks are placed in free time only, with 15 minutes between them, before the due date (or within 7 days if there is none).</p>
        </div>
        <div class="dialog-foot"><button type="button" class="btn" id="planCancel">Cancel</button><button class="btn primary" type="submit">Plan it</button></div>
      </form>
    </dialog>
  </main>
</div>
</body>
</html>
'''

# ===== frontend/session.html =================================================
FILES['frontend/session.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Focus Session · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/session.js"></script>
</head>
<body>
<div class="shell">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="main">
    <div class="page-head">
      <div>
        <button class="btn ghost small menu-btn" id="menuBtn" aria-label="Menu"></button>
        <h1>Focus Session</h1>
        <p>Your camera is analysed on this device. Only six numbers per frame are sent to the server, never video.</p>
      </div>
    </div>

    <!-- Step 1: setup -->
    <section id="setup" class="grid cols-2">
      <div class="card">
        <h2>Set up your session</h2>
        <div id="setupError" class="alert error hidden" role="alert"></div>
        <form id="setupForm">
          <div class="field">
            <label for="title">What are you working on?</label>
            <input id="title" maxlength="120" placeholder="e.g. Chapter 7 practice problems" required>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="subject">Subject</label>
              <input id="subject" maxlength="60" placeholder="e.g. Chemistry" list="subjectList">
              <datalist id="subjectList"></datalist>
            </div>
            <div class="field">
              <label for="planned">Planned length (minutes)</label>
              <input id="planned" type="number" min="5" max="240" value="50">
            </div>
          </div>
          <div class="field">
            <label for="eventSel">Linked schedule block (optional)</label>
            <select id="eventSel"><option value="">None</option></select>
          </div>
          <div class="field">
            <label class="check"><input type="checkbox" id="doCal" checked> Calibrate first (recommended, about 30 seconds)</label>
          </div>
          <button class="btn primary big" type="submit" id="startBtn">Start camera</button>
        </form>
      </div>
      <div class="card">
        <h2>How it works</h2>
        <ol class="small muted">
          <li><strong>Calibration.</strong> You look at the screen centre, its four corners and then your desk. This teaches NeuroFocus where <em>your</em> screen is relative to <em>your</em> camera.</li>
          <li><strong>Tracking.</strong> About 10 times a second a face-landmark model estimates head direction, eye openness and iris position.</li>
          <li><strong>Classification.</strong> Each frame is compared with your calibration: <span class="s-FOCUSED">focused</span>, <span class="s-LOOKING_AWAY">looking away</span>, <span class="s-LOOKING_DOWN">looking down</span>, <span class="s-EYES_CLOSED">eyes closed</span> or <span class="s-ABSENT">not detected</span>. A state must last ~2 s (1 s for closed eyes) before it counts, so blinks and quick glances are ignored.</li>
          <li><strong>Focus Score</strong> = percentage of session time classified as focused.</li>
        </ol>
        <div class="disclaimer small">NeuroFocus measures where your head and eyes point, not what you are thinking. Looking down to take notes may be counted as "looking down". It is a study aid, not a medical or diagnostic tool.</div>
      </div>
    </section>

    <!-- Step 2/3: camera + live -->
    <section id="live" class="session-grid hidden">
      <div class="stack">
        <div class="card">
          <div class="video-box" id="videoBox">
            <video id="video" autoplay muted playsinline></video>
            <canvas id="overlay"></canvas>
            <div class="overlay-msg" id="videoMsg">Starting camera…</div>
          </div>
          <div class="row between small">
            <label class="check"><input type="checkbox" id="privacyBlur"> Blur my preview</label>
            <label class="check"><input type="checkbox" id="showSensors"> Show sensor data</label>
            <span class="tiny" id="fps"></span>
          </div>
          <div id="sensorBox" class="feature-readout hidden"></div>
        </div>
        <div class="card">
          <div class="card-head"><h3>This session</h3><span class="tiny" id="timeLabel"></span></div>
          <div id="liveTimeline"></div>
          <div class="legend" id="legend"></div>
        </div>
      </div>
      <div class="stack">
        <div class="card center">
          <div id="statePill" class="state-pill"><span class="dot"></span><span>Waiting…</span></div>
          <div id="ringLive"></div>
          <div class="grid cols-3">
            <div class="stat"><div class="label">Elapsed</div><div class="value" id="elapsed">0:00</div></div>
            <div class="stat"><div class="label">Session score</div><div class="value" id="sessScore">–</div></div>
            <div class="stat"><div class="label">Distractions</div><div class="value" id="distractions">0</div></div>
          </div>
          <div class="meter" id="planMeter"><div></div></div>
          <div class="tiny" id="planLabel"></div>
        </div>
        <div class="card">
          <div id="liveAlert" class="alert warn hidden" role="status"></div>
          <div id="calInfo" class="small muted"></div>
          <div class="field">
            <label for="notes">Session notes</label>
            <textarea id="notes" maxlength="2000" placeholder="What did you get done?"></textarea>
          </div>
          <label class="check small hidden" id="completeWrap"><input type="checkbox" id="completeEvent" checked> Mark linked schedule block as done</label>
          <div class="row">
            <button class="btn" id="pauseBtn">Pause</button>
            <button class="btn danger" id="endBtn">End session</button>
          </div>
          <p class="tiny">Tip: keep this window visible (for example side-by-side with your work) for the most reliable tracking.</p>
        </div>
      </div>
    </section>

    <!-- Calibration overlay -->
    <div id="calStage" class="cal-stage hidden">
      <div id="calTarget" class="cal-target hidden"></div>
      <div class="cal-instructions">
        <h2 id="calTitle">Calibration</h2>
        <p id="calText" class="muted"></p>
        <div class="meter cal-progress"><div id="calBar"></div></div>
        <div id="calResult" class="hidden"></div>
        <button class="btn ghost small" id="calCancel">Cancel</button>
      </div>
    </div>
  </main>
</div>
</body>
</html>
'''

# ===== frontend/settings.html ================================================
FILES['frontend/settings.html'] = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Settings · NeuroFocus AI</title>
  <link rel="stylesheet" href="/static/css/app.css">
  <script type="module" src="/static/js/settings.js"></script>
</head>
<body>
<div class="shell">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="main">
    <div class="page-head"><div><button class="btn ghost small menu-btn" id="menuBtn" aria-label="Menu"></button><h1>Settings</h1><p>Profile, study preferences, privacy and your data.</p></div></div>
    <div class="grid cols-2">
      <form class="card" id="profileForm">
        <h2>Profile &amp; study preferences</h2>
        <div class="field"><label for="name">Name</label><input id="name" maxlength="60" required></div>
        <div class="field-row">
          <div class="field"><label for="goal">Daily focus goal (min)</label><input id="goal" type="number" min="10" max="900"></div>
          <div class="field"><label for="sessionLen">Default session length (min)</label><input id="sessionLen" type="number" min="5" max="240"></div>
        </div>
        <div class="field-row">
          <div class="field"><label for="breakLen">Break length (min)</label><input id="breakLen" type="number" min="1" max="60"></div>
          <div class="field"><label for="alertAfter">Nudge me after distracted for (s)</label><input id="alertAfter" type="number" min="5" max="600"></div>
        </div>
        <div class="field"><label class="check"><input type="checkbox" id="sound"> Play a soft chime with nudges</label></div>
        <div class="field"><label for="theme">Theme</label><select id="theme"><option value="">Match system</option><option value="light">Light</option><option value="dark">Dark</option></select></div>
        <button class="btn primary" type="submit">Save</button>
      </form>
      <div class="stack">
        <form class="card" id="pwForm">
          <h2>Change password</h2>
          <div class="field"><label for="curPw">Current password</label><input id="curPw" type="password" autocomplete="current-password" required></div>
          <div class="field"><label for="newPw">New password</label><input id="newPw" type="password" autocomplete="new-password" minlength="10" required></div>
          <button class="btn" type="submit">Update password</button>
        </form>
        <div class="card">
          <h2>Privacy &amp; data</h2>
          <ul class="small muted">
            <li>Video is processed in your browser and never uploaded or stored.</li>
            <li>Stored per session: calibration values, one attention state per second, distraction episodes, and the scores shown to you.</li>
            <li>Passwords are stored only as salted, slow hashes (scrypt).</li>
          </ul>
          <div class="row"><a class="btn" href="/api/account/export" download>Download my data (JSON)</a></div>
          <hr>
          <h3 class="s-LOOKING_AWAY">Delete account</h3>
          <p class="small muted">Permanently deletes your account, sessions, schedule and tasks.</p>
          <form id="deleteForm" class="row">
            <input id="delPw" type="password" placeholder="Confirm with your password" autocomplete="current-password" required aria-label="Password" class="grow">
            <button class="btn danger" type="submit">Delete everything</button>
          </form>
        </div>
      </div>
    </div>
  </main>
</div>
</body>
</html>
'''

# ===== frontend/vendor/README.md =============================================
FILES['frontend/vendor/README.md'] = r'''# Vendored third-party files

Bundled locally so the app works offline (e.g. at a science fair with no Wi-Fi)
and so the Content-Security-Policy can forbid all third-party scripts.

| Path | Source | Version | License |
|---|---|---|---|
| `mediapipe/vision_bundle.mjs`, `mediapipe/wasm/*` | npm package `@mediapipe/tasks-vision` | 0.10.14 | Apache-2.0 |
| `models/face_landmarker.task` | https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task | float16 v1 | Apache-2.0 (see the MediaPipe Face Landmarker model card) |

SHA-256 at the time of vendoring:

```
64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff  models/face_landmarker.task
e77f281f9619150d937023c355bae170e9120e3b9e43f1e23a2a7bee07197669  mediapipe/vision_bundle.mjs
```

Record these in your research paper's Materials section: the face-landmark
model is a fixed, versioned component of the system under test.
'''

# ===== neurofocus_engine/__init__.py =========================================
FILES['neurofocus_engine/__init__.py'] = r'''"""NeuroFocus attention engine.

This package is shared by the web backend and the research pipeline, so the
algorithm evaluated in the experiment is exactly the algorithm users run.
It must never import from research/ (the simulator / ground truth); a test in
tests/test_separation.py enforces this.
"""

from .params import (EngineParams, DEFAULT_PARAMS, ENGINE_VERSION, STATES,
                     DISTRACTED_STATES, FOCUSED, LOOKING_AWAY, LOOKING_DOWN,
                     EYES_CLOSED, ABSENT)
from .features import FeatureFrame, FEATURE_COLUMNS
from .calibration import Calibration, calibrate, default_calibration
from .classifier import AttentionEngine, TemporalFilter, raw_state
from .scoring import focus_score, episodes, LiveScore
'''

# ===== neurofocus_engine/calibration.py ======================================
FILES['neurofocus_engine/calibration.py'] = r'''"""Personal calibration.

Protocol (identical in the web app and in the simulator):
  phase "center"  ~10 s  look at the middle of the screen as if studying
  phase "corners" ~12 s  look at each screen corner in turn (3 s each)
  phase "down"     ~4 s  look down at the desk/keyboard

From these frames we estimate the person's neutral head pose (camera placement
differs between people), the angular size of their screen, and their open-eye
EAR. Thresholds are then expressed relative to this personal baseline.
"""

from dataclasses import dataclass, asdict
import math
import statistics

from .params import DEFAULT_PARAMS


def _median(xs):
    return statistics.median(xs) if xs else math.nan


def _mad(xs):
    if len(xs) < 2:
        return math.nan
    m = statistics.median(xs)
    return statistics.median(abs(x - m) for x in xs)


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


@dataclass
class Calibration:
    calibrated: bool
    yaw0: float
    pitch0: float
    ear0: float
    gaze_h0: float
    yaw_threshold: float
    pitch_down_threshold: float
    ear_closed_threshold: float
    pitch_sign: float = 1.0      # flipped if the "down" phase shows pitch increasing
    quality: str = "default"
    warnings: tuple = ()

    def to_dict(self):
        d = asdict(self)
        d["warnings"] = list(self.warnings)
        return d

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        d["warnings"] = tuple(d.get("warnings", ()))
        return cls(**d)


def default_calibration(params=DEFAULT_PARAMS):
    """Population defaults, used when a user skips calibration (and as the
    'uncalibrated' experimental condition)."""
    return Calibration(
        calibrated=False,
        yaw0=params.default_yaw_deg,
        pitch0=params.default_pitch_deg,
        ear0=params.default_ear,
        gaze_h0=params.default_gaze_h,
        yaw_threshold=params.default_yaw_threshold_deg,
        pitch_down_threshold=params.default_pitch_down_threshold_deg,
        ear_closed_threshold=params.default_ear * params.ear_closed_ratio,
    )


def calibrate(frames_by_phase, params=DEFAULT_PARAMS):
    """frames_by_phase: dict phase -> list[FeatureFrame].

    Returns (Calibration, ok: bool). When ok is False the caller should ask the
    user to repeat calibration; the returned object still holds best-effort
    values plus warnings explaining the problem.
    """
    warnings = []
    center = frames_by_phase.get("center", [])
    seen = [f for f in center if f.face_present]
    if not center:
        return default_calibration(params), False
    face_fraction = len(seen) / len(center)
    if face_fraction < params.min_calibration_face_fraction or len(seen) < 10:
        warnings.append(f"Face detected in only {face_fraction:.0%} of centre frames.")
        cal = default_calibration(params)
        cal.warnings = tuple(warnings)
        cal.quality = "failed"
        return cal, False

    yaws = [f.yaw for f in seen]
    pitches = [f.pitch for f in seen]
    ears = [f.ear for f in seen if not math.isnan(f.ear)]
    gazes = [f.gaze_h for f in seen if not math.isnan(f.gaze_h)]
    yaw0, pitch0 = _median(yaws), _median(pitches)
    ear0 = _median(ears) if ears else params.default_ear
    gaze0 = _median(gazes) if gazes else 0.0
    ok = True
    if max(_mad(yaws), _mad(pitches)) > params.max_calibration_pose_mad_deg:
        warnings.append("Head was moving a lot during the centre phase.")
        ok = False

    # Direction of "down": verify with the down phase (guards against a sign
    # convention mismatch between camera pipelines).
    pitch_sign = 1.0
    down = [f for f in frames_by_phase.get("down", []) if f.face_present]
    down_dev = None
    if len(down) >= 5:
        down_dev = _median([f.pitch for f in down]) - pitch0
        if down_dev > 0:
            pitch_sign = -1.0
            down_dev = -down_dev
        if abs(down_dev) < 5:
            warnings.append("Looking down barely changed head pitch; down-detection may be weak.")
    else:
        warnings.append("Down phase missing; assuming standard pitch direction.")

    # Screen envelope from the corner looks.
    corners = [f for f in frames_by_phase.get("corners", []) if f.face_present]
    if len(corners) >= 10:
        yaw_span = max(abs(f.yaw - yaw0 + params.gaze_to_deg * ((f.gaze_h if not math.isnan(f.gaze_h) else gaze0) - gaze0))
                       for f in corners)
        lowest = min(pitch_sign * (f.pitch - pitch0) for f in corners)
        yaw_thr = _clamp(yaw_span + params.yaw_margin_deg, *params.yaw_threshold_bounds)
        pitch_thr = _clamp(abs(min(lowest, 0.0)) + params.pitch_margin_deg, *params.pitch_threshold_bounds)
    else:
        warnings.append("Corner phase missing; using default screen size.")
        yaw_thr = params.default_yaw_threshold_deg
        pitch_thr = params.default_pitch_down_threshold_deg

    # If looking at the desk was not clearly beyond the threshold, move the
    # threshold to halfway between the lowest corner and the desk.
    if down_dev is not None and abs(down_dev) <= pitch_thr:
        pitch_thr = _clamp(abs(down_dev) * 0.75, *params.pitch_threshold_bounds)

    cal = Calibration(
        calibrated=True, yaw0=yaw0, pitch0=pitch0, ear0=ear0, gaze_h0=gaze0,
        yaw_threshold=yaw_thr, pitch_down_threshold=pitch_thr,
        ear_closed_threshold=ear0 * params.ear_closed_ratio,
        pitch_sign=pitch_sign, quality="good" if ok and not warnings else "fair",
        warnings=tuple(warnings),
    )
    return cal, ok
'''

# ===== neurofocus_engine/classifier.py =======================================
FILES['neurofocus_engine/classifier.py'] = r'''"""Frame classification + temporal filtering.

Stage 1 (instantaneous): each frame gets a raw state from fixed rules applied
to deviations from the calibrated baseline. Rule order = priority:
  1. no face                                   -> ABSENT
  2. EAR below closed-eye threshold            -> EYES_CLOSED
  3. head pitched down beyond threshold        -> LOOKING_DOWN
  4. |head yaw + eye gaze| beyond threshold    -> LOOKING_AWAY
  5. otherwise                                 -> FOCUSED

Stage 2 (temporal): a non-focused raw state is only reported after it has
persisted for onset_s[state] seconds, and the filter returns to FOCUSED after
recovery_s seconds of focused frames. This suppresses blinks, brief glances
and single-frame detector misses, at the cost of a built-in detection delay.
"""

import math

from .params import (DEFAULT_PARAMS, FOCUSED, LOOKING_AWAY, LOOKING_DOWN,
                     EYES_CLOSED, ABSENT)


def raw_state(frame, cal, params=DEFAULT_PARAMS):
    if not frame.face_present:
        return ABSENT
    if not math.isnan(frame.ear) and frame.ear < cal.ear_closed_threshold:
        return EYES_CLOSED
    dpitch = cal.pitch_sign * (frame.pitch - cal.pitch0)
    if dpitch < -cal.pitch_down_threshold:
        return LOOKING_DOWN
    dgaze = 0.0 if math.isnan(frame.gaze_h) else frame.gaze_h - cal.gaze_h0
    horizontal = (frame.yaw - cal.yaw0) + params.gaze_to_deg * dgaze
    if abs(horizontal) > cal.yaw_threshold:
        return LOOKING_AWAY
    return FOCUSED


class TemporalFilter:
    """Streaming state machine. Feed frames in time order with update()."""

    def __init__(self, params=DEFAULT_PARAMS):
        self.params = params
        self.state = FOCUSED
        self._cand = FOCUSED
        self._cand_since = None

    def update(self, t, raw):
        if raw != self._cand:
            self._cand, self._cand_since = raw, t
        if self._cand_since is None:
            self._cand_since = t
        held = t - self._cand_since
        if self._cand == self.state:
            return self.state
        if self._cand == FOCUSED:
            if held >= self.params.recovery_s:
                self.state = FOCUSED
        elif held >= self.params.onset_s[self._cand]:
            self.state = self._cand
        return self.state


class AttentionEngine:
    """Calibration + classifier + filter for one study session."""

    def __init__(self, calibration, params=DEFAULT_PARAMS):
        self.cal = calibration
        self.params = params
        self.filter = TemporalFilter(params)

    def process(self, frame):
        raw = raw_state(frame, self.cal, self.params)
        return raw, self.filter.update(frame.t, raw)

    def process_many(self, frames):
        return [(f.t, *self.process(f)) for f in frames]
'''

# ===== neurofocus_engine/features.py =========================================
FILES['neurofocus_engine/features.py'] = r'''"""The feature frame: the ONLY input the engine ever receives.

In the web app these numbers are computed in the browser from MediaPipe Face
Landmarker output (frontend/js/vision.js); raw video never leaves the device.
In the experiment they are read from the simulator's features CSV files.
The engine never sees ground-truth labels.
"""

from dataclasses import dataclass
import math

FEATURE_COLUMNS = ("t", "face_present", "yaw", "pitch", "ear", "gaze_h", "gaze_v")


@dataclass
class FeatureFrame:
    t: float              # seconds since session start
    face_present: bool
    yaw: float = math.nan     # head yaw, degrees (sign arbitrary; engine uses deviation)
    pitch: float = math.nan   # head pitch, degrees, positive = up
    ear: float = math.nan     # mean eye aspect ratio of both eyes
    gaze_h: float = math.nan  # horizontal iris offset within eye, -1..1
    gaze_v: float = math.nan  # vertical iris offset within eye, -1..1

    @classmethod
    def from_dict(cls, d):
        def num(key):
            v = d.get(key)
            try:
                v = float(v)
            except (TypeError, ValueError):
                return math.nan
            return v if math.isfinite(v) else math.nan

        present = d.get("face_present")
        if isinstance(present, str):
            present = present.strip().lower() in ("1", "true", "yes")
        frame = cls(t=num("t"), face_present=bool(present), yaw=num("yaw"),
                    pitch=num("pitch"), ear=num("ear"), gaze_h=num("gaze_h"),
                    gaze_v=num("gaze_v"))
        if not math.isfinite(frame.t):
            raise ValueError("frame is missing a numeric 't'")
        # A frame claiming a face but lacking pose is treated as no detection.
        if frame.face_present and (math.isnan(frame.yaw) or math.isnan(frame.pitch)):
            frame.face_present = False
        return frame
'''

# ===== neurofocus_engine/params.py ===========================================
FILES['neurofocus_engine/params.py'] = r'''"""All tunable constants of the NeuroFocus attention engine, in one place.

Every number here is a design choice, not an empirically validated constant.
They are fixed BEFORE an experiment run and recorded in the run manifest so
results are reproducible. Changing any value means a new experiment version.
See research/docs/03_algorithm.md for the rationale behind each value.
"""

from dataclasses import dataclass, asdict, field

# Attention states produced by the engine (and used as ground-truth vocabulary
# by the simulator, which defines them independently in its own module).
FOCUSED = "FOCUSED"
LOOKING_AWAY = "LOOKING_AWAY"
LOOKING_DOWN = "LOOKING_DOWN"
EYES_CLOSED = "EYES_CLOSED"
ABSENT = "ABSENT"
STATES = (FOCUSED, LOOKING_AWAY, LOOKING_DOWN, EYES_CLOSED, ABSENT)
DISTRACTED_STATES = (LOOKING_AWAY, LOOKING_DOWN, EYES_CLOSED, ABSENT)


@dataclass(frozen=True)
class EngineParams:
    # --- Population defaults used when NO personal calibration is available ---
    default_yaw_deg: float = 0.0
    default_pitch_deg: float = 0.0
    default_ear: float = 0.28
    default_gaze_h: float = 0.0
    default_yaw_threshold_deg: float = 25.0
    default_pitch_down_threshold_deg: float = 20.0

    # --- Calibration-derived threshold rules ---
    yaw_margin_deg: float = 8.0          # added beyond the widest screen-corner look
    pitch_margin_deg: float = 6.0        # added beyond the lowest screen-corner look
    yaw_threshold_bounds: tuple = (15.0, 45.0)
    pitch_threshold_bounds: tuple = (10.0, 35.0)
    ear_closed_ratio: float = 0.65       # eyes "closed" when EAR < ratio * personal open-eye EAR
    min_calibration_face_fraction: float = 0.85
    max_calibration_pose_mad_deg: float = 4.0

    # --- Combining head and eye direction ---
    gaze_to_deg: float = 30.0            # normalized iris offset (-1..1) -> approx. degrees

    # --- Temporal filter (seconds a raw state must persist before it is reported) ---
    onset_s: dict = field(default_factory=lambda: {
        LOOKING_AWAY: 2.0,
        LOOKING_DOWN: 2.0,
        EYES_CLOSED: 1.0,   # longer than a normal blink (~0.1-0.4 s)
        ABSENT: 2.0,
    })
    recovery_s: float = 0.5              # focused this long before returning to FOCUSED

    # --- Focus Score ---
    live_window_s: float = 60.0          # trailing window for the live score

    def to_dict(self):
        d = asdict(self)
        d["yaw_threshold_bounds"] = list(self.yaw_threshold_bounds)
        d["pitch_threshold_bounds"] = list(self.pitch_threshold_bounds)
        return d


DEFAULT_PARAMS = EngineParams()
ENGINE_VERSION = "1.0.0"
'''

# ===== neurofocus_engine/scoring.py ==========================================
FILES['neurofocus_engine/scoring.py'] = r'''"""Focus Score and distraction-episode extraction.

Focus Score (0-100) = 100 x (time the filtered state is FOCUSED) / (elapsed time)

Time is measured by frame durations (gap to the next frame, capped so a pause
in data does not count as either focused or distracted). Time with no face
counts as not focused, because the engine reports it as ABSENT.

The definition is deliberately simple so it can be checked directly against
the simulator's ground-truth on-task percentage.
"""

from collections import deque

from .params import DEFAULT_PARAMS, FOCUSED

MAX_FRAME_GAP_S = 1.0


def focus_score(timeline):
    """timeline: list of (t, state) in time order. Returns score or None."""
    focused = total = 0.0
    for (t, s), (t_next, _) in zip(timeline, timeline[1:]):
        dt = min(max(t_next - t, 0.0), MAX_FRAME_GAP_S)
        total += dt
        if s == FOCUSED:
            focused += dt
    if total <= 0:
        return None
    return 100.0 * focused / total


def episodes(timeline):
    """Contiguous non-FOCUSED runs: list of dict(state, start, end)."""
    out, cur = [], None
    for t, s in timeline:
        if cur and (s != cur["state"]):
            cur["end"] = t
            out.append(cur)
            cur = None
        if s != FOCUSED and cur is None:
            cur = {"state": s, "start": t, "end": t}
    if cur:
        cur["end"] = timeline[-1][0]
        out.append(cur)
    return out


class LiveScore:
    """Trailing-window Focus Score for the live dashboard."""

    def __init__(self, params=DEFAULT_PARAMS):
        self.window = params.live_window_s
        self.buf = deque()

    def add(self, t, state):
        self.buf.append((t, state))
        while self.buf and t - self.buf[0][0] > self.window:
            self.buf.popleft()
        return focus_score(list(self.buf))
'''

# ===== requirements.txt ======================================================
FILES['requirements.txt'] = r'''flask>=3.0
numpy>=1.26
scipy>=1.11
matplotlib>=3.8
pytest>=8.0
'''

# ===== research/README.md ====================================================
FILES['research/README.md'] = r'''# NeuroFocus AI: research package

This folder holds everything for the **science-fair experiment**, kept
separate from the product code so it is clear which is which.

| | Product (`backend/`, `frontend/`) | Experiment (`research/`) |
|---|---|---|
| Purpose | A working study app | Measure how accurate the attention engine is |
| Evidence of quality | Automated software tests | Quantitative results with statistics |
| Shared code | `neurofocus_engine/`, the exact same algorithm in both | |

## Read in this order

1. [`docs/01_research_question.md`](docs/01_research_question.md): problem, question, hypotheses, variables
2. [`docs/02_procedure.md`](docs/02_procedure.md): step-by-step procedure, pre-specified analysis, data management
3. [`docs/03_algorithm.md`](docs/03_algorithm.md): features, calibration, rules, filter, Focus Score
4. [`docs/04_simulator_model.md`](docs/04_simulator_model.md): virtual students and all their assumptions
5. [`docs/05_evaluation_metrics.md`](docs/05_evaluation_metrics.md): metric definitions
6. [`docs/06_limitations_and_ethics.md`](docs/06_limitations_and_ethics.md): what you can and cannot claim
7. [`docs/07_references.md`](docs/07_references.md): references (verify each one)
8. [`docs/08_lab_notebook_template.md`](docs/08_lab_notebook_template.md)

## Run it

```bash
pip install -r requirements.txt
python -m pytest                                    # software tests
python -m research.pipeline.run_experiment --config research/config/experiment_v1.json
python -m research.pipeline.run_experiment --config research/config/onset_sweep_v1.json   # exploratory
```

A full primary run (30 students x 3 noise levels x 2 conditions, 20-minute
sessions) takes a few minutes on a laptop. Results appear in
`research/results/<run_id>/`, starting with `statistics_report.md`, and on
the app's **Research & Method** page.

## Folder map

```
research/
  config/        experiment definitions (a changed config = a new experiment)
  simulator/     virtual students + ground-truth definitions (never imported by the engine)
  pipeline/      predict.py (blind engine run) and run_experiment.py (orchestrator)
  analysis/      evaluate.py, statistics.py, figures.py
  data/raw/      simulator output: features/ and ground_truth/ in separate folders (not in git)
  data/processed/engine predictions (not in git)
  results/       metrics, confusion matrices, statistics, figures, manifest (commit these)
  docs/          methodology documents for the paper and the judges
```

## Status

No official experiment results exist yet. Run the official experiment
yourself, after completing the "Before the official run" checklist in
`docs/02_procedure.md`.
'''

# ===== research/__init__.py ==================================================
FILES['research/__init__.py'] = r''''''

# ===== research/analysis/__init__.py =========================================
FILES['research/analysis/__init__.py'] = r''''''

# ===== research/analysis/evaluate.py =========================================
FILES['research/analysis/evaluate.py'] = r'''"""Stage 3 - compare engine predictions with ground truth.

This is the first stage allowed to read BOTH predictions and ground truth.

Metrics (definitions in research/docs/05_evaluation_metrics.md):
  frame level (positive class = distracted):
    accuracy, precision, recall (sensitivity), specificity, F1, balanced accuracy, Cohen's kappa
  multiclass: 5x5 confusion matrix (expected state x predicted state),
              7x5 behavior x predicted state matrix
  episode level: episode recall, correct-type rate, detection latency, false alarms per hour
  Focus Score: |engine Focus Score - ground-truth on-task %|

Usage: python -m research.analysis.evaluate --run-id RUN
"""

import argparse
import csv
import json
import statistics
from pathlib import Path

from research.simulator.ground_truth import BEHAVIORS, STATE_ORDER

ROOT = Path(__file__).resolve().parents[1]
FOCUSED = "FOCUSED"


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _safe_div(a, b):
    return a / b if b else None


def binary_metrics(gt_distracted, pred_distracted):
    tp = sum(g and p for g, p in zip(gt_distracted, pred_distracted))
    fp = sum((not g) and p for g, p in zip(gt_distracted, pred_distracted))
    fn = sum(g and (not p) for g, p in zip(gt_distracted, pred_distracted))
    tn = sum((not g) and (not p) for g, p in zip(gt_distracted, pred_distracted))
    n = tp + fp + fn + tn
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    spec = _safe_div(tn, tn + fp)
    f1 = _safe_div(2 * tp, 2 * tp + fp + fn)
    acc = _safe_div(tp + tn, n)
    p_yes = ((tp + fp) / n) * ((tp + fn) / n) if n else 0
    p_no = ((tn + fn) / n) * ((tn + fp) / n) if n else 0
    pe = p_yes + p_no
    kappa = _safe_div(acc - pe, 1 - pe) if acc is not None else None
    bal = (recall + spec) / 2 if recall is not None and spec is not None else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "accuracy": acc,
            "precision_distracted": precision, "recall_distracted": recall,
            "specificity": spec, "f1_distracted": f1, "balanced_accuracy": bal,
            "cohen_kappa": kappa}


def gt_episodes(truth):
    eps, cur = [], None
    for r in truth:
        t, distracted = float(r["t"]), r["on_task"] == "0"
        if cur and (not distracted or r["episode_id"] != cur["id"]):
            eps.append(cur)
            cur = None
        if distracted and cur is None:
            cur = {"id": r["episode_id"], "behavior": r["behavior"],
                   "gt_state": r["gt_state"], "start": t, "end": t}
        if cur:
            cur["end"] = t
    if cur:
        eps.append(cur)
    return eps


def pred_episodes(times, states):
    eps, cur = [], None
    for i, (t, s) in enumerate(zip(times, states)):
        if cur and s == FOCUSED:
            eps.append(cur)
            cur = None
        if s != FOCUSED and cur is None:
            cur = {"start_i": i, "end_i": i}
        if cur:
            cur["end_i"] = i
    if cur:
        eps.append(cur)
    return eps


def evaluate_student(truth, pred, grace_s, hz):
    times = [float(r["t"]) for r in truth]
    if len(truth) != len(pred) or any(abs(float(p["t"]) - t) > 1e-6 for p, t in zip(pred, times)):
        raise ValueError("prediction and ground-truth timelines do not align")
    states = [p["state"] for p in pred]
    gt_dis = [r["on_task"] == "0" for r in truth]
    m = binary_metrics(gt_dis, [s != FOCUSED for s in states])

    conf = {g: {p: 0 for p in STATE_ORDER} for g in STATE_ORDER}
    bconf = {b: {p: 0 for p in STATE_ORDER} for b in BEHAVIORS}
    for r, s in zip(truth, states):
        conf[r["gt_state"]][s] += 1
        bconf[r["behavior"]][s] += 1

    # Episode-level detection
    episodes = []
    for e in gt_episodes(truth):
        i0 = int(round(e["start"] * hz))
        i1 = min(len(states) - 1, int(round((e["end"] + grace_s) * hz)))
        hits = [i for i in range(i0, i1 + 1) if states[i] != FOCUSED]
        rec = {"behavior": e["behavior"], "gt_state": e["gt_state"],
               "duration_s": round(e["end"] - e["start"] + 1 / hz, 3),
               "detected": bool(hits), "latency_s": None, "type_correct": False}
        if hits:
            rec["latency_s"] = round(times[hits[0]] - e["start"], 3)
            votes = [states[i] for i in hits]
            rec["type_correct"] = max(set(votes), key=votes.count) == e["gt_state"]
        episodes.append(rec)

    fa_by_behavior = {}
    false_alarms = 0
    for pe in pred_episodes(times, states):
        span = range(pe["start_i"], pe["end_i"] + 1)
        if not any(gt_dis[i] for i in span):
            false_alarms += 1
            behs = [truth[i]["behavior"] for i in span]
            b = max(set(behs), key=behs.count)
            fa_by_behavior[b] = fa_by_behavior.get(b, 0) + 1
    on_task_hours = sum(1 for g in gt_dis if not g) / hz / 3600

    detected = [e for e in episodes if e["detected"]]
    lat = [e["latency_s"] for e in detected]
    gt_pct = 100 * sum(1 for g in gt_dis if not g) / len(gt_dis)
    pred_pct = 100 * sum(1 for s in states if s == FOCUSED) / len(states)
    m.update({
        "n_gt_episodes": len(episodes),
        "episode_recall": _safe_div(len(detected), len(episodes)),
        "episode_type_accuracy": _safe_div(sum(e["type_correct"] for e in detected), len(detected)),
        "median_latency_s": statistics.median(lat) if lat else None,
        "mean_latency_s": statistics.fmean(lat) if lat else None,
        "false_alarms": false_alarms,
        "false_alarms_per_hour": _safe_div(false_alarms, on_task_hours),
        "gt_focus_pct": gt_pct,
        "engine_focus_score": pred_pct,
        "focus_score_abs_error": abs(pred_pct - gt_pct),
        "focus_score_signed_error": pred_pct - gt_pct,
    })
    return m, conf, bconf, episodes, fa_by_behavior


def _summ(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "mean": statistics.fmean(vals),
            "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "median": statistics.median(vals), "min": min(vals), "max": max(vals)}


def evaluate(run_id):
    raw = ROOT / "data" / "raw" / run_id
    pred_root = ROOT / "data" / "processed" / run_id / "predictions"
    out = ROOT / "results" / run_id
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads((raw / "config.json").read_text())
    hz, grace = config["frame_rate_hz"], config["evaluation"]["detection_grace_s"]
    truths = {sid: _read(raw / "ground_truth" / f"student_{sid:02d}.csv")
              for sid in range(1, config["n_students"] + 1)}

    rows, ep_rows, summary = [], [], {}
    for level in config["noise_levels"]:
        for cond in config["conditions"]:
            name = cond["name"]
            pooled = {g: {p: 0 for p in STATE_ORDER} for g in STATE_ORDER}
            pooled_b = {b: {p: 0 for p in STATE_ORDER} for b in BEHAVIORS}
            fa_pooled, cal_failures = {}, 0
            for sid, truth in truths.items():
                pdir = pred_root / level / name
                pred = _read(pdir / f"student_{sid:02d}.csv")
                cal_info = json.loads((pdir / f"student_{sid:02d}_calibration.json").read_text())
                cal_failures += int(cond["use_calibration"] and not cal_info["calibration_ok"])
                m, conf, bconf, eps, fab = evaluate_student(truth, pred, grace, hz)
                rows.append({"run_id": run_id, "noise": level, "condition": name,
                             "student": sid, "calibration_ok": cal_info["calibration_ok"], **m})
                for e in eps:
                    ep_rows.append({"noise": level, "condition": name, "student": sid, **e})
                for g in STATE_ORDER:
                    for p in STATE_ORDER:
                        pooled[g][p] += conf[g][p]
                for b in BEHAVIORS:
                    for p in STATE_ORDER:
                        pooled_b[b][p] += bconf[b][p]
                for b, c in fab.items():
                    fa_pooled[b] = fa_pooled.get(b, 0) + c
            _write_matrix(out / f"confusion_states_{level}_{name}.csv", pooled, STATE_ORDER)
            _write_matrix(out / f"confusion_behaviors_{level}_{name}.csv", pooled_b, BEHAVIORS)
            sub = [r for r in rows if r["noise"] == level and r["condition"] == name]
            metric_keys = [k for k in sub[0] if k not in ("run_id", "noise", "condition", "student", "calibration_ok")]
            summary.setdefault(level, {})[name] = {
                "metrics": {k: _summ([r[k] for r in sub]) for k in metric_keys},
                "pooled_state_confusion": pooled,
                "pooled_behavior_confusion": pooled_b,
                "false_alarms_by_behavior": fa_pooled,
                "calibration_failures": cal_failures,
            }

    _write_rows(out / "metrics_per_student.csv", rows)
    _write_rows(out / "episodes.csv", ep_rows)
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    return out


def _write_rows(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _write_matrix(path, m, row_labels):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["truth \\ predicted", *STATE_ORDER])
        for r in row_labels:
            w.writerow([r, *[m[r][c] for c in STATE_ORDER]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"evaluation written to {evaluate(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
'''

# ===== research/analysis/figures.py ==========================================
FILES['research/analysis/figures.py'] = r'''"""Stage 5 - figures for the research paper / poster.

Usage: python -m research.analysis.figures --run-id RUN
"""

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from research.simulator.ground_truth import STATE_ORDER, BEHAVIORS

ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#2563eb", "#ea580c", "#16a34a", "#9333ea"]


def _rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _matrix_plot(path, out, title):
    rows = _rows(path)
    labels = [r["truth \\ predicted"] for r in rows]
    m = np.array([[float(r[c]) for c in STATE_ORDER] for r in rows])
    norm = m / np.maximum(m.sum(axis=1, keepdims=True), 1)
    fig, ax = plt.subplots(figsize=(7, 0.6 * len(labels) + 2))
    ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
    for i in range(len(labels)):
        for j in range(len(STATE_ORDER)):
            ax.text(j, i, f"{norm[i, j]:.2f}", ha="center", va="center",
                    color="white" if norm[i, j] > 0.6 else "black", fontsize=8)
    ax.set_xticks(range(len(STATE_ORDER)), [s.replace("_", "\n") for s in STATE_ORDER], fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.set_xlabel("Engine output")
    ax.set_ylabel("Ground truth")
    ax.set_title(title + "\n(row-normalized: share of each true class's frames)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def make_figures(run_id):
    res = ROOT / "results" / run_id
    figdir = res / "figures"
    figdir.mkdir(exist_ok=True)
    cfg = json.loads((ROOT / "data" / "raw" / run_id / "config.json").read_text())
    levels = list(cfg["noise_levels"])
    conds = [c["name"] for c in cfg["conditions"]]
    rows = _rows(res / "metrics_per_student.csv")

    metrics = ["f1_distracted", "focus_score_abs_error", "median_latency_s", "false_alarms_per_hour"]
    for metric in metrics:
        fig, ax = plt.subplots(figsize=(6.5, 4))
        width = 0.8 / len(conds)
        for ci, cond in enumerate(conds):
            for li, lv in enumerate(levels):
                vals = [_num(r[metric]) for r in rows if r["noise"] == lv and r["condition"] == cond]
                vals = [v for v in vals if v is not None]
                x = li + (ci - (len(conds) - 1) / 2) * width
                bp = ax.boxplot(vals, positions=[x], widths=width * 0.8, patch_artist=True,
                                showfliers=False)
                for patch in bp["boxes"]:
                    patch.set_facecolor(COLORS[ci % len(COLORS)])
                    patch.set_alpha(0.5)
                jitter = np.random.default_rng(ci * 10 + li).uniform(-width * 0.25, width * 0.25, len(vals))
                ax.scatter(x + jitter, vals, s=8, color=COLORS[ci % len(COLORS)], zorder=3)
        ax.set_xticks(range(len(levels)), [f"{lv} noise" for lv in levels])
        ax.set_ylabel(metric.replace("_", " "))
        handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[i % len(COLORS)], alpha=0.5) for i in range(len(conds))]
        ax.legend(handles, conds, fontsize=8)
        ax.set_title(f"{metric.replace('_', ' ')} per virtual student (n={cfg['n_students']})", fontsize=10)
        fig.tight_layout()
        fig.savefig(figdir / f"{metric}.png", dpi=200)
        plt.close(fig)

    # Paired lines for the primary comparison
    pc = cfg.get("primary_comparison")
    if pc:
        fig, axes = plt.subplots(1, len(levels), figsize=(3.2 * len(levels), 3.6), sharey=True)
        axes = np.atleast_1d(axes)
        for ax, lv in zip(axes, levels):
            a = {r["student"]: _num(r[pc["metric"]]) for r in rows if r["noise"] == lv and r["condition"] == pc["control"]}
            b = {r["student"]: _num(r[pc["metric"]]) for r in rows if r["noise"] == lv and r["condition"] == pc["treatment"]}
            for s in a:
                ax.plot([0, 1], [a[s], b[s]], color="gray", alpha=0.5, lw=0.8, marker="o", ms=3)
            ax.set_xticks([0, 1], [pc["control"], pc["treatment"]], fontsize=8)
            ax.set_title(f"{lv} noise", fontsize=9)
        axes[0].set_ylabel(pc["metric"].replace("_", " "))
        fig.suptitle("Paired results: each line is one virtual student", fontsize=10)
        fig.tight_layout()
        fig.savefig(figdir / "paired_primary.png", dpi=200)
        plt.close(fig)

    # Latency vs false alarms trade-off (useful for the onset sweep)
    fig, ax = plt.subplots(figsize=(5.5, 4))
    for ci, cond in enumerate(conds):
        for li, lv in enumerate(levels):
            sel = [r for r in rows if r["noise"] == lv and r["condition"] == cond]
            lat = np.nanmean([_num(r["median_latency_s"]) or np.nan for r in sel])
            fa = np.mean([_num(r["false_alarms_per_hour"]) for r in sel])
            ax.scatter(lat, fa, color=COLORS[ci % len(COLORS)], marker="osD^"[li % 4], s=50,
                       label=f"{cond} / {lv}")
    ax.set_xlabel("mean of per-student median detection latency (s)")
    ax.set_ylabel("mean false alarms per on-task hour")
    ax.legend(fontsize=7)
    ax.set_title("Detection speed vs false alarms", fontsize=10)
    fig.tight_layout()
    fig.savefig(figdir / "latency_vs_false_alarms.png", dpi=200)
    plt.close(fig)

    for lv in levels:
        for cond in conds:
            _matrix_plot(res / f"confusion_states_{lv}_{cond}.csv",
                         figdir / f"confusion_states_{lv}_{cond}.png",
                         f"State confusion matrix - {cond}, {lv} noise")
            _matrix_plot(res / f"confusion_behaviors_{lv}_{cond}.csv",
                         figdir / f"confusion_behaviors_{lv}_{cond}.png",
                         f"Behavior x engine output - {cond}, {lv} noise")
    return figdir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"figures written to {make_figures(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
'''

# ===== research/analysis/statistics.py =======================================
FILES['research/analysis/statistics.py'] = r'''"""Stage 4 - statistical analysis (pre-specified in research/docs/02_procedure.md).

Primary test, at each noise level separately:
  paired difference (treatment - control) of the primary metric across virtual
  students; Wilcoxon signed-rank test (two-sided); Holm-Bonferroni correction
  across noise levels; bootstrap 95% CI of the mean difference; effect sizes:
  matched-pairs rank-biserial correlation and Cohen's d_z.
Noise effect: Friedman test across noise levels within each condition.
Everything else is descriptive (mean, SD, bootstrap 95% CI).

Usage: python -m research.analysis.statistics --run-id RUN
"""

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


def _load(run_id):
    with open(ROOT / "results" / run_id / "metrics_per_student.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except (TypeError, ValueError):
                r[k] = None if v in ("", "None") else v
    return rows


def _values(rows, level, cond, metric):
    sel = sorted((r for r in rows if r["noise"] == level and r["condition"] == cond),
                 key=lambda r: r["student"])
    return [r[metric] for r in sel]


def bootstrap_ci(x, n_boot, seed, stat=np.mean):
    x = np.asarray([v for v in x if v is not None], dtype=float)
    if len(x) < 2:
        return (math.nan, math.nan)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = stat(x[idx], axis=1)
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def paired_test(a, b, n_boot, seed):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    d = np.array([x - y for x, y in pairs])
    res = {"n_pairs": len(d), "mean_a": float(np.mean([p[0] for p in pairs])),
           "mean_b": float(np.mean([p[1] for p in pairs])), "mean_diff": float(np.mean(d)),
           "median_diff": float(np.median(d))}
    res["ci95_mean_diff"] = bootstrap_ci(d, n_boot, seed)
    sd = float(np.std(d, ddof=1)) if len(d) > 1 else math.nan
    res["cohen_dz"] = float(np.mean(d) / sd) if sd and sd > 0 else math.nan
    nz = d[d != 0]
    if len(nz) == 0:
        res.update(W=math.nan, p_value=1.0, rank_biserial=0.0)
        return res
    w = stats.wilcoxon(nz)
    ranks = stats.rankdata(np.abs(nz))
    w_pos, w_neg = ranks[nz > 0].sum(), ranks[nz < 0].sum()
    res.update(W=float(w.statistic), p_value=float(w.pvalue),
               rank_biserial=float((w_pos - w_neg) / (w_pos + w_neg)))
    return res


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def analyze(run_id):
    raw_cfg = json.loads((ROOT / "data" / "raw" / run_id / "config.json").read_text())
    rows = _load(run_id)
    levels = list(raw_cfg["noise_levels"])
    conds = [c["name"] for c in raw_cfg["conditions"]]
    n_boot, alpha, seed = raw_cfg["bootstrap_resamples"], raw_cfg["alpha"], raw_cfg["seed"]
    metrics = list(dict.fromkeys(
        ([raw_cfg["primary_comparison"]["metric"]] if raw_cfg.get("primary_comparison") else [])
        + raw_cfg["secondary_metrics"]))
    result = {"run_id": run_id, "alpha": alpha, "descriptive": {}, "primary": None,
              "secondary_paired": {}, "noise_effect": {}}

    for level in levels:
        for cond in conds:
            for m in metrics:
                vals = [v for v in _values(rows, level, cond, m) if v is not None]
                result["descriptive"].setdefault(level, {}).setdefault(cond, {})[m] = {
                    "n": len(vals), "mean": float(np.mean(vals)) if vals else None,
                    "sd": float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
                    "ci95_mean": bootstrap_ci(vals, n_boot, seed)}

    pc = raw_cfg.get("primary_comparison")
    if pc:
        tests = {lv: paired_test(_values(rows, lv, pc["treatment"], pc["metric"]),
                                 _values(rows, lv, pc["control"], pc["metric"]), n_boot, seed)
                 for lv in levels}
        adj = holm([tests[lv]["p_value"] for lv in levels])
        for lv, p in zip(levels, adj):
            tests[lv]["p_holm"] = p
            tests[lv]["significant"] = p < alpha
        result["primary"] = {"comparison": pc, "by_noise": tests}
        for m in metrics:
            if m == pc["metric"]:
                continue
            result["secondary_paired"][m] = {
                lv: paired_test(_values(rows, lv, pc["treatment"], m),
                                _values(rows, lv, pc["control"], m), n_boot, seed)
                for lv in levels}

    if len(levels) >= 3:
        key = pc["metric"] if pc else metrics[0]
        for cond in conds:
            series = [_values(rows, lv, cond, key) for lv in levels]
            complete = [i for i in range(len(series[0])) if all(s[i] is not None for s in series)]
            st = stats.friedmanchisquare(*[[s[i] for i in complete] for s in series])
            result["noise_effect"][cond] = {"metric": key, "chi2": float(st.statistic),
                                            "p_value": float(st.pvalue), "n": len(complete)}

    out = ROOT / "results" / run_id
    (out / "statistics.json").write_text(json.dumps(result, indent=2))
    (out / "statistics_report.md").write_text(render_report(result, raw_cfg, levels, conds, metrics))
    return out


def _f(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.{nd}f}"


def render_report(res, cfg, levels, conds, metrics):
    L = [f"# Statistical report: {cfg['experiment_id']}", "",
         f"Run: `{res['run_id']}`  |  virtual students per cell: {cfg['n_students']}  |  "
         f"session length: {cfg['session_duration_s']} s  |  alpha = {res['alpha']}", "",
         "> These numbers describe the engine's performance on SIMULATED students generated by the "
         "model in research/docs/04_simulator_model.md. They are evidence about the algorithm under "
         "the stated assumptions, not evidence of accuracy with real students.", ""]
    if res["primary"]:
        pc = res["primary"]["comparison"]
        L += [f"## Primary test: {pc['treatment']} vs {pc['control']} on `{pc['metric']}`", "",
              "| noise | mean treatment | mean control | mean diff [95% CI] | Wilcoxon W | p | p (Holm) | rank-biserial r | d_z |",
              "|---|---|---|---|---|---|---|---|---|"]
        for lv in levels:
            t = res["primary"]["by_noise"][lv]
            lo, hi = t["ci95_mean_diff"]
            L.append(f"| {lv} | {_f(t['mean_a'])} | {_f(t['mean_b'])} | {_f(t['mean_diff'])} "
                     f"[{_f(lo)}, {_f(hi)}] | {_f(t['W'], 1)} | {_f(t['p_value'], 4)} | "
                     f"{_f(t['p_holm'], 4)} | {_f(t['rank_biserial'])} | {_f(t['cohen_dz'])} |")
        L.append("")
        if res["secondary_paired"]:
            L += ["## Secondary paired comparisons (not corrected; interpret as exploratory)", "",
                  "| metric | noise | mean treatment | mean control | mean diff [95% CI] | p |",
                  "|---|---|---|---|---|---|"]
            for m, by in res["secondary_paired"].items():
                for lv in levels:
                    t = by[lv]
                    lo, hi = t["ci95_mean_diff"]
                    L.append(f"| {m} | {lv} | {_f(t['mean_a'])} | {_f(t['mean_b'])} | "
                             f"{_f(t['mean_diff'])} [{_f(lo)}, {_f(hi)}] | {_f(t['p_value'], 4)} |")
            L.append("")
    if res["noise_effect"]:
        L += ["## Effect of noise level (Friedman test)", "", "| condition | metric | chi2 | p | n |",
              "|---|---|---|---|---|"]
        for c, t in res["noise_effect"].items():
            L.append(f"| {c} | {t['metric']} | {_f(t['chi2'], 2)} | {_f(t['p_value'], 4)} | {t['n']} |")
        L.append("")
    L += ["## Descriptive statistics (mean ± SD, bootstrap 95% CI of the mean)", ""]
    for m in metrics:
        L += [f"### {m}", "", "| noise | " + " | ".join(conds) + " |",
              "|---|" + "---|" * len(conds)]
        for lv in levels:
            cells = []
            for c in conds:
                d = res["descriptive"][lv][c][m]
                lo, hi = d["ci95_mean"]
                cells.append(f"{_f(d['mean'])} ± {_f(d['sd'])} [{_f(lo)}, {_f(hi)}]")
            L.append(f"| {lv} | " + " | ".join(cells) + " |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"statistics written to {analyze(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
'''

# ===== research/config/experiment_v1.json ====================================
FILES['research/config/experiment_v1.json'] = r'''{
  "experiment_id": "calibration_vs_default_v1",
  "description": "Primary experiment. Does personal calibration improve the accuracy of distraction detection compared with population-default thresholds, and how does performance change as sensor noise increases?",
  "seed": 20261026,
  "n_students": 30,
  "frame_rate_hz": 10,
  "session_duration_s": 1200,
  "calibration_protocol_s": {"center": 10, "corner_each": 3, "down": 4},
  "noise_levels": {
    "low":    {"pose_sd": 1.0, "ear_sd": 0.010, "gaze_sd": 0.04, "dropout_rate": 0.002, "dropout_mean_s": 0.3, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5},
    "medium": {"pose_sd": 2.5, "ear_sd": 0.020, "gaze_sd": 0.08, "dropout_rate": 0.006, "dropout_mean_s": 0.5, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5},
    "high":   {"pose_sd": 4.0, "ear_sd": 0.035, "gaze_sd": 0.15, "dropout_rate": 0.015, "dropout_mean_s": 0.8, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5}
  },
  "conditions": [
    {"name": "uncalibrated", "use_calibration": false, "engine_overrides": {}},
    {"name": "calibrated",   "use_calibration": true,  "engine_overrides": {}}
  ],
  "primary_comparison": {"treatment": "calibrated", "control": "uncalibrated", "metric": "f1_distracted"},
  "secondary_metrics": ["accuracy", "precision_distracted", "recall_distracted", "specificity", "focus_score_abs_error", "episode_recall", "median_latency_s", "false_alarms_per_hour"],
  "evaluation": {"detection_grace_s": 0.5},
  "alpha": 0.05,
  "bootstrap_resamples": 10000
}
'''

# ===== research/config/onset_sweep_v1.json ===================================
FILES['research/config/onset_sweep_v1.json'] = r'''{
  "experiment_id": "onset_sweep_v1",
  "description": "Secondary, exploratory experiment. How does the temporal-filter onset time trade detection latency against false alarms? Calibrated engine only, medium noise.",
  "seed": 20261027,
  "n_students": 30,
  "frame_rate_hz": 10,
  "session_duration_s": 1200,
  "calibration_protocol_s": {"center": 10, "corner_each": 3, "down": 4},
  "noise_levels": {
    "medium": {"pose_sd": 2.5, "ear_sd": 0.020, "gaze_sd": 0.08, "dropout_rate": 0.006, "dropout_mean_s": 0.5, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5}
  },
  "conditions": [
    {"name": "onset_0.5s", "use_calibration": true, "engine_overrides": {"onset_s": {"LOOKING_AWAY": 0.5, "LOOKING_DOWN": 0.5, "EYES_CLOSED": 0.5, "ABSENT": 0.5}}},
    {"name": "onset_1s",   "use_calibration": true, "engine_overrides": {"onset_s": {"LOOKING_AWAY": 1.0, "LOOKING_DOWN": 1.0, "EYES_CLOSED": 1.0, "ABSENT": 1.0}}},
    {"name": "onset_2s",   "use_calibration": true, "engine_overrides": {"onset_s": {"LOOKING_AWAY": 2.0, "LOOKING_DOWN": 2.0, "EYES_CLOSED": 1.0, "ABSENT": 2.0}}},
    {"name": "onset_3s",   "use_calibration": true, "engine_overrides": {"onset_s": {"LOOKING_AWAY": 3.0, "LOOKING_DOWN": 3.0, "EYES_CLOSED": 2.0, "ABSENT": 3.0}}}
  ],
  "primary_comparison": null,
  "secondary_metrics": ["f1_distracted", "median_latency_s", "false_alarms_per_hour", "episode_recall"],
  "evaluation": {"detection_grace_s": 0.5},
  "alpha": 0.05,
  "bootstrap_resamples": 10000
}
'''

# ===== research/data/processed/.gitkeep ======================================
FILES['research/data/processed/.gitkeep'] = r''''''

# ===== research/data/raw/.gitkeep ============================================
FILES['research/data/raw/.gitkeep'] = r''''''

# ===== research/docs/01_research_question.md =================================
FILES['research/docs/01_research_question.md'] = r'''# 1. Engineering problem, question, hypothesis and variables

## Engineering problem

Students studying alone at a computer have no objective feedback about how
much of their study time is spent attending to the work in front of them.
Webcam-based attention estimates exist, but a single fixed rule ("the face
must point straight at the camera") breaks when the camera is not directly in
front of the student: a laptop on the side, an external monitor, or a camera
below eye level all change what "looking at the screen" looks like to the
camera.

**Engineering goal:** build a webcam-based system that classifies a
student's visible attention state in real time, on an ordinary laptop, without
sending video off the device, and **measure** how accurately it does so.

## Design criteria (what "works" means, set before testing)

| Criterion | Target | How it is measured |
|---|---|---|
| Distraction detection quality | F1 (distracted class) as high as possible; reported with 95% CI | Experiment, frame level |
| Few false alarms | reported as false alarms per on-task hour | Experiment, episode level |
| Timely detection | median detection latency reported (the filter design implies at least ~2 s) | Experiment, episode level |
| Accurate summary metric | Focus Score absolute error reported (percentage points) | Experiment |
| Real-time | >= 8 frames/s on a typical laptop browser | Measured in the app (frames/s readout) |
| Privacy | no images or video leave the device | Code inspection + network inspection |

The targets above are deliberately not given pass/fail numbers chosen after
seeing results. If you want numeric thresholds (e.g. "F1 >= 0.80"), write
them into your lab notebook **before** running the official experiment.

## Testable engineering question (the experiment)

> On simulated study sessions with known ground truth, does personal
> calibration of the NeuroFocus attention engine improve distraction-detection
> accuracy compared with population-default thresholds, and how does
> detection accuracy change as camera-sensor noise increases?

The experiment evaluates **only the attention engine** (feature frames ->
attention state -> Focus Score). Accounts, scheduling, analytics and the user
interface are product features; they are verified by software tests, not by
this experiment.

## Hypotheses (state these in your notebook before the official run)

* **H1 (primary):** At each noise level, per-student F1 for the "distracted"
  class will be higher with personal calibration than with population-default
  thresholds.
* **H0 (null for H1):** The median paired difference in F1 (calibrated minus
  uncalibrated) is zero.
* **H2 (secondary):** F1 decreases as sensor noise increases (low > medium > high).

Rationale for H1: virtual students differ in camera placement (head yaw
offset up to +/-25 degrees, pitch offset -20 to +10 degrees). A fixed threshold
around 0 degrees will mislabel students whose "looking at the screen" pose is
far from 0, while calibration re-centres the thresholds.

Note: a hypothesis can be wrong. If calibration does not help, or helps only
at some noise levels, that is a valid and reportable engineering result. Do
not change the hypothesis, the engine parameters or the analysis after seeing
the official results. If you change anything, it is a new version of the
experiment and must be reported as such.

## Variables

| Type | Variable | Levels / units |
|---|---|---|
| Independent 1 | Calibration mode | `calibrated` (personal calibration) vs `uncalibrated` (population defaults) |
| Independent 2 | Sensor-noise level | `low`, `medium`, `high` (pose jitter 1.0 / 2.5 / 4.0 degrees SD; EAR jitter; gaze jitter; detection dropout rate) |
| Dependent (primary) | F1 score, distracted class, per virtual student | 0-1 |
| Dependent (secondary) | Accuracy, precision, recall, specificity, balanced accuracy, Cohen's kappa | 0-1 |
| Dependent (secondary) | Episode detection rate, correct-type rate | 0-1 |
| Dependent (secondary) | Detection latency | seconds |
| Dependent (secondary) | False alarms per on-task hour | count/hour |
| Dependent (secondary) | Focus Score absolute error | percentage points |
| Controlled | Virtual students and their behaviour timelines (same seeds in every condition) | 30 students |
| Controlled | Session length, frame rate | 20 min, 10 frames/s |
| Controlled | Engine version and parameters | `neurofocus_engine` v1.0.0, `params.py` |
| Controlled | Ground-truth definition of "distracted" | `research/simulator/ground_truth.py` |

## Experimental design

Within-subjects (paired) factorial design: every virtual student is
evaluated in all 2 x 3 = 6 conditions, using the identical behaviour timeline.
Paired designs remove between-student variation from the comparison.

A second, **exploratory** experiment (`research/config/onset_sweep_v1.json`)
varies the temporal-filter onset time (0.5, 1, 2, 3 s) to show the trade-off
between detection speed and false alarms. It has no pre-registered hypothesis
test and must be presented as exploratory.
'''

# ===== research/docs/02_procedure.md =========================================
FILES['research/docs/02_procedure.md'] = r'''# 2. Procedure and pre-specified analysis plan

## Before the official run (do these first, and write them in your lab notebook)

1. Read `01_research_question.md` and write your hypotheses and any numeric
   success targets in your lab notebook, with the date.
2. Freeze the code: commit everything to git. The pipeline records the git
   commit and whether there were uncommitted changes in `manifest.json`.
   Official runs should show `"git_uncommitted_changes": false`.
3. Run the automated tests: `python -m pytest`. All must pass. Record the
   result. (Passing tests show the software does what it was designed to do;
   they are not evidence of real-world accuracy.)
4. Do not edit `neurofocus_engine/params.py`, the simulator, or the
   evaluation code after this point. If you must, start a new experiment
   version (`experiment_v2.json`) and report both.

### Smoke tests vs official runs

`--students` / `--duration` flags produce a **smoke test**: a small run whose
only purpose is to check the pipeline works. Smoke-test run IDs end in
`_SMOKE` and `manifest.json` has `"smoke_test": true`. Never use smoke-test
numbers in your paper, and never tune parameters to improve them; doing so
would leak information from the test data into the design.

## Running the official experiment

```bash
python -m research.pipeline.run_experiment --config research/config/experiment_v1.json
```

The pipeline runs these stages in order:

| Stage | Module | Reads | Writes |
|---|---|---|---|
| 1. Simulate | `research/simulator/generate.py` | config | `data/raw/<run>/features/` (engine input) and `data/raw/<run>/ground_truth/` (labels), in **separate folders** |
| 2. Predict | `research/pipeline/predict.py` | **features only** | `data/processed/<run>/predictions/` |
| 3. Evaluate | `research/analysis/evaluate.py` | predictions + ground truth | `results/<run>/metrics_per_student.csv`, confusion matrices, `episodes.csv`, `summary.json` |
| 4. Statistics | `research/analysis/statistics.py` | metrics | `results/<run>/statistics.json`, `statistics_report.md` |
| 5. Figures | `research/analysis/figures.py` | metrics, confusion matrices | `results/<run>/figures/*.png` |

`manifest.json` records the config file hash, effective config, engine
version and parameters, git commit, Python/numpy/scipy versions and timings.

The exploratory experiment is run the same way with
`research/config/onset_sweep_v1.json`.

### Reproducibility

All randomness comes from `numpy.random.default_rng` seeded with
`[seed, student_id, stream]`. The same config on the same software versions
produces identical raw data. To check: run the experiment twice with
different `--run-id` values and compare `metrics_per_student.csv` (they should
be identical). Record that check in your notebook.

## Simulated calibration procedure (mirrors the app)

For each virtual student, before the session:
1. "centre" phase: 10 s looking near the screen centre;
2. "corners" phase: 3 s at each of the four screen corners;
3. "down" phase: 4 s looking at the desk.

In the `calibrated` condition the engine computes a personal calibration from
these frames. In the `uncalibrated` condition it ignores them and uses
population defaults. The calibration frames are generated with the same
sensor noise as the session.

## Pre-specified statistical analysis

All of the following was fixed before the first official run.

* **Unit of analysis:** the virtual student (n = 30 per condition). Frame-level
  metrics are computed within each student, then compared across students.
* **Primary test:** for each noise level, the paired difference in F1
  (calibrated minus uncalibrated) is tested with a two-sided **Wilcoxon
  signed-rank test** (chosen because F1 differences need not be normally
  distributed). The three p-values are adjusted with the **Holm-Bonferroni**
  method; significance level alpha = 0.05.
* **Effect sizes:** mean paired difference with a **bootstrap 95% confidence
  interval** (10,000 resamples, percentile method), matched-pairs
  **rank-biserial correlation** r, and **Cohen's d_z**.
* **Noise effect (H2):** **Friedman test** across the three noise levels
  within each calibration mode.
* **Secondary metrics:** reported with the same paired statistics but without
  multiple-comparison correction, and labelled exploratory.
* **Descriptive statistics:** mean, SD and bootstrap 95% CI for every metric
  in every condition; pooled confusion matrices.

### Interpreting the statistics honestly

* "n = 30" is 30 **simulated** students. A p-value here tells you how
  consistent the effect is across the simulated population, not how likely
  it is to hold for real people.
* Because simulated n can be increased cheaply, almost any non-zero effect can
  be made "significant". Emphasise effect sizes and confidence intervals over
  p-values, and keep n fixed at the pre-registered value.
* Report every pre-registered result, including ones that do not support
  your hypothesis.

## Data management

| Folder | Contents | Edit? |
|---|---|---|
| `research/data/raw/<run>/` | simulator output (features, ground truth, profiles, config) | Never edit. Re-generate from config + seed if lost. |
| `research/data/processed/<run>/` | engine predictions and per-student calibrations | Never edit. |
| `research/results/<run>/` | metrics, statistics, figures, manifest | Generated; do not hand-edit numbers. |
| `research/config/` | experiment definitions | Versioned; a changed config is a new experiment. |

Raw and processed data for a full run are tens of megabytes and are excluded
from git (`.gitignore`). Keep a copy (e.g. zipped on a USB drive or cloud
folder) of the raw data for every official run; judges may ask to see it.
The results folder is small and should be committed.

## Human participants

No human participants are involved. The study uses only simulated data.
Do not record anyone's camera data (including your own, or family members')
as experimental data without first checking your school's rules and the
current ISEF rules on human participants (these normally require
Institutional Review Board / Scientific Review Committee approval **before**
any data collection). Using the app yourself to check that it runs is software
testing, not data collection; do not report it as results.
'''

# ===== research/docs/03_algorithm.md =========================================
FILES['research/docs/03_algorithm.md'] = r'''# 3. The NeuroFocus attention engine (v1.0.0)

Code: `neurofocus_engine/` (shared by the web app and the experiment, so the
algorithm that is tested is exactly the algorithm users run). Parameters:
`neurofocus_engine/params.py`. These parameter values were chosen as design
decisions **before** any experiment was run and were not tuned on experiment
results.

## Pipeline

```
webcam frame (browser)
  -> MediaPipe Face Landmarker 0.10.14 (478 landmarks + 4x4 face transform)
  -> 6 features: face_present, yaw, pitch, ear, gaze_h, gaze_v       [frontend/js/vision.js]
  -> calibration-relative rules -> raw state per frame               [classifier.raw_state]
  -> temporal filter -> reported state                               [classifier.TemporalFilter]
  -> Focus Score and distraction episodes                            [scoring.py]
```

Frames are sampled at 10 frames per second. Video stays in the browser; only
the six numbers are sent to the server.

## Features

| Feature | Definition |
|---|---|
| `face_present` | Face Landmarker returned a face (with a transform matrix) for this frame. |
| `yaw`, `pitch` | Direction of the face's forward axis f = R * (0, 0, 1), where R is the rotation part of MediaPipe's face transform: yaw = atan2(f_x, f_z), pitch = atan2(f_y, sqrt(f_x^2 + f_z^2)), in degrees. The matrix storage order (row/column-major) is detected from where the translation sits. The sign of pitch is verified during calibration. |
| `ear` | Eye aspect ratio (Soukupova & Cech, 2016), averaged over both eyes: EAR = (\|p2-p6\| + \|p3-p5\|) / (2 \|p1-p4\|) using landmarks 33,160,158,133,153,144 (right eye) and 362,385,387,263,373,380 (left eye), in pixel units. |
| `gaze_h` | Iris centre (landmarks 468, 473) projected onto the eye-corner axis, as a fraction u from 0 to 1; gaze_h = clamp(4 (mean u - 0.5), -1, 1). |
| `gaze_v` | Vertical iris offset from the eyelid midpoint, divided by eye width, x4, clamped. Recorded but not used by v1.0.0 rules. |

## Calibration (`calibration.py`)

Protocol: centre 10 s, four corners 3 s each, desk 4 s (identical in the app
and in the simulator).

1. Quality gate: at least 85% of centre frames (and at least 10 frames) must
   contain a face, otherwise calibration fails.
2. Neutral pose: `yaw0`, `pitch0`, `ear0`, `gaze_h0` = medians over centre
   frames with a face.
3. Stability: if the median absolute deviation (MAD) of yaw or pitch in the
   centre phase exceeds 4 degrees, calibration is flagged "needs another try".
4. Pitch direction: if the desk phase's median pitch is **above** `pitch0`,
   the pitch sign is flipped (guards against a sign convention error in the
   camera pipeline).
5. Away threshold = clamp(max over corner frames of |(yaw - yaw0) +
   30 x (gaze_h - gaze_h0)| + 8 degrees, 15, 45).
6. Down threshold = clamp(|lowest corner pitch deviation| + 6 degrees, 10, 35).
   If the desk look was not clearly beyond this, the threshold becomes
   0.75 x the desk deviation (clamped).
7. Eyes-closed threshold = 0.65 x `ear0`.

Population defaults (used when calibration is skipped and in the
`uncalibrated` condition): yaw0 = 0, pitch0 = 0, ear0 = 0.28, gaze_h0 = 0,
away threshold 25 degrees, down threshold 20 degrees, eyes-closed EAR 0.182.

## Frame rules (`classifier.raw_state`)

Evaluated in order; the first match wins.

1. no face -> `ABSENT`
2. ear < eyes-closed threshold -> `EYES_CLOSED`
3. pitch_sign x (pitch - pitch0) < -down threshold -> `LOOKING_DOWN`
4. |(yaw - yaw0) + 30 x (gaze_h - gaze_h0)| > away threshold -> `LOOKING_AWAY`
5. otherwise -> `FOCUSED`

## Temporal filter (`classifier.TemporalFilter`)

A new non-focused raw state is reported only after it has persisted for its
onset time: 2.0 s for `LOOKING_AWAY`, `LOOKING_DOWN` and `ABSENT`, 1.0 s for
`EYES_CLOSED` (longer than a typical blink). The filter returns to `FOCUSED`
after 0.5 s of focused frames. This suppresses blinks, brief glances and
single-frame detection misses, at the cost of a built-in detection delay. The
exploratory onset-sweep experiment measures this trade-off.

## Focus Score (`scoring.py`)

```
Focus Score = 100 x (time the reported state is FOCUSED) / (session time)
```

Each frame's state is weighted by the time until the next frame, capped at
1 s so pauses are not counted. Time with no detected face counts as not
focused. The live score in the app is the same formula over the last 60 s.

The definition is deliberately simple so that it can be compared directly
with the simulator's ground-truth on-task percentage.

## What the engine does not do

* It does not use machine learning trained on people; it is a transparent,
  rule-based classifier on top of a pre-trained face-landmark model.
* It does not infer thinking, comprehension, emotion, or any medical condition.
'''

# ===== research/docs/04_simulator_model.md ===================================
FILES['research/docs/04_simulator_model.md'] = r'''# 4. The virtual-student simulator

Code: `research/simulator/`. The simulator generates (1) a ground-truth
behaviour timeline for each virtual student and (2) the noisy feature stream
a webcam face-landmark pipeline would report. **Every number below is an
assumption chosen by the researcher, not a measurement of real students.**
These assumptions define the scope of the experiment's conclusions.

## Separation from the engine

* `research/simulator/` never imports `neurofocus_engine`, and the engine never
  imports anything from `research/`. Automated tests enforce both
  (`tests/test_research_pipeline.py`).
* The engine-facing feature files contain only `t, phase, face_present, yaw,
  pitch, ear, gaze_h, gaze_v`. Labels are written to a separate
  `ground_truth/` folder that the prediction stage never opens (also tested).
* Where the engine has to assume a constant (e.g. 30 degrees per unit of iris
  offset), the simulator draws its own per-student value (25-35 degrees)
  instead of reusing the engine's value, so the engine cannot "know" the
  simulator's internals.

Remaining risk of circularity: the same person designed the simulator and the
engine, so the simulator may unconsciously reflect the engine's design
assumptions (for example, that looking away means turning the head). State
this in your limitations.

## Ground truth (`ground_truth.py`)

| Behaviour | Duration | Ground truth | Expected engine state |
|---|---|---|---|
| on_task (reading the screen) | lognormal, median 0.8 x student mean bout, 5-600 s | on-task | FOCUSED |
| glance (brief look aside) | uniform 0.3-1.5 s | on-task | FOCUSED |
| notes (looking down to write) | uniform 3-15 s | on-task | FOCUSED |
| away (sustained look away) | lognormal median 6 s, 3-40 s | distracted | LOOKING_AWAY |
| phone | lognormal median 15 s, 5-90 s | distracted | LOOKING_DOWN |
| drowsy (eyes closed) | lognormal median 4 s, 2-15 s | distracted | EYES_CLOSED |
| left_desk | lognormal median 30 s, 10-120 s | distracted | ABSENT |

Operational definition used in this study: a frame is **distracted** when the
virtual student is executing an off-task behaviour. Brief glances and note
taking count as on-task because they are normal parts of studying. Note
taking is intentionally included as a **known hard case**: it looks like
"looking down" to a camera.

## Student profiles (one per virtual student, `sample_profile`)

| Parameter | Distribution | Meaning |
|---|---|---|
| yaw_offset | U(-25, 25) degrees | camera placed to the side |
| pitch_offset | U(-20, 10) degrees | camera below/above eye level |
| screen_half_w, screen_half_h | U(12, 22), U(7, 13) degrees | angular size of the screen |
| head_fraction | U(0.4, 0.8) | share of a gaze shift made by the head (rest by the eyes) |
| eye_deg_per_unit | U(25, 35) degrees | eye rotation per unit of normalized iris offset |
| sway_sd | U(1, 3) degrees | natural head sway (Ornstein-Uhlenbeck, time constant 2 s) |
| ear_open | Normal(0.29, 0.025), clipped 0.22-0.36 | open-eye EAR |
| blink_per_min | U(10, 25) | blink rate; blink duration U(0.1, 0.4) s |
| mean_on_task_bout_s | U(30, 120) s | how long the student stays on task |
| next-behaviour probabilities | Dirichlet around glance .35, notes .15, away .20, phone .15, drowsy .08, left .07 | what interrupts on-task bouts |
| phone_high_prob | 0.2 | chance a phone is held near screen height (hard case) |

## Movement model

* Behaviour targets: glance yaw +/-U(15, 35) degrees; away yaw +/-U(30, 70);
  notes pitch -U(25, 45); phone pitch -U(20, 45) (or -U(5, 15) when held up);
  drowsy pitch -U(0, 10) with eyelids at 15-40% of open EAR.
* While on task, gaze moves between random fixations within 70% of the
  screen every 0.3-1.5 s.
* The head moves its share of the target angle with a first-order lag
  (time constant 0.25 s); the eyes cover the rest instantly (clipped to +/-1).
* Looking down lowers the eyelids: EAR x (1 - 0.25 x downward fraction).

## Sensor (observation) model, per noise level

| Parameter | low | medium | high |
|---|---|---|---|
| pose noise SD (degrees, yaw and pitch) | 1.0 | 2.5 | 4.0 |
| EAR noise SD | 0.010 | 0.020 | 0.035 |
| gaze noise SD | 0.04 | 0.08 | 0.15 |
| dropout start probability per frame | 0.002 | 0.006 | 0.015 |
| mean dropout length (s) | 0.3 | 0.5 | 0.8 |
| missed detection when \|yaw\| > 60 degrees | 50% | 50% | 50% |

These levels are a plausible range, not a calibration against a specific
camera. A strong extension (no human participants needed) would be to measure
real landmark jitter from a recorded video of a mannequin head or a printed
face photo at known angles, and set the noise levels from that.

## Validity threats to report

* External validity: real students' behaviour, posture and camera noise may
  differ from these distributions.
* Construct validity: "looking at the screen" is used as a proxy for
  attention; a student can look at the screen while mind-wandering.
* Circularity: designer of the simulator also designed the engine (see above).
* Perfect calibration compliance: virtual students always follow calibration
  instructions; real users may not.
'''

# ===== research/docs/05_evaluation_metrics.md ================================
FILES['research/docs/05_evaluation_metrics.md'] = r'''# 5. Evaluation metrics

Code: `research/analysis/evaluate.py`. Positive class = **distracted**
(ground truth `on_task == 0`; engine state not `FOCUSED`).

## Frame-level (computed per virtual student)

With TP, FP, FN, TN counted over all frames of a session:

| Metric | Formula |
|---|---|
| Accuracy | (TP + TN) / (TP + FP + FN + TN) |
| Precision (distracted) | TP / (TP + FP): when the engine says distracted, how often it is right |
| Recall / sensitivity (distracted) | TP / (TP + FN): how much distracted time it catches |
| Specificity | TN / (TN + FP): how much on-task time it correctly leaves alone |
| F1 (distracted) | 2TP / (2TP + FP + FN): balance of precision and recall (primary metric) |
| Balanced accuracy | (recall + specificity) / 2 |
| Cohen's kappa | (accuracy - p_e) / (1 - p_e), p_e = chance agreement |

Why F1 is primary: students are on task most of the time, so accuracy is
inflated by the large number of easy on-task frames (if a student is on task
85% of the time, a system that always says "focused" scores 85% accuracy
while detecting nothing). F1 ignores true negatives and
focuses on the distracted class.

Frame-level scoring includes the engine's built-in onset delay (the first ~2 s
of each distraction count as misses). This is intentional: it is how the
system behaves for a user.

## Multiclass confusion matrices

* 5 x 5: expected state (from the ground-truth behaviour) x engine state.
* 7 x 5: ground-truth behaviour (including glance and notes) x engine state.
  This shows **which behaviours** cause errors (e.g. note taking -> LOOKING_DOWN).

Figures show row-normalized matrices (each row sums to 1).

## Episode-level

A ground-truth distraction episode is a run of consecutive distracted frames
with the same behaviour.

* **Detected** if the engine reports any non-FOCUSED state between the
  episode's start and 0.5 s after its end (`detection_grace_s`).
* **Detection latency** = time of the first such frame - episode start.
* **Correct type** if the most common non-FOCUSED engine state during the
  detection window matches the expected state.
* **False alarm** = a run of non-FOCUSED engine output that does not overlap
  any ground-truth distracted frame. Reported per hour of ground-truth
  on-task time, and broken down by the behaviour that was happening.

## Focus Score error

* Ground-truth focus percentage = 100 x on-task frames / all frames.
* Engine Focus Score = 100 x FOCUSED frames / all frames (equal to the app's
  score for evenly spaced frames).
* Absolute error = |engine - ground truth| in percentage points; signed error
  is also stored to show systematic over- or under-estimation.
'''

# ===== research/docs/06_limitations_and_ethics.md ============================
FILES['research/docs/06_limitations_and_ethics.md'] = r'''# 6. Limitations, claims and ethics

## What the evidence supports, and what it does not

| Evidence | What it shows | What it does NOT show |
|---|---|---|
| Automated tests pass (`pytest`) | The code behaves as designed: rules, calibration, scoring, security checks, data separation, metric formulas. | That the design is accurate for real people. |
| Virtual-student experiment | How accurately the engine recovers known attention states from simulated feature streams, how calibration and noise affect that, under the stated simulator assumptions. | Accuracy with real students, real cameras, real lighting; that the app improves studying or grades. |
| The app runs in a browser at ~10 frames/s | Real-time feasibility on that computer. | Accuracy (no ground truth is collected). |

Claims you **can** make (if the data support them):
* "On N = 30 simulated students, personal calibration changed F1 by X
  (95% CI ...) at medium sensor noise."
* "The engine's main error source in simulation was ... (from the behaviour
  confusion matrix)."

Claims you **must not** make:
* That NeuroFocus measures attention, focus or learning in real students.
* That NeuroFocus detects, screens for, or diagnoses ADHD or any other
  condition. (The name "NeuroFocus" refers to focus, not neurology.)
* That simulated results prove the product is effective.

## Technical limitations

1. Head/eye direction is a proxy. Looking at the screen is not the same as
   paying attention (mind-wandering is invisible), and looking away is not
   always distraction (thinking, reading paper notes).
2. Note taking and phones held near the screen are known hard cases.
3. The iris-offset scale and the head-pose pitch sign have not been validated
   against measured ground truth on real hardware. Calibration checks the
   pitch direction but not the scale.
4. Face-landmark accuracy can depend on lighting, camera quality, glasses,
   head coverings and skin tone. None of these were tested. MediaPipe's own
   model card describes its evaluation; cite it rather than assuming fairness.
5. Background browser tabs: the app uses a worker timer to keep sampling, but
   browsers may still slow pages that are not visible.
6. Single-process server design: the live engine state is cached in memory
   (and reconstructed from the database after a restart). This is fine for a
   personal or demo deployment, not for many simultaneous users.

## Ethics, privacy and safety

* Camera frames are processed in the browser; only six numbers per frame are
  sent to the server. No images are stored.
* Users can export all their data as JSON and permanently delete their
  account.
* Passwords are hashed with scrypt (Werkzeug). Sessions use HttpOnly,
  SameSite=Lax cookies. All state-changing requests require a CSRF token.
  Login is rate-limited. A strict Content-Security-Policy allows scripts only
  from the app itself (MediaPipe is bundled locally).
* Monitoring tools can be misused (e.g. a parent or school monitoring a
  student without consent). NeuroFocus is designed for self-use: each account
  sees only its own data, and there is no supervisor view. Keep it that way
  unless you add explicit consent features.

## Human participants (ISEF)

The study was designed around a school restriction on human-participant
research: it uses only simulated "virtual students". Under ISEF rules,
research that collects data from people (including the student researcher)
generally needs prior review and approval (IRB/SRC) and informed consent.
Check the current *International Rules for Precollege Science Research*
and your fair's SRC before collecting any camera data from people for
research purposes. Possible future work that does **not** involve people:
measuring landmark noise from a mannequin head or printed face photo at known
angles to ground the simulator's noise model.
'''

# ===== research/docs/07_references.md ========================================
FILES['research/docs/07_references.md'] = r'''# 7. References

**Verify every reference yourself before citing it.** These were compiled
from memory by an AI assistant while writing the code. Look each one up
(Google Scholar, arXiv, the publisher's site), confirm authors, year, title
and page numbers, and read at least the abstract and relevant section
before you cite it. Delete any you cannot verify. Add sources you find
yourself, especially on webcam-based attention estimation and gaze/head-pose
accuracy.

## Methods used in the engine

1. Soukupová, T., & Čech, J. (2016). Real-time eye blink detection using
   facial landmarks. *21st Computer Vision Winter Workshop (CVWW)*.
   Used for: eye aspect ratio (EAR) definition.
2. Kartynnik, Y., Ablavatski, A., Grishchenko, I., & Grundmann, M. (2019).
   Real-time facial surface geometry from monocular video on mobile GPUs.
   *arXiv:1907.06724*. Used for: the face-mesh model behind MediaPipe Face
   Landmarker.
3. Ablavatski, A., Vakunov, A., Grishchenko, I., Raveendran, K., &
   Zhdanovich, M. (2020). Real-time pupil tracking from monocular video for
   digital puppetry. *arXiv:2006.11341*. Used for: iris landmarks.
4. Lugaresi, C., et al. (2019). MediaPipe: A framework for building
   perception pipelines. *arXiv:1906.08172*. Used for: the MediaPipe framework.
5. Google. MediaPipe Face Landmarker documentation and model card (online;
   cite with the access date). Used for: model inputs/outputs, the facial
   transformation matrix, and the model's own evaluation and fairness notes.
6. Dinges, D. F., & Grace, R. (1998). PERCLOS: A valid psychophysiological
   measure of alertness as assessed by psychomotor vigilance. *Federal
   Highway Administration Tech Brief FHWA-MCRT-98-006*. Background for
   eye-closure-based drowsiness measures.

## Evaluation and statistics

7. Sokolova, M., & Lapalme, G. (2009). A systematic analysis of performance
   measures for classification tasks. *Information Processing & Management,
   45*(4), 427-437. Used for: precision, recall, F1 definitions.
8. Powers, D. M. W. (2011). Evaluation: From precision, recall and F-measure
   to ROC, informedness, markedness and correlation. *Journal of Machine
   Learning Technologies, 2*(1), 37-63. Used for: limitations of accuracy/F1.
9. Cohen, J. (1960). A coefficient of agreement for nominal scales.
   *Educational and Psychological Measurement, 20*(1), 37-46. Used for:
   Cohen's kappa.
10. Wilcoxon, F. (1945). Individual comparisons by ranking methods.
    *Biometrics Bulletin, 1*(6), 80-83. Used for: signed-rank test.
11. Holm, S. (1979). A simple sequentially rejective multiple test
    procedure. *Scandinavian Journal of Statistics, 6*(2), 65-70. Used for:
    multiple-comparison correction.
12. Friedman, M. (1937). The use of ranks to avoid the assumption of
    normality implicit in the analysis of variance. *Journal of the American
    Statistical Association, 32*(200), 675-701. Used for: noise-level effect.
13. Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the
    Bootstrap*. Chapman & Hall/CRC. Used for: bootstrap confidence intervals.
14. Kerby, D. S. (2014). The simple difference formula: An approach to
    teaching nonparametric correlation. *Comprehensive Psychology, 3*.
    Used for: matched-pairs rank-biserial correlation.

## Rules

15. Society for Science. *International Rules for Precollege Science
    Research: Guidelines for Science and Engineering Fairs* (use the edition
    for your competition year). Used for: human-participant rules, project
    categories, required forms.

## Software

16. Python, NumPy, SciPy, Matplotlib, Flask: cite the versions recorded in
    each run's `manifest.json`.
17. MediaPipe Tasks Vision 0.10.14 (npm `@mediapipe/tasks-vision`), Apache-2.0.

## Gaps to fill with your own literature search

* Prior webcam- or eye-tracking-based attention/engagement detection in
  learning settings, and how it was validated.
* Accuracy of webcam head-pose and gaze estimation versus lab eye trackers.
* Mind-wandering research showing that gaze direction is an imperfect
  proxy for attention (useful for your limitations section).
'''

# ===== research/docs/08_lab_notebook_template.md =============================
FILES['research/docs/08_lab_notebook_template.md'] = r'''# 8. Lab notebook template

Keep a dated entry for every working session. Copy this block each time.
(ISEF projects are expected to have a research notebook; a handwritten or
dated digital notebook both work. Check your fair's preference.)

---

**Date:**
**Time spent:**
**Git commit (run `git rev-parse --short HEAD`):**

**Goal for today:**

**What I did:**

**Commands run / run IDs:**

**Observations (raw, before interpretation):**

**Problems and how I solved them:**

**Decisions made and why (especially any change to code, parameters,
simulator or analysis; note whether it happened before or after seeing
official results):**

**Next steps:**

---

## Required entries before the official run

- [ ] Hypotheses (H1, H2) written in my own words, dated
- [ ] Any numeric success targets written, dated
- [ ] `python -m pytest` result recorded
- [ ] All code committed; commit hash recorded
- [ ] Config file used: `research/config/experiment_v1.json`, SHA-256 recorded
      (from `manifest.json` after the run)

## Required entries after the official run

- [ ] Run ID
- [ ] Reproducibility check: second run with a new run ID gives identical metrics
- [ ] Primary result table copied from `statistics_report.md`
- [ ] Whether H1 / H2 were supported, in plain language
- [ ] Surprises, and what the confusion matrices say about the error sources
- [ ] Raw data backed up (where)
'''

# ===== research/pipeline/__init__.py =========================================
FILES['research/pipeline/__init__.py'] = r''''''

# ===== research/pipeline/predict.py ==========================================
FILES['research/pipeline/predict.py'] = r'''"""Stage 2 - run the NeuroFocus engine on the simulated FEATURE files only.

This stage is deliberately blind: it reads research/data/raw/<run>/features
and never opens ground_truth/. Output goes to
research/data/processed/<run>/predictions/<noise>/<condition>/.

Usage: python -m research.pipeline.predict --run-id RUN
"""

import argparse
import csv
import dataclasses
import json
from pathlib import Path

from neurofocus_engine import (AttentionEngine, DEFAULT_PARAMS, FeatureFrame,
                               calibrate, default_calibration, focus_score)

ROOT = Path(__file__).resolve().parents[1]


def engine_params(overrides):
    if not overrides:
        return DEFAULT_PARAMS
    kw = dict(overrides)
    if "onset_s" in kw:
        kw["onset_s"] = {**DEFAULT_PARAMS.onset_s, **kw["onset_s"]}
    return dataclasses.replace(DEFAULT_PARAMS, **kw)


def _read_frames(path):
    with open(path, newline="") as f:
        return [(row["phase"], FeatureFrame.from_dict(row)) for row in csv.DictReader(f)]


def run_condition(cal_path, session_path, use_calibration, params):
    if use_calibration:
        by_phase = {}
        for phase, fr in _read_frames(cal_path):
            by_phase.setdefault(phase, []).append(fr)
        cal, ok = calibrate(by_phase, params)
    else:
        cal, ok = default_calibration(params), True
    engine = AttentionEngine(cal, params)
    out = engine.process_many([fr for _, fr in _read_frames(session_path)])
    return cal, ok, out


def predict(run_id):
    raw = ROOT / "data" / "raw" / run_id
    config = json.loads((raw / "config.json").read_text())
    out_root = ROOT / "data" / "processed" / run_id / "predictions"
    for level in config["noise_levels"]:
        fdir = raw / "features" / level
        for cond in config["conditions"]:
            params = engine_params(cond.get("engine_overrides"))
            odir = out_root / level / cond["name"]
            odir.mkdir(parents=True, exist_ok=True)
            for sid in range(1, config["n_students"] + 1):
                stem = f"student_{sid:02d}"
                cal, ok, rows = run_condition(fdir / f"{stem}_calibration.csv",
                                              fdir / f"{stem}_session.csv",
                                              cond["use_calibration"], params)
                with open(odir / f"{stem}.csv", "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["t", "raw_state", "state"])
                    w.writerows(rows)
                (odir / f"{stem}_calibration.json").write_text(json.dumps(
                    {"calibration": cal.to_dict(), "calibration_ok": ok,
                     "focus_score": focus_score([(t, s) for t, _, s in rows]),
                     "engine_params": params.to_dict()}, indent=2))
    return out_root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"predictions written to {predict(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
'''

# ===== research/pipeline/run_experiment.py ===================================
FILES['research/pipeline/run_experiment.py'] = r'''"""Run the full, reproducible experiment pipeline.

  1 simulate  -> research/data/raw/<run_id>/            (features + ground truth, separate folders)
  2 predict   -> research/data/processed/<run_id>/      (engine sees features only)
  3 evaluate  -> research/results/<run_id>/             (first stage that reads ground truth)
  4 statistics, 5 figures, plus manifest.json recording exactly what was run.

Usage:
  python -m research.pipeline.run_experiment --config research/config/experiment_v1.json
  python -m research.pipeline.run_experiment --config ... --run-id my_run --students 5 --duration 300
     (--students/--duration produce a SMOKE TEST run, labelled as such; not for the paper)
"""

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import scipy

from neurofocus_engine import DEFAULT_PARAMS, ENGINE_VERSION
from research.simulator.generate import generate
from research.pipeline.predict import predict
from research.analysis.evaluate import evaluate
from research.analysis.statistics import analyze
from research.analysis.figures import make_figures

ROOT = Path(__file__).resolve().parents[1]


def _git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                              cwd=ROOT, check=True).stdout.strip()
    except Exception:
        return None


def _git_dirty():
    try:
        out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                             cwd=ROOT, check=True).stdout
        return bool(out.strip())
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--run-id")
    ap.add_argument("--students", type=int, help="override n_students (smoke test only)")
    ap.add_argument("--duration", type=float, help="override session_duration_s (smoke test only)")
    args = ap.parse_args()

    cfg_text = Path(args.config).read_text()
    config = json.loads(cfg_text)
    smoke = args.students is not None or args.duration is not None
    if args.students:
        config["n_students"] = args.students
    if args.duration:
        config["session_duration_s"] = args.duration
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = args.run_id or f"{config['experiment_id']}_{stamp}" + ("_SMOKE" if smoke else "")
    raw_dir = ROOT / "data" / "raw" / run_id
    if raw_dir.exists():
        raise SystemExit(f"run {run_id} already exists; choose a new --run-id")

    timings = {}
    t0 = time.time()
    print(f"[1/5] simulating {config['n_students']} virtual students ...")
    generate(config, raw_dir)
    timings["simulate_s"] = time.time() - t0
    t0 = time.time()
    print("[2/5] running engine on feature files (blind to ground truth) ...")
    predict(run_id)
    timings["predict_s"] = time.time() - t0
    print("[3/5] evaluating against ground truth ...")
    out = evaluate(run_id)
    print("[4/5] statistics ...")
    analyze(run_id)
    print("[5/5] figures ...")
    make_figures(run_id)

    manifest = {
        "run_id": run_id,
        "smoke_test": smoke,
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "config_file": str(Path(args.config)),
        "config_sha256": hashlib.sha256(cfg_text.encode()).hexdigest(),
        "effective_config": config,
        "engine_version": ENGINE_VERSION,
        "engine_default_params": DEFAULT_PARAMS.to_dict(),
        "git_commit": _git_commit(),
        "git_uncommitted_changes": _git_dirty(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "timings_s": timings,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"done. results in {out}")
    print(f"read {out / 'statistics_report.md'} first.")


if __name__ == "__main__":
    main()
'''

# ===== research/results/.gitkeep =============================================
FILES['research/results/.gitkeep'] = r''''''

# ===== research/simulator/__init__.py ========================================
FILES['research/simulator/__init__.py'] = r''''''

# ===== research/simulator/generate.py ========================================
FILES['research/simulator/generate.py'] = r'''"""Stage 1 - generate virtual-student data.

Writes to research/data/raw/<run_id>/:
  features/<noise>/student_XX_calibration.csv   <- given to the engine
  features/<noise>/student_XX_session.csv       <- given to the engine
  ground_truth/student_XX.csv                   <- NEVER given to the engine
  ground_truth/profiles.json                    <- hidden student parameters

Usage: python -m research.simulator.generate --config research/config/experiment_v1.json --run-id RUN
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from .virtual_student import sample_profile, simulate_calibration, simulate_session, observe

ROOT = Path(__file__).resolve().parents[1]
FEATURE_FIELDS = ["t", "phase", "face_present", "yaw", "pitch", "ear", "gaze_h", "gaze_v"]
TRUTH_FIELDS = ["t", "behavior", "gt_state", "on_task", "episode_id"]


def _write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _rng(seed, *keys):
    return np.random.default_rng([seed, *keys])


def generate(config, run_dir):
    hz = config["frame_rate_hz"]
    seed = config["seed"]
    proto = config["calibration_protocol_s"]
    profiles = []
    for sid in range(1, config["n_students"] + 1):
        p = sample_profile(sid, _rng(seed, sid, 0))
        profiles.append(p.to_dict())
        # Behavior is generated ONCE per student, so every noise level and every
        # engine condition sees the same underlying behavior (paired design).
        cal_latent = simulate_calibration(p, _rng(seed, sid, 1), hz, proto["center"],
                                          proto["corner_each"], proto["down"])
        latent, truth = simulate_session(p, _rng(seed, sid, 2), hz, config["session_duration_s"])
        _write_csv(run_dir / "ground_truth" / f"student_{sid:02d}.csv", TRUTH_FIELDS, truth)
        for li, (level, noise) in enumerate(config["noise_levels"].items()):
            cal_obs = observe([s for _, s in cal_latent], _rng(seed, sid, 3, li), hz, noise)
            for (phase, _), row in zip(cal_latent, cal_obs):
                row["phase"] = phase
            obs = observe(latent, _rng(seed, sid, 4, li), hz, noise)
            for row in obs:
                row["phase"] = "session"
            fdir = run_dir / "features" / level
            _write_csv(fdir / f"student_{sid:02d}_calibration.csv", FEATURE_FIELDS, cal_obs)
            _write_csv(fdir / f"student_{sid:02d}_session.csv", FEATURE_FIELDS, obs)
    (run_dir / "ground_truth" / "profiles.json").write_text(json.dumps(profiles, indent=2))
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))
    return profiles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    config = json.loads(Path(args.config).read_text())
    run_dir = ROOT / "data" / "raw" / args.run_id
    if run_dir.exists():
        raise SystemExit(f"{run_dir} already exists; raw data is never overwritten.")
    generate(config, run_dir)
    print(f"raw data written to {run_dir}")


if __name__ == "__main__":
    main()
'''

# ===== research/simulator/ground_truth.py ====================================
FILES['research/simulator/ground_truth.py'] = r'''"""Ground-truth vocabulary for the virtual-student experiment.

These definitions belong to the RESEARCH DESIGN, not to the engine. They are
written independently of neurofocus_engine (which must never import this
file) and fixed before any experiment run.

Operational definition of "distracted" used in this study:
  The virtual student is executing an off-task behavior (looking away from the
  screen for >= 3 s, using a phone, eyes closed for >= 2 s, or away from the
  desk). Brief glances (< 1.5 s) and looking down to write notes are treated as
  ON-TASK, because they are normal parts of studying.
"""

# Behaviors the simulator can perform.
ON_TASK = "on_task"          # reading / looking at screen
GLANCE = "glance"            # brief look aside, 0.3-1.5 s   (on-task)
NOTES = "notes"              # looking down to write notes  (on-task, known confound)
AWAY = "away"                # sustained look away          (distracted)
PHONE = "phone"              # using a phone                (distracted)
DROWSY = "drowsy"            # eyes closed                  (distracted)
LEFT_DESK = "left_desk"      # not in front of camera       (distracted)

BEHAVIORS = (ON_TASK, GLANCE, NOTES, AWAY, PHONE, DROWSY, LEFT_DESK)
ON_TASK_BEHAVIORS = (ON_TASK, GLANCE, NOTES)

# Expected attention-state label for each behavior. Strings match the engine's
# output vocabulary so predictions and truth can be compared, but they are
# declared here independently.
EXPECTED_STATE = {
    ON_TASK: "FOCUSED",
    GLANCE: "FOCUSED",
    NOTES: "FOCUSED",
    AWAY: "LOOKING_AWAY",
    PHONE: "LOOKING_DOWN",
    DROWSY: "EYES_CLOSED",
    LEFT_DESK: "ABSENT",
}
STATE_ORDER = ("FOCUSED", "LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT")
'''

# ===== research/simulator/virtual_student.py =================================
FILES['research/simulator/virtual_student.py'] = r'''"""Virtual-student simulator.

Generates (1) the latent behavior of a simulated student over time, which is
the ground truth, and (2) the noisy feature stream a webcam + face-landmark
pipeline would report, which is the ONLY thing the engine is given.

The model is a set of stated assumptions, not measurements of real students.
Every distribution below is listed in research/docs/04_simulator_model.md and
is a limitation of the study: results show how the engine behaves on THIS
model of behavior and sensor noise, not on real people.

Independence from the engine: this module does not import neurofocus_engine.
Where the engine needs a constant (e.g. how many degrees an iris offset
corresponds to), the simulator draws its own per-student value instead of
reusing the engine's assumption.
"""

from dataclasses import dataclass, asdict
import math

import numpy as np

from .ground_truth import (ON_TASK, GLANCE, NOTES, AWAY, PHONE, DROWSY,
                           LEFT_DESK, ON_TASK_BEHAVIORS, EXPECTED_STATE)

DISTRACTIONS = (GLANCE, NOTES, AWAY, PHONE, DROWSY, LEFT_DESK)
BASE_NEXT_PROBS = np.array([0.35, 0.15, 0.20, 0.15, 0.08, 0.07])


@dataclass
class StudentProfile:
    student_id: int
    yaw_offset: float          # camera placement (deg)
    pitch_offset: float
    screen_half_w: float       # angular half-width of the screen (deg)
    screen_half_h: float
    head_fraction: float       # share of a gaze shift done by the head (rest by eyes)
    eye_deg_per_unit: float    # deg of eye rotation per unit normalized iris offset
    sway_sd: float             # natural head sway (deg)
    ear_open: float
    blink_per_min: float
    mean_on_task_bout_s: float
    next_probs: list           # probabilities over DISTRACTIONS after an on-task bout
    phone_high_prob: float     # chance a phone is held up near screen height

    def to_dict(self):
        return asdict(self)


def sample_profile(student_id, rng):
    alpha = BASE_NEXT_PROBS * 40
    return StudentProfile(
        student_id=student_id,
        yaw_offset=float(rng.uniform(-25, 25)),
        pitch_offset=float(rng.uniform(-20, 10)),
        screen_half_w=float(rng.uniform(12, 22)),
        screen_half_h=float(rng.uniform(7, 13)),
        head_fraction=float(rng.uniform(0.4, 0.8)),
        eye_deg_per_unit=float(rng.uniform(25, 35)),
        sway_sd=float(rng.uniform(1.0, 3.0)),
        ear_open=float(np.clip(rng.normal(0.29, 0.025), 0.22, 0.36)),
        blink_per_min=float(rng.uniform(10, 25)),
        mean_on_task_bout_s=float(rng.uniform(30, 120)),
        next_probs=[float(p) for p in rng.dirichlet(alpha)],
        phone_high_prob=0.2,
    )


def _lognormal_clipped(rng, median, lo, hi, sigma=0.6):
    return float(np.clip(median * math.exp(rng.normal(0, sigma)), lo, hi))


def _behavior_duration(rng, b, p):
    if b == ON_TASK:
        return _lognormal_clipped(rng, p.mean_on_task_bout_s * 0.8, 5, 600)
    if b == GLANCE:
        return float(rng.uniform(0.3, 1.5))
    if b == NOTES:
        return float(rng.uniform(3, 15))
    if b == AWAY:
        return _lognormal_clipped(rng, 6, 3, 40)
    if b == PHONE:
        return _lognormal_clipped(rng, 15, 5, 90)
    if b == DROWSY:
        return _lognormal_clipped(rng, 4, 2, 15)
    if b == LEFT_DESK:
        return _lognormal_clipped(rng, 30, 10, 120)
    raise ValueError(b)


def _behavior_target(rng, b, p):
    """Where the student is looking, relative to the screen center:
    (yaw deg, pitch deg, eyes_closed, face_visible)."""
    side = 1 if rng.random() < 0.5 else -1
    if b == GLANCE:
        return side * rng.uniform(15, 35), rng.uniform(-5, 5), False, True
    if b == AWAY:
        return side * rng.uniform(30, 70), rng.uniform(-10, 10), False, True
    if b == NOTES:
        return rng.uniform(-10, 10), -rng.uniform(25, 45), False, True
    if b == PHONE:
        if rng.random() < p.phone_high_prob:  # held up near the screen: hard case
            return rng.uniform(-15, 15), -rng.uniform(5, 15), False, True
        return rng.uniform(-15, 15), -rng.uniform(20, 45), False, True
    if b == DROWSY:
        return rng.uniform(-5, 5), -rng.uniform(0, 10), True, True
    if b == LEFT_DESK:
        return 0.0, 0.0, False, False
    raise ValueError(b)


class _Body:
    """Head/eye/eyelid dynamics shared by calibration and session simulation."""

    def __init__(self, p, rng, dt):
        self.p, self.rng, self.dt = p, rng, dt
        self.head_yaw = self.head_pitch = 0.0
        self.sway_yaw = self.sway_pitch = 0.0
        self.blink_left = 0.0
        self.fix_left = 0.0
        self.fix = (0.0, 0.0)

    def step(self, target_yaw, target_pitch, eyes_closed, visible, reading):
        p, rng, dt = self.p, self.rng, self.dt
        if reading:  # small fixations moving around the screen
            self.fix_left -= dt
            if self.fix_left <= 0:
                self.fix = (rng.uniform(-0.7, 0.7) * p.screen_half_w,
                            rng.uniform(-0.7, 0.7) * p.screen_half_h)
                self.fix_left = rng.uniform(0.3, 1.5)
            target_yaw, target_pitch = target_yaw + self.fix[0], target_pitch + self.fix[1]
        # Ornstein-Uhlenbeck head sway, tau = 2 s
        k = dt / 2.0
        s = p.sway_sd * math.sqrt(2 * k)
        self.sway_yaw += -k * self.sway_yaw + s * rng.normal()
        self.sway_pitch += -k * self.sway_pitch + s * rng.normal()
        # head follows its share of the target with a 0.25 s lag
        a = 1 - math.exp(-dt / 0.25)
        self.head_yaw += a * (p.head_fraction * target_yaw - self.head_yaw)
        self.head_pitch += a * (p.head_fraction * target_pitch - self.head_pitch)
        eye_yaw = target_yaw - self.head_yaw
        eye_pitch = target_pitch - self.head_pitch
        # eyelids: closed when drowsy, short blinks otherwise; looking down lowers lids
        if self.blink_left <= 0 and rng.random() < p.blink_per_min / 60 * dt:
            self.blink_left = rng.uniform(0.1, 0.4)
        blinking = self.blink_left > 0
        self.blink_left -= dt
        down = min(max(-target_pitch / 45.0, 0.0), 1.0)
        ear = p.ear_open * (1 - 0.25 * down)
        if eyes_closed:
            ear = p.ear_open * rng.uniform(0.15, 0.4)
        elif blinking:
            ear = p.ear_open * 0.2
        return {
            "visible": visible,
            "yaw": p.yaw_offset + self.head_yaw + self.sway_yaw,
            "pitch": p.pitch_offset + self.head_pitch + self.sway_pitch,
            "ear": ear,
            "gaze_h": float(np.clip(eye_yaw / p.eye_deg_per_unit, -1, 1)),
            "gaze_v": float(np.clip(eye_pitch / p.eye_deg_per_unit, -1, 1)),
        }


def simulate_calibration(p, rng, hz, center_s=10.0, corner_s=3.0, down_s=4.0):
    """Student follows the calibration instructions (an assumption: real users
    may not). Returns list of (phase, latent dict)."""
    dt = 1.0 / hz
    body = _Body(p, rng, dt)
    out = []
    for _ in range(int(center_s * hz)):
        st = body.step(rng.normal(0, 0.1 * p.screen_half_w), rng.normal(0, 0.1 * p.screen_half_h),
                       False, True, False)
        out.append(("center", st))
    for cy, cp in ((-1, 1), (1, 1), (1, -1), (-1, -1)):
        for _ in range(int(corner_s * hz)):
            st = body.step(cy * p.screen_half_w, cp * p.screen_half_h, False, True, False)
            out.append(("corners", st))
    desk = -rng.uniform(30, 45)
    for _ in range(int(down_s * hz)):
        out.append(("down", body.step(0.0, desk, False, True, False)))
    return out


def simulate_session(p, rng, hz, duration_s):
    """Returns (latent list, ground-truth list). Ground truth rows:
    dict(t, behavior, gt_state, on_task, episode_id)."""
    dt = 1.0 / hz
    n = int(round(duration_s * hz))
    body = _Body(p, rng, dt)
    latent, truth = [], []
    behavior, left, episode = ON_TASK, _behavior_duration(rng, ON_TASK, p), 0
    target = (0.0, 0.0, False, True)
    for i in range(n):
        if left <= 0:
            if behavior == ON_TASK:
                behavior = DISTRACTIONS[rng.choice(len(DISTRACTIONS), p=p.next_probs)]
                target = _behavior_target(rng, behavior, p)
            else:
                behavior, target = ON_TASK, (0.0, 0.0, False, True)
            left = _behavior_duration(rng, behavior, p)
            episode += 1
        left -= dt
        reading = behavior == ON_TASK
        st = body.step(*target, reading=reading)
        latent.append(st)
        truth.append({
            "t": round(i * dt, 3), "behavior": behavior,
            "gt_state": EXPECTED_STATE[behavior],
            "on_task": int(behavior in ON_TASK_BEHAVIORS), "episode_id": episode,
        })
    return latent, truth


def observe(latent, rng, hz, noise):
    """Measurement model: what a face-landmark pipeline would report.

    noise: dict with pose_sd, ear_sd, gaze_sd, dropout_rate, dropout_mean_s,
           extreme_yaw_deg, extreme_yaw_miss_prob.
    """
    dt = 1.0 / hz
    rows, miss_left = [], 0.0
    for i, st in enumerate(latent):
        t = round(i * dt, 3)
        if miss_left <= 0 and rng.random() < noise["dropout_rate"]:
            miss_left = rng.exponential(noise["dropout_mean_s"])
        missed = miss_left > 0
        miss_left -= dt
        if st["visible"] and abs(st["yaw"]) > noise["extreme_yaw_deg"] \
                and rng.random() < noise["extreme_yaw_miss_prob"]:
            missed = True
        if not st["visible"] or missed:
            rows.append({"t": t, "face_present": 0, "yaw": "", "pitch": "", "ear": "",
                         "gaze_h": "", "gaze_v": ""})
            continue
        rows.append({
            "t": t, "face_present": 1,
            "yaw": round(st["yaw"] + rng.normal(0, noise["pose_sd"]), 3),
            "pitch": round(st["pitch"] + rng.normal(0, noise["pose_sd"]), 3),
            "ear": round(max(0.0, st["ear"] + rng.normal(0, noise["ear_sd"])), 4),
            "gaze_h": round(float(np.clip(st["gaze_h"] + rng.normal(0, noise["gaze_sd"]), -1, 1)), 4),
            "gaze_v": round(float(np.clip(st["gaze_v"] + rng.normal(0, noise["gaze_sd"]), -1, 1)), 4),
        })
    return rows
'''

# ===== run.py ================================================================
FILES['run.py'] = r'''"""Start the NeuroFocus AI web app:  python run.py   then open http://127.0.0.1:5000"""

import os

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug mode is off by default; never enable it on a network-reachable host.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("NEUROFOCUS_DEBUG") == "1")
'''

# ===== tests/__init__.py =====================================================
FILES['tests/__init__.py'] = r''''''

# ===== tests/conftest.py =====================================================
FILES['tests/conftest.py'] = r'''import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app import create_app  # noqa: E402
from backend.security import login_limiter  # noqa: E402


@pytest.fixture
def app(tmp_path):
    login_limiter._hits.clear()
    return create_app({"DATABASE": str(tmp_path / "test.sqlite3"), "SECRET_KEY": "test", "TESTING": True})


class Api:
    def __init__(self, client):
        self.c = client
        self.csrf = client.get("/api/auth/csrf").get_json()["csrf"]

    def _do(self, method, url, json=None):
        r = getattr(self.c, method)(url, json=json, headers={"X-CSRF-Token": self.csrf})
        body = r.get_json(silent=True) or {}
        if "csrf" in body:
            self.csrf = body["csrf"]
        return r

    def get(self, url):
        return self.c.get(url)

    def post(self, url, json=None):
        return self._do("post", url, json)

    def put(self, url, json=None):
        return self._do("put", url, json)

    def patch(self, url, json=None):
        return self._do("patch", url, json)

    def delete(self, url, json=None):
        return self._do("delete", url, json)


@pytest.fixture
def api(app):
    return Api(app.test_client())


@pytest.fixture
def user(api):
    r = api.post("/api/auth/register", {"email": "student@example.com", "password": "correct-horse-9",
                                         "display_name": "Test Student"})
    assert r.status_code == 201, r.get_json()
    return api
'''

# ===== tests/test_api.py =====================================================
FILES['tests/test_api.py'] = r'''def _frames(t0, n, **kw):
    base = {"face_present": True, "yaw": 0.0, "pitch": 0.0, "ear": 0.3, "gaze_h": 0.0, "gaze_v": 0.0}
    return [{**base, **kw, "t": round(t0 + i / 10, 2)} for i in range(n)]


def test_register_login_logout(api):
    r = api.post("/api/auth/register", {"email": "A@Example.com", "password": "short", "display_name": "A"})
    assert r.status_code == 400
    r = api.post("/api/auth/register", {"email": "a@example.com", "password": "long-enough-1", "display_name": "A"})
    assert r.status_code == 201
    assert api.get("/api/auth/me").status_code == 200
    assert api.post("/api/auth/register", {"email": "A@example.com", "password": "long-enough-1",
                                           "display_name": "B"}).status_code == 409
    api.post("/api/auth/logout")
    assert api.get("/api/auth/me").status_code == 401
    assert api.post("/api/auth/login", {"email": "a@example.com", "password": "wrong-pass-1"}).status_code == 401
    assert api.post("/api/auth/login", {"email": "a@example.com", "password": "long-enough-1"}).status_code == 200


def test_csrf_required(user):
    r = user.c.post("/api/sessions", json={"title": "x"})
    assert r.status_code == 403
    r = user.c.post("/api/sessions", json={"title": "x"}, headers={"X-CSRF-Token": "bogus"})
    assert r.status_code == 403


def test_login_rate_limit(api):
    api.post("/api/auth/register", {"email": "b@example.com", "password": "long-enough-1", "display_name": "B"})
    api.post("/api/auth/logout")
    for _ in range(5):
        api.post("/api/auth/login", {"email": "b@example.com", "password": "nope-nope-1"})
    r = api.post("/api/auth/login", {"email": "b@example.com", "password": "long-enough-1"})
    assert r.status_code == 429


def test_security_headers(api):
    r = api.get("/")
    assert "Content-Security-Policy" in r.headers and r.headers["X-Frame-Options"] == "DENY"


def test_session_lifecycle(user):
    sid = user.post("/api/sessions", {"title": "Biology", "subject": "Bio"}).get_json()["session"]["id"]
    # frames rejected before calibration
    assert user.post(f"/api/sessions/{sid}/frames", {"frames": _frames(0, 5)}).status_code == 409
    cal = {"center": _frames(0, 100, yaw=10, pitch=-8),
           "corners": _frames(10, 120, yaw=22, pitch=-2) ,
           "down": _frames(22, 40, yaw=10, pitch=-40)}
    r = user.post(f"/api/sessions/{sid}/calibration", {"phases": cal}).get_json()
    assert r["ok"] and r["calibration"]["calibrated"]
    assert abs(r["calibration"]["yaw0"] - 10) < 0.01
    # 30 s focused at the calibrated pose, then 10 s looking down
    r = user.post(f"/api/sessions/{sid}/frames", {"frames": _frames(0, 300, yaw=10, pitch=-8)}).get_json()
    assert r["state"] == "FOCUSED" and r["live_score"] == 100
    r = user.post(f"/api/sessions/{sid}/frames", {"frames": _frames(30, 100, yaw=10, pitch=-45)}).get_json()
    assert r["state"] == "LOOKING_DOWN" and r["distraction_count"] == 1
    # duplicates are ignored
    r2 = user.post(f"/api/sessions/{sid}/frames", {"frames": _frames(30, 100, yaw=10, pitch=-45)}).get_json()
    assert r2["total_s"] == r["total_s"]
    s = user.post(f"/api/sessions/{sid}/end", {"notes": "ok"}).get_json()["session"]
    assert s["status"] == "ended"
    # 30 s focused + 2 s onset delay focused, out of 39.9 s
    assert abs(s["focus_score"] - 100 * 32.0 / 39.9) < 0.5
    d = user.get(f"/api/sessions/{sid}").get_json()
    assert d["episodes"][0]["state"] == "LOOKING_DOWN"
    assert len(d["samples"]) == 40
    assert user.get("/api/sessions").get_json()["total"] == 1
    a = user.get("/api/analytics/summary?days=7").get_json()
    assert a["totals"]["sessions"] == 1 and a["distraction_breakdown"]["LOOKING_DOWN"]["count"] == 1


def test_sessions_are_private(app, user):
    sid = user.post("/api/sessions", {"title": "mine"}).get_json()["session"]["id"]
    from tests.conftest import Api
    other = Api(app.test_client())
    other.post("/api/auth/register", {"email": "o@example.com", "password": "long-enough-2", "display_name": "O"})
    assert other.get(f"/api/sessions/{sid}").status_code == 404
    assert other.delete(f"/api/sessions/{sid}").status_code == 404


def test_skip_calibration(user):
    sid = user.post("/api/sessions", {}).get_json()["session"]["id"]
    r = user.post(f"/api/sessions/{sid}/calibration", {"skip": True}).get_json()
    assert r["ok"] and not r["calibration"]["calibrated"]


def test_schedule_events_conflicts_and_recurrence(user):
    r = user.post("/api/schedule/events", {"title": "Chem", "kind": "class",
                                           "start_at": "2026-11-02T09:00", "end_at": "2026-11-02T10:00",
                                           "repeat_weekly": 2})
    assert r.status_code == 201 and len(r.get_json()["events"]) == 3
    r = user.post("/api/schedule/events", {"title": "Study", "start_at": "2026-11-09T09:30",
                                           "end_at": "2026-11-09T10:30"}).get_json()
    assert len(r["conflicts"]) == 1
    evs = user.get("/api/schedule/events?start=2026-11-01&end=2026-11-30").get_json()["events"]
    assert len(evs) == 4
    first = [e for e in evs if e["title"] == "Chem"][0]
    assert user.delete(f"/api/schedule/events/{first['id']}?scope=series").get_json()["deleted"] == 3
    bad = user.post("/api/schedule/events", {"title": "x", "start_at": "2026-11-02T10:00", "end_at": "2026-11-02T09:00"})
    assert bad.status_code == 400


def test_task_auto_planning_avoids_conflicts(user):
    user.post("/api/schedule/events", {"title": "Practice", "kind": "other",
                                       "start_at": "2026-11-02T16:00", "end_at": "2026-11-02T17:30"})
    t = user.post("/api/schedule/tasks", {"title": "Essay", "due_at": "2026-11-05T23:00",
                                          "estimated_min": 150, "priority": "high"}).get_json()["task"]
    r = user.post(f"/api/schedule/tasks/{t['id']}/plan", {"now": "2026-11-02T12:00", "block_min": 50}).get_json()
    assert r["placed_blocks"] == 3
    starts = [e["start_at"] for e in r["events"]]
    assert starts[0] == "2026-11-02T17:30"
    assert all(e["kind"] == "study" for e in r["events"])
    ov = user.get("/api/schedule/overview?date=2026-11-02").get_json()
    assert len(ov["today"]) >= 2 and ov["due_soon"][0]["title"] == "Essay"


def test_account_export_and_delete(user):
    user.post("/api/schedule/tasks", {"title": "x"})
    data = user.get("/api/account/export").get_json()
    assert data["user"]["email"] == "student@example.com" and len(data["tasks"]) == 1
    assert user.delete("/api/account", {"password": "wrong"}).status_code == 400
    assert user.delete("/api/account", {"password": "correct-horse-9"}).status_code == 200
    assert user.get("/api/auth/me").status_code == 401


def test_public_status_and_engine_params(api):
    assert api.get("/api/auth/status").get_json() == {"signed_in": False}
    p = api.get("/api/engine/params").get_json()
    assert p["params"]["onset_s"]["LOOKING_AWAY"] == 2.0
    assert api.get("/api/research/runs").status_code == 200
    assert api.get("/research-files/x/../../backend/app.py").status_code == 404


def test_frames_validation(user):
    sid = user.post("/api/sessions", {}).get_json()["session"]["id"]
    user.post(f"/api/sessions/{sid}/calibration", {"skip": True})
    assert user.post(f"/api/sessions/{sid}/frames", {"frames": [{"face_present": True}]}).status_code == 400
    assert user.post(f"/api/sessions/{sid}/frames", {"frames": "nope"}).status_code == 400
    assert user.post(f"/api/sessions/{sid}/frames", {"frames": [{"t": 0}] * 601}).status_code == 400
'''

# ===== tests/test_engine.py ==================================================
FILES['tests/test_engine.py'] = r'''import math

from neurofocus_engine import (ABSENT, EYES_CLOSED, FOCUSED, LOOKING_AWAY, LOOKING_DOWN,
                               AttentionEngine, FeatureFrame, TemporalFilter, calibrate,
                               default_calibration, episodes, focus_score, raw_state)


def frame(t, yaw=0.0, pitch=0.0, ear=0.3, gaze_h=0.0, present=True):
    return FeatureFrame(t=t, face_present=present, yaw=yaw, pitch=pitch, ear=ear, gaze_h=gaze_h, gaze_v=0.0)


def test_raw_state_rules():
    cal = default_calibration()
    assert raw_state(frame(0), cal) == FOCUSED
    assert raw_state(frame(0, present=False), cal) == ABSENT
    assert raw_state(frame(0, ear=0.1), cal) == EYES_CLOSED
    assert raw_state(frame(0, pitch=-30), cal) == LOOKING_DOWN
    assert raw_state(frame(0, yaw=40), cal) == LOOKING_AWAY
    assert raw_state(frame(0, yaw=-40), cal) == LOOKING_AWAY
    # eyes alone can push the combined angle over threshold
    assert raw_state(frame(0, yaw=10, gaze_h=0.6), cal) == LOOKING_AWAY


def test_filter_ignores_blinks_and_glances():
    f = TemporalFilter()
    out = [f.update(i / 10, EYES_CLOSED if 5 <= i < 8 else FOCUSED) for i in range(30)]
    assert set(out) == {FOCUSED}
    f = TemporalFilter()
    out = [f.update(i / 10, LOOKING_AWAY if 5 <= i < 20 else FOCUSED) for i in range(40)]
    assert set(out) == {FOCUSED}  # 1.5 s glance < 2 s onset


def test_filter_detects_sustained_state_with_expected_latency():
    f = TemporalFilter()
    states = [f.update(i / 10, LOOKING_AWAY if i >= 10 else FOCUSED) for i in range(60)]
    first = states.index(LOOKING_AWAY)
    assert math.isclose(first / 10 - 1.0, 2.0, abs_tol=0.11)


def test_calibration_recovers_offset_and_flips_sign():
    centre = [frame(i / 10, yaw=30 + (i % 3) * 0.2, pitch=-10, ear=0.25) for i in range(100)]
    corners = [frame(i / 10, yaw=30 + s * 12, pitch=-10 + p * 6, ear=0.25)
               for i, (s, p) in enumerate([(1, 1), (-1, 1), (1, -1), (-1, -1)] * 10)]
    down = [frame(i / 10, yaw=30, pitch=+20, ear=0.22) for i in range(30)]  # inverted convention
    cal, ok = calibrate({"center": centre, "corners": corners, "down": down})
    assert ok and cal.calibrated
    assert abs(cal.yaw0 - 30.2) < 0.5 and abs(cal.pitch0 + 10) < 0.01
    assert cal.pitch_sign == -1.0
    assert 15 <= cal.yaw_threshold <= 45
    # sitting at the calibrated pose is focused; with defaults it is not
    assert raw_state(frame(0, yaw=30, pitch=-10, ear=0.25), cal) == FOCUSED
    assert raw_state(frame(0, yaw=30, pitch=-10, ear=0.25), default_calibration()) != FOCUSED


def test_calibration_fails_without_face():
    cal, ok = calibrate({"center": [frame(i / 10, present=False) for i in range(100)]})
    assert not ok and cal.quality == "failed"


def test_focus_score_and_episodes():
    tl = [(i / 10, FOCUSED if i < 50 else LOOKING_DOWN) for i in range(101)]
    assert math.isclose(focus_score(tl), 50.0, abs_tol=0.01)
    eps = episodes(tl)
    assert len(eps) == 1 and eps[0]["state"] == LOOKING_DOWN and eps[0]["start"] == 5.0


def test_frame_from_dict_handles_blanks():
    f = FeatureFrame.from_dict({"t": "1.5", "face_present": "1", "yaw": "", "pitch": "2"})
    assert f.face_present is False  # missing pose -> treated as no detection
    f = FeatureFrame.from_dict({"t": 2, "face_present": True, "yaw": 1, "pitch": 2, "ear": "nan"})
    assert f.face_present and math.isnan(f.ear)


def test_engine_end_to_end():
    eng = AttentionEngine(default_calibration())
    frames = [frame(i / 10, pitch=-35 if 20 <= i < 80 else 0) for i in range(120)]
    out = eng.process_many(frames)
    states = [s for _, _, s in out]
    assert LOOKING_DOWN in states and states[-1] == FOCUSED
'''

# ===== tests/test_research_pipeline.py =======================================
FILES['tests/test_research_pipeline.py'] = r'''"""Tests for the experimental pipeline: separation of ground truth from the
engine, reproducibility, and correctness of the metric code."""

import ast
import csv
import json
from pathlib import Path

import numpy as np

from research.analysis.evaluate import binary_metrics, evaluate_student, gt_episodes
from research.analysis.statistics import holm, paired_test
from research.simulator.virtual_student import (observe, sample_profile, simulate_calibration,
                                                simulate_session)

ROOT = Path(__file__).resolve().parents[1]


def _imports(path):
    tree = ast.parse(path.read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add(("." * node.level) + (node.module or ""))
    return mods


def test_engine_never_imports_research_or_simulator():
    for py in (ROOT / "neurofocus_engine").glob("*.py"):
        for m in _imports(py):
            assert not m.startswith("research"), f"{py.name} imports {m}"


def test_simulator_never_imports_engine():
    for py in (ROOT / "research" / "simulator").glob("*.py"):
        for m in _imports(py):
            assert "neurofocus_engine" not in m, f"{py.name} imports {m}"


def test_predict_stage_never_reads_ground_truth():
    src = (ROOT / "research" / "pipeline" / "predict.py").read_text()
    code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
    body = code.split('"""', 2)[2]  # skip module docstring, which explains the rule
    assert "ground_truth" not in body
    assert not any(m.startswith("research.simulator") for m in _imports(ROOT / "research" / "pipeline" / "predict.py"))


def test_simulation_is_reproducible():
    def run():
        rng = np.random.default_rng([7, 1])
        p = sample_profile(1, rng)
        latent, truth = simulate_session(p, np.random.default_rng([7, 2]), 10, 120)
        obs = observe(latent, np.random.default_rng([7, 3]), 10,
                      {"pose_sd": 2, "ear_sd": 0.02, "gaze_sd": 0.05, "dropout_rate": 0.01,
                       "dropout_mean_s": 0.5, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5})
        return truth, obs
    assert run() == run()


def test_feature_rows_contain_no_label_columns():
    p = sample_profile(1, np.random.default_rng(0))
    latent, _ = simulate_session(p, np.random.default_rng(1), 10, 30)
    obs = observe(latent, np.random.default_rng(2), 10,
                  {"pose_sd": 1, "ear_sd": 0.01, "gaze_sd": 0.04, "dropout_rate": 0,
                   "dropout_mean_s": 0.3, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5})
    assert set(obs[0]) == {"t", "face_present", "yaw", "pitch", "ear", "gaze_h", "gaze_v"}
    cal = simulate_calibration(p, np.random.default_rng(3), 10)
    assert [ph for ph, _ in cal].count("center") == 100


def test_binary_metrics_hand_example():
    gt = [1, 1, 1, 0, 0, 0, 0, 0]
    pr = [1, 1, 0, 1, 0, 0, 0, 0]
    m = binary_metrics([bool(x) for x in gt], [bool(x) for x in pr])
    assert (m["tp"], m["fp"], m["fn"], m["tn"]) == (2, 1, 1, 4)
    assert abs(m["precision_distracted"] - 2 / 3) < 1e-9
    assert abs(m["recall_distracted"] - 2 / 3) < 1e-9
    assert abs(m["accuracy"] - 6 / 8) < 1e-9
    assert abs(m["specificity"] - 0.8) < 1e-9


def _truth(seq):
    rows, ep, prev = [], 0, None
    for i, b in enumerate(seq):
        if b != prev:
            ep += 1
        prev = b
        rows.append({"t": f"{i / 10:.1f}", "behavior": b,
                     "gt_state": "FOCUSED" if b == "on_task" else "LOOKING_AWAY",
                     "on_task": "1" if b == "on_task" else "0", "episode_id": str(ep)})
    return rows


def test_episode_latency_and_false_alarm():
    seq = ["on_task"] * 50 + ["away"] * 50 + ["on_task"] * 100
    truth = _truth(seq)
    pred_states = (["FOCUSED"] * 70 + ["LOOKING_AWAY"] * 35 + ["FOCUSED"] * 45
                   + ["LOOKING_DOWN"] * 20 + ["FOCUSED"] * 30)
    pred = [{"t": r["t"], "state": s} for r, s in zip(truth, pred_states)]
    m, conf, _, eps, fab = evaluate_student(truth, pred, grace_s=0.5, hz=10)
    assert len(gt_episodes(truth)) == 1
    assert eps[0]["detected"] and abs(eps[0]["latency_s"] - 2.0) < 1e-6 and eps[0]["type_correct"]
    assert m["false_alarms"] == 1 and fab == {"on_task": 1}
    assert conf["LOOKING_AWAY"]["LOOKING_AWAY"] == 30


def test_holm_and_paired_test():
    assert holm([0.01, 0.04, 0.03]) == [0.03, 0.06, 0.06]
    a = [0.8 + 0.01 * i for i in range(20)]
    b = [x - 0.05 for x in a]
    t = paired_test(a, b, 2000, 1)
    assert t["p_value"] < 0.001 and abs(t["mean_diff"] - 0.05) < 1e-9 and t["rank_biserial"] == 1.0
'''


# =============================================================================
#  LAUNCHER LOGIC
# =============================================================================

def unpack():
    """Write the project folder. Your database and experiment data are never touched."""
    marker = PROJECT_DIR / ".neurofocus_version"
    if marker.exists() and marker.read_text().strip() == VERSION:
        return
    print(f"Unpacking project into {PROJECT_DIR} ...")
    for rel, text in FILES.items():
        path = PROJECT_DIR / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    marker.write_text(VERSION)


def ensure_packages():
    missing = []
    for mod in ("flask", "numpy", "scipy", "matplotlib", "pytest"):
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"Installing Python packages ({', '.join(missing)}) ... this can take a minute.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *REQUIREMENTS])


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_vendor():
    for rel, url, digest in VENDOR:
        path = PROJECT_DIR / rel
        if path.exists() and _sha256(path) == digest:
            continue
        if MIRROR:
            url = MIRROR.rstrip("/") + "/" + rel.split("vendor/", 1)[1]
        print(f"Downloading {path.name} ...")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        try:
            with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
        except Exception as e:
            tmp.unlink(missing_ok=True)
            sys.exit(f"\nCould not download {url}\n  ({e})\n"
                     "Check your internet connection (a school network may block it) and run again.")
        if _sha256(tmp) != digest:
            tmp.unlink(missing_ok=True)
            sys.exit(f"\nDownloaded {path.name} but it did not match the expected file. Run again.")
        tmp.replace(path)


def main():
    if sys.version_info < (3, 10):
        sys.exit("NeuroFocus needs Python 3.10 or newer. Install it from python.org.")
    unpack()
    ensure_packages()
    args = sys.argv[1:]
    if "--unpack-only" in args:
        print(f"Project is in {PROJECT_DIR}")
        return
    if "--tests" in args:
        sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=PROJECT_DIR))
    if "--experiment" in args:
        sys.exit(subprocess.call([sys.executable, "-m", "research.pipeline.run_experiment",
                                  "--config", "research/config/experiment_v1.json"], cwd=PROJECT_DIR))
    ensure_vendor()
    os.chdir(PROJECT_DIR)
    sys.path.insert(0, str(PROJECT_DIR))
    from backend.app import create_app
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    url = f"http://127.0.0.1:{port}"
    print(f"\nNeuroFocus AI is running at {url}  (press Ctrl+C to stop)\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
