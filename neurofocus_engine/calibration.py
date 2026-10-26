"""Personal calibration.

Protocol (identical in the web app and in the simulator):
  phase "center"  ~10 s  look at the middle of the screen as if studying
  phase "corners" ~12 s  look at each screen corner in turn (3 s each)
  phase "down"     ~4 s  look down at the desk/keyboard

From these frames we estimate the person's neutral head pose (camera placement
differs between people), the angular size of their screen, and their open-eye
EAR. Thresholds are then expressed relative to this personal baseline.
"""

from dataclasses import dataclass, asdict
import math
import statistics

from .params import DEFAULT_PARAMS


def _median(xs):
    return statistics.median(xs) if xs else math.nan


def _mad(xs):
    if len(xs) < 2:
        return math.nan
    m = statistics.median(xs)
    return statistics.median(abs(x - m) for x in xs)


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


@dataclass
class Calibration:
    calibrated: bool
    yaw0: float
    pitch0: float
    ear0: float
    gaze_h0: float
    yaw_threshold: float
    pitch_down_threshold: float
    ear_closed_threshold: float
    pitch_sign: float = 1.0      # flipped if the "down" phase shows pitch increasing
    quality: str = "default"
    warnings: tuple = ()

    def to_dict(self):
        d = asdict(self)
        d["warnings"] = list(self.warnings)
        return d

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        d["warnings"] = tuple(d.get("warnings", ()))
        return cls(**d)


def default_calibration(params=DEFAULT_PARAMS):
    """Population defaults, used when a user skips calibration (and as the
    'uncalibrated' experimental condition)."""
    return Calibration(
        calibrated=False,
        yaw0=params.default_yaw_deg,
        pitch0=params.default_pitch_deg,
        ear0=params.default_ear,
        gaze_h0=params.default_gaze_h,
        yaw_threshold=params.default_yaw_threshold_deg,
        pitch_down_threshold=params.default_pitch_down_threshold_deg,
        ear_closed_threshold=params.default_ear * params.ear_closed_ratio,
    )


def calibrate(frames_by_phase, params=DEFAULT_PARAMS):
    """frames_by_phase: dict phase -> list[FeatureFrame].

    Returns (Calibration, ok: bool). When ok is False the caller should ask the
    user to repeat calibration; the returned object still holds best-effort
    values plus warnings explaining the problem.
    """
    warnings = []
    center = frames_by_phase.get("center", [])
    seen = [f for f in center if f.face_present]
    if not center:
        return default_calibration(params), False
    face_fraction = len(seen) / len(center)
    if face_fraction < params.min_calibration_face_fraction or len(seen) < 10:
        warnings.append(f"Face detected in only {face_fraction:.0%} of centre frames.")
        cal = default_calibration(params)
        cal.warnings = tuple(warnings)
        cal.quality = "failed"
        return cal, False

    yaws = [f.yaw for f in seen]
    pitches = [f.pitch for f in seen]
    ears = [f.ear for f in seen if not math.isnan(f.ear)]
    gazes = [f.gaze_h for f in seen if not math.isnan(f.gaze_h)]
    yaw0, pitch0 = _median(yaws), _median(pitches)
    ear0 = _median(ears) if ears else params.default_ear
    gaze0 = _median(gazes) if gazes else 0.0
    ok = True
    if max(_mad(yaws), _mad(pitches)) > params.max_calibration_pose_mad_deg:
        warnings.append("Head was moving a lot during the centre phase.")
        ok = False

    # Direction of "down": verify with the down phase (guards against a sign
    # convention mismatch between camera pipelines).
    pitch_sign = 1.0
    down = [f for f in frames_by_phase.get("down", []) if f.face_present]
    down_dev = None
    if len(down) >= 5:
        down_dev = _median([f.pitch for f in down]) - pitch0
        if down_dev > 0:
            pitch_sign = -1.0
            down_dev = -down_dev
        if abs(down_dev) < 5:
            warnings.append("Looking down barely changed head pitch; down-detection may be weak.")
    else:
        warnings.append("Down phase missing; assuming standard pitch direction.")

    # Screen envelope from the corner looks.
    corners = [f for f in frames_by_phase.get("corners", []) if f.face_present]
    if len(corners) >= 10:
        yaw_span = max(abs(f.yaw - yaw0 + params.gaze_to_deg * ((f.gaze_h if not math.isnan(f.gaze_h) else gaze0) - gaze0))
                       for f in corners)
        lowest = min(pitch_sign * (f.pitch - pitch0) for f in corners)
        yaw_thr = _clamp(yaw_span + params.yaw_margin_deg, *params.yaw_threshold_bounds)
        pitch_thr = _clamp(abs(min(lowest, 0.0)) + params.pitch_margin_deg, *params.pitch_threshold_bounds)
    else:
        warnings.append("Corner phase missing; using default screen size.")
        yaw_thr = params.default_yaw_threshold_deg
        pitch_thr = params.default_pitch_down_threshold_deg

    # If looking at the desk was not clearly beyond the threshold, move the
    # threshold to halfway between the lowest corner and the desk.
    if down_dev is not None and abs(down_dev) <= pitch_thr:
        pitch_thr = _clamp(abs(down_dev) * 0.75, *params.pitch_threshold_bounds)

    cal = Calibration(
        calibrated=True, yaw0=yaw0, pitch0=pitch0, ear0=ear0, gaze_h0=gaze0,
        yaw_threshold=yaw_thr, pitch_down_threshold=pitch_thr,
        ear_closed_threshold=ear0 * params.ear_closed_ratio,
        pitch_sign=pitch_sign, quality="good" if ok and not warnings else "fair",
        warnings=tuple(warnings),
    )
    return cal, ok
