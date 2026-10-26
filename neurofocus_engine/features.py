"""The feature frame: the ONLY input the engine ever receives.

In the web app these numbers are computed in the browser from MediaPipe Face
Landmarker output (frontend/js/vision.js); raw video never leaves the device.
In the experiment they are read from the simulator's features CSV files.
The engine never sees ground-truth labels.
"""

from dataclasses import dataclass
import math

FEATURE_COLUMNS = ("t", "face_present", "yaw", "pitch", "ear", "gaze_h", "gaze_v")


@dataclass
class FeatureFrame:
    t: float              # seconds since session start
    face_present: bool
    yaw: float = math.nan     # head yaw, degrees (sign arbitrary; engine uses deviation)
    pitch: float = math.nan   # head pitch, degrees, positive = up
    ear: float = math.nan     # mean eye aspect ratio of both eyes
    gaze_h: float = math.nan  # horizontal iris offset within eye, -1..1
    gaze_v: float = math.nan  # vertical iris offset within eye, -1..1

    @classmethod
    def from_dict(cls, d):
        def num(key):
            v = d.get(key)
            try:
                v = float(v)
            except (TypeError, ValueError):
                return math.nan
            return v if math.isfinite(v) else math.nan

        present = d.get("face_present")
        if isinstance(present, str):
            present = present.strip().lower() in ("1", "true", "yes")
        frame = cls(t=num("t"), face_present=bool(present), yaw=num("yaw"),
                    pitch=num("pitch"), ear=num("ear"), gaze_h=num("gaze_h"),
                    gaze_v=num("gaze_v"))
        if not math.isfinite(frame.t):
            raise ValueError("frame is missing a numeric 't'")
        # A frame claiming a face but lacking pose is treated as no detection.
        if frame.face_present and (math.isnan(frame.yaw) or math.isnan(frame.pitch)):
            frame.face_present = False
        return frame
