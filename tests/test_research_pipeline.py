"""Tests for the experimental pipeline: separation of ground truth from the
engine, reproducibility, and correctness of the metric code."""

import ast
import csv
import json
from pathlib import Path

import numpy as np

from research.analysis.evaluate import binary_metrics, evaluate_student, gt_episodes
from research.analysis.statistics import holm, paired_test
from research.simulator.virtual_student import (observe, sample_profile, simulate_calibration,
                                                simulate_session)

ROOT = Path(__file__).resolve().parents[1]


def _imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add(("." * node.level) + (node.module or ""))
    return mods


def test_engine_never_imports_research_or_simulator():
    for py in (ROOT / "neurofocus_engine").glob("*.py"):
        for m in _imports(py):
            assert not m.startswith("research"), f"{py.name} imports {m}"


def test_simulator_never_imports_engine():
    for py in (ROOT / "research" / "simulator").glob("*.py"):
        for m in _imports(py):
            assert "neurofocus_engine" not in m, f"{py.name} imports {m}"


def test_predict_stage_never_reads_ground_truth():
    src = (ROOT / "research" / "pipeline" / "predict.py").read_text(encoding="utf-8")
    code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
    body = code.split('"""', 2)[2]  # skip module docstring, which explains the rule
    assert "ground_truth" not in body
    assert not any(m.startswith("research.simulator") for m in _imports(ROOT / "research" / "pipeline" / "predict.py"))


def test_simulation_is_reproducible():
    def run():
        rng = np.random.default_rng([7, 1])
        p = sample_profile(1, rng)
        latent, truth = simulate_session(p, np.random.default_rng([7, 2]), 10, 120)
        obs = observe(latent, np.random.default_rng([7, 3]), 10,
                      {"pose_sd": 2, "ear_sd": 0.02, "gaze_sd": 0.05, "dropout_rate": 0.01,
                       "dropout_mean_s": 0.5, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5})
        return truth, obs
    assert run() == run()


def test_feature_rows_contain_no_label_columns():
    p = sample_profile(1, np.random.default_rng(0))
    latent, _ = simulate_session(p, np.random.default_rng(1), 10, 30)
    obs = observe(latent, np.random.default_rng(2), 10,
                  {"pose_sd": 1, "ear_sd": 0.01, "gaze_sd": 0.04, "dropout_rate": 0,
                   "dropout_mean_s": 0.3, "extreme_yaw_deg": 60, "extreme_yaw_miss_prob": 0.5})
    assert set(obs[0]) == {"t", "face_present", "yaw", "pitch", "ear", "gaze_h", "gaze_v"}
    cal = simulate_calibration(p, np.random.default_rng(3), 10)
    assert [ph for ph, _ in cal].count("center") == 100


def test_binary_metrics_hand_example():
    gt = [1, 1, 1, 0, 0, 0, 0, 0]
    pr = [1, 1, 0, 1, 0, 0, 0, 0]
    m = binary_metrics([bool(x) for x in gt], [bool(x) for x in pr])
    assert (m["tp"], m["fp"], m["fn"], m["tn"]) == (2, 1, 1, 4)
    assert abs(m["precision_distracted"] - 2 / 3) < 1e-9
    assert abs(m["recall_distracted"] - 2 / 3) < 1e-9
    assert abs(m["accuracy"] - 6 / 8) < 1e-9
    assert abs(m["specificity"] - 0.8) < 1e-9


def _truth(seq):
    rows, ep, prev = [], 0, None
    for i, b in enumerate(seq):
        if b != prev:
            ep += 1
        prev = b
        rows.append({"t": f"{i / 10:.1f}", "behavior": b,
                     "gt_state": "FOCUSED" if b == "on_task" else "LOOKING_AWAY",
                     "on_task": "1" if b == "on_task" else "0", "episode_id": str(ep)})
    return rows


def test_episode_latency_and_false_alarm():
    seq = ["on_task"] * 50 + ["away"] * 50 + ["on_task"] * 100
    truth = _truth(seq)
    pred_states = (["FOCUSED"] * 70 + ["LOOKING_AWAY"] * 35 + ["FOCUSED"] * 45
                   + ["LOOKING_DOWN"] * 20 + ["FOCUSED"] * 30)
    pred = [{"t": r["t"], "state": s} for r, s in zip(truth, pred_states)]
    m, conf, _, eps, fab = evaluate_student(truth, pred, grace_s=0.5, hz=10)
    assert len(gt_episodes(truth)) == 1
    assert eps[0]["detected"] and abs(eps[0]["latency_s"] - 2.0) < 1e-6 and eps[0]["type_correct"]
    assert m["false_alarms"] == 1 and fab == {"on_task": 1}
    assert conf["LOOKING_AWAY"]["LOOKING_AWAY"] == 30


def test_holm_and_paired_test():
    assert holm([0.01, 0.04, 0.03]) == [0.03, 0.06, 0.06]
    a = [0.8 + 0.01 * i for i in range(20)]
    b = [x - 0.05 for x in a]
    t = paired_test(a, b, 2000, 1)
    assert t["p_value"] < 0.001 and abs(t["mean_diff"] - 0.05) < 1e-9 and t["rank_biserial"] == 1.0
