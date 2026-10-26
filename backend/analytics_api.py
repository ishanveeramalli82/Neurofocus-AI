import datetime as dt
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
