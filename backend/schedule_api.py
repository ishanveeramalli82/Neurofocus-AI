"""Schedule department: study blocks / classes / exams (calendar events),
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
