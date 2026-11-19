"""Run the full, reproducible experiment pipeline.

  1 simulate  -> research/data/raw/<run_id>/            (features + ground truth, separate folders)
  2 predict   -> research/data/processed/<run_id>/      (engine sees features only)
  3 evaluate  -> research/results/<run_id>/             (first stage that reads ground truth)
  4 statistics, 5 figures, plus manifest.json recording exactly what was run.

Usage:
  python -m research.pipeline.run_experiment --config research/config/experiment_v1.json
  python -m research.pipeline.run_experiment --config ... --run-id my_run --students 5 --duration 300
     (--students/--duration produce a SMOKE TEST run, labelled as such; not for the paper)
"""

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import scipy

from neurofocus_engine import DEFAULT_PARAMS, ENGINE_VERSION
from research.simulator.generate import generate
from research.pipeline.predict import predict
from research.analysis.evaluate import evaluate
from research.analysis.statistics import analyze
from research.analysis.figures import make_figures

ROOT = Path(__file__).resolve().parents[1]


def _git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                              cwd=ROOT, check=True).stdout.strip()
    except Exception:
        return None


def _git_dirty():
    try:
        out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                             cwd=ROOT, check=True).stdout
        return bool(out.strip())
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--run-id")
    ap.add_argument("--students", type=int, help="override n_students (smoke test only)")
    ap.add_argument("--duration", type=float, help="override session_duration_s (smoke test only)")
    args = ap.parse_args()

    cfg_text = Path(args.config).read_text(encoding="utf-8")
    config = json.loads(cfg_text)
    smoke = args.students is not None or args.duration is not None
    if args.students:
        config["n_students"] = args.students
    if args.duration:
        config["session_duration_s"] = args.duration
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = args.run_id or f"{config['experiment_id']}_{stamp}" + ("_SMOKE" if smoke else "")
    raw_dir = ROOT / "data" / "raw" / run_id
    if raw_dir.exists():
        raise SystemExit(f"run {run_id} already exists; choose a new --run-id")

    timings = {}
    t0 = time.time()
    print(f"[1/5] simulating {config['n_students']} virtual students ...")
    generate(config, raw_dir)
    timings["simulate_s"] = time.time() - t0
    t0 = time.time()
    print("[2/5] running engine on feature files (blind to ground truth) ...")
    predict(run_id)
    timings["predict_s"] = time.time() - t0
    print("[3/5] evaluating against ground truth ...")
    out = evaluate(run_id)
    print("[4/5] statistics ...")
    analyze(run_id)
    print("[5/5] figures ...")
    make_figures(run_id)

    manifest = {
        "run_id": run_id,
        "smoke_test": smoke,
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "config_file": str(Path(args.config)),
        "config_sha256": hashlib.sha256(cfg_text.encode()).hexdigest(),
        "effective_config": config,
        "engine_version": ENGINE_VERSION,
        "engine_default_params": DEFAULT_PARAMS.to_dict(),
        "git_commit": _git_commit(),
        "git_uncommitted_changes": _git_dirty(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "timings_s": timings,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"done. results in {out}")
    print(f"read {out / 'statistics_report.md'} first.")


if __name__ == "__main__":
    main()
