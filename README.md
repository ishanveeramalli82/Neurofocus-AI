# NeuroFocus AI

A webcam-based study-focus tracker with a transparent, testable attention
engine, built as both a working product and a science-fair engineering
research project.

* **Product:** accounts, camera calibration, on-device computer vision, live
  Focus Score, session history, analytics, and a Schedule department (calendar,
  tasks, recurring classes, conflict detection, automatic study-block planning).
* **Research:** a reproducible virtual-student experiment that measures how
  accurately the attention engine detects distraction. See
  [`research/README.md`](research/README.md).

> NeuroFocus estimates where your head and eyes point. It does not measure
> learning, and it is not a medical or diagnostic tool (it does not detect or
> diagnose ADHD or any other condition). Current accuracy figures come from
> simulated students only.

## Quick start

Requires Python 3.10+ and a modern Chromium-based browser, Firefox or Safari.

```bash
pip install -r requirements.txt
python run.py
# open http://127.0.0.1:5000
```

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
neurofocus_engine/   attention engine shared by the app and the experiment
backend/             Flask API: auth, sessions, schedule, analytics, research results
frontend/            HTML/CSS/JS pages; vendor/ holds MediaPipe + the face model
research/            experiment: simulator, pipeline, analysis, docs, results
tests/               automated tests
run.py               starts the web app
```

## Security & privacy

* Video never leaves the browser; only numeric features are sent.
* Passwords hashed with scrypt; HttpOnly SameSite cookies; CSRF tokens on all
  state-changing requests; login rate limiting; strict Content-Security-Policy
  (no third-party scripts); per-user data isolation; data export and account
  deletion.
* The development server (`python run.py`) is for local use. For anything
  public, run behind HTTPS with a production WSGI server.
