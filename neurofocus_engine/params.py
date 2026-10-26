"""All tunable constants of the NeuroFocus attention engine, in one place.

Every number here is a design choice, not an empirically validated constant.
They are fixed BEFORE an experiment run and recorded in the run manifest so
results are reproducible. Changing any value means a new experiment version.
See research/docs/03_algorithm.md for the rationale behind each value.
"""

from dataclasses import dataclass, asdict, field

# Attention states produced by the engine (and used as ground-truth vocabulary
# by the simulator, which defines them independently in its own module).
FOCUSED = "FOCUSED"
LOOKING_AWAY = "LOOKING_AWAY"
LOOKING_DOWN = "LOOKING_DOWN"
EYES_CLOSED = "EYES_CLOSED"
ABSENT = "ABSENT"
STATES = (FOCUSED, LOOKING_AWAY, LOOKING_DOWN, EYES_CLOSED, ABSENT)
DISTRACTED_STATES = (LOOKING_AWAY, LOOKING_DOWN, EYES_CLOSED, ABSENT)


@dataclass(frozen=True)
class EngineParams:
    # --- Population defaults used when NO personal calibration is available ---
    default_yaw_deg: float = 0.0
    default_pitch_deg: float = 0.0
    default_ear: float = 0.28
    default_gaze_h: float = 0.0
    default_yaw_threshold_deg: float = 25.0
    default_pitch_down_threshold_deg: float = 20.0

    # --- Calibration-derived threshold rules ---
    yaw_margin_deg: float = 8.0          # added beyond the widest screen-corner look
    pitch_margin_deg: float = 6.0        # added beyond the lowest screen-corner look
    yaw_threshold_bounds: tuple = (15.0, 45.0)
    pitch_threshold_bounds: tuple = (10.0, 35.0)
    ear_closed_ratio: float = 0.65       # eyes "closed" when EAR < ratio * personal open-eye EAR
    min_calibration_face_fraction: float = 0.85
    max_calibration_pose_mad_deg: float = 4.0

    # --- Combining head and eye direction ---
    gaze_to_deg: float = 30.0            # normalized iris offset (-1..1) -> approx. degrees

    # --- Temporal filter (seconds a raw state must persist before it is reported) ---
    onset_s: dict = field(default_factory=lambda: {
        LOOKING_AWAY: 2.0,
        LOOKING_DOWN: 2.0,
        EYES_CLOSED: 1.0,   # longer than a normal blink (~0.1-0.4 s)
        ABSENT: 2.0,
    })
    recovery_s: float = 0.5              # focused this long before returning to FOCUSED

    # --- Focus Score ---
    live_window_s: float = 60.0          # trailing window for the live score

    def to_dict(self):
        d = asdict(self)
        d["yaw_threshold_bounds"] = list(self.yaw_threshold_bounds)
        d["pitch_threshold_bounds"] = list(self.pitch_threshold_bounds)
        return d


DEFAULT_PARAMS = EngineParams()
ENGINE_VERSION = "1.0.0"
