# Onboarding survey, personal plan and focus supports

These are **product features**. They are not part of the science-fair
experiment, and data they collect from real users must **not** be used as
research data (that would be human-participant research needing IRB/SRC
approval under ISEF rules). Evidence behind every design choice:
[`docs/research/`](research/).

## 1. "How do you study?" survey (`backend/survey.py`)

* 12 optional questions, about 2 minutes, shown after sign-up (can be skipped
  and retaken from Settings).
* Original wording, each *informed by* a published construct (MSLQ time/study
  environment and effort regulation, Pure Procrastination Scale, reduced MEQ /
  MCTQ chronotype). Copyrighted items are not copied.
* **Non-diagnostic**: no question about ADHD, diagnosis or medication (a test
  enforces this). Needs are expressed as opt-in **focus support options**
  available to everyone.

## 2. Personal study plan (`backend/planner.py`, unlocks after 3 sessions)

The student chooses **which days and times** they can study and **what they
will learn** (subject, topic, minutes needed, optional test/due date). The
planner then decides block length, breaks, order and reviews, and explains
every decision ("Why this plan?" and "Why here?" on each block).

**Method: rule-based personalization with statistical shrinkage, not a
trained ML model.** 3-4 sessions are far too few observations to train or
validate a model.

| Decision | Rule | Basis |
|---|---|---|
| Block length | `w x (your median focus streak) + (1 - w) x prior`, `w = n/(n+4)`, rounded to 5, 10-50 min; prior = survey answer or 25 min | empirical-Bayes shrinkage; 25+5 near Biwer et al. 2023 |
| Breaks | 5 min after each block, 15 min after every 3 | Biwer et al. 2023; Albulescu et al. 2022 |
| Best time of day | your time band only if >= 3 sessions there and >= 5 points above your average (shrunk); otherwise survey answer | heuristic minimum-data rule |
| Buffer | plan <= 75% of free time (70% if you often start late); finish new material 1-2 days before a test | planning fallacy (Buehler et al. 1994) |
| Spreading | <= ~60 min of new material per topic per day | distributed practice (Cepeda et al. 2006) |
| Reviews | self-test reviews about 30% of the time-to-test apart (10% for long horizons), last one on the last study day before the test | Cepeda et al. 2008; Dunlosky et al. 2013 |
| Order | earliest deadline first; alternate topics without letting undated topics push aside dated ones | interleaving (moderate evidence) |

Numbers marked heuristic (k = 4, thresholds, 75%) are design choices, not
published values. Confidence (none/low/medium/high) is shown from the number
of sessions.

**How it is evaluated (no human participants):** `tests/test_plan.py` runs
300 random plans and checks that every one obeys every rule (inside chosen
times, no clashes, before deadlines, reviews after learning, buffer kept,
every block explained), plus worked examples. This shows the planner does
what it is designed to do. It does **not** show that plans improve learning;
that would need a human-participant study with approval.

## 3. Focus support options (Settings, or chosen in the survey)

| Feature | What it does | Basis |
|---|---|---|
| Calm focus mode | hides everything except the task, a big timer and Pause/End | W3C COGA "help users focus" |
| Big visual countdown | shrinking ring for the block or plan | externalizing time (ADHD timing research) |
| Study blocks + break timer | block, then a timed break with a "ready to start again?" cue | Biwer 2023; task re-initiation support |
| Gentle nudges | quiet message after drifting; mutable per session; sound off by default | COGA "limit interruptions" |
| Self check-ins | "Were you on task just now?" every N minutes, non-blocking | self-monitoring with accuracy checks (Briesch & Briesch 2016) |
| If-then plan | "If I pick up my phone, then I will..." written before starting | implementation intentions (Gollwitzer & Sheeran 2006) |
| End-of-session reflection | how focused you felt, what pulled you away, what helped | reflecting over time |

The session report shows **your ratings next to the camera estimate**, so the
camera acts as a mirror rather than a judge. Low scores are shown in a neutral
colour, and "days studied in the last 7" replaces an all-or-nothing streak.
