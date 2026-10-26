"""Stage 2 - run the NeuroFocus engine on the simulated FEATURE files only.

This stage is deliberately blind: it reads research/data/raw/<run>/features
and never opens ground_truth/. Output goes to
research/data/processed/<run>/predictions/<noise>/<condition>/.

Usage: python -m research.pipeline.predict --run-id RUN
"""

import argparse
import csv
import dataclasses
import json
from pathlib import Path

from neurofocus_engine import (AttentionEngine, DEFAULT_PARAMS, FeatureFrame,
                               calibrate, default_calibration, focus_score)

ROOT = Path(__file__).resolve().parents[1]


def engine_params(overrides):
    if not overrides:
        return DEFAULT_PARAMS
    kw = dict(overrides)
    if "onset_s" in kw:
        kw["onset_s"] = {**DEFAULT_PARAMS.onset_s, **kw["onset_s"]}
    return dataclasses.replace(DEFAULT_PARAMS, **kw)


def _read_frames(path):
    with open(path, newline="") as f:
        return [(row["phase"], FeatureFrame.from_dict(row)) for row in csv.DictReader(f)]


def run_condition(cal_path, session_path, use_calibration, params):
    if use_calibration:
        by_phase = {}
        for phase, fr in _read_frames(cal_path):
            by_phase.setdefault(phase, []).append(fr)
        cal, ok = calibrate(by_phase, params)
    else:
        cal, ok = default_calibration(params), True
    engine = AttentionEngine(cal, params)
    out = engine.process_many([fr for _, fr in _read_frames(session_path)])
    return cal, ok, out


def predict(run_id):
    raw = ROOT / "data" / "raw" / run_id
    config = json.loads((raw / "config.json").read_text())
    out_root = ROOT / "data" / "processed" / run_id / "predictions"
    for level in config["noise_levels"]:
        fdir = raw / "features" / level
        for cond in config["conditions"]:
            params = engine_params(cond.get("engine_overrides"))
            odir = out_root / level / cond["name"]
            odir.mkdir(parents=True, exist_ok=True)
            for sid in range(1, config["n_students"] + 1):
                stem = f"student_{sid:02d}"
                cal, ok, rows = run_condition(fdir / f"{stem}_calibration.csv",
                                              fdir / f"{stem}_session.csv",
                                              cond["use_calibration"], params)
                with open(odir / f"{stem}.csv", "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["t", "raw_state", "state"])
                    w.writerows(rows)
                (odir / f"{stem}_calibration.json").write_text(json.dumps(
                    {"calibration": cal.to_dict(), "calibration_ok": ok,
                     "focus_score": focus_score([(t, s) for t, _, s in rows]),
                     "engine_params": params.to_dict()}, indent=2))
    return out_root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"predictions written to {predict(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
