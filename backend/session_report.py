"""Detailed end-of-session report.

Everything here is derived from what the engine stored for the session (one
attention state per second, distraction episodes, frame counts, calibration)
plus the user's earlier sessions for comparison. No new measurements are made,
and the wording of insights is descriptive: it reports what the camera-based
engine observed, never what the student was thinking or any condition.
"""

import datetime as dt
import json
import statistics

from neurofocus_engine import DISTRACTED_STATES, FOCUSED, STATES

STATE_LABEL = {
    "FOCUSED": "Focused",
    "LOOKING_AWAY": "Looking away",
    "LOOKING_DOWN": "Looking down",
    "EYES_CLOSED": "Eyes closed",
    "ABSENT": "Not detected",
}
DISCLAIMER = ("Focus Score is the percentage of tracked time the engine classified your head and eyes "
              "as pointed at the screen. It describes camera-visible behaviour only. It does not measure "
              "learning or understanding, and it is not a medical or diagnostic measure.")


def _runs(samples, predicate):
    """Contiguous runs of seconds where predicate(state) holds. A missing
    second (pause or dropped data) breaks a run."""
    runs, start, prev = [], None, None
    for s in samples:
        sec, ok = s["second"], predicate(s["state"])
        if start is not None and (not ok or sec != prev + 1):
            runs.append((start, prev + 1))
            start = None
        if ok and start is None:
            start = sec
        prev = sec
    if start is not None:
        runs.append((start, prev + 1))
    return runs


def _pct(n, d):
    return 100.0 * n / d if d else None


def _segment_len(total_s):
    if total_s <= 15 * 60:
        return 60
    if total_s <= 90 * 60:
        return 300
    return 600


def _weighted_score(rows):
    tot = sum(r["total_s"] for r in rows)
    return 100.0 * sum(r["focused_s"] for r in rows) / tot if tot else None


def _clock(sec):
    sec = int(round(sec))
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _minutes(sec):
    return f"{sec / 60:.1f} min" if sec >= 60 else f"{sec:.0f} s"


def build_report(sess, samples, episodes, others, event=None):
    """sess: study_sessions row as dict; samples: [{second, state, live_score}];
    episodes: [{state, start_t, end_t}]; others: the user's other ended sessions
    (dicts with id, focus_score, focused_s, total_s, subject, started_at);
    event: linked schedule event dict or None."""
    total_s = sess["total_s"] or 0.0
    focused_s = sess["focused_s"] or 0.0
    n = len(samples)
    calibration = json.loads(sess["calibration_json"] or "null")
    params = json.loads(sess["params_json"] or "{}")

    # ---------------------------------------------------------------- overview
    started = dt.datetime.fromisoformat(sess["started_at"])
    ended = dt.datetime.fromisoformat(sess["ended_at"]) if sess.get("ended_at") else None
    overview = {
        "title": sess["title"], "subject": sess["subject"], "status": sess["status"],
        "started_at": sess["started_at"], "ended_at": sess.get("ended_at"),
        "focus_score": sess["focus_score"],
        "tracked_s": total_s, "focused_s": focused_s, "distracted_s": max(total_s - focused_s, 0.0),
        "wall_clock_s": (ended - started).total_seconds() if ended else None,
        "distraction_count": sess["distraction_count"],
        "distractions_per_hour": (sess["distraction_count"] / (total_s / 3600)) if total_s >= 60 else None,
        "planned_min": sess.get("planned_min"),
        "plan_completion_pct": _pct(total_s / 60, sess["planned_min"]) if sess.get("planned_min") else None,
        "schedule_event": event,
        "notes": sess["notes"],
    }

    # ------------------------------------------------- time in each state
    state_time = {}
    for st in STATES:
        k = sum(1 for s in samples if s["state"] == st)
        state_time[st] = {"label": STATE_LABEL[st], "seconds": k, "pct": _pct(k, n)}

    # ------------------------------------------------------ focus pattern
    bouts = [b - a for a, b in _runs(samples, lambda st: st == FOCUSED)]
    longest = max(_runs(samples, lambda st: st == FOCUSED), key=lambda r: r[1] - r[0], default=None)
    seg = _segment_len(total_s)
    segments = []
    if samples:
        first, last = samples[0]["second"], samples[-1]["second"]
        for a in range(first, last + 1, seg):
            in_seg = [s for s in samples if a <= s["second"] < a + seg]
            if in_seg:
                segments.append({"start_s": a - first, "end_s": min(a + seg, last + 1) - first,
                                 "score": _pct(sum(s["state"] == FOCUSED for s in in_seg), len(in_seg)),
                                 "seconds": len(in_seg)})
    half = n // 2
    first_half = _pct(sum(s["state"] == FOCUSED for s in samples[:half]), half) if n >= 120 else None
    second_half = _pct(sum(s["state"] == FOCUSED for s in samples[half:]), n - half) if n >= 120 else None
    first_dist = min((e["start_t"] for e in episodes), default=None)
    focus_pattern = {
        "focus_bouts": len(bouts),
        "longest_focus_s": max(bouts, default=0),
        "longest_focus_window": ({"start_s": longest[0] - samples[0]["second"],
                                  "end_s": longest[1] - samples[0]["second"]} if longest else None),
        "mean_focus_bout_s": statistics.fmean(bouts) if bouts else None,
        "median_focus_bout_s": statistics.median(bouts) if bouts else None,
        "time_to_first_distraction_s": first_dist,
        "segment_length_s": seg,
        "segments": segments,
        "first_half_score": first_half,
        "second_half_score": second_half,
        "best_segment": max(segments, key=lambda x: x["score"], default=None),
        "worst_segment": min(segments, key=lambda x: x["score"], default=None),
    }

    # ------------------------------------------------------- distractions
    end_of = lambda e: e["end_t"] if e["end_t"] is not None else sess["last_t"]  # noqa: E731
    ep_list = [{"state": e["state"], "label": STATE_LABEL[e["state"]], "start_s": e["start_t"],
                "end_s": end_of(e), "duration_s": max(end_of(e) - e["start_t"], 0.0)} for e in episodes]
    by_type = {}
    for st in DISTRACTED_STATES:
        d = [e["duration_s"] for e in ep_list if e["state"] == st]
        by_type[st] = {"label": STATE_LABEL[st], "count": len(d), "total_s": sum(d),
                       "mean_s": statistics.fmean(d) if d else None, "longest_s": max(d, default=None),
                       "pct_of_distracted_time": None}
    dist_total = sum(b["total_s"] for b in by_type.values())
    for b in by_type.values():
        b["pct_of_distracted_time"] = _pct(b["total_s"], dist_total)
    distractions = {
        "episodes": ep_list,
        "by_type": by_type,
        "longest": max(ep_list, key=lambda e: e["duration_s"], default=None),
        "mean_duration_s": statistics.fmean([e["duration_s"] for e in ep_list]) if ep_list else None,
        "short_under_10s": sum(e["duration_s"] < 10 for e in ep_list),
        "medium_10_60s": sum(10 <= e["duration_s"] < 60 for e in ep_list),
        "long_over_60s": sum(e["duration_s"] >= 60 for e in ep_list),
    }

    # -------------------------------------------------------- comparisons
    prev = [o for o in others if o["total_s"] and o["focus_score"] is not None]
    order = lambda o: (o["started_at"], o["id"])  # noqa: E731  (id breaks same-second ties)
    earlier = sorted([o for o in prev if order(o) < order(sess)], key=order)
    same_subject = [o for o in prev if sess["subject"] and o["subject"] == sess["subject"]]
    scores = sorted([o["focus_score"] for o in prev] + ([sess["focus_score"]] if sess["focus_score"] is not None else []),
                    reverse=True)
    comparison = {
        "other_sessions": len(prev),
        "your_average_score": _weighted_score(prev),
        "your_average_length_s": statistics.fmean([o["total_s"] for o in prev]) if prev else None,
        "subject_average_score": _weighted_score(same_subject),
        "subject_sessions": len(same_subject),
        "previous_session_score": earlier[-1]["focus_score"] if earlier else None,
        "rank": (scores.index(sess["focus_score"]) + 1) if sess["focus_score"] is not None and prev else None,
        "rank_of": len(scores) if prev else None,
    }

    # ------------------------------------------------------- data quality
    frames = sess.get("frames_total") or 0
    face = sess.get("frames_face") or 0
    data_quality = {
        "frames_received": frames,
        "frames_with_face": face,
        "face_detected_pct": _pct(face, frames),
        "average_frame_rate": frames / total_s if total_s else None,
        "seconds_recorded": n,
        "calibrated": bool(sess["calibrated"]),
        "calibration": calibration,
        "engine_version": sess["engine_version"],
        "engine_params": params,
    }

    report = {"overview": overview, "state_time": state_time, "focus_pattern": focus_pattern,
              "distractions": distractions, "comparison": comparison, "data_quality": data_quality,
              "disclaimer": DISCLAIMER}
    report["insights"] = _insights(report)
    return report


def _insights(r):
    """Plain-language observations. Each one states a measured fact."""
    out = []
    ov, fp, ds, cmp_, dq = r["overview"], r["focus_pattern"], r["distractions"], r["comparison"], r["data_quality"]
    if ov["tracked_s"] < 60:
        return ["This session was shorter than a minute, so there is not enough data for a detailed report."]
    if fp["longest_focus_s"]:
        w = fp["longest_focus_window"]
        out.append(f"Your longest unbroken focused stretch was {_minutes(fp['longest_focus_s'])} "
                   f"(from {_clock(w['start_s'])} to {_clock(w['end_s'])} into the session).")
    if fp["time_to_first_distraction_s"] is not None:
        out.append(f"The first distraction was detected {_clock(fp['time_to_first_distraction_s'])} into the session.")
    elif ov["tracked_s"] >= 60:
        out.append("No distraction was detected during this session.")
    top = max(ds["by_type"].values(), key=lambda b: b["total_s"])
    if top["total_s"] > 0:
        line = (f"Most distracted time was \"{top['label']}\" ({_minutes(top['total_s'])}, "
                f"{top['pct_of_distracted_time']:.0f}% of distracted time, {top['count']} episode"
                f"{'' if top['count'] == 1 else 's'}).")
        if top["label"] == "Looking down":
            line += " Note: writing notes also looks like looking down to the camera."
        out.append(line)
    if fp["first_half_score"] is not None and abs(fp["first_half_score"] - fp["second_half_score"]) >= 10:
        higher = "first" if fp["first_half_score"] > fp["second_half_score"] else "second"
        out.append(f"Focus Score was {fp['first_half_score']:.0f} in the first half and "
                   f"{fp['second_half_score']:.0f} in the second half (higher in the {higher} half).")
    if len(fp["segments"]) >= 3:
        b, w = fp["best_segment"], fp["worst_segment"]
        if b["score"] - w["score"] >= 15:
            out.append(f"Best stretch: {_clock(b['start_s'])}-{_clock(b['end_s'])} (score {b['score']:.0f}). "
                       f"Lowest: {_clock(w['start_s'])}-{_clock(w['end_s'])} (score {w['score']:.0f}).")
    if ds["long_over_60s"]:
        n_long, n_short = ds["long_over_60s"], ds["short_under_10s"]
        out.append(f"{n_long} distraction{'s' if n_long != 1 else ''} lasted over a minute, and "
                   f"{n_short} {'was' if n_short == 1 else 'were'} under 10 seconds.")
    avg = cmp_["your_average_score"]
    if avg is not None and ov["focus_score"] is not None:
        diff = ov["focus_score"] - avg
        if abs(diff) >= 5:
            out.append(f"This score is {abs(diff):.0f} points {'above' if diff > 0 else 'below'} your average "
                       f"of {avg:.0f} across {cmp_['other_sessions']} other session"
                       f"{'' if cmp_['other_sessions'] == 1 else 's'}.")
        else:
            out.append(f"This score is close to your average of {avg:.0f}.")
    if ov["plan_completion_pct"] is not None:
        out.append(f"You tracked {ov['tracked_s'] / 60:.0f} of your planned {ov['planned_min']} minutes "
                   f"({ov['plan_completion_pct']:.0f}%).")
    if not dq["calibrated"]:
        out.append("This session ran without personal calibration, so results may be less accurate "
                   "if your camera is off to the side.")
    if dq["face_detected_pct"] is not None and dq["face_detected_pct"] < 80:
        out.append(f"Your face was detected in only {dq['face_detected_pct']:.0f}% of frames. Better lighting "
                   "or facing the camera more directly would make results more reliable.")
    if dq["average_frame_rate"] is not None and dq["average_frame_rate"] < 6:
        out.append(f"The camera averaged {dq['average_frame_rate']:.1f} frames per second (target 10). "
                   "Keeping the NeuroFocus window visible helps.")
    return out
