"""Stage 5 - figures for the research paper / poster.

Usage: python -m research.analysis.figures --run-id RUN
"""

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from research.simulator.ground_truth import STATE_ORDER, BEHAVIORS

ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#2563eb", "#ea580c", "#16a34a", "#9333ea"]


def _rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _matrix_plot(path, out, title):
    rows = _rows(path)
    labels = [r["truth \\ predicted"] for r in rows]
    m = np.array([[float(r[c]) for c in STATE_ORDER] for r in rows])
    norm = m / np.maximum(m.sum(axis=1, keepdims=True), 1)
    fig, ax = plt.subplots(figsize=(7, 0.6 * len(labels) + 2))
    ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
    for i in range(len(labels)):
        for j in range(len(STATE_ORDER)):
            ax.text(j, i, f"{norm[i, j]:.2f}", ha="center", va="center",
                    color="white" if norm[i, j] > 0.6 else "black", fontsize=8)
    ax.set_xticks(range(len(STATE_ORDER)), [s.replace("_", "\n") for s in STATE_ORDER], fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.set_xlabel("Engine output")
    ax.set_ylabel("Ground truth")
    ax.set_title(title + "\n(row-normalized: share of each true class's frames)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def make_figures(run_id):
    res = ROOT / "results" / run_id
    figdir = res / "figures"
    figdir.mkdir(exist_ok=True)
    cfg = json.loads((ROOT / "data" / "raw" / run_id / "config.json").read_text(encoding="utf-8"))
    levels = list(cfg["noise_levels"])
    conds = [c["name"] for c in cfg["conditions"]]
    rows = _rows(res / "metrics_per_student.csv")

    metrics = ["f1_distracted", "focus_score_abs_error", "median_latency_s", "false_alarms_per_hour"]
    for metric in metrics:
        fig, ax = plt.subplots(figsize=(6.5, 4))
        width = 0.8 / len(conds)
        for ci, cond in enumerate(conds):
            for li, lv in enumerate(levels):
                vals = [_num(r[metric]) for r in rows if r["noise"] == lv and r["condition"] == cond]
                vals = [v for v in vals if v is not None]
                x = li + (ci - (len(conds) - 1) / 2) * width
                bp = ax.boxplot(vals, positions=[x], widths=width * 0.8, patch_artist=True,
                                showfliers=False)
                for patch in bp["boxes"]:
                    patch.set_facecolor(COLORS[ci % len(COLORS)])
                    patch.set_alpha(0.5)
                jitter = np.random.default_rng(ci * 10 + li).uniform(-width * 0.25, width * 0.25, len(vals))
                ax.scatter(x + jitter, vals, s=8, color=COLORS[ci % len(COLORS)], zorder=3)
        ax.set_xticks(range(len(levels)), [f"{lv} noise" for lv in levels])
        ax.set_ylabel(metric.replace("_", " "))
        handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[i % len(COLORS)], alpha=0.5) for i in range(len(conds))]
        ax.legend(handles, conds, fontsize=8)
        ax.set_title(f"{metric.replace('_', ' ')} per virtual student (n={cfg['n_students']})", fontsize=10)
        fig.tight_layout()
        fig.savefig(figdir / f"{metric}.png", dpi=200)
        plt.close(fig)

    # Paired lines for the primary comparison
    pc = cfg.get("primary_comparison")
    if pc:
        fig, axes = plt.subplots(1, len(levels), figsize=(3.2 * len(levels), 3.6), sharey=True)
        axes = np.atleast_1d(axes)
        for ax, lv in zip(axes, levels):
            a = {r["student"]: _num(r[pc["metric"]]) for r in rows if r["noise"] == lv and r["condition"] == pc["control"]}
            b = {r["student"]: _num(r[pc["metric"]]) for r in rows if r["noise"] == lv and r["condition"] == pc["treatment"]}
            for s in a:
                ax.plot([0, 1], [a[s], b[s]], color="gray", alpha=0.5, lw=0.8, marker="o", ms=3)
            ax.set_xticks([0, 1], [pc["control"], pc["treatment"]], fontsize=8)
            ax.set_title(f"{lv} noise", fontsize=9)
        axes[0].set_ylabel(pc["metric"].replace("_", " "))
        fig.suptitle("Paired results: each line is one virtual student", fontsize=10)
        fig.tight_layout()
        fig.savefig(figdir / "paired_primary.png", dpi=200)
        plt.close(fig)

    # Latency vs false alarms trade-off (useful for the onset sweep)
    fig, ax = plt.subplots(figsize=(5.5, 4))
    for ci, cond in enumerate(conds):
        for li, lv in enumerate(levels):
            sel = [r for r in rows if r["noise"] == lv and r["condition"] == cond]
            lat = np.nanmean([_num(r["median_latency_s"]) or np.nan for r in sel])
            fa = np.mean([_num(r["false_alarms_per_hour"]) for r in sel])
            ax.scatter(lat, fa, color=COLORS[ci % len(COLORS)], marker="osD^"[li % 4], s=50,
                       label=f"{cond} / {lv}")
    ax.set_xlabel("mean of per-student median detection latency (s)")
    ax.set_ylabel("mean false alarms per on-task hour")
    ax.legend(fontsize=7)
    ax.set_title("Detection speed vs false alarms", fontsize=10)
    fig.tight_layout()
    fig.savefig(figdir / "latency_vs_false_alarms.png", dpi=200)
    plt.close(fig)

    for lv in levels:
        for cond in conds:
            _matrix_plot(res / f"confusion_states_{lv}_{cond}.csv",
                         figdir / f"confusion_states_{lv}_{cond}.png",
                         f"State confusion matrix - {cond}, {lv} noise")
            _matrix_plot(res / f"confusion_behaviors_{lv}_{cond}.csv",
                         figdir / f"confusion_behaviors_{lv}_{cond}.png",
                         f"Behavior x engine output - {cond}, {lv} noise")
    return figdir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"figures written to {make_figures(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
