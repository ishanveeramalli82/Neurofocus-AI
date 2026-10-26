"""NeuroFocus attention engine.

This package is shared by the web backend and the research pipeline, so the
algorithm evaluated in the experiment is exactly the algorithm users run.
It must never import from research/ (the simulator / ground truth); a test in
tests/test_separation.py enforces this.
"""

from .params import (EngineParams, DEFAULT_PARAMS, ENGINE_VERSION, STATES,
                     DISTRACTED_STATES, FOCUSED, LOOKING_AWAY, LOOKING_DOWN,
                     EYES_CLOSED, ABSENT)
from .features import FeatureFrame, FEATURE_COLUMNS
from .calibration import Calibration, calibrate, default_calibration
from .classifier import AttentionEngine, TemporalFilter, raw_state
from .scoring import focus_score, episodes, LiveScore
