"""Runs the browser-side JavaScript unit tests (tests/js) with Node if it is installed."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js not installed")
def test_javascript_units():
    files = sorted(str(p) for p in (ROOT / "tests" / "js").glob("*.test.mjs"))
    r = subprocess.run(["node", "--test", *files], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
