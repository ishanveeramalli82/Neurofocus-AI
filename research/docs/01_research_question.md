# 1. Engineering problem, question, hypothesis and variables

## Engineering problem

Students studying alone at a computer have no objective feedback about how
much of their study time is spent attending to the work in front of them.
Webcam-based attention estimates exist, but a single fixed rule ("the face
must point straight at the camera") breaks when the camera is not directly in
front of the student: a laptop on the side, an external monitor, or a camera
below eye level all change what "looking at the screen" looks like to the
camera.

**Engineering goal:** build a webcam-based system that classifies a
student's visible attention state in real time, on an ordinary laptop, without
sending video off the device, and **measure** how accurately it does so.

## Design criteria (what "works" means, set before testing)

| Criterion | Target | How it is measured |
|---|---|---|
| Distraction detection quality | F1 (distracted class) as high as possible; reported with 95% CI | Experiment, frame level |
| Few false alarms | reported as false alarms per on-task hour | Experiment, episode level |
| Timely detection | median detection latency reported (the filter design implies at least ~2 s) | Experiment, episode level |
| Accurate summary metric | Focus Score absolute error reported (percentage points) | Experiment |
| Real-time | >= 8 frames/s on a typical laptop browser | Measured in the app (frames/s readout) |
| Privacy | no images or video leave the device | Code inspection + network inspection |

The targets above are deliberately not given pass/fail numbers chosen after
seeing results. If you want numeric thresholds (e.g. "F1 >= 0.80"), write
them into your lab notebook **before** running the official experiment.

## Testable engineering question (the experiment)

> On simulated study sessions with known ground truth, does personal
> calibration of the NeuroFocus attention engine improve distraction-detection
> accuracy compared with population-default thresholds, and how does
> detection accuracy change as camera-sensor noise increases?

The experiment evaluates **only the attention engine** (feature frames ->
attention state -> Focus Score). Accounts, scheduling, analytics and the user
interface are product features; they are verified by software tests, not by
this experiment.

## Hypotheses (state these in your notebook before the official run)

* **H1 (primary):** At each noise level, per-student F1 for the "distracted"
  class will be higher with personal calibration than with population-default
  thresholds.
* **H0 (null for H1):** The median paired difference in F1 (calibrated minus
  uncalibrated) is zero.
* **H2 (secondary):** F1 decreases as sensor noise increases (low > medium > high).

Rationale for H1: virtual students differ in camera placement (head yaw
offset up to +/-25 degrees, pitch offset -20 to +10 degrees). A fixed threshold
around 0 degrees will mislabel students whose "looking at the screen" pose is
far from 0, while calibration re-centres the thresholds.

Note: a hypothesis can be wrong. If calibration does not help, or helps only
at some noise levels, that is a valid and reportable engineering result. Do
not change the hypothesis, the engine parameters or the analysis after seeing
the official results. If you change anything, it is a new version of the
experiment and must be reported as such.

## Variables

| Type | Variable | Levels / units |
|---|---|---|
| Independent 1 | Calibration mode | `calibrated` (personal calibration) vs `uncalibrated` (population defaults) |
| Independent 2 | Sensor-noise level | `low`, `medium`, `high` (pose jitter 1.0 / 2.5 / 4.0 degrees SD; EAR jitter; gaze jitter; detection dropout rate) |
| Dependent (primary) | F1 score, distracted class, per virtual student | 0-1 |
| Dependent (secondary) | Accuracy, precision, recall, specificity, balanced accuracy, Cohen's kappa | 0-1 |
| Dependent (secondary) | Episode detection rate, correct-type rate | 0-1 |
| Dependent (secondary) | Detection latency | seconds |
| Dependent (secondary) | False alarms per on-task hour | count/hour |
| Dependent (secondary) | Focus Score absolute error | percentage points |
| Controlled | Virtual students and their behaviour timelines (same seeds in every condition) | 30 students |
| Controlled | Session length, frame rate | 20 min, 10 frames/s |
| Controlled | Engine version and parameters | `neurofocus_engine` v1.0.0, `params.py` |
| Controlled | Ground-truth definition of "distracted" | `research/simulator/ground_truth.py` |

## Experimental design

Within-subjects (paired) factorial design: every virtual student is
evaluated in all 2 x 3 = 6 conditions, using the identical behaviour timeline.
Paired designs remove between-student variation from the comparison.

A second, **exploratory** experiment (`research/config/onset_sweep_v1.json`)
varies the temporal-filter onset time (0.5, 1, 2, 3 s) to show the trade-off
between detection speed and false alarms. It has no pre-registered hypothesis
test and must be presented as exploratory.
