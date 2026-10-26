import json

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
