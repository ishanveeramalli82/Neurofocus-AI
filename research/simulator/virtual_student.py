"""Virtual-student simulator.

Generates (1) the latent behavior of a simulated student over time, which is
the ground truth, and (2) the noisy feature stream a webcam + face-landmark
pipeline would report, which is the ONLY thing the engine is given.

The model is a set of stated assumptions, not measurements of real students.
Every distribution below is listed in research/docs/04_simulator_model.md and
is a limitation of the study: results show how the engine behaves on THIS
model of behavior and sensor noise, not on real people.

Independence from the engine: this module does not import neurofocus_engine.
Where the engine needs a constant (e.g. how many degrees an iris offset
corresponds to), the simulator draws its own per-student value instead of
reusing the engine's assumption.
"""

from dataclasses import dataclass, asdict
import math

import numpy as np

from .ground_truth import (ON_TASK, GLANCE, NOTES, AWAY, PHONE, DROWSY,
                           LEFT_DESK, ON_TASK_BEHAVIORS, EXPECTED_STATE)

DISTRACTIONS = (GLANCE, NOTES, AWAY, PHONE, DROWSY, LEFT_DESK)
BASE_NEXT_PROBS = np.array([0.35, 0.15, 0.20, 0.15, 0.08, 0.07])


@dataclass
class StudentProfile:
    student_id: int
    yaw_offset: float          # camera placement (deg)
    pitch_offset: float
    screen_half_w: float       # angular half-width of the screen (deg)
    screen_half_h: float
    head_fraction: float       # share of a gaze shift done by the head (rest by eyes)
    eye_deg_per_unit: float    # deg of eye rotation per unit normalized iris offset
    sway_sd: float             # natural head sway (deg)
    ear_open: float
    blink_per_min: float
    mean_on_task_bout_s: float
    next_probs: list           # probabilities over DISTRACTIONS after an on-task bout
    phone_high_prob: float     # chance a phone is held up near screen height

    def to_dict(self):
        return asdict(self)


def sample_profile(student_id, rng):
    alpha = BASE_NEXT_PROBS * 40
    return StudentProfile(
        student_id=student_id,
        yaw_offset=float(rng.uniform(-25, 25)),
        pitch_offset=float(rng.uniform(-20, 10)),
        screen_half_w=float(rng.uniform(12, 22)),
        screen_half_h=float(rng.uniform(7, 13)),
        head_fraction=float(rng.uniform(0.4, 0.8)),
        eye_deg_per_unit=float(rng.uniform(25, 35)),
        sway_sd=float(rng.uniform(1.0, 3.0)),
        ear_open=float(np.clip(rng.normal(0.29, 0.025), 0.22, 0.36)),
        blink_per_min=float(rng.uniform(10, 25)),
        mean_on_task_bout_s=float(rng.uniform(30, 120)),
        next_probs=[float(p) for p in rng.dirichlet(alpha)],
        phone_high_prob=0.2,
    )


def _lognormal_clipped(rng, median, lo, hi, sigma=0.6):
    return float(np.clip(median * math.exp(rng.normal(0, sigma)), lo, hi))


def _behavior_duration(rng, b, p):
    if b == ON_TASK:
        return _lognormal_clipped(rng, p.mean_on_task_bout_s * 0.8, 5, 600)
    if b == GLANCE:
        return float(rng.uniform(0.3, 1.5))
    if b == NOTES:
        return float(rng.uniform(3, 15))
    if b == AWAY:
        return _lognormal_clipped(rng, 6, 3, 40)
    if b == PHONE:
        return _lognormal_clipped(rng, 15, 5, 90)
    if b == DROWSY:
        return _lognormal_clipped(rng, 4, 2, 15)
    if b == LEFT_DESK:
        return _lognormal_clipped(rng, 30, 10, 120)
    raise ValueError(b)


def _behavior_target(rng, b, p):
    """Where the student is looking, relative to the screen center:
    (yaw deg, pitch deg, eyes_closed, face_visible)."""
    side = 1 if rng.random() < 0.5 else -1
    if b == GLANCE:
        return side * rng.uniform(15, 35), rng.uniform(-5, 5), False, True
    if b == AWAY:
        return side * rng.uniform(30, 70), rng.uniform(-10, 10), False, True
    if b == NOTES:
        return rng.uniform(-10, 10), -rng.uniform(25, 45), False, True
    if b == PHONE:
        if rng.random() < p.phone_high_prob:  # held up near the screen: hard case
            return rng.uniform(-15, 15), -rng.uniform(5, 15), False, True
        return rng.uniform(-15, 15), -rng.uniform(20, 45), False, True
    if b == DROWSY:
        return rng.uniform(-5, 5), -rng.uniform(0, 10), True, True
    if b == LEFT_DESK:
        return 0.0, 0.0, False, False
    raise ValueError(b)


class _Body:
    """Head/eye/eyelid dynamics shared by calibration and session simulation."""

    def __init__(self, p, rng, dt):
        self.p, self.rng, self.dt = p, rng, dt
        self.head_yaw = self.head_pitch = 0.0
        self.sway_yaw = self.sway_pitch = 0.0
        self.blink_left = 0.0
        self.fix_left = 0.0
        self.fix = (0.0, 0.0)

    def step(self, target_yaw, target_pitch, eyes_closed, visible, reading):
        p, rng, dt = self.p, self.rng, self.dt
        if reading:  # small fixations moving around the screen
            self.fix_left -= dt
            if self.fix_left <= 0:
                self.fix = (rng.uniform(-0.7, 0.7) * p.screen_half_w,
                            rng.uniform(-0.7, 0.7) * p.screen_half_h)
                self.fix_left = rng.uniform(0.3, 1.5)
            target_yaw, target_pitch = target_yaw + self.fix[0], target_pitch + self.fix[1]
        # Ornstein-Uhlenbeck head sway, tau = 2 s
        k = dt / 2.0
        s = p.sway_sd * math.sqrt(2 * k)
        self.sway_yaw += -k * self.sway_yaw + s * rng.normal()
        self.sway_pitch += -k * self.sway_pitch + s * rng.normal()
        # head follows its share of the target with a 0.25 s lag
        a = 1 - math.exp(-dt / 0.25)
        self.head_yaw += a * (p.head_fraction * target_yaw - self.head_yaw)
        self.head_pitch += a * (p.head_fraction * target_pitch - self.head_pitch)
        eye_yaw = target_yaw - self.head_yaw
        eye_pitch = target_pitch - self.head_pitch
        # eyelids: closed when drowsy, short blinks otherwise; looking down lowers lids
        if self.blink_left <= 0 and rng.random() < p.blink_per_min / 60 * dt:
            self.blink_left = rng.uniform(0.1, 0.4)
        blinking = self.blink_left > 0
        self.blink_left -= dt
        down = min(max(-target_pitch / 45.0, 0.0), 1.0)
        ear = p.ear_open * (1 - 0.25 * down)
        if eyes_closed:
            ear = p.ear_open * rng.uniform(0.15, 0.4)
        elif blinking:
            ear = p.ear_open * 0.2
        return {
            "visible": visible,
            "yaw": p.yaw_offset + self.head_yaw + self.sway_yaw,
            "pitch": p.pitch_offset + self.head_pitch + self.sway_pitch,
            "ear": ear,
            "gaze_h": float(np.clip(eye_yaw / p.eye_deg_per_unit, -1, 1)),
            "gaze_v": float(np.clip(eye_pitch / p.eye_deg_per_unit, -1, 1)),
        }


def simulate_calibration(p, rng, hz, center_s=10.0, corner_s=3.0, down_s=4.0):
    """Student follows the calibration instructions (an assumption: real users
    may not). Returns list of (phase, latent dict)."""
    dt = 1.0 / hz
    body = _Body(p, rng, dt)
    out = []
    for _ in range(int(center_s * hz)):
        st = body.step(rng.normal(0, 0.1 * p.screen_half_w), rng.normal(0, 0.1 * p.screen_half_h),
                       False, True, False)
        out.append(("center", st))
    for cy, cp in ((-1, 1), (1, 1), (1, -1), (-1, -1)):
        for _ in range(int(corner_s * hz)):
            st = body.step(cy * p.screen_half_w, cp * p.screen_half_h, False, True, False)
            out.append(("corners", st))
    desk = -rng.uniform(30, 45)
    for _ in range(int(down_s * hz)):
        out.append(("down", body.step(0.0, desk, False, True, False)))
    return out


def simulate_session(p, rng, hz, duration_s):
    """Returns (latent list, ground-truth list). Ground truth rows:
    dict(t, behavior, gt_state, on_task, episode_id)."""
    dt = 1.0 / hz
    n = int(round(duration_s * hz))
    body = _Body(p, rng, dt)
    latent, truth = [], []
    behavior, left, episode = ON_TASK, _behavior_duration(rng, ON_TASK, p), 0
    target = (0.0, 0.0, False, True)
    for i in range(n):
        if left <= 0:
            if behavior == ON_TASK:
                behavior = DISTRACTIONS[rng.choice(len(DISTRACTIONS), p=p.next_probs)]
                target = _behavior_target(rng, behavior, p)
            else:
                behavior, target = ON_TASK, (0.0, 0.0, False, True)
            left = _behavior_duration(rng, behavior, p)
            episode += 1
        left -= dt
        reading = behavior == ON_TASK
        st = body.step(*target, reading=reading)
        latent.append(st)
        truth.append({
            "t": round(i * dt, 3), "behavior": behavior,
            "gt_state": EXPECTED_STATE[behavior],
            "on_task": int(behavior in ON_TASK_BEHAVIORS), "episode_id": episode,
        })
    return latent, truth


def observe(latent, rng, hz, noise):
    """Measurement model: what a face-landmark pipeline would report.

    noise: dict with pose_sd, ear_sd, gaze_sd, dropout_rate, dropout_mean_s,
           extreme_yaw_deg, extreme_yaw_miss_prob.
    """
    dt = 1.0 / hz
    rows, miss_left = [], 0.0
    for i, st in enumerate(latent):
        t = round(i * dt, 3)
        if miss_left <= 0 and rng.random() < noise["dropout_rate"]:
            miss_left = rng.exponential(noise["dropout_mean_s"])
        missed = miss_left > 0
        miss_left -= dt
        if st["visible"] and abs(st["yaw"]) > noise["extreme_yaw_deg"] \
                and rng.random() < noise["extreme_yaw_miss_prob"]:
            missed = True
        if not st["visible"] or missed:
            rows.append({"t": t, "face_present": 0, "yaw": "", "pitch": "", "ear": "",
                         "gaze_h": "", "gaze_v": ""})
            continue
        rows.append({
            "t": t, "face_present": 1,
            "yaw": round(st["yaw"] + rng.normal(0, noise["pose_sd"]), 3),
            "pitch": round(st["pitch"] + rng.normal(0, noise["pose_sd"]), 3),
            "ear": round(max(0.0, st["ear"] + rng.normal(0, noise["ear_sd"])), 4),
            "gaze_h": round(float(np.clip(st["gaze_h"] + rng.normal(0, noise["gaze_sd"]), -1, 1)), 4),
            "gaze_v": round(float(np.clip(st["gaze_v"] + rng.normal(0, noise["gaze_sd"]), -1, 1)), 4),
        })
    return rows
