def _frames(t0, n, **kw):
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
