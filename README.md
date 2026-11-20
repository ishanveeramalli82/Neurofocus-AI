# NeuroFocus AI

A webcam-based study-focus tracker with a transparent, testable attention
engine, built as both a working product and a science-fair engineering
research project.

* **Product:** accounts, camera calibration, on-device computer vision, live
  Focus Score, a "How do you study?" survey, a personal study plan that
  unlocks after 3 sessions, ADHD-friendly focus supports (calm mode, visual
  timer, break timer, self check-ins, if-then plans), a pop-out mini window that floats over other tabs and apps,
  detailed session reports, session history, analytics, and a Schedule
  department (calendar, tasks, recurring classes, conflict detection,
  automatic study-block planning).
* **Research:** a reproducible virtual-student experiment that measures how
  accurately the attention engine detects distraction. See
  [`research/README.md`](research/README.md).

> NeuroFocus estimates where your head and eyes point. It does not measure
> learning, and it is not a medical or diagnostic tool (it does not detect or
> diagnose ADHD or any other condition). Current accuracy figures come from
> simulated students only.

## Quick start

Requires Python 3.10+ and Chrome, Edge, Firefox or Safari.
New to this? Follow [`docs/HOW_TO_RUN.md`](docs/HOW_TO_RUN.md) (VS Code, step by step).

```bash
git clone https://github.com/ishanveeramalli82/Neurofocus-AI.git
cd Neurofocus-AI
pip install -r requirements.txt
python run.py
# open http://127.0.0.1:5000
```

In VS Code you can also press **F5** and choose **Run NeuroFocus AI (web app)**.

The camera only works on `localhost` or over HTTPS (a browser rule).
Everything, including the MediaPipe face model, is served locally, so the
app works offline once installed.

Environment variables (optional):

| Variable | Purpose |
|---|---|
| `NEUROFOCUS_SECRET_KEY` | session-signing key (otherwise generated into `instance/secret_key`) |
| `NEUROFOCUS_SECURE_COOKIES=1` | set when serving over HTTPS |
| `PORT` | port (default 5000) |

## Tests

```bash
python -m pytest
```

The tests cover the engine rules, calibration and scoring; the API (auth,
CSRF, rate limiting, privacy between users, sessions, schedule, auto-planning,
export/delete); and the research pipeline (ground-truth separation,
reproducibility, metric formulas, statistics).

## How it works

```
Browser                                        Server (Flask + SQLite)
-------                                        -----------------------
webcam -> MediaPipe Face Landmarker            neurofocus_engine
       -> 6 numbers/frame (10 fps) --JSON-->     calibration -> frame rules -> temporal filter
                                                 -> attention state, Focus Score, episodes
live UI <------------------------------------   stored per second; history & analytics
```

Full algorithm: [`research/docs/03_algorithm.md`](research/docs/03_algorithm.md).

## Project structure

```
Neurofocus-AI/
├── run.py                 starts the web app
├── requirements.txt       Python packages
├── neurofocus_engine/     attention engine shared by the app and the experiment
│   ├── params.py            every threshold and constant, in one place
│   ├── features.py          the 6-number feature frame (the engine's only input)
│   ├── calibration.py       personal calibration
│   ├── classifier.py        frame rules + temporal filter
│   └── scoring.py           Focus Score and distraction episodes
├── backend/               Flask API (see docs/ARCHITECTURE.md)
├── frontend/              HTML pages, css/, js/, vendor/ (MediaPipe + face model)
├── research/              the science-fair experiment (see research/README.md)
│   ├── config/              experiment definitions
│   ├── simulator/           virtual students + ground truth
│   ├── pipeline/            blind engine run + experiment runner
│   ├── analysis/            metrics, statistics, figures
│   ├── docs/                question, procedure, algorithm, limitations, references
│   ├── data/                raw + processed data (created by runs, not in git)
│   └── results/             metrics, statistics reports, figures (commit these)
├── tests/                 automated tests (pytest)
├── docs/                  HOW_TO_RUN.md, ARCHITECTURE.md
├── tools/                 build_all_in_one.py (makes a single-file copy of the project)
└── .vscode/               F5 run configurations
```

| Read this | For |
|---|---|
| [`docs/HOW_TO_RUN.md`](docs/HOW_TO_RUN.md) | installing and running, troubleshooting |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | how the code fits together, API, database, security |
| [`research/README.md`](research/README.md) | the experiment and all research documents |
| [`docs/PERSONALIZATION.md`](docs/PERSONALIZATION.md) | survey, personal plan and focus supports: how they work and why |
| [`docs/research/`](docs/research/) | literature review behind the ADHD-friendly design (verify citations before use) |

## Security & privacy

* Video never leaves the browser; only numeric features are sent.
* Passwords hashed with scrypt; HttpOnly SameSite cookies; CSRF tokens on all
  state-changing requests; login rate limiting; strict Content-Security-Policy
  (no third-party scripts); per-user data isolation; data export and account
  deletion.
* The development server (`python run.py`) is for local use. For anything
  public, run behind HTTPS with a production WSGI server.
