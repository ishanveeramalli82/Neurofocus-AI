# Architecture

## Components

```
Browser (frontend/)                         Server (backend/, Flask + SQLite)
-------------------                         ----------------------------------
webcam -> MediaPipe Face Landmarker         /api/sessions/<id>/frames
       -> js/vision.js: 6 features/frame      -> neurofocus_engine (calibration,
          (10 frames/s) ---- JSON ---------->     frame rules, temporal filter,
                                                  Focus Score, episodes)
live UI  <---- state + scores --------------   -> SQLite: 1 state/second, episodes
```

* **`neurofocus_engine/`**: the attention algorithm, pure Python with no web
  code. Used by the backend for live sessions and by `research/` for the
  experiment, so the tested algorithm is the deployed algorithm. Documented
  in [`research/docs/03_algorithm.md`](../research/docs/03_algorithm.md).
* **`backend/`**: Flask application factory (`app.py`), one blueprint per
  area, SQLite schema in `schema.sql`.
* **`frontend/`**: plain HTML/CSS/JavaScript modules, no build step.
  `vendor/` holds MediaPipe Tasks Vision 0.10.14 and the face model.
* **`research/`**: the experiment (simulator, blind prediction stage,
  evaluation, statistics, figures, docs). See [`research/README.md`](../research/README.md).

## Backend modules

| Module | Responsibility |
|---|---|
| `app.py` | app factory, page routes, error handlers, secret key |
| `db.py`, `schema.sql` | SQLite connection per request, schema creation |
| `security.py` | CSRF check, login rate limiter, `login_required`, security headers / CSP |
| `validation.py` | input validation helpers |
| `auth.py` | register, login, logout, profile, password, export, delete account |
| `sessions_api.py` | study sessions: calibration, frame streaming through the engine, history |
| `schedule_api.py` | events, recurrence, conflicts, tasks, auto-planning, overview |
| `analytics_api.py` | daily / hourly / subject summaries, streaks, distraction breakdown |
| `research_api.py` | read-only engine parameters and experiment results |

## API

All `/api` responses are JSON. Every POST/PUT/PATCH/DELETE must send the
`X-CSRF-Token` header (token from `GET /api/auth/csrf`, also returned on login).

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | liveness check |
| GET | `/api/auth/status` | `{signed_in}` (public) |
| GET | `/api/auth/csrf` | CSRF token |
| POST | `/api/auth/register` | create account (`email`, `password`, `display_name`) |
| POST | `/api/auth/login` / `/api/auth/logout` | sign in / out |
| GET | `/api/auth/me` | current user and settings |
| PUT | `/api/account/profile` | name and study settings |
| PUT | `/api/account/password` | change password |
| GET | `/api/account/export` | download all data as JSON |
| DELETE | `/api/account` | delete account and all data (needs password) |
| POST | `/api/sessions` | start a session (optional `schedule_event_id`) |
| POST | `/api/sessions/<id>/calibration` | `{phases: {center, corners, down}}` or `{skip: true}` |
| POST | `/api/sessions/<id>/frames` | up to 600 feature frames; returns state and scores |
| POST | `/api/sessions/<id>/end` | finish; optional `notes`, `complete_event` |
| GET | `/api/sessions`, `/api/sessions/<id>` | history list / detail with timeline |
| PATCH, DELETE | `/api/sessions/<id>` | edit title/subject/notes, delete |
| GET, POST | `/api/schedule/events` | list by `start`/`end`, create (`repeat_weekly`) |
| PUT, DELETE | `/api/schedule/events/<id>` | edit, delete (`?scope=series`) |
| GET, POST | `/api/schedule/tasks` | list, create |
| PUT, DELETE | `/api/schedule/tasks/<id>` | edit, delete |
| POST | `/api/schedule/tasks/<id>/plan` | auto-plan study blocks before the due date |
| GET | `/api/schedule/overview?date=` | today's agenda, due soon, week totals |
| GET | `/api/analytics/summary?days=&tz_offset_min=` | analytics |
| GET | `/api/engine/params` | current engine parameters (public) |
| GET | `/api/research/runs` | finished experiment runs (public) |

## Data model (SQLite)

| Table | Contents |
|---|---|
| `users` | email, scrypt password hash, display name, settings JSON |
| `study_sessions` | title, subject, linked schedule event, calibration JSON, engine version and parameters, focused/total seconds, Focus Score |
| `session_samples` | one engine state and live score per second |
| `session_episodes` | distraction episodes (state, start, end) |
| `schedule_events` | title, kind, local start/end, completed, recurrence group |
| `tasks` | title, subject, due, priority, estimated minutes, done |

No images or video are stored anywhere.

## Security

* Passwords hashed with scrypt; constant-time login path for unknown emails.
* Signed, HttpOnly, SameSite=Lax session cookies (Secure when
  `NEUROFOCUS_SECURE_COOKIES=1`).
* CSRF token required on all state-changing API calls.
* Login rate limit: 5 failures per IP+email per 15 minutes.
* Every query is parameterized and filtered by the signed-in user.
* Content-Security-Policy allows scripts only from the app itself; no inline
  scripts or styles; framing forbidden.
