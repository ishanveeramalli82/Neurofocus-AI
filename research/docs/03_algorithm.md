# 3. The NeuroFocus attention engine (v1.0.0)

Code: `neurofocus_engine/` (shared by the web app and the experiment, so the
algorithm that is tested is exactly the algorithm users run). Parameters:
`neurofocus_engine/params.py`. These parameter values were chosen as design
decisions **before** any experiment was run and were not tuned on experiment
results.

## Pipeline

```
webcam frame (browser)
  -> MediaPipe Face Landmarker 0.10.14 (478 landmarks + 4x4 face transform)
  -> 6 features: face_present, yaw, pitch, ear, gaze_h, gaze_v       [frontend/js/vision.js]
  -> calibration-relative rules -> raw state per frame               [classifier.raw_state]
  -> temporal filter -> reported state                               [classifier.TemporalFilter]
  -> Focus Score and distraction episodes                            [scoring.py]
```

Frames are sampled at 10 frames per second. Video stays in the browser; only
the six numbers are sent to the server.

## Features

| Feature | Definition |
|---|---|
| `face_present` | Face Landmarker returned a face (with a transform matrix) for this frame. |
| `yaw`, `pitch` | Direction of the face's forward axis f = R * (0, 0, 1), where R is the rotation part of MediaPipe's face transform: yaw = atan2(f_x, f_z), pitch = atan2(f_y, sqrt(f_x^2 + f_z^2)), in degrees. The matrix storage order (row/column-major) is detected from where the translation sits. The sign of pitch is verified during calibration. |
| `ear` | Eye aspect ratio (Soukupova & Cech, 2016), averaged over both eyes: EAR = (\|p2-p6\| + \|p3-p5\|) / (2 \|p1-p4\|) using landmarks 33,160,158,133,153,144 (right eye) and 362,385,387,263,373,380 (left eye), in pixel units. |
| `gaze_h` | Iris centre (landmarks 468, 473) projected onto the eye-corner axis, as a fraction u from 0 to 1; gaze_h = clamp(4 (mean u - 0.5), -1, 1). |
| `gaze_v` | Vertical iris offset from the eyelid midpoint, divided by eye width, x4, clamped. Recorded but not used by v1.0.0 rules. |

## Calibration (`calibration.py`)

Protocol: centre 10 s, four corners 3 s each, desk 4 s (identical in the app
and in the simulator).

1. Quality gate: at least 85% of centre frames (and at least 10 frames) must
   contain a face, otherwise calibration fails.
2. Neutral pose: `yaw0`, `pitch0`, `ear0`, `gaze_h0` = medians over centre
   frames with a face.
3. Stability: if the median absolute deviation (MAD) of yaw or pitch in the
   centre phase exceeds 4 degrees, calibration is flagged "needs another try".
4. Pitch direction: if the desk phase's median pitch is **above** `pitch0`,
   the pitch sign is flipped (guards against a sign convention error in the
   camera pipeline).
5. Away threshold = clamp(max over corner frames of |(yaw - yaw0) +
   30 x (gaze_h - gaze_h0)| + 8 degrees, 15, 45).
6. Down threshold = clamp(|lowest corner pitch deviation| + 6 degrees, 10, 35).
   If the desk look was not clearly beyond this, the threshold becomes
   0.75 x the desk deviation (clamped).
7. Eyes-closed threshold = 0.65 x `ear0`.

Population defaults (used when calibration is skipped and in the
`uncalibrated` condition): yaw0 = 0, pitch0 = 0, ear0 = 0.28, gaze_h0 = 0,
away threshold 25 degrees, down threshold 20 degrees, eyes-closed EAR 0.182.

## Frame rules (`classifier.raw_state`)

Evaluated in order; the first match wins.

1. no face -> `ABSENT`
2. ear < eyes-closed threshold -> `EYES_CLOSED`
3. pitch_sign x (pitch - pitch0) < -down threshold -> `LOOKING_DOWN`
4. |(yaw - yaw0) + 30 x (gaze_h - gaze_h0)| > away threshold -> `LOOKING_AWAY`
5. otherwise -> `FOCUSED`

## Temporal filter (`classifier.TemporalFilter`)

A new non-focused raw state is reported only after it has persisted for its
onset time: 2.0 s for `LOOKING_AWAY`, `LOOKING_DOWN` and `ABSENT`, 1.0 s for
`EYES_CLOSED` (longer than a typical blink). The filter returns to `FOCUSED`
after 0.5 s of focused frames. This suppresses blinks, brief glances and
single-frame detection misses, at the cost of a built-in detection delay. The
exploratory onset-sweep experiment measures this trade-off.

## Focus Score (`scoring.py`)

```
Focus Score = 100 x (time the reported state is FOCUSED) / (session time)
```

Each frame's state is weighted by the time until the next frame, capped at
1 s so pauses are not counted. Time with no detected face counts as not
focused. The live score in the app is the same formula over the last 60 s.

The definition is deliberately simple so that it can be compared directly
with the simulator's ground-truth on-task percentage.

## What the engine does not do

* It does not use machine learning trained on people; it is a transparent,
  rule-based classifier on top of a pre-trained face-landmark model.
* It does not infer thinking, comprehension, emotion, or any medical condition.
