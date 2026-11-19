"""Stage 4 - statistical analysis (pre-specified in research/docs/02_procedure.md).

Primary test, at each noise level separately:
  paired difference (treatment - control) of the primary metric across virtual
  students; Wilcoxon signed-rank test (two-sided); Holm-Bonferroni correction
  across noise levels; bootstrap 95% CI of the mean difference; effect sizes:
  matched-pairs rank-biserial correlation and Cohen's d_z.
Noise effect: Friedman test across noise levels within each condition.
Everything else is descriptive (mean, SD, bootstrap 95% CI).

Usage: python -m research.analysis.statistics --run-id RUN
"""

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


def _load(run_id):
    with open(ROOT / "results" / run_id / "metrics_per_student.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except (TypeError, ValueError):
                r[k] = None if v in ("", "None") else v
    return rows


def _values(rows, level, cond, metric):
    sel = sorted((r for r in rows if r["noise"] == level and r["condition"] == cond),
                 key=lambda r: r["student"])
    return [r[metric] for r in sel]


def bootstrap_ci(x, n_boot, seed, stat=np.mean):
    x = np.asarray([v for v in x if v is not None], dtype=float)
    if len(x) < 2:
        return (math.nan, math.nan)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = stat(x[idx], axis=1)
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def paired_test(a, b, n_boot, seed):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    d = np.array([x - y for x, y in pairs])
    res = {"n_pairs": len(d), "mean_a": float(np.mean([p[0] for p in pairs])),
           "mean_b": float(np.mean([p[1] for p in pairs])), "mean_diff": float(np.mean(d)),
           "median_diff": float(np.median(d))}
    res["ci95_mean_diff"] = bootstrap_ci(d, n_boot, seed)
    sd = float(np.std(d, ddof=1)) if len(d) > 1 else math.nan
    res["cohen_dz"] = float(np.mean(d) / sd) if sd and sd > 0 else math.nan
    nz = d[d != 0]
    if len(nz) == 0:
        res.update(W=math.nan, p_value=1.0, rank_biserial=0.0)
        return res
    w = stats.wilcoxon(nz)
    ranks = stats.rankdata(np.abs(nz))
    w_pos, w_neg = ranks[nz > 0].sum(), ranks[nz < 0].sum()
    res.update(W=float(w.statistic), p_value=float(w.pvalue),
               rank_biserial=float((w_pos - w_neg) / (w_pos + w_neg)))
    return res


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def analyze(run_id):
    raw_cfg = json.loads((ROOT / "data" / "raw" / run_id / "config.json").read_text(encoding="utf-8"))
    rows = _load(run_id)
    levels = list(raw_cfg["noise_levels"])
    conds = [c["name"] for c in raw_cfg["conditions"]]
    n_boot, alpha, seed = raw_cfg["bootstrap_resamples"], raw_cfg["alpha"], raw_cfg["seed"]
    metrics = list(dict.fromkeys(
        ([raw_cfg["primary_comparison"]["metric"]] if raw_cfg.get("primary_comparison") else [])
        + raw_cfg["secondary_metrics"]))
    result = {"run_id": run_id, "alpha": alpha, "descriptive": {}, "primary": None,
              "secondary_paired": {}, "noise_effect": {}}

    for level in levels:
        for cond in conds:
            for m in metrics:
                vals = [v for v in _values(rows, level, cond, m) if v is not None]
                result["descriptive"].setdefault(level, {}).setdefault(cond, {})[m] = {
                    "n": len(vals), "mean": float(np.mean(vals)) if vals else None,
                    "sd": float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
                    "ci95_mean": bootstrap_ci(vals, n_boot, seed)}

    pc = raw_cfg.get("primary_comparison")
    if pc:
        tests = {lv: paired_test(_values(rows, lv, pc["treatment"], pc["metric"]),
                                 _values(rows, lv, pc["control"], pc["metric"]), n_boot, seed)
                 for lv in levels}
        adj = holm([tests[lv]["p_value"] for lv in levels])
        for lv, p in zip(levels, adj):
            tests[lv]["p_holm"] = p
            tests[lv]["significant"] = p < alpha
        result["primary"] = {"comparison": pc, "by_noise": tests}
        for m in metrics:
            if m == pc["metric"]:
                continue
            result["secondary_paired"][m] = {
                lv: paired_test(_values(rows, lv, pc["treatment"], m),
                                _values(rows, lv, pc["control"], m), n_boot, seed)
                for lv in levels}

    if len(levels) >= 3:
        key = pc["metric"] if pc else metrics[0]
        for cond in conds:
            series = [_values(rows, lv, cond, key) for lv in levels]
            complete = [i for i in range(len(series[0])) if all(s[i] is not None for s in series)]
            st = stats.friedmanchisquare(*[[s[i] for i in complete] for s in series])
            result["noise_effect"][cond] = {"metric": key, "chi2": float(st.statistic),
                                            "p_value": float(st.pvalue), "n": len(complete)}

    out = ROOT / "results" / run_id
    (out / "statistics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "statistics_report.md").write_text(render_report(result, raw_cfg, levels, conds, metrics), encoding="utf-8")
    return out


def _f(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.{nd}f}"


def render_report(res, cfg, levels, conds, metrics):
    L = [f"# Statistical report: {cfg['experiment_id']}", "",
         f"Run: `{res['run_id']}`  |  virtual students per cell: {cfg['n_students']}  |  "
         f"session length: {cfg['session_duration_s']} s  |  alpha = {res['alpha']}", "",
         "> These numbers describe the engine's performance on SIMULATED students generated by the "
         "model in research/docs/04_simulator_model.md. They are evidence about the algorithm under "
         "the stated assumptions, not evidence of accuracy with real students.", ""]
    if res["primary"]:
        pc = res["primary"]["comparison"]
        L += [f"## Primary test: {pc['treatment']} vs {pc['control']} on `{pc['metric']}`", "",
              "| noise | mean treatment | mean control | mean diff [95% CI] | Wilcoxon W | p | p (Holm) | rank-biserial r | d_z |",
              "|---|---|---|---|---|---|---|---|---|"]
        for lv in levels:
            t = res["primary"]["by_noise"][lv]
            lo, hi = t["ci95_mean_diff"]
            L.append(f"| {lv} | {_f(t['mean_a'])} | {_f(t['mean_b'])} | {_f(t['mean_diff'])} "
                     f"[{_f(lo)}, {_f(hi)}] | {_f(t['W'], 1)} | {_f(t['p_value'], 4)} | "
                     f"{_f(t['p_holm'], 4)} | {_f(t['rank_biserial'])} | {_f(t['cohen_dz'])} |")
        L.append("")
        if res["secondary_paired"]:
            L += ["## Secondary paired comparisons (not corrected; interpret as exploratory)", "",
                  "| metric | noise | mean treatment | mean control | mean diff [95% CI] | p |",
                  "|---|---|---|---|---|---|"]
            for m, by in res["secondary_paired"].items():
                for lv in levels:
                    t = by[lv]
                    lo, hi = t["ci95_mean_diff"]
                    L.append(f"| {m} | {lv} | {_f(t['mean_a'])} | {_f(t['mean_b'])} | "
                             f"{_f(t['mean_diff'])} [{_f(lo)}, {_f(hi)}] | {_f(t['p_value'], 4)} |")
            L.append("")
    if res["noise_effect"]:
        L += ["## Effect of noise level (Friedman test)", "", "| condition | metric | chi2 | p | n |",
              "|---|---|---|---|---|"]
        for c, t in res["noise_effect"].items():
            L.append(f"| {c} | {t['metric']} | {_f(t['chi2'], 2)} | {_f(t['p_value'], 4)} | {t['n']} |")
        L.append("")
    L += ["## Descriptive statistics (mean ± SD, bootstrap 95% CI of the mean)", ""]
    for m in metrics:
        L += [f"### {m}", "", "| noise | " + " | ".join(conds) + " |",
              "|---|" + "---|" * len(conds)]
        for lv in levels:
            cells = []
            for c in conds:
                d = res["descriptive"][lv][c][m]
                lo, hi = d["ci95_mean"]
                cells.append(f"{_f(d['mean'])} ± {_f(d['sd'])} [{_f(lo)}, {_f(hi)}]")
            L.append(f"| {lv} | " + " | ".join(cells) + " |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(f"statistics written to {analyze(ap.parse_args().run_id)}")


if __name__ == "__main__":
    main()
