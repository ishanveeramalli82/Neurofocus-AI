"""Frame classification + temporal filtering.

Stage 1 (instantaneous): each frame gets a raw state from fixed rules applied
to deviations from the calibrated baseline. Rule order = priority:
  1. no face                                   -> ABSENT
  2. EAR below closed-eye threshold            -> EYES_CLOSED
  3. head pitched down beyond threshold        -> LOOKING_DOWN
  4. |head yaw + eye gaze| beyond threshold    -> LOOKING_AWAY
  5. otherwise                                 -> FOCUSED

Stage 2 (temporal): a non-focused raw state is only reported after it has
persisted for onset_s[state] seconds, and the filter returns to FOCUSED after
recovery_s seconds of focused frames. This suppresses blinks, brief glances
and single-frame detector misses, at the cost of a built-in detection delay.
"""

import math

from .params import (DEFAULT_PARAMS, FOCUSED, LOOKING_AWAY, LOOKING_DOWN,
                     EYES_CLOSED, ABSENT)


def raw_state(frame, cal, params=DEFAULT_PARAMS):
    if not frame.face_present:
        return ABSENT
    if not math.isnan(frame.ear) and frame.ear < cal.ear_closed_threshold:
        return EYES_CLOSED
    dpitch = cal.pitch_sign * (frame.pitch - cal.pitch0)
    if dpitch < -cal.pitch_down_threshold:
        return LOOKING_DOWN
    dgaze = 0.0 if math.isnan(frame.gaze_h) else frame.gaze_h - cal.gaze_h0
    horizontal = (frame.yaw - cal.yaw0) + params.gaze_to_deg * dgaze
    if abs(horizontal) > cal.yaw_threshold:
        return LOOKING_AWAY
    return FOCUSED


class TemporalFilter:
    """Streaming state machine. Feed frames in time order with update()."""

    def __init__(self, params=DEFAULT_PARAMS):
        self.params = params
        self.state = FOCUSED
        self._cand = FOCUSED
        self._cand_since = None

    def update(self, t, raw):
        if raw != self._cand:
            self._cand, self._cand_since = raw, t
        if self._cand_since is None:
            self._cand_since = t
        held = t - self._cand_since
        if self._cand == self.state:
            return self.state
        if self._cand == FOCUSED:
            if held >= self.params.recovery_s:
                self.state = FOCUSED
        elif held >= self.params.onset_s[self._cand]:
            self.state = self._cand
        return self.state


class AttentionEngine:
    """Calibration + classifier + filter for one study session."""

    def __init__(self, calibration, params=DEFAULT_PARAMS):
        self.cal = calibration
        self.params = params
        self.filter = TemporalFilter(params)

    def process(self, frame):
        raw = raw_state(frame, self.cal, self.params)
        return raw, self.filter.update(frame.t, raw)

    def process_many(self, frames):
        return [(f.t, *self.process(f)) for f in frames]
