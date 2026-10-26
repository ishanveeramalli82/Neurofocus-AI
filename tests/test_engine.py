import math

from neurofocus_engine import (ABSENT, EYES_CLOSED, FOCUSED, LOOKING_AWAY, LOOKING_DOWN,
                               AttentionEngine, FeatureFrame, TemporalFilter, calibrate,
                               default_calibration, episodes, focus_score, raw_state)


def frame(t, yaw=0.0, pitch=0.0, ear=0.3, gaze_h=0.0, present=True):
    return FeatureFrame(t=t, face_present=present, yaw=yaw, pitch=pitch, ear=ear, gaze_h=gaze_h, gaze_v=0.0)


def test_raw_state_rules():
    cal = default_calibration()
    assert raw_state(frame(0), cal) == FOCUSED
    assert raw_state(frame(0, present=False), cal) == ABSENT
    assert raw_state(frame(0, ear=0.1), cal) == EYES_CLOSED
    assert raw_state(frame(0, pitch=-30), cal) == LOOKING_DOWN
    assert raw_state(frame(0, yaw=40), cal) == LOOKING_AWAY
    assert raw_state(frame(0, yaw=-40), cal) == LOOKING_AWAY
    # eyes alone can push the combined angle over threshold
    assert raw_state(frame(0, yaw=10, gaze_h=0.6), cal) == LOOKING_AWAY


def test_filter_ignores_blinks_and_glances():
    f = TemporalFilter()
    out = [f.update(i / 10, EYES_CLOSED if 5 <= i < 8 else FOCUSED) for i in range(30)]
    assert set(out) == {FOCUSED}
    f = TemporalFilter()
    out = [f.update(i / 10, LOOKING_AWAY if 5 <= i < 20 else FOCUSED) for i in range(40)]
    assert set(out) == {FOCUSED}  # 1.5 s glance < 2 s onset


def test_filter_detects_sustained_state_with_expected_latency():
    f = TemporalFilter()
    states = [f.update(i / 10, LOOKING_AWAY if i >= 10 else FOCUSED) for i in range(60)]
    first = states.index(LOOKING_AWAY)
    assert math.isclose(first / 10 - 1.0, 2.0, abs_tol=0.11)


def test_calibration_recovers_offset_and_flips_sign():
    centre = [frame(i / 10, yaw=30 + (i % 3) * 0.2, pitch=-10, ear=0.25) for i in range(100)]
    corners = [frame(i / 10, yaw=30 + s * 12, pitch=-10 + p * 6, ear=0.25)
               for i, (s, p) in enumerate([(1, 1), (-1, 1), (1, -1), (-1, -1)] * 10)]
    down = [frame(i / 10, yaw=30, pitch=+20, ear=0.22) for i in range(30)]  # inverted convention
    cal, ok = calibrate({"center": centre, "corners": corners, "down": down})
    assert ok and cal.calibrated
    assert abs(cal.yaw0 - 30.2) < 0.5 and abs(cal.pitch0 + 10) < 0.01
    assert cal.pitch_sign == -1.0
    assert 15 <= cal.yaw_threshold <= 45
    # sitting at the calibrated pose is focused; with defaults it is not
    assert raw_state(frame(0, yaw=30, pitch=-10, ear=0.25), cal) == FOCUSED
    assert raw_state(frame(0, yaw=30, pitch=-10, ear=0.25), default_calibration()) != FOCUSED


def test_calibration_fails_without_face():
    cal, ok = calibrate({"center": [frame(i / 10, present=False) for i in range(100)]})
    assert not ok and cal.quality == "failed"


def test_focus_score_and_episodes():
    tl = [(i / 10, FOCUSED if i < 50 else LOOKING_DOWN) for i in range(101)]
    assert math.isclose(focus_score(tl), 50.0, abs_tol=0.01)
    eps = episodes(tl)
    assert len(eps) == 1 and eps[0]["state"] == LOOKING_DOWN and eps[0]["start"] == 5.0


def test_frame_from_dict_handles_blanks():
    f = FeatureFrame.from_dict({"t": "1.5", "face_present": "1", "yaw": "", "pitch": "2"})
    assert f.face_present is False  # missing pose -> treated as no detection
    f = FeatureFrame.from_dict({"t": 2, "face_present": True, "yaw": 1, "pitch": 2, "ear": "nan"})
    assert f.face_present and math.isnan(f.ear)


def test_engine_end_to_end():
    eng = AttentionEngine(default_calibration())
    frames = [frame(i / 10, pitch=-35 if 20 <= i < 80 else 0) for i in range(120)]
    out = eng.process_many(frames)
    states = [s for _, _, s in out]
    assert LOOKING_DOWN in states and states[-1] == FOCUSED
