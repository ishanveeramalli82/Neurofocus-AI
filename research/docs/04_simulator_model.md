# 4. The virtual-student simulator

Code: `research/simulator/`. The simulator generates (1) a ground-truth
behaviour timeline for each virtual student and (2) the noisy feature stream
a webcam face-landmark pipeline would report. **Every number below is an
assumption chosen by the researcher, not a measurement of real students.**
These assumptions define the scope of the experiment's conclusions.

## Separation from the engine

* `research/simulator/` never imports `neurofocus_engine`, and the engine never
  imports anything from `research/`. Automated tests enforce both
  (`tests/test_research_pipeline.py`).
* The engine-facing feature files contain only `t, phase, face_present, yaw,
  pitch, ear, gaze_h, gaze_v`. Labels are written to a separate
  `ground_truth/` folder that the prediction stage never opens (also tested).
* Where the engine has to assume a constant (e.g. 30 degrees per unit of iris
  offset), the simulator draws its own per-student value (25-35 degrees)
  instead of reusing the engine's value, so the engine cannot "know" the
  simulator's internals.

Remaining risk of circularity: the same person designed the simulator and the
engine, so the simulator may unconsciously reflect the engine's design
assumptions (for example, that looking away means turning the head). State
this in your limitations.

## Ground truth (`ground_truth.py`)

| Behaviour | Duration | Ground truth | Expected engine state |
|---|---|---|---|
| on_task (reading the screen) | lognormal, median 0.8 x student mean bout, 5-600 s | on-task | FOCUSED |
| glance (brief look aside) | uniform 0.3-1.5 s | on-task | FOCUSED |
| notes (looking down to write) | uniform 3-15 s | on-task | FOCUSED |
| away (sustained look away) | lognormal median 6 s, 3-40 s | distracted | LOOKING_AWAY |
| phone | lognormal median 15 s, 5-90 s | distracted | LOOKING_DOWN |
| drowsy (eyes closed) | lognormal median 4 s, 2-15 s | distracted | EYES_CLOSED |
| left_desk | lognormal median 30 s, 10-120 s | distracted | ABSENT |

Operational definition used in this study: a frame is **distracted** when the
virtual student is executing an off-task behaviour. Brief glances and note
taking count as on-task because they are normal parts of studying. Note
taking is intentionally included as a **known hard case**: it looks like
"looking down" to a camera.

## Student profiles (one per virtual student, `sample_profile`)

| Parameter | Distribution | Meaning |
|---|---|---|
| yaw_offset | U(-25, 25) degrees | camera placed to the side |
| pitch_offset | U(-20, 10) degrees | camera below/above eye level |
| screen_half_w, screen_half_h | U(12, 22), U(7, 13) degrees | angular size of the screen |
| head_fraction | U(0.4, 0.8) | share of a gaze shift made by the head (rest by the eyes) |
| eye_deg_per_unit | U(25, 35) degrees | eye rotation per unit of normalized iris offset |
| sway_sd | U(1, 3) degrees | natural head sway (Ornstein-Uhlenbeck, time constant 2 s) |
| ear_open | Normal(0.29, 0.025), clipped 0.22-0.36 | open-eye EAR |
| blink_per_min | U(10, 25) | blink rate; blink duration U(0.1, 0.4) s |
| mean_on_task_bout_s | U(30, 120) s | how long the student stays on task |
| next-behaviour probabilities | Dirichlet around glance .35, notes .15, away .20, phone .15, drowsy .08, left .07 | what interrupts on-task bouts |
| phone_high_prob | 0.2 | chance a phone is held near screen height (hard case) |

## Movement model

* Behaviour targets: glance yaw +/-U(15, 35) degrees; away yaw +/-U(30, 70);
  notes pitch -U(25, 45); phone pitch -U(20, 45) (or -U(5, 15) when held up);
  drowsy pitch -U(0, 10) with eyelids at 15-40% of open EAR.
* While on task, gaze moves between random fixations within 70% of the
  screen every 0.3-1.5 s.
* The head moves its share of the target angle with a first-order lag
  (time constant 0.25 s); the eyes cover the rest instantly (clipped to +/-1).
* Looking down lowers the eyelids: EAR x (1 - 0.25 x downward fraction).

## Sensor (observation) model, per noise level

| Parameter | low | medium | high |
|---|---|---|---|
| pose noise SD (degrees, yaw and pitch) | 1.0 | 2.5 | 4.0 |
| EAR noise SD | 0.010 | 0.020 | 0.035 |
| gaze noise SD | 0.04 | 0.08 | 0.15 |
| dropout start probability per frame | 0.002 | 0.006 | 0.015 |
| mean dropout length (s) | 0.3 | 0.5 | 0.8 |
| missed detection when \|yaw\| > 60 degrees | 50% | 50% | 50% |

These levels are a plausible range, not a calibration against a specific
camera. A strong extension (no human participants needed) would be to measure
real landmark jitter from a recorded video of a mannequin head or a printed
face photo at known angles, and set the noise levels from that.

## Validity threats to report

* External validity: real students' behaviour, posture and camera noise may
  differ from these distributions.
* Construct validity: "looking at the screen" is used as a proxy for
  attention; a student can look at the screen while mind-wandering.
* Circularity: designer of the simulator also designed the engine (see above).
* Perfect calibration compliance: virtual students always follow calibration
  instructions; real users may not.
