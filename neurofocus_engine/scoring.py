"""Focus Score and distraction-episode extraction.

Focus Score (0-100) = 100 x (time the filtered state is FOCUSED) / (elapsed time)

Time is measured by frame durations (gap to the next frame, capped so a pause
in data does not count as either focused or distracted). Time with no face
counts as not focused, because the engine reports it as ABSENT.

The definition is deliberately simple so it can be checked directly against
the simulator's ground-truth on-task percentage.
"""

from collections import deque

from .params import DEFAULT_PARAMS, FOCUSED

MAX_FRAME_GAP_S = 1.0


def focus_score(timeline):
    """timeline: list of (t, state) in time order. Returns score or None."""
    focused = total = 0.0
    for (t, s), (t_next, _) in zip(timeline, timeline[1:]):
        dt = min(max(t_next - t, 0.0), MAX_FRAME_GAP_S)
        total += dt
        if s == FOCUSED:
            focused += dt
    if total <= 0:
        return None
    return 100.0 * focused / total


def episodes(timeline):
    """Contiguous non-FOCUSED runs: list of dict(state, start, end)."""
    out, cur = [], None
    for t, s in timeline:
        if cur and (s != cur["state"]):
            cur["end"] = t
            out.append(cur)
            cur = None
        if s != FOCUSED and cur is None:
            cur = {"state": s, "start": t, "end": t}
    if cur:
        cur["end"] = timeline[-1][0]
        out.append(cur)
    return out


class LiveScore:
    """Trailing-window Focus Score for the live dashboard."""

    def __init__(self, params=DEFAULT_PARAMS):
        self.window = params.live_window_s
        self.buf = deque()

    def add(self, t, state):
        self.buf.append((t, state))
        while self.buf and t - self.buf[0][0] > self.window:
            self.buf.popleft()
        return focus_score(list(self.buf))
