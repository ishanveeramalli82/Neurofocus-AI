"""Read-only access to the engine's parameters and to finished experiment
results, so the Research & Method page always shows the real, current values
rather than numbers copied by hand."""

import json
from pathlib import Path

from flask import Blueprint, abort, jsonify, send_from_directory

from neurofocus_engine import DEFAULT_PARAMS, ENGINE_VERSION

bp = Blueprint("research", __name__)
RESULTS = Path(__file__).resolve().parents[1] / "research" / "results"
ALLOWED = {".png", ".csv", ".json", ".md"}


@bp.get("/api/engine/params")
def engine_params():
    return jsonify(version=ENGINE_VERSION, params=DEFAULT_PARAMS.to_dict())


@bp.get("/api/research/runs")
def runs():
    out = []
    if RESULTS.exists():
        for d in sorted(RESULTS.iterdir(), reverse=True):
            man, st = d / "manifest.json", d / "statistics.json"
            if not (man.exists() and st.exists()):
                continue
            manifest = json.loads(man.read_text(encoding="utf-8"))
            out.append({
                "run_id": d.name,
                "smoke_test": manifest.get("smoke_test", False),
                "created": manifest.get("created"),
                "experiment_id": manifest["effective_config"]["experiment_id"],
                "n_students": manifest["effective_config"]["n_students"],
                "session_duration_s": manifest["effective_config"]["session_duration_s"],
                "engine_version": manifest.get("engine_version"),
                "statistics": json.loads(st.read_text(encoding="utf-8")),
                "figures": sorted(p.name for p in (d / "figures").glob("*.png")) if (d / "figures").exists() else [],
            })
    return jsonify(runs=out)


@bp.get("/research-files/<run_id>/<path:name>")
def research_file(run_id, name):
    if Path(name).suffix not in ALLOWED or ".." in run_id:
        abort(404)
    return send_from_directory(RESULTS / run_id, name)
