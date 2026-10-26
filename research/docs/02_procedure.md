# 2. Procedure and pre-specified analysis plan

## Before the official run (do these first, and write them in your lab notebook)

1. Read `01_research_question.md` and write your hypotheses and any numeric
   success targets in your lab notebook, with the date.
2. Freeze the code: commit everything to git. The pipeline records the git
   commit and whether there were uncommitted changes in `manifest.json`.
   Official runs should show `"git_uncommitted_changes": false`.
3. Run the automated tests: `python -m pytest`. All must pass. Record the
   result. (Passing tests show the software does what it was designed to do;
   they are not evidence of real-world accuracy.)
4. Do not edit `neurofocus_engine/params.py`, the simulator, or the
   evaluation code after this point. If you must, start a new experiment
   version (`experiment_v2.json`) and report both.

### Smoke tests vs official runs

`--students` / `--duration` flags produce a **smoke test**: a small run whose
only purpose is to check the pipeline works. Smoke-test run IDs end in
`_SMOKE` and `manifest.json` has `"smoke_test": true`. Never use smoke-test
numbers in your paper, and never tune parameters to improve them; doing so
would leak information from the test data into the design.

## Running the official experiment

```bash
python -m research.pipeline.run_experiment --config research/config/experiment_v1.json
```

The pipeline runs these stages in order:

| Stage | Module | Reads | Writes |
|---|---|---|---|
| 1. Simulate | `research/simulator/generate.py` | config | `data/raw/<run>/features/` (engine input) and `data/raw/<run>/ground_truth/` (labels), in **separate folders** |
| 2. Predict | `research/pipeline/predict.py` | **features only** | `data/processed/<run>/predictions/` |
| 3. Evaluate | `research/analysis/evaluate.py` | predictions + ground truth | `results/<run>/metrics_per_student.csv`, confusion matrices, `episodes.csv`, `summary.json` |
| 4. Statistics | `research/analysis/statistics.py` | metrics | `results/<run>/statistics.json`, `statistics_report.md` |
| 5. Figures | `research/analysis/figures.py` | metrics, confusion matrices | `results/<run>/figures/*.png` |

`manifest.json` records the config file hash, effective config, engine
version and parameters, git commit, Python/numpy/scipy versions and timings.

The exploratory experiment is run the same way with
`research/config/onset_sweep_v1.json`.

### Reproducibility

All randomness comes from `numpy.random.default_rng` seeded with
`[seed, student_id, stream]`. The same config on the same software versions
produces identical raw data. To check: run the experiment twice with
different `--run-id` values and compare `metrics_per_student.csv` (they should
be identical). Record that check in your notebook.

## Simulated calibration procedure (mirrors the app)

For each virtual student, before the session:
1. "centre" phase: 10 s looking near the screen centre;
2. "corners" phase: 3 s at each of the four screen corners;
3. "down" phase: 4 s looking at the desk.

In the `calibrated` condition the engine computes a personal calibration from
these frames. In the `uncalibrated` condition it ignores them and uses
population defaults. The calibration frames are generated with the same
sensor noise as the session.

## Pre-specified statistical analysis

All of the following was fixed before the first official run.

* **Unit of analysis:** the virtual student (n = 30 per condition). Frame-level
  metrics are computed within each student, then compared across students.
* **Primary test:** for each noise level, the paired difference in F1
  (calibrated minus uncalibrated) is tested with a two-sided **Wilcoxon
  signed-rank test** (chosen because F1 differences need not be normally
  distributed). The three p-values are adjusted with the **Holm-Bonferroni**
  method; significance level alpha = 0.05.
* **Effect sizes:** mean paired difference with a **bootstrap 95% confidence
  interval** (10,000 resamples, percentile method), matched-pairs
  **rank-biserial correlation** r, and **Cohen's d_z**.
* **Noise effect (H2):** **Friedman test** across the three noise levels
  within each calibration mode.
* **Secondary metrics:** reported with the same paired statistics but without
  multiple-comparison correction, and labelled exploratory.
* **Descriptive statistics:** mean, SD and bootstrap 95% CI for every metric
  in every condition; pooled confusion matrices.

### Interpreting the statistics honestly

* "n = 30" is 30 **simulated** students. A p-value here tells you how
  consistent the effect is across the simulated population, not how likely
  it is to hold for real people.
* Because simulated n can be increased cheaply, almost any non-zero effect can
  be made "significant". Emphasise effect sizes and confidence intervals over
  p-values, and keep n fixed at the pre-registered value.
* Report every pre-registered result, including ones that do not support
  your hypothesis.

## Data management

| Folder | Contents | Edit? |
|---|---|---|
| `research/data/raw/<run>/` | simulator output (features, ground truth, profiles, config) | Never edit. Re-generate from config + seed if lost. |
| `research/data/processed/<run>/` | engine predictions and per-student calibrations | Never edit. |
| `research/results/<run>/` | metrics, statistics, figures, manifest | Generated; do not hand-edit numbers. |
| `research/config/` | experiment definitions | Versioned; a changed config is a new experiment. |

Raw and processed data for a full run are tens of megabytes and are excluded
from git (`.gitignore`). Keep a copy (e.g. zipped on a USB drive or cloud
folder) of the raw data for every official run; judges may ask to see it.
The results folder is small and should be committed.

## Human participants

No human participants are involved. The study uses only simulated data.
Do not record anyone's camera data (including your own, or family members')
as experimental data without first checking your school's rules and the
current ISEF rules on human participants (these normally require
Institutional Review Board / Scientific Review Committee approval **before**
any data collection). Using the app yourself to check that it runs is software
testing, not data collection; do not report it as results.
