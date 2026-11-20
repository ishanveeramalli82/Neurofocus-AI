"""Personal study planner (algorithm v1.0).

Builds a week-by-week study plan from
  * what the student enters: the days and times they can study, and what they
    will learn (subject, topic, minutes needed, optional test/due date);
  * their onboarding-survey answers (backend/survey.py);
  * their own recorded sessions (focus streaks, Focus Score by time of day).

This is RULE-BASED PERSONALIZATION WITH STATISTICAL SHRINKAGE, not a trained
machine-learning model: 3-4 sessions are far too few observations to train or
validate one. Each rule below names its source; numbers marked "heuristic"
are design choices, not published values. Every scheduled block carries a
plain-language reason. Full write-up: docs/PERSONALIZATION.md.
"""

import datetime as dt
import math
import statistics

ALGORITHM_VERSION = "1.0"

# ---- defaults and constants ------------------------------------------------
DEFAULT_BLOCK_MIN = 25          # 25 + 5 is close to the 24 + 6 "systematic breaks" condition (Biwer et al. 2023)
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15             # longer break after several blocks (Albulescu et al. 2022 meta-regression)
LONG_BREAK_EVERY = 3
BLOCK_RANGE = (10, 50)          # heuristic safe range
PRIOR_STRENGTH_K = 4            # shrinkage prior strength in "sessions" (heuristic, k ~ 4-5)
MIN_SESSIONS = 3                # below this, defaults only (heuristic minimum-data rule)
MIN_SESSIONS_PER_BAND = 3       # needed before ranking a time of day (heuristic)
BAND_MIN_DIFF = 5.0             # Focus Score points a band must beat the average by (heuristic)
FILL_RATIO = 0.75               # plan at most 75% of available time (planning fallacy; Buehler et al. 1994; heuristic %)
FILL_RATIO_LATE_STARTER = 0.70
MAX_LEARN_MIN_PER_TOPIC_PER_DAY = 60    # spread practice over days (distributed practice; Cepeda et al. 2006; heuristic cap)
MAX_REVIEWS = 3

BANDS = (("morning", 5, 12), ("afternoon", 12, 17), ("evening", 17, 21), ("night", 21, 29))
BAND_LABEL = {"morning": "morning", "afternoon": "afternoon", "evening": "evening", "night": "late night"}
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

SOURCES = {
    "spacing": "Cepeda et al. 2006 (Psychological Bulletin); Cepeda et al. 2008 (Psychological Science)",
    "testing": "Dunlosky et al. 2013 (Psychological Science in the Public Interest); Rowland 2014 (Psychological Bulletin)",
    "breaks": "Biwer et al. 2023 (British Journal of Educational Psychology); Albulescu et al. 2022 (PLOS ONE)",
    "buffer": "Buehler, Griffin & Ross 1994 (Journal of Personality and Social Psychology), planning fallacy",
    "shrinkage": "Empirical-Bayes shrinkage (Efron & Morris 1975)",
    "if_then": "Gollwitzer & Sheeran 2006 (Advances in Experimental Social Psychology)",
}


def max_learn_blocks(block_min):
    """Per-day cap on new-learning blocks of one topic: about an hour, at least 2 blocks."""
    return max(2, MAX_LEARN_MIN_PER_TOPIC_PER_DAY // block_min)


def band_of(hour):
    h = hour if hour >= 5 else hour + 24
    for name, lo, hi in BANDS:
        if lo <= h < hi:
            return name
    return "night"


def _round5(x):
    return int(5 * round(x / 5))


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _to_min(hhmm):
    return int(hhmm[:2]) * 60 + int(hhmm[3:5])


# ---------------------------------------------------------------------------
# 1. Personalization: block length and best time of day
# ---------------------------------------------------------------------------

def personalize(sessions, answers):
    """sessions: [{local_start: datetime, focus_score: float, median_streak_min: float}]
    answers: survey answers dict. Returns a dict of decisions + explanations."""
    n = len(sessions)
    supports = set(answers.get("supports", []))
    prior = int(answers["break_after"]) if answers.get("break_after") else DEFAULT_BLOCK_MIN
    prior_src = "your survey answer" if answers.get("break_after") else "the research default"
    if "short_blocks" in supports and prior > 15:
        prior, prior_src = 15, "your 'shorter study blocks' choice"
    prior = _clamp(prior, *BLOCK_RANGE)

    out = {"sessions_used": n, "prior_block_min": prior, "prior_source": prior_src}
    if n < MIN_SESSIONS:
        out.update(block_min=prior, weight=0.0, personal_median_min=None, confidence="none",
                   block_reason=(f"Block length is {prior} min from {prior_src}. Your own sessions are not used yet: "
                                 f"at least {MIN_SESSIONS} are needed (you have {n})."))
    else:
        personal = statistics.median(s["median_streak_min"] for s in sessions)
        w = n / (n + PRIOR_STRENGTH_K)
        raw = w * personal + (1 - w) * prior
        block = _clamp(_round5(raw), *BLOCK_RANGE)
        out.update(block_min=block, weight=w, personal_median_min=personal,
                   confidence="low" if n < 5 else "medium" if n < 10 else "high",
                   block_reason=(f"Block length = {w:.2f} x your typical focus streak ({personal:.1f} min) + "
                                 f"{1 - w:.2f} x {prior} min ({prior_src}) = {raw:.1f}, rounded to {block} min. "
                                 f"The weight {w:.2f} = n/(n+k) with n = {n} sessions and k = {PRIOR_STRENGTH_K}, so "
                                 f"your own data counts more as you record more sessions. Source: {SOURCES['shrinkage']}."))

    # Time of day: shrink each band's average toward your overall average.
    scored = [s for s in sessions if s.get("focus_score") is not None]
    overall = statistics.fmean(s["focus_score"] for s in scored) if scored else None
    bands = {}
    for name, _, _ in BANDS:
        sc = [s["focus_score"] for s in scored if band_of(s["local_start"].hour) == name]
        if sc:
            adj = (len(sc) * statistics.fmean(sc) + PRIOR_STRENGTH_K * overall) / (len(sc) + PRIOR_STRENGTH_K)
            bands[name] = {"sessions": len(sc), "mean": statistics.fmean(sc), "adjusted": adj}
    best = None
    eligible = {k: b for k, b in bands.items() if b["sessions"] >= MIN_SESSIONS_PER_BAND}
    if eligible and overall is not None:
        k, b = max(eligible.items(), key=lambda kv: kv[1]["adjusted"])
        if b["adjusted"] - overall >= BAND_MIN_DIFF:
            best = k
    if best:
        pref, pref_reason = best, (f"Your {BAND_LABEL[best]} sessions score higher (adjusted average "
                                   f"{bands[best]['adjusted']:.0f} vs {overall:.0f} overall), so those slots are filled first.")
    elif answers.get("alert_time"):
        pref = answers["alert_time"]
        pref_reason = (f"You said you feel most alert in the {BAND_LABEL[pref]}, so those slots are filled first. "
                       f"Your sessions don't show a clear best time yet (needs {MIN_SESSIONS_PER_BAND}+ sessions "
                       f"in a time of day and a {BAND_MIN_DIFF:.0f}-point difference).")
    else:
        pref, pref_reason = None, "No preferred time of day yet, so the earliest free slots are used first."
    out.update(time_bands=bands, overall_score=overall, preferred_band=pref, preferred_reason=pref_reason)

    late = answers.get("starts_late") in ("often", "always")
    out["fill_ratio"] = FILL_RATIO_LATE_STARTER if late else FILL_RATIO
    out["lead_days"] = 2 if late else 1
    out["buffer_reason"] = (f"At most {out['fill_ratio']:.0%} of your available time is planned; the rest is catch-up "
                            f"time, because people usually underestimate how long work takes ({SOURCES['buffer']}). "
                            f"New material is finished {out['lead_days']} day{'s' if out['lead_days'] > 1 else ''} "
                            f"before each test, leaving time to review." + (" (More buffer because you said you often start "
                                                                           "later than planned.)" if late else ""))
    return out


# ---------------------------------------------------------------------------
# 2. Scheduling
# ---------------------------------------------------------------------------

def _free_intervals(day, windows, busy):
    """Windows [(start_min, end_min)] on `day`, minus busy (start_dt, end_dt) intervals."""
    out = []
    for ws, we in windows:
        s = dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=ws)
        e = dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=we)
        pieces = [(s, e)]
        for bs, be in busy:
            nxt = []
            for ps, pe in pieces:
                if be <= ps or bs >= pe:
                    nxt.append((ps, pe))
                    continue
                if bs > ps:
                    nxt.append((ps, bs))
                if be < pe:
                    nxt.append((be, pe))
            pieces = nxt
        out += [p for p in pieces if p[1] > p[0]]
    return sorted(out)


def _slots(interval, block):
    """Cut a free interval into study blocks with short/long breaks between them."""
    s, e = interval
    out, k = [], 0
    while s + dt.timedelta(minutes=block) <= e:
        out.append((s, s + dt.timedelta(minutes=block)))
        k += 1
        brk = LONG_BREAK_MIN if k % LONG_BREAK_EVERY == 0 else SHORT_BREAK_MIN
        s = s + dt.timedelta(minutes=block + brk)
    return out


def _review_dates(first, last, deadline, horizon_end, study_days=None):
    """Spaced self-test dates after learning finished on `last`. The final review
    goes on the last day before the test that has study time (`study_days`)."""
    if deadline:
        span = max((deadline - first).days, 1)
        frac = 0.3 if span <= 14 else 0.1
        gap = max(1, round(frac * span))
        dates = []
        d = last + dt.timedelta(days=gap)
        while d < deadline and len(dates) < MAX_REVIEWS - 1:
            dates.append(d)
            d += dt.timedelta(days=gap)
        final = deadline - dt.timedelta(days=1)
        if study_days:
            earlier = [x for x in study_days if last < x < deadline]
            final = max(earlier) if earlier else final
        dates = [x for x in dates if x < final]
        if final > last and final not in dates:
            dates.append(final)
        return sorted(set(dates))[:MAX_REVIEWS], gap, frac
    dates = [last + dt.timedelta(days=g) for g in (2, 7) if last + dt.timedelta(days=g) <= horizon_end]
    return dates, None, None


def build_plan(inputs, personal, busy=()):
    """inputs: {start_date, weeks, availability: [{day, start, end}], topics: [...]}
    personal: output of personalize(). busy: [(start_dt, end_dt)] existing events.
    Returns the plan dict (blocks with reasons, summary, warnings)."""
    block = personal["block_min"]
    start = dt.date.fromisoformat(inputs["start_date"])
    days = [start + dt.timedelta(days=i) for i in range(7 * inputs["weeks"])]
    horizon_end = days[-1]
    by_day = {}
    for a in inputs["availability"]:
        by_day.setdefault(a["day"], []).append((_to_min(a["start"]), _to_min(a["end"])))
    pref = personal.get("preferred_band")
    rank = lambda s: (0 if pref and band_of(s[0].hour) == pref else 1, s[0])  # noqa: E731

    all_slots, available_min = [], 0
    for d in days:
        free = _free_intervals(d, by_day.get(d.weekday(), []), busy)
        available_min += sum((e - s).total_seconds() / 60 for s, e in free)
        day_slots = [sl for iv in free for sl in _slots(iv, block)]
        all_slots += sorted(day_slots, key=rank)          # preferred time of day first
    budget = math.floor(available_min * personal["fill_ratio"])

    topics = []
    for i, t in enumerate(inputs["topics"]):
        dl = dt.date.fromisoformat(t["deadline"]) if t.get("deadline") else None
        topics.append({**t, "idx": i, "deadline_d": dl, "need": math.ceil(t["minutes"] / block),
                       "done": 0, "first": None, "last": None, "reviews": [], "learn_dates": {},
                       "learn_by": (dl - dt.timedelta(days=personal["lead_days"])) if dl else horizon_end})
    order = sorted(topics, key=lambda t: (t["deadline_d"] or dt.date.max, PRIORITY_RANK[t["priority"]], t["idx"]))

    study_days = sorted({s.date() for s, _ in all_slots})
    blocks, used, last_topic_on = [], 0, {}
    cap = max_learn_blocks(block)
    for s, e in all_slots:
        if used + block > budget:
            break
        d = s.date()
        choice, kind, reason = None, None, None
        # (a) a spaced review that is due
        for t in order:
            due = [r for r in t["reviews"] if r["date"] <= d and not r["done"]]
            if due and (t["deadline_d"] is None or d < t["deadline_d"]):
                choice, kind, review = t, "review", due[0]
                review["done"] = True
                reason = review["reason"]
                break
        # (b) otherwise new learning, earliest deadline first, avoiding the same topic twice in a row
        if not choice:
            cands = [t for t in order if t["done"] < t["need"] and d <= t["learn_by"]
                     and t["learn_dates"].get(d, 0) < cap]
            if cands:
                # Alternate topics (interleaving), but never let a topic without a deadline
                # push aside one that has a deadline.
                alt = [t for t in cands if last_topic_on.get(d) != t["idx"]
                       and (cands[0]["deadline_d"] is None or t["deadline_d"] is not None)]
                choice = (alt or cands)[0]
                kind = "learn"
                part = choice["done"] + 1
                reason = (f"Part {part} of {choice['need']}. " +
                          (f"Scheduled before the {choice['deadline_d'].isoformat()} deadline "
                           f"(earliest deadline first). " if choice["deadline_d"] else "") +
                          f"At most {cap * block} min of one topic per day, so practice is "
                          f"spread over several days ({SOURCES['spacing']}).")
                choice["done"] += 1
                choice["learn_dates"][d] = choice["learn_dates"].get(d, 0) + 1
                choice["first"] = choice["first"] or d
                choice["last"] = d
                if choice["done"] == choice["need"]:
                    dates, gap, frac = _review_dates(choice["first"], d, choice["deadline_d"], horizon_end,
                                                     study_days)
                    for rd in dates:
                        why = (f"Self-test review: test yourself instead of rereading ({SOURCES['testing']}). ")
                        if gap:
                            why += (f"Reviews are spaced about {frac:.0%} of the time until the test apart "
                                    f"(every {gap} day{'s' if gap > 1 else ''}) ({SOURCES['spacing']}).")
                        else:
                            why += f"Spaced 2 and 7 days after learning ({SOURCES['spacing']})."
                        choice["reviews"].append({"date": rd, "done": False, "reason": why})
        if not choice:
            continue
        last_topic_on[d] = choice["idx"]
        used += block
        blocks.append({
            "date": d.isoformat(), "start": s.strftime("%H:%M"), "end": e.strftime("%H:%M"),
            "start_at": s.isoformat(timespec="minutes"), "end_at": e.isoformat(timespec="minutes"),
            "subject": choice.get("subject", ""), "topic": choice["topic"], "kind": kind,
            "title": f"{choice['topic']} - {'learn' if kind == 'learn' else 'self-test review'}",
            "reason": reason,
        })
    blocks.sort(key=lambda b: b["start_at"])

    warnings = []
    for t in topics:
        missing = (t["need"] - t["done"]) * block
        if missing > 0:
            where = f" before {t['learn_by'].isoformat()}" if t["deadline_d"] else " in this plan"
            warnings.append(f"Could not fit {missing} min of \"{t['topic']}\"{where}. Add more study times, "
                            f"lower the minutes needed, or move the deadline.")
        skipped = [r for r in t["reviews"] if not r["done"]]
        if skipped:
            warnings.append(f"{len(skipped)} review(s) for \"{t['topic']}\" did not fit (no free study time on or "
                            f"after the review date{' before the deadline' if t['deadline_d'] else ''}).")
    if not inputs["availability"]:
        warnings.append("No study times were entered.")

    return {
        "algorithm_version": ALGORITHM_VERSION,
        "block_min": block, "short_break_min": SHORT_BREAK_MIN, "long_break_min": LONG_BREAK_MIN,
        "long_break_every": LONG_BREAK_EVERY,
        "blocks": blocks,
        "summary": {
            "available_min": round(available_min), "planned_min": used, "budget_min": budget,
            "free_pct": round(100 * (1 - used / available_min)) if available_min else None,
            "topics": [{"topic": t["topic"], "subject": t.get("subject", ""), "learn_blocks": t["done"],
                        "learn_needed": t["need"], "reviews": sum(r["done"] for r in t["reviews"]),
                        "deadline": t["deadline_d"].isoformat() if t["deadline_d"] else None} for t in topics],
        },
        "warnings": warnings,
        "why": [
            personal["block_reason"],
            (f"After each {block}-min block you get a {SHORT_BREAK_MIN}-min break, and a {LONG_BREAK_MIN}-min break "
             f"after every {LONG_BREAK_EVERY} blocks. Planned breaks improved mood and reduced fatigue in studies "
             f"({SOURCES['breaks']}); they are a popular default, not proven to raise grades."),
            personal["preferred_reason"],
            personal["buffer_reason"],
            (f"Topics with the nearest deadline are scheduled first; each topic is spread over several days and "
             f"followed by spaced self-test reviews ({SOURCES['spacing']}; {SOURCES['testing']})."),
        ],
        "confidence": personal["confidence"],
    }
