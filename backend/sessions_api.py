"""Study sessions: calibration, streaming feature frames through the engine,
history. The browser sends only numeric face features (never video)."""

import csv
import io
import json
import threading

from flask import Blueprint, Response, jsonify, request, session

from neurofocus_engine import (AttentionEngine, Calibration, DEFAULT_PARAMS, ENGINE_VERSION,
                               FOCUSED, FeatureFrame, LiveScore, calibrate,
                               default_calibration)
from neurofocus_engine.scoring import MAX_FRAME_GAP_S

from .db import get_db, now_iso, row_dict
from .security import login_required
from .session_report import build_report
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
    planned = v.integer(d, "planned_min", lo=5, hi=240)
    db = get_db()
    if event_id is not None:
        ev = db.execute("SELECT id FROM schedule_events WHERE id = ? AND user_id = ?",
                        (event_id, session["user_id"])).fetchone()
        if not ev:
            return jsonify(error="Schedule block not found."), 404
    cur = db.execute(
        """INSERT INTO study_sessions (user_id, title, subject, schedule_event_id, status, started_at,
           engine_version, params_json, planned_min) VALUES (?,?,?,?, 'calibrating', ?, ?, ?, ?)""",
        (session["user_id"], title, subject, event_id, now_iso(), ENGINE_VERSION,
         json.dumps(DEFAULT_PARAMS.to_dict()), planned))
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
        n_frames, n_face = row["frames_total"], row["frames_face"]
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
            n_frames += 1
            n_face += int(fr.face_present)
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
                      distraction_count = ?, filter_state_json = ?, frames_total = ?, frames_face = ?
                      WHERE id = ?""",
                   (last_t, focused_s, total_s, score, distractions, json.dumps(fs), n_frames, n_face, sid))
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


@bp.get("/<int:sid>/report")
@login_required
def report(sid):
    """Detailed end-of-session report (see backend/session_report.py)."""
    row = _own_session(sid)
    if not row:
        return _not_found()
    db = get_db()
    samples = [dict(r) for r in db.execute(
        "SELECT second, state, live_score FROM session_samples WHERE session_id = ? ORDER BY second", (sid,))]
    episodes = [dict(r) for r in db.execute(
        "SELECT state, start_t, end_t FROM session_episodes WHERE session_id = ? ORDER BY start_t", (sid,))]
    others = [dict(r) for r in db.execute(
        """SELECT id, focus_score, focused_s, total_s, subject, started_at FROM study_sessions
           WHERE user_id = ? AND status = 'ended' AND id != ?""", (session["user_id"], sid))]
    event = None
    if row["schedule_event_id"]:
        event = row_dict(db.execute("SELECT id, title, kind, start_at, end_at, completed FROM schedule_events "
                                    "WHERE id = ? AND user_id = ?", (row["schedule_event_id"], session["user_id"])).fetchone())
    rep = build_report(dict(row), samples, episodes, others, event)
    rep["session_id"] = sid
    rep["samples"] = samples
    resp = jsonify(rep)
    if request.args.get("download"):
        resp.headers["Content-Disposition"] = f"attachment; filename=neurofocus-session-{sid}-report.json"
    return resp


@bp.get("/<int:sid>/timeline.csv")
@login_required
def timeline_csv(sid):
    """Per-second attention timeline as a spreadsheet-friendly CSV."""
    row = _own_session(sid)
    if not row:
        return _not_found()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["second", "clock", "state", "live_focus_score_60s"])
    for r in get_db().execute(
            "SELECT second, state, live_score FROM session_samples WHERE session_id = ? ORDER BY second", (sid,)):
        w.writerow([r["second"], f"{r['second'] // 60}:{r['second'] % 60:02d}", r["state"],
                    "" if r["live_score"] is None else round(r["live_score"], 2)])
    return Response(buf.getvalue(), mimetype="text/csv", headers={
        "Content-Disposition": f"attachment; filename=neurofocus-session-{sid}-timeline.csv"})


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
