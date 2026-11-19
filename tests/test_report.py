"""Tests for the detailed session report, the timeline CSV and the database upgrade."""

import sqlite3
import subprocess
from pathlib import Path

import pytest

from backend.db import init_db
from backend.session_report import build_report
from tests.test_api import _frames


def _run_session(user, segments, planned=30, subject="Chem"):
    """segments: list of (seconds, frame overrides). Returns session id."""
    sid = user.post("/api/sessions", {"title": "Test", "subject": subject, "planned_min": planned}).get_json()["session"]["id"]
    user.post(f"/api/sessions/{sid}/calibration", {"skip": True})
    t = 0.0
    for secs, kw in segments:
        frames = _frames(t, int(secs * 10), **kw)
        for i in range(0, len(frames), 600):
            user.post(f"/api/sessions/{sid}/frames", {"frames": frames[i:i + 600]})
        t += secs
    user.post(f"/api/sessions/{sid}/end", {})
    return sid


def test_report_contents(user):
    sid = _run_session(user, [(300, {}), (30, {"pitch": -45}), (200, {}), (20, {"face_present": False}), (50, {})])
    r = user.get(f"/api/sessions/{sid}/report").get_json()
    ov, fp, ds, dq = r["overview"], r["focus_pattern"], r["distractions"], r["data_quality"]
    assert ov["planned_min"] == 30 and 25 < ov["plan_completion_pct"] < 40
    assert ov["distraction_count"] == 2
    assert [e["state"] for e in ds["episodes"]] == ["LOOKING_DOWN", "ABSENT"]
    assert ds["by_type"]["LOOKING_DOWN"]["count"] == 1
    assert 27 <= ds["by_type"]["LOOKING_DOWN"]["total_s"] <= 31
    assert ds["medium_10_60s"] == 2 and ds["long_over_60s"] == 0
    assert 300 <= fp["longest_focus_s"] <= 303 and fp["focus_bouts"] == 3
    assert 301 <= fp["time_to_first_distraction_s"] <= 303
    assert fp["segment_length_s"] == 60 and len(fp["segments"]) == 10
    assert dq["frames_received"] == 6000 and abs(dq["face_detected_pct"] - 100 * 5800 / 6000) < 0.01
    assert 9.5 < dq["average_frame_rate"] < 10.5
    assert abs(sum(v["pct"] for v in r["state_time"].values()) - 100) < 1e-6
    assert any("Looking down" in s and "notes" in s for s in r["insights"])
    assert any("without personal calibration" in s for s in r["insights"])
    assert "not a medical" in r["disclaimer"]


def test_report_comparison_with_earlier_sessions(user):
    _run_session(user, [(120, {})])
    _run_session(user, [(60, {}), (60, {"yaw": 60})], subject="Bio")
    sid = _run_session(user, [(100, {}), (20, {"yaw": 60})])
    c = user.get(f"/api/sessions/{sid}/report").get_json()["comparison"]
    assert c["other_sessions"] == 2 and c["subject_sessions"] == 1
    assert c["rank_of"] == 3 and c["rank"] == 2
    assert c["previous_session_score"] is not None


def test_timeline_csv_and_privacy(app, user):
    sid = _run_session(user, [(5, {})])
    r = user.get(f"/api/sessions/{sid}/timeline.csv")
    lines = r.get_data(as_text=True).strip().splitlines()
    assert r.mimetype == "text/csv" and lines[0].startswith("second,clock,state")
    assert len(lines) == 6 and lines[1].split(",")[2] == "FOCUSED"
    from tests.conftest import Api
    other = Api(app.test_client())
    other.post("/api/auth/register", {"email": "z@example.com", "password": "long-enough-3", "display_name": "Z"})
    assert other.get(f"/api/sessions/{sid}/report").status_code == 404
    assert other.get(f"/api/sessions/{sid}/timeline.csv").status_code == 404


def test_short_session_report_is_safe():
    sess = {"title": "x", "subject": "", "status": "ended", "started_at": "2026-01-01T10:00:00+00:00",
            "ended_at": "2026-01-01T10:00:20+00:00", "focus_score": None, "total_s": 0, "focused_s": 0,
            "distraction_count": 0, "planned_min": None, "notes": "", "calibration_json": None,
            "params_json": "{}", "last_t": 0, "calibrated": 0, "engine_version": "1.0.0",
            "frames_total": 0, "frames_face": 0}
    r = build_report(sess, [], [], [])
    assert r["insights"] and r["focus_pattern"]["segments"] == []


def test_old_database_is_upgraded(tmp_path):
    # The schema as first released (before planned_min / frame counts existed).
    old_schema = subprocess.run(["git", "show", "deb818d:backend/schema.sql"], capture_output=True,
                                text=True, cwd=Path(__file__).resolve().parents[1])
    if old_schema.returncode != 0:
        pytest.skip("first-release schema not available in this checkout")
    db = tmp_path / "old.sqlite3"
    con = sqlite3.connect(db)
    con.executescript(old_schema.stdout)
    con.execute("INSERT INTO users (email, password_hash, display_name, created_at) VALUES ('a@b.c', 'x', 'A', 'now')")
    con.execute("INSERT INTO study_sessions (user_id, title, started_at, engine_version, params_json) "
                "VALUES (1, 'old session', 'now', '1.0.0', '{}')")
    con.commit()
    con.close()
    init_db(db)
    cols = {r[1] for r in sqlite3.connect(db).execute("PRAGMA table_info(study_sessions)")}
    assert {"planned_min", "frames_total", "frames_face"} <= cols
    row = sqlite3.connect(db).execute("SELECT title, frames_total FROM study_sessions").fetchone()
    assert row == ("old session", 0)  # existing data kept
