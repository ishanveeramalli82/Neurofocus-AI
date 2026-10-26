# 5. Evaluation metrics

Code: `research/analysis/evaluate.py`. Positive class = **distracted**
(ground truth `on_task == 0`; engine state not `FOCUSED`).

## Frame-level (computed per virtual student)

With TP, FP, FN, TN counted over all frames of a session:

| Metric | Formula |
|---|---|
| Accuracy | (TP + TN) / (TP + FP + FN + TN) |
| Precision (distracted) | TP / (TP + FP): when the engine says distracted, how often it is right |
| Recall / sensitivity (distracted) | TP / (TP + FN): how much distracted time it catches |
| Specificity | TN / (TN + FP): how much on-task time it correctly leaves alone |
| F1 (distracted) | 2TP / (2TP + FP + FN): balance of precision and recall (primary metric) |
| Balanced accuracy | (recall + specificity) / 2 |
| Cohen's kappa | (accuracy - p_e) / (1 - p_e), p_e = chance agreement |

Why F1 is primary: students are on task most of the time, so accuracy is
inflated by the large number of easy on-task frames (if a student is on task
85% of the time, a system that always says "focused" scores 85% accuracy
while detecting nothing). F1 ignores true negatives and
focuses on the distracted class.

Frame-level scoring includes the engine's built-in onset delay (the first ~2 s
of each distraction count as misses). This is intentional: it is how the
system behaves for a user.

## Multiclass confusion matrices

* 5 x 5: expected state (from the ground-truth behaviour) x engine state.
* 7 x 5: ground-truth behaviour (including glance and notes) x engine state.
  This shows **which behaviours** cause errors (e.g. note taking -> LOOKING_DOWN).

Figures show row-normalized matrices (each row sums to 1).

## Episode-level

A ground-truth distraction episode is a run of consecutive distracted frames
with the same behaviour.

* **Detected** if the engine reports any non-FOCUSED state between the
  episode's start and 0.5 s after its end (`detection_grace_s`).
* **Detection latency** = time of the first such frame - episode start.
* **Correct type** if the most common non-FOCUSED engine state during the
  detection window matches the expected state.
* **False alarm** = a run of non-FOCUSED engine output that does not overlap
  any ground-truth distracted frame. Reported per hour of ground-truth
  on-task time, and broken down by the behaviour that was happening.

## Focus Score error

* Ground-truth focus percentage = 100 x on-task frames / all frames.
* Engine Focus Score = 100 x FOCUSED frames / all frames (equal to the app's
  score for evenly spaced frames).
* Absolute error = |engine - ground truth| in percentage points; signed error
  is also stored to show systematic over- or under-estimation.
