# NeuroFocus AI: research package

This folder holds everything for the **science-fair experiment**, kept
separate from the product code so it is clear which is which.

| | Product (`backend/`, `frontend/`) | Experiment (`research/`) |
|---|---|---|
| Purpose | A working study app | Measure how accurate the attention engine is |
| Evidence of quality | Automated software tests | Quantitative results with statistics |
| Shared code | `neurofocus_engine/`, the exact same algorithm in both | |

## Read in this order

1. [`docs/01_research_question.md`](docs/01_research_question.md): problem, question, hypotheses, variables
2. [`docs/02_procedure.md`](docs/02_procedure.md): step-by-step procedure, pre-specified analysis, data management
3. [`docs/03_algorithm.md`](docs/03_algorithm.md): features, calibration, rules, filter, Focus Score
4. [`docs/04_simulator_model.md`](docs/04_simulator_model.md): virtual students and all their assumptions
5. [`docs/05_evaluation_metrics.md`](docs/05_evaluation_metrics.md): metric definitions
6. [`docs/06_limitations_and_ethics.md`](docs/06_limitations_and_ethics.md): what you can and cannot claim
7. [`docs/07_references.md`](docs/07_references.md): references (verify each one)
8. [`docs/08_lab_notebook_template.md`](docs/08_lab_notebook_template.md)

## Run it

```bash
pip install -r requirements.txt
python -m pytest                                    # software tests
python -m research.pipeline.run_experiment --config research/config/experiment_v1.json
python -m research.pipeline.run_experiment --config research/config/onset_sweep_v1.json   # exploratory
```

A full primary run (30 students x 3 noise levels x 2 conditions, 20-minute
sessions) takes a few minutes on a laptop. Results appear in
`research/results/<run_id>/`, starting with `statistics_report.md`, and on
the app's **Research & Method** page.

## Folder map

```
research/
  config/        experiment definitions (a changed config = a new experiment)
  simulator/     virtual students + ground-truth definitions (never imported by the engine)
  pipeline/      predict.py (blind engine run) and run_experiment.py (orchestrator)
  analysis/      evaluate.py, statistics.py, figures.py
  data/raw/      simulator output: features/ and ground_truth/ in separate folders (not in git)
  data/processed/engine predictions (not in git)
  results/       metrics, confusion matrices, statistics, figures, manifest (commit these)
  docs/          methodology documents for the paper and the judges
```

## Status

No official experiment results exist yet. Run the official experiment
yourself, after completing the "Before the official run" checklist in
`docs/02_procedure.md`.
