"""Tests for the onboarding survey, the personal planner and self check-ins.

The planner tests are the "constraint-satisfaction" evaluation described in
docs/PERSONALIZATION.md: hundreds of random inputs, and every generated plan
must obey every stated rule. This verifies the software does what it is
designed to do; it is not evidence that plans improve learning.
"""

import datetime as dt
import math
import random

import pytest

from backend import planner, survey
from backend.validation import ValidationError
from tests.test_report import _run_session


# ---------------------------------------------------------------- survey

def test_survey_validation_and_settings():
    ans = survey.validate_answers({"phone_pull": "often", "break_after": "45", "supports": ["calm_mode", "checkins"],
                                   "wake_school": "06:45", "wake_free": "09:30", "unknown": "x", "goal": ""})
    assert ans == {"phone_pull": "often", "break_after": "45", "supports": ["calm_mode", "checkins"],
                   "wake_school": "06:45", "wake_free": "09:30"}
    s = survey.settings_from_answers(ans, {"block_min": 25})
    assert s["calm_mode"] and s["checkins"] and s["block_min"] == 45
    s = survey.settings_from_answers({"supports": ["short_blocks"]}, {"block_min": 25})
    assert s["block_timer"] and s["block_min"] == 15
    assert survey.chronotype_hint(ans) == "evening"
    for bad in ({"phone_pull": "very"}, {"supports": ["diagnosis"]}, {"wake_free": "25:00"}, {"goal": "x"}):
        with pytest.raises(ValidationError):
            survey.validate_answers(bad)


def test_survey_is_non_diagnostic():
    text = " ".join(q["text"] + " " + " ".join(o[1] for o in q.get("options", []))
                    for q in survey.public_questions()).lower()
    for word in ("adhd", "diagnos", "medication", "disorder", "504", "iep"):
        assert word not in text


def test_profile_api(user):
    assert user.get("/api/auth/me").get_json()["user"]["onboarding"]["done"] is False
    qs = user.get("/api/profile/questions").get_json()["questions"]
    assert len(qs) >= 10 and all("why" in q for q in qs)
    r = user.put("/api/profile", {"answers": {"supports": ["calm_mode"], "alert_time": "evening"}})
    assert r.status_code == 200 and r.get_json()["settings"]["calm_mode"] is True
    assert user.get("/api/auth/me").get_json()["user"]["onboarding"]["done"] is True
    assert user.get("/api/profile").get_json()["answers"]["alert_time"] == "evening"


# ---------------------------------------------------------------- personalization

def _sessions(n, streak_min=12.0, hour=19, score=80.0):
    base = dt.datetime(2026, 11, 2, hour)
    return [{"local_start": base + dt.timedelta(days=i), "focus_score": score, "median_streak_min": streak_min}
            for i in range(n)]


def test_shrinkage_formula():
    p = planner.personalize(_sessions(2), {})
    assert p["block_min"] == 25 and p["weight"] == 0 and p["confidence"] == "none"   # < 3 sessions: defaults only
    p = planner.personalize(_sessions(3, streak_min=10), {})
    w = 3 / 7
    assert math.isclose(p["weight"], w)
    assert p["block_min"] == planner._round5(w * 10 + (1 - w) * 25) == 20
    assert p["confidence"] == "low"
    p = planner.personalize(_sessions(12, streak_min=10), {})
    assert p["block_min"] == 15 and p["confidence"] == "high"   # more data -> closer to own streak
    p = planner.personalize(_sessions(3, streak_min=90), {"supports": ["short_blocks"]})
    assert p["prior_block_min"] == 15 and p["block_min"] <= 50  # clamped


def test_time_of_day_needs_enough_evidence():
    evening = _sessions(3, hour=19, score=90)
    morning = _sessions(3, hour=9, score=60)
    p = planner.personalize(evening + morning, {"alert_time": "morning"})
    assert p["preferred_band"] == "evening"            # data beats survey when there is enough of it
    p = planner.personalize(evening[:2] + morning, {"alert_time": "afternoon"})
    assert p["preferred_band"] == "afternoon"          # not enough evening sessions: fall back to survey


# ---------------------------------------------------------------- scheduling rules

def _random_inputs(rng):
    start = dt.date(2026, 11, 2) + dt.timedelta(days=rng.randint(0, 6))
    weeks = rng.randint(1, 4)
    avail = []
    for day in rng.sample(range(7), rng.randint(1, 7)):
        s = rng.choice([7, 9, 13, 15, 16, 18, 19]) * 60 + rng.choice([0, 30])
        e = min(s + rng.randint(30, 240), 23 * 60 + 59)
        avail.append({"day": day, "start": f"{s // 60:02d}:{s % 60:02d}", "end": f"{e // 60:02d}:{e % 60:02d}"})
    topics = []
    for i in range(rng.randint(1, 5)):
        dl = start + dt.timedelta(days=rng.randint(2, 7 * weeks)) if rng.random() < 0.7 else None
        topics.append({"subject": rng.choice(["Math", "Bio", "History"]), "topic": f"Topic {i}",
                       "minutes": rng.randint(15, 400), "deadline": dl.isoformat() if dl else None,
                       "priority": rng.choice(["low", "medium", "high"])})
    return {"start_date": start.isoformat(), "weeks": weeks, "availability": avail, "topics": topics}


@pytest.mark.parametrize("seed", range(300))
def test_every_plan_obeys_its_rules(seed):
    rng = random.Random(seed)
    inputs = _random_inputs(rng)
    personal = planner.personalize(_sessions(rng.randint(0, 12), streak_min=rng.uniform(3, 40),
                                             hour=rng.choice([8, 14, 19])),
                                   {"starts_late": rng.choice(["never", "often", None]) or None})
    start = dt.date.fromisoformat(inputs["start_date"])
    busy_s = dt.datetime.combine(start + dt.timedelta(days=1), dt.time(16))
    busy = [(busy_s, busy_s + dt.timedelta(hours=2))]
    plan = planner.build_plan(inputs, personal, busy)
    bl = plan["block_min"]
    assert planner.BLOCK_RANGE[0] <= bl <= planner.BLOCK_RANGE[1] and bl % 5 == 0
    end = start + dt.timedelta(days=7 * inputs["weeks"])
    windows = {}
    for a in inputs["availability"]:
        windows.setdefault(a["day"], []).append((a["start"], a["end"]))
    blocks = [(dt.datetime.fromisoformat(b["start_at"]), dt.datetime.fromisoformat(b["end_at"]), b) for b in plan["blocks"]]
    for s, e, b in blocks:
        assert (e - s) == dt.timedelta(minutes=bl)                                   # block length
        assert start <= s.date() < end                                               # inside the plan
        assert any(ws <= b["start"] and b["end"] <= we for ws, we in windows[s.weekday()])  # inside chosen times
        assert not any(s < be and bs < e for bs, be in busy)                         # no clash with schedule
        assert b["reason"]                                                           # every decision explained
    for (s1, e1, _), (s2, _, _) in zip(blocks, blocks[1:]):
        assert e1 <= s2                                                              # no overlaps
    assert plan["summary"]["planned_min"] <= plan["summary"]["budget_min"]          # buffer kept
    assert plan["summary"]["budget_min"] <= math.floor(plan["summary"]["available_min"] * 0.75) + 1
    for t in inputs["topics"]:
        tb = [(s, b) for s, _, b in blocks if b["topic"] == t["topic"]]
        learn = [s for s, b in tb if b["kind"] == "learn"]
        reviews = [s for s, b in tb if b["kind"] == "review"]
        per_day = {}
        for s in learn:
            per_day[s.date()] = per_day.get(s.date(), 0) + 1
        assert all(c <= planner.max_learn_blocks(bl) for c in per_day.values())        # spread out
        assert len(learn) <= math.ceil(t["minutes"] / bl)
        if t["deadline"]:
            dl = dt.date.fromisoformat(t["deadline"])
            assert all(s.date() < dl for s, _ in tb)                                  # all before the test
        if learn and reviews:
            assert min(reviews).date() > max(learn).date()                           # reviews after learning
        assert len(reviews) <= planner.MAX_REVIEWS
        if len(learn) < math.ceil(t["minutes"] / bl):
            assert any(t["topic"] in w for w in plan["warnings"])                     # shortfalls reported


def test_review_spacing_example():
    """Exam in 10 days -> reviews ~30% of the gap apart, last one the day before (Cepeda et al. 2008)."""
    inputs = {"start_date": "2026-11-02", "weeks": 2,
              "availability": [{"day": d, "start": "16:00", "end": "18:00"} for d in range(7)],
              "topics": [{"subject": "Bio", "topic": "Cells", "minutes": 50, "deadline": "2026-11-12", "priority": "high"}]}
    plan = planner.build_plan(inputs, planner.personalize([], {}), [])
    kinds = [(b["date"], b["kind"]) for b in plan["blocks"]]
    assert kinds[:2] == [("2026-11-02", "learn"), ("2026-11-02", "learn")]
    review_dates = [d for d, k in kinds if k == "review"]
    assert review_dates[-1] == "2026-11-11" and len(review_dates) >= 2
    assert all(dt.date.fromisoformat(b) > dt.date.fromisoformat(a) for a, b in zip(review_dates, review_dates[1:]))


# ---------------------------------------------------------------- plan API

PLAN = {"start_date": "2030-01-07", "weeks": 1,
        "availability": [{"day": d, "start": "16:00", "end": "18:00"} for d in range(5)],
        "topics": [{"subject": "Math", "topic": "Quadratics", "minutes": 90, "deadline": "2030-01-12", "priority": "high"}]}


def test_plan_locked_until_three_sessions_then_applies(user):
    st = user.get("/api/plan/status").get_json()
    assert st["unlocked"] is False and st["sessions_needed"] == 3
    assert user.post("/api/plan", PLAN).status_code == 409
    for _ in range(3):
        _run_session(user, [(150, {}), (30, {"yaw": 60}), (60, {})])
    assert user.get("/api/plan/status").get_json()["unlocked"] is True
    prev = user.post("/api/plan/preview", PLAN).get_json()["plan"]
    assert prev["blocks"] and prev["personalization"]["sessions_used"] == 3
    r = user.post("/api/plan", PLAN)
    assert r.status_code == 201
    evs = user.get("/api/schedule/events?start=2030-01-07&end=2030-01-14").get_json()["events"]
    assert len(evs) == len(prev["blocks"]) and all(e["notes"].startswith("Personal plan:") for e in evs)
    # regenerating replaces the old plan's future blocks instead of duplicating them
    user.post("/api/plan", PLAN)
    evs2 = user.get("/api/schedule/events?start=2030-01-07&end=2030-01-14").get_json()["events"]
    assert len(evs2) == len(evs)
    pid = user.get("/api/plan/latest").get_json()["id"]
    assert user.delete(f"/api/plan/{pid}").get_json()["removed_events"] == len(evs2)


def test_plan_input_validation(user):
    bad = [{**PLAN, "availability": []}, {**PLAN, "topics": []},
           {**PLAN, "availability": [{"day": 1, "start": "18:00", "end": "17:00"}]},
           {**PLAN, "topics": [{"topic": "x", "minutes": 60, "deadline": "2029-01-01"}]},
           {**PLAN, "start_date": "soon"}]
    for b in bad:
        assert user.post("/api/plan/preview", b).status_code == 400


# ---------------------------------------------------------------- self check-ins & reflection

def test_checkins_reflection_and_if_then(user):
    sid = user.post("/api/sessions", {"title": "t", "if_then_plan": "If I pick up my phone, then I put it away"}).get_json()["session"]["id"]
    user.post(f"/api/sessions/{sid}/calibration", {"skip": True})
    from tests.test_api import _frames
    user.post(f"/api/sessions/{sid}/frames", {"frames": _frames(0, 600)})
    assert user.post(f"/api/sessions/{sid}/checkins", {"t": 55, "rating": "on"}).status_code == 201
    assert user.post(f"/api/sessions/{sid}/checkins", {"t": 55, "rating": "bored"}).status_code == 400
    user.post(f"/api/sessions/{sid}/end", {"reflection": {"felt_focus": 5, "pulled_away": ["phone"], "helped": "music"}})
    sm = user.get(f"/api/sessions/{sid}/report").get_json()["self_monitoring"]
    assert sm["if_then_plan"].startswith("If I pick up")
    assert sm["checkins"][0]["agrees"] is True and sm["checkin_agreement_pct"] == 100
    assert sm["felt_focus_pct"] == 100 and sm["reflection"]["pulled_away"] == ["phone"]


def test_topic_without_deadline_never_starves_deadline_topic():
    """Regression: interleaving used to give half the slots to an undated topic."""
    inputs = {"start_date": "2026-11-20", "weeks": 2,
              "availability": [{"day": d, "start": "16:00", "end": "18:00"} for d in range(5)],
              "topics": [{"subject": "Bio", "topic": "Cells", "minutes": 150, "deadline": "2026-11-29", "priority": "medium"},
                         {"subject": "Math", "topic": "Quadratics", "minutes": 90, "deadline": None, "priority": "medium"}]}
    personal = planner.personalize(_sessions(3, streak_min=8), {"supports": ["short_blocks"]})
    plan = planner.build_plan(inputs, personal, [])
    assert not any("Cells" in w for w in plan["warnings"])
    assert plan["summary"]["topics"][0]["learn_blocks"] == plan["summary"]["topics"][0]["learn_needed"]
