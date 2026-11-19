"""Stage 1 - generate virtual-student data.

Writes to research/data/raw/<run_id>/:
  features/<noise>/student_XX_calibration.csv   <- given to the engine
  features/<noise>/student_XX_session.csv       <- given to the engine
  ground_truth/student_XX.csv                   <- NEVER given to the engine
  ground_truth/profiles.json                    <- hidden student parameters

Usage: python -m research.simulator.generate --config research/config/experiment_v1.json --run-id RUN
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from .virtual_student import sample_profile, simulate_calibration, simulate_session, observe

ROOT = Path(__file__).resolve().parents[1]
FEATURE_FIELDS = ["t", "phase", "face_present", "yaw", "pitch", "ear", "gaze_h", "gaze_v"]
TRUTH_FIELDS = ["t", "behavior", "gt_state", "on_task", "episode_id"]


def _write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _rng(seed, *keys):
    return np.random.default_rng([seed, *keys])


def generate(config, run_dir):
    hz = config["frame_rate_hz"]
    seed = config["seed"]
    proto = config["calibration_protocol_s"]
    profiles = []
    for sid in range(1, config["n_students"] + 1):
        p = sample_profile(sid, _rng(seed, sid, 0))
        profiles.append(p.to_dict())
        # Behavior is generated ONCE per student, so every noise level and every
        # engine condition sees the same underlying behavior (paired design).
        cal_latent = simulate_calibration(p, _rng(seed, sid, 1), hz, proto["center"],
                                          proto["corner_each"], proto["down"])
        latent, truth = simulate_session(p, _rng(seed, sid, 2), hz, config["session_duration_s"])
        _write_csv(run_dir / "ground_truth" / f"student_{sid:02d}.csv", TRUTH_FIELDS, truth)
        for li, (level, noise) in enumerate(config["noise_levels"].items()):
            cal_obs = observe([s for _, s in cal_latent], _rng(seed, sid, 3, li), hz, noise)
            for (phase, _), row in zip(cal_latent, cal_obs):
                row["phase"] = phase
            obs = observe(latent, _rng(seed, sid, 4, li), hz, noise)
            for row in obs:
                row["phase"] = "session"
            fdir = run_dir / "features" / level
            _write_csv(fdir / f"student_{sid:02d}_calibration.csv", FEATURE_FIELDS, cal_obs)
            _write_csv(fdir / f"student_{sid:02d}_session.csv", FEATURE_FIELDS, obs)
    (run_dir / "ground_truth" / "profiles.json").write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    return profiles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    run_dir = ROOT / "data" / "raw" / args.run_id
    if run_dir.exists():
        raise SystemExit(f"{run_dir} already exists; raw data is never overwritten.")
    generate(config, run_dir)
    print(f"raw data written to {run_dir}")


if __name__ == "__main__":
    main()
