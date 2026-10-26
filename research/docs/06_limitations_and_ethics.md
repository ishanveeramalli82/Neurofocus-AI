# 6. Limitations, claims and ethics

## What the evidence supports, and what it does not

| Evidence | What it shows | What it does NOT show |
|---|---|---|
| Automated tests pass (`pytest`) | The code behaves as designed: rules, calibration, scoring, security checks, data separation, metric formulas. | That the design is accurate for real people. |
| Virtual-student experiment | How accurately the engine recovers known attention states from simulated feature streams, how calibration and noise affect that, under the stated simulator assumptions. | Accuracy with real students, real cameras, real lighting; that the app improves studying or grades. |
| The app runs in a browser at ~10 frames/s | Real-time feasibility on that computer. | Accuracy (no ground truth is collected). |

Claims you **can** make (if the data support them):
* "On N = 30 simulated students, personal calibration changed F1 by X
  (95% CI ...) at medium sensor noise."
* "The engine's main error source in simulation was ... (from the behaviour
  confusion matrix)."

Claims you **must not** make:
* That NeuroFocus measures attention, focus or learning in real students.
* That NeuroFocus detects, screens for, or diagnoses ADHD or any other
  condition. (The name "NeuroFocus" refers to focus, not neurology.)
* That simulated results prove the product is effective.

## Technical limitations

1. Head/eye direction is a proxy. Looking at the screen is not the same as
   paying attention (mind-wandering is invisible), and looking away is not
   always distraction (thinking, reading paper notes).
2. Note taking and phones held near the screen are known hard cases.
3. The iris-offset scale and the head-pose pitch sign have not been validated
   against measured ground truth on real hardware. Calibration checks the
   pitch direction but not the scale.
4. Face-landmark accuracy can depend on lighting, camera quality, glasses,
   head coverings and skin tone. None of these were tested. MediaPipe's own
   model card describes its evaluation; cite it rather than assuming fairness.
5. Background browser tabs: the app uses a worker timer to keep sampling, but
   browsers may still slow pages that are not visible.
6. Single-process server design: the live engine state is cached in memory
   (and reconstructed from the database after a restart). This is fine for a
   personal or demo deployment, not for many simultaneous users.

## Ethics, privacy and safety

* Camera frames are processed in the browser; only six numbers per frame are
  sent to the server. No images are stored.
* Users can export all their data as JSON and permanently delete their
  account.
* Passwords are hashed with scrypt (Werkzeug). Sessions use HttpOnly,
  SameSite=Lax cookies. All state-changing requests require a CSRF token.
  Login is rate-limited. A strict Content-Security-Policy allows scripts only
  from the app itself (MediaPipe is bundled locally).
* Monitoring tools can be misused (e.g. a parent or school monitoring a
  student without consent). NeuroFocus is designed for self-use: each account
  sees only its own data, and there is no supervisor view. Keep it that way
  unless you add explicit consent features.

## Human participants (ISEF)

The study was designed around a school restriction on human-participant
research: it uses only simulated "virtual students". Under ISEF rules,
research that collects data from people (including the student researcher)
generally needs prior review and approval (IRB/SRC) and informed consent.
Check the current *International Rules for Precollege Science Research*
and your fair's SRC before collecting any camera data from people for
research purposes. Possible future work that does **not** involve people:
measuring landmark noise from a mannequin head or printed face photo at known
angles to ground the simulator's noise model.
