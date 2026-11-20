"""Onboarding survey and personal study plan endpoints."""

import datetime as dt
import json
import statistics
import uuid

from flask import Blueprint, jsonify, request, session

from neurofocus_engine import FOCUSED

from . import planner, survey
from . import validation as v
from .auth import DEFAULT_SETTINGS
from .db import get_db, now_iso, row_dict
from .security import login_required
from .session_report import _runs

bp = Blueprint("plan", __name__, url_prefix="/api")

MIN_SESSION_S = 120          # a session must be at least 2 minutes to count toward the plan


def _uid():
    return session["user_id"]


def _profile_row():
    return get_db().execute("SELECT * FROM study_profiles WHERE user_id = ?", (_uid(),)).fetchone()


def _answers():
    row = _profile_row()
    return json.loads(row["answers_json"]) if row else {}


# ------------------------------------------------------------------ survey

@bp.get("/profile/questions")
@login_required
def questions():
    return jsonify(questions=survey.public_questions())


@bp.get("/profile")
@login_required
def get_profile():
    row = _profile_row()
    answers = json.loads(row["answers_json"]) if row else {}
    return jsonify(answers=answers, completed_at=row["completed_at"] if row else None,
                   skipped=bool(row["skipped"]) if row else False,
                   chronotype_hint=survey.chronotype_hint(answers))


def _save_profile(answers, completed, skipped):
    db = get_db()
    db.execute(
        """INSERT INTO study_profiles (user_id, answers_json, completed_at, skipped, updated_at) VALUES (?,?,?,?,?)
           ON CONFLICT(user_id) DO UPDATE SET answers_json = excluded.answers_json,
             completed_at = COALESCE(excluded.completed_at, study_profiles.completed_at),
             skipped = excluded.skipped, updated_at = excluded.updated_at""",
        (_uid(), json.dumps(answers), now_iso() if completed else None, int(skipped), now_iso()))


@bp.put("/profile")
@login_required
def put_profile():
    d = request.get_json(silent=True) or {}
    answers = survey.validate_answers(d.get("answers", {}))
    db = get_db()
    _save_profile(answers, completed=True, skipped=False)
    # Turn chosen focus-support options into settings (switches features on only).
    row = db.execute("SELECT settings_json FROM users WHERE id = ?", (_uid(),)).fetchone()
    settings = {**DEFAULT_SETTINGS, **json.loads(row["settings_json"] or "{}")}
    settings = survey.settings_from_answers(answers, settings)
    db.execute("UPDATE users SET settings_json = ? WHERE id = ?", (json.dumps(settings), _uid()))
    db.commit()
    return jsonify(answers=answers, settings=settings, chronotype_hint=survey.chronotype_hint(answers))


@bp.post("/profile/skip")
@login_required
def skip_profile():
    if not _profile_row():
        _save_profile({}, completed=False, skipped=True)
        get_db().commit()
    return jsonify(ok=True)


# ------------------------------------------------------------------ plan

def _session_stats(tz):
    """Per-session numbers the planner uses: local start time, Focus Score and the
    median length of unbroken focused stretches (minutes)."""
    db = get_db()
    rows = db.execute(
        """SELECT id, started_at, focus_score, total_s FROM study_sessions
           WHERE user_id = ? AND status = 'ended' AND total_s >= ? ORDER BY started_at DESC LIMIT 30""",
        (_uid(), MIN_SESSION_S)).fetchall()
    out = []
    for r in rows:
        samples = [dict(s) for s in db.execute(
            "SELECT second, state FROM session_samples WHERE session_id = ? ORDER BY second", (r["id"],))]
        streaks = [b - a for a, b in _runs(samples, lambda st: st == FOCUSED)]
        if not streaks:
            continue
        local = dt.datetime.fromisoformat(r["started_at"]).replace(tzinfo=None) + tz
        out.append({"id": r["id"], "local_start": local, "focus_score": r["focus_score"],
                    "median_streak_min": statistics.median(streaks) / 60})
    return out


def _tz():
    d = request.get_json(silent=True) or {}
    raw = d.get("tz_offset_min", request.args.get("tz_offset_min", 0))
    return dt.timedelta(minutes=v.integer({"x": raw}, "x", lo=-840, hi=840, default=0))


def _parse_inputs(d):
    start = v.date(d, "start_date", label="Plan start date", required=True)
    weeks = v.integer(d, "weeks", lo=1, hi=4, default=2)
    avail = d.get("availability")
    if not isinstance(avail, list) or not avail:
        raise v.ValidationError("Choose at least one day and time you can study.")
    if len(avail) > 50:
        raise v.ValidationError("Too many study times.")
    clean_av = []
    for a in avail:
        if not isinstance(a, dict):
            raise v.ValidationError("Invalid study time.")
        day = v.integer(a, "day", lo=0, hi=6, required=True)
        s, e = str(a.get("start", "")), str(a.get("end", ""))
        try:
            sm, em = planner._to_min(s), planner._to_min(e)
        except ValueError:
            raise v.ValidationError("Study times must look like 16:00.")
        if len(s) != 5 or len(e) != 5 or not (0 <= sm < em <= 24 * 60) or em - sm < 15:
            raise v.ValidationError("Each study time needs an end at least 15 minutes after its start, on the same day.")
        clean_av.append({"day": day, "start": s, "end": e})
    topics = d.get("topics")
    if not isinstance(topics, list) or not topics:
        raise v.ValidationError("Add at least one thing you will learn.")
    if len(topics) > 20:
        raise v.ValidationError("At most 20 topics per plan.")
    clean_t = []
    for t in topics:
        if not isinstance(t, dict):
            raise v.ValidationError("Invalid topic.")
        deadline = v.date(t, "deadline", label="Test/due date")
        if deadline and deadline <= start:
            raise v.ValidationError(f"The test/due date for \"{t.get('topic', '')}\" must be after the plan start date.")
        clean_t.append({
            "subject": v.text(t, "subject", max_len=60),
            "topic": v.text(t, "topic", required=True, max_len=120),
            "minutes": v.integer(t, "minutes", lo=15, hi=3000, required=True),
            "deadline": deadline,
            "priority": v.choice(t, "priority", tuple(planner.PRIORITY_RANK), "medium"),
        })
    return {"start_date": start, "weeks": weeks, "availability": clean_av, "topics": clean_t}


def _plan_groups():
    return [r["group_id"] for r in get_db().execute("SELECT group_id FROM study_plans WHERE user_id = ?", (_uid(),))]


def _busy(inputs, ignore_groups=()):
    start = inputs["start_date"]
    end = (dt.date.fromisoformat(start) + dt.timedelta(days=7 * inputs["weeks"] + 1)).isoformat()
    rows = get_db().execute(
        "SELECT start_at, end_at, recurrence_group FROM schedule_events WHERE user_id = ? AND start_at < ? AND end_at > ?",
        (_uid(), end, start)).fetchall()
    return [(dt.datetime.fromisoformat(r["start_at"]), dt.datetime.fromisoformat(r["end_at"]))
            for r in rows if r["recurrence_group"] not in ignore_groups]


def _make_plan(d):
    inputs = _parse_inputs(d)
    replace = d.get("replace_previous", True)
    stats = _session_stats(_tz())
    personal = planner.personalize(stats, _answers())
    plan = planner.build_plan(inputs, personal, _busy(inputs, set(_plan_groups()) if replace else ()))
    plan["personalization"] = {k: val for k, val in personal.items() if k != "time_bands"}
    plan["personalization"]["time_bands"] = personal["time_bands"]
    return inputs, plan, replace


@bp.get("/plan/status")
@login_required
def plan_status():
    stats = _session_stats(_tz())
    db = get_db()
    latest = db.execute("SELECT id, created_at, applied_at FROM study_plans WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                        (_uid(),)).fetchone()
    return jsonify(sessions_done=len(stats), sessions_needed=planner.MIN_SESSIONS,
                   unlocked=len(stats) >= planner.MIN_SESSIONS, survey_done=_profile_row() is not None,
                   latest_plan=row_dict(latest))


@bp.post("/plan/preview")
@login_required
def plan_preview():
    inputs, plan, _ = _make_plan(request.get_json(silent=True) or {})
    return jsonify(inputs=inputs, plan=plan)


@bp.post("/plan")
@login_required
def plan_create():
    """Generate the plan, save it, and add its blocks to the schedule."""
    d = request.get_json(silent=True) or {}
    stats_n = len(_session_stats(_tz()))
    if stats_n < planner.MIN_SESSIONS:
        return jsonify(error=f"Record {planner.MIN_SESSIONS - stats_n} more session(s) of at least 2 minutes "
                             f"to unlock your personal plan."), 409
    inputs, plan, replace = _make_plan(d)
    db = get_db()
    removed = 0
    if replace:
        today = request.args.get("today") or inputs["start_date"]
        for g in _plan_groups():
            removed += db.execute("DELETE FROM schedule_events WHERE user_id = ? AND recurrence_group = ? "
                                  "AND start_at >= ? AND completed = 0", (_uid(), g, today)).rowcount
    group = "plan-" + uuid.uuid4().hex
    for b in plan["blocks"]:
        db.execute(
            """INSERT INTO schedule_events (user_id, title, subject, kind, start_at, end_at, notes, completed,
               recurrence_group, created_at) VALUES (?,?,?,?,?,?,?,0,?,?)""",
            (_uid(), b["title"], b["subject"], "study", b["start_at"], b["end_at"],
             "Personal plan: " + b["reason"], group, now_iso()))
    # Session block timer follows the plan's block length.
    urow = db.execute("SELECT settings_json FROM users WHERE id = ?", (_uid(),)).fetchone()
    settings = {**DEFAULT_SETTINGS, **json.loads(urow["settings_json"] or "{}"), "block_min": plan["block_min"]}
    db.execute("UPDATE users SET settings_json = ? WHERE id = ?", (json.dumps(settings), _uid()))
    cur = db.execute("INSERT INTO study_plans (user_id, created_at, inputs_json, plan_json, applied_at, group_id) "
                     "VALUES (?,?,?,?,?,?)",
                     (_uid(), now_iso(), json.dumps(inputs), json.dumps(plan, default=str), now_iso(), group))
    db.commit()
    return jsonify(id=cur.lastrowid, inputs=inputs, plan=plan, replaced_events=removed), 201


@bp.get("/plan/latest")
@login_required
def plan_latest():
    row = get_db().execute("SELECT * FROM study_plans WHERE user_id = ? ORDER BY id DESC LIMIT 1", (_uid(),)).fetchone()
    if not row:
        return jsonify(plan=None)
    return jsonify(id=row["id"], created_at=row["created_at"], inputs=json.loads(row["inputs_json"]),
                   plan=json.loads(row["plan_json"]))


@bp.delete("/plan/<int:pid>")
@login_required
def plan_delete(pid):
    db = get_db()
    row = db.execute("SELECT * FROM study_plans WHERE id = ? AND user_id = ?", (pid, _uid())).fetchone()
    if not row:
        return jsonify(error="Plan not found."), 404
    removed = db.execute("DELETE FROM schedule_events WHERE user_id = ? AND recurrence_group = ? AND completed = 0",
                         (_uid(), row["group_id"])).rowcount
    db.execute("DELETE FROM study_plans WHERE id = ?", (pid,))
    db.commit()
    return jsonify(ok=True, removed_events=removed)
