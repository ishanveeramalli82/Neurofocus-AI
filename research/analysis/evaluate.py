"""Stage 3 - compare engine predictions with ground truth.

This is the first stage allowed to read BOTH predictions and ground truth.

Metrics (definitions in research/docs/05_evaluation_metrics.md):
  frame level (positive class = distracted):
    accuracy, precision, recall (sensitivity), specificity, F1, balanced accuracy, Cohen's kappa
  multiclass: 5x5 confusion matrix (expected state x predicted state),
              7x5 behavior x predicted state matrix
  episode level: episode recall, correct-type rate, detection latency, false alarms per hour
  Focus Score: |engine Focus Score - ground-truth on-task %|

Usage: python -m research.analysis.evaluate --run-id RUN
"""

import argparse
import csv
import json
import statistics
from pathlib import Path

from research.simulator.ground_truth import BEHAVIORS, STATE_ORDER

ROOT = Path(__file__).resolve().parents[1]
FOCUSED = "FOCUSED"


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _safe_div(a, b):
    return a / b if b else None


def binary_metrics(gt_distracted, pred_distracted):
    tp = sum(g and p for g, p in zip(gt_distracted, pred_distracted))
    fp = sum((not g) and p for g, p in zip(gt_distracted, pred_distracted))
    fn = sum(g and (not p) for g, p in zip(gt_distracted, pred_distracted))
    tn = sum((not g) and (not p) for g, p in zip(gt_distracted, pred_distracted))
    n = tp + fp + fn + tn
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    spec = _safe_div(tn, tn + fp)
    f1 = _safe_div(2 * tp, 2 * tp + fp + fn)
    acc = _safe_div(tp + tn, n)
    p_yes = ((tp + fp) / n) * ((tp + fn) / n) if n else 0
    p_no = ((tn + fn) / n) * ((tn + fp) / n) if n else 0
    pe = p_yes + p_no
    kappa = _safe_div(acc - pe, 1 - pe) if acc is not None else None
    bal = (recall + spec) / 2 if recall is not None and spec is not None else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "accuracy": acc,
            "precision_distracted": precision, "recall_distracted": recall,
            "specificity": spec, "f1_distracted": f1, "balanced_accuracy": bal,
            "cohen_kappa": kappa}


def gt_episodes(truth):
    eps, cur = [], None
    for r in truth:
        t, distracted = float(r["t"]), r["on_task"] == "0"
        if cur and (not distracted or r["episode_id"] != cur["id"]):
            eps.append(cur)
            cur = None
        if distracted and cur is None:
            cur = {"id": r["episode_id"], "behavior": r["behavior"],
                   "gt_state": r["gt_state"], "start": t, "end": t}
        if cur:
            cur["end"] = t
    if cur:
        eps.append(cur)
    return eps


def pred_episodes(times, states):
    eps, cur = [], None
    for i, (t, s) in enumerate(zip(times, states)):
        if cur and s == FOCUSED:
            eps.append(cur)
            cur = None
        if s != FOCUSED and cur is None:
            cur = {"start_i": i, "end_i": i}
        if cur:
            cur["end_i"] = i
    if cur:
        eps.append(cur)
    return eps


def evaluate_student(truth, pred, grace_s, hz):
    times = [float(r["t"]) for r in truth]
    if len(truth) != len(pred) or any(abs(float(p["t"]) - t) > 1e-6 for p, t in zip(pred, times)):
        raise ValueError("prediction and ground-truth timelines do not align")
    states = [p["state"] for p in pred]
    gt_dis = [r["on_task"] == "0" for r in truth]
    m = binary_metrics(gt_dis, [s != FOCUSED for s in states])

    conf = {g: {p: 0 for p in STATE_ORDER} for g in STATE_ORDER}
    bconf = {b: {p: 0 for p in STATE_ORDER} for b in BEHAVIORS}
    for r, s in zip(truth, states):
        conf[r["gt_state"]][s] += 1
        bconf[r["behavior"]][s] += 1

    # Episode-level detection
    episodes = []
    for e in gt_episodes(truth):
        i0 = int(round(e["start"] * hz))
        i1 = min(len(states) - 1, int(round((e["end"] + grace_s) * hz)))
        hits = [i for i in range(i0, i1 + 1) if states[i] != FOCUSED]
        rec = {"behavior": e["behavior"], "gt_state": e["gt_state"],
               "duration_s": round(e["end"] - e["start"] + 1 / hz, 3),
               "detected": bool(hits), "latency_s": None, "type_correct": False}
        if hits:
            rec["latency_s"] = round(times[hits[0]] - e["start"], 3)
            votes = [states[i] for i in hits]
            rec["type_correct"] = max(set(votes), key=votes.count) == e["gt_state"]
        episodes.append(rec)

    fa_by_behavior = {}
    false_alarms = 0
    for pe in pred_episodes(times, states):
        span = range(pe["start_i"], pe["end_i"] + 1)
        if not any(gt_dis[i] for i in span):
            false_alarms += 1
            behs = [truth[i]["behavior"] for i in span]
            b = max(set(behs), key=behs.count)
            fa_by_behavior[b] = fa_by_behavior.get(b, 0) + 1
    on_task_hours = sum(1 for g in gt_dis if not g) / hz / 3600

    detected = [e for e in episodes if e["detected"]]
    lat = [e["latency_s"] for e in detected]
    gt_pct = 100 * sum(1 for g in gt_dis if not g) / len(gt_dis)
    pred_pct = 100 * sum(1 for s in states if s == FOCUSED) / len(states)
    m.update({
        "n_gt_episodes": len(episodes),
        "episode_recall": _safe_div(len(detected), len(episodes)),
        "episode_type_accuracy": _safe_div(sum(e["type_correct"] for e in detected), len(detected)),
        "median_latency_s": statistics.median(lat) if lat else None,
        "mean_latency_s": statistics.fmean(lat) if lat else None,
        "false_alarms": false_alarms,
        "false_alarms_per_hour": _safe_div(false_alarms, on_task_hours),
        "gt_focus_pct": gt_pct,
        "engine_focus_score": pred_pct,
        "focus_score_abs_error": abs(pred_pct - gt_pct),
        "focus_score_signed_error": pred_pct - gt_pct,
    })
    return m, conf, bconf, episodes, fa_by_behavior


def _summ(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "mean": statistics.fmean(vals),
            "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "median": statistics.median(vals), "min": min(vals), "max": max(vals)}


def evaluate(run_id):
    raw = ROOT / "data" / "raw" / run_id
    pred_root = ROOT / "data" / "processed" / run_id / "predictions"
    out = ROOT / "results" / run_id
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads((raw / "config.json").read_text(encoding="utf-8"))
    hz, grace = config["frame_rate_hz"], config["evaluation"]["detection_grace_s"]
    truths = {sid: _read(raw / "ground_truth" / f"student_{sid:02d}.csv")
              for sid in range(1, config["n_students"] + 1)}

    rows, ep_rows, summary = [], [], {}
    for level in config["noise_levels"]:
        for cond in config["conditions"]:
            name = cond["name"]
            pooled = {g: {p: 0 for p in STATE_ORDER} for g in STATE_ORDER}
            pooled_b = {b: {p: 0 for p in STATE_ORDER} for b in BEHAVIORS}
            fa_pooled, cal_failures = {}, 0
            for sid, truth in truths.items():
                pdir = pred_root / level / name
                pred = _read(pdir / f"student_{sid:02d}.csv")
                cal_info = json.loads((pdir / f"student_{sid:02d}_calibration.json").read_text(encoding="utf-8"))
                cal_failures += int(cond["use_calibration"] and not cal_info["calibration_ok"])
                m, conf, bconf, eps, fab = evaluate_student(truth, pred, grace, hz)
                rows.append({"run_id": run_id, "noise": level, "condition": name,
                             "student": sid, "calibration_ok": cal_info["calibration_ok"], **m})
                for e in eps:
                    ep_rows.append({"noise": level, "condition": name, "student": sid, **e})
                for g in STATE_ORDER:
                    for p in STATE_ORDER:
                        pooled[g][p] += conf[g][p]
                for b in BEHAVIORS:
                    for p in STATE_ORDER:
                        pooled_b[b][p] += bconf[b][p]
                for b, c in fab.items():
                    fa_pooled[b] = fa_pooled.get(b, 0) + c
            _write_matrix(out / f"confusion_states_{level}_{name}.csv", pooled, STATE_ORDER)
            _write_matrix(out / f"confusion_behaviors_{level}_{name}.csv", pooled_b, BEHAVIORS)
            sub = [r for r in rows if r["noise"] == level and r["condition"] == name]
            metric_keys = [k for k in sub[0] if k not in ("run_id", "noise", "condition", "student", "calibration_ok")]
            summary.setdefault(level, {})[name] = {
                "metrics": {k: _summ([r[k] for r in sub]) for k in metric_keys},
                "pooled_state_confusion": pooled,
                "pooled_behavior_confusion": pooled_b,
                "false_alarms_by_behavior": fa_pooled,
                "calibration_failures": cal_failures,
            }

    _write_rows(out / "metrics_per_student.csv", rows)
    _write_rows(out / "episodes.csv", ep_rows)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return out


def _write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _write_matrix(path, m, row_labels):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["truth \\ predicted", *STATE_ORDER])
        for r in row_labels:
            w.writerow([r, *[m[r][c] for c in STATE_ORDER]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"evaluation written to {evaluate(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
