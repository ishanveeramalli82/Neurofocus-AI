"""Builds neurofocus_all_in_one.py: a single, copy-pasteable launcher that
contains every source file of the project and recreates the folder on run.

Usage: python tools/build_all_in_one.py   (writes neurofocus_all_in_one.py at the repo root)
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "neurofocus_all_in_one.py"
SKIP_PREFIXES = ("frontend/vendor/mediapipe/", "frontend/vendor/models/", "tools/")
SKIP_FILES = {"neurofocus_all_in_one.py"}

# Large binary assets are downloaded once on first run, then verified by SHA-256.
VENDOR = [
    ("frontend/vendor/mediapipe/vision_bundle.mjs",
     "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs",
     "e77f281f9619150d937023c355bae170e9120e3b9e43f1e23a2a7bee07197669"),
    ("frontend/vendor/mediapipe/wasm/vision_wasm_internal.js",
     "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_internal.js",
     "9440cf0cc0cea21800e31581ec32aeedcc5fbf9df4509796bbc7d3f99e52ab9c"),
    ("frontend/vendor/mediapipe/wasm/vision_wasm_internal.wasm",
     "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_internal.wasm",
     "f82a8e6c05e08a44cc9f9e7ec5f845935bcbb1b1500ebe8c2f4812fb4e2917dc"),
    ("frontend/vendor/mediapipe/wasm/vision_wasm_nosimd_internal.js",
     "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_nosimd_internal.js",
     "abe9b6fbeaf86fcb53a5edce3926c82ccb0619e18fed4d9d9ce561ee7f55e054"),
    ("frontend/vendor/mediapipe/wasm/vision_wasm_nosimd_internal.wasm",
     "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_nosimd_internal.wasm",
     "38b61feab2fd7934e05cbe9f68baa308978a5e3b7f85c1913bb8ae89b8ef8b97"),
    ("frontend/vendor/models/face_landmarker.task",
     "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
     "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff"),
]

HEADER = '''#!/usr/bin/env python3
# =============================================================================
#  NeuroFocus AI - ALL-IN-ONE LAUNCHER
# =============================================================================
#  HOW TO USE (VS Code):
#    1. Make an empty folder, e.g. Documents\\NeuroFocusAI, and open it in VS Code
#       (File > Open Folder).
#    2. Create a new file in it called  neurofocus_all_in_one.py  and paste
#       this entire file into it. Save (Ctrl+S).
#    3. Open a terminal (Terminal > New Terminal) and run:
#           python neurofocus_all_in_one.py
#       (on Mac: python3 neurofocus_all_in_one.py)
#    4. Chrome opens http://127.0.0.1:5000 . Create an account, allow the
#       camera, and start a Focus Session. Press Ctrl+C in the terminal to stop.
#
#  WHAT IT DOES ON FIRST RUN:
#    - installs the Python packages it needs (Flask, NumPy, SciPy, Matplotlib, pytest)
#    - unpacks the full, organized project into a folder called  neurofocus\\
#      (engine, backend, frontend, research experiment, docs, tests)
#    - downloads the MediaPipe face-tracking files (~22 MB, needs internet once)
#    - starts the app. After the first run it also works offline.
#
#  OTHER COMMANDS (run from the same folder as this file):
#    python neurofocus_all_in_one.py --tests        run the automated tests
#    python neurofocus_all_in_one.py --experiment   run the official experiment
#    python neurofocus_all_in_one.py --unpack-only  only create the project folder
#
#  NeuroFocus estimates where your head and eyes point. It does not measure
#  learning and is not a medical or diagnostic tool.
#  Generated from project commit {commit}. Do not edit the embedded files here;
#  edit them in the unpacked neurofocus\\ folder instead.
# =============================================================================

import hashlib
import os
import subprocess
import sys
import urllib.request
import webbrowser
from pathlib import Path

VERSION = "{commit}"
PROJECT_DIR = Path(__file__).resolve().parent / "neurofocus"
REQUIREMENTS = ["flask>=3.0", "numpy>=1.26", "scipy>=1.11", "matplotlib>=3.8", "pytest>=8.0"]
# Optional override for where the face-tracking files are downloaded from.
MIRROR = os.environ.get("NEUROFOCUS_VENDOR_MIRROR")

VENDOR = {vendor}

FILES = {{}}
'''

FOOTER = r'''

# =============================================================================
#  LAUNCHER LOGIC
# =============================================================================

def unpack():
    """Write the project folder. Your database and experiment data are never touched."""
    marker = PROJECT_DIR / ".neurofocus_version"
    if marker.exists() and marker.read_text(encoding="utf-8").strip() == VERSION:
        return
    print(f"Unpacking project into {PROJECT_DIR} ...")
    for rel, text in FILES.items():
        path = PROJECT_DIR / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    marker.write_text(VERSION, encoding="utf-8")


def ensure_packages():
    missing = []
    for mod in ("flask", "numpy", "scipy", "matplotlib", "pytest"):
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"Installing Python packages ({', '.join(missing)}) ... this can take a minute.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *REQUIREMENTS])


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_vendor():
    for rel, url, digest in VENDOR:
        path = PROJECT_DIR / rel
        if path.exists() and _sha256(path) == digest:
            continue
        if MIRROR:
            url = MIRROR.rstrip("/") + "/" + rel.split("vendor/", 1)[1]
        print(f"Downloading {path.name} ...")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        try:
            with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
        except Exception as e:
            tmp.unlink(missing_ok=True)
            sys.exit(f"\nCould not download {url}\n  ({e})\n"
                     "Check your internet connection (a school network may block it) and run again.")
        if _sha256(tmp) != digest:
            tmp.unlink(missing_ok=True)
            sys.exit(f"\nDownloaded {path.name} but it did not match the expected file. Run again.")
        tmp.replace(path)


def main():
    if sys.version_info < (3, 10):
        sys.exit("NeuroFocus needs Python 3.10 or newer. Install it from python.org.")
    unpack()
    ensure_packages()
    args = sys.argv[1:]
    if "--unpack-only" in args:
        print(f"Project is in {PROJECT_DIR}")
        return
    if "--tests" in args:
        sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=PROJECT_DIR))
    if "--experiment" in args:
        sys.exit(subprocess.call([sys.executable, "-m", "research.pipeline.run_experiment",
                                  "--config", "research/config/experiment_v1.json"], cwd=PROJECT_DIR))
    ensure_vendor()
    os.chdir(PROJECT_DIR)
    sys.path.insert(0, str(PROJECT_DIR))
    from backend.app import create_app
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    url = f"http://127.0.0.1:{port}"
    print(f"\nNeuroFocus AI is running at {url}  (press Ctrl+C to stop)\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
'''


def main():
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip() or "dev"
    files = [f for f in subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                                       text=True, check=True).stdout.splitlines()
             if not f.startswith(SKIP_PREFIXES) and f not in SKIP_FILES]
    vendor = "[\n" + "".join(f"    ({r!r},\n     {u!r},\n     {d!r}),\n" for r, u, d in VENDOR) + "]"
    parts = [HEADER.format(commit=commit, vendor=vendor)]
    for rel in files:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "'''" in text or text.endswith("\\"):
            raise SystemExit(f"cannot embed {rel} as a raw string")
        bar = "=" * max(10, 70 - len(rel))
        parts.append(f"\n# ===== {rel} {bar}\nFILES[{rel!r}] = r'''{text}'''\n")
    parts.append(FOOTER)
    OUT.write_text("".join(parts), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(files)} files)")


if __name__ == "__main__":
    main()
