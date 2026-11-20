"""Security helpers: CSRF protection, login rate limiting, auth decorator, headers."""

import functools
import hmac
import secrets
import threading
import time

from flask import jsonify, request, session

CSRF_HEADER = "X-CSRF-Token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def check_csrf():
    """Called before every API request. State-changing requests must echo the
    per-session token in a header (double-submit pattern)."""
    if request.method in SAFE_METHODS or not request.path.startswith("/api/"):
        return None
    sent = request.headers.get(CSRF_HEADER, "")
    expected = session.get("csrf", "")
    if not expected or not hmac.compare_digest(sent, expected):
        return jsonify(error="Missing or invalid CSRF token. Reload the page and try again."), 403
    return None


class RateLimiter:
    """Counts failures per key in a sliding window (in-memory, single process)."""

    def __init__(self, max_failures=5, window_s=900):
        self.max, self.window = max_failures, window_s
        self._hits = {}
        self._lock = threading.Lock()

    def _prune(self, key, now):
        self._hits[key] = [t for t in self._hits.get(key, []) if now - t < self.window]

    def blocked(self, key):
        with self._lock:
            now = time.time()
            self._prune(key, now)
            return len(self._hits[key]) >= self.max

    def fail(self, key):
        with self._lock:
            now = time.time()
            self._prune(key, now)
            self._hits[key].append(now)

    def reset(self, key):
        with self._lock:
            self._hits.pop(key, None)


login_limiter = RateLimiter()


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(error="Please sign in."), 401
        return view(*args, **kwargs)
    return wrapped


CSP = "; ".join([
    "default-src 'self'",
    # MediaPipe is served locally (frontend/vendor); WebAssembly needs wasm-unsafe-eval.
    "script-src 'self' 'wasm-unsafe-eval'",
    "connect-src 'self'",
    "img-src 'self' data: blob:",
    "media-src 'self' blob:",
    "style-src 'self'",
    "font-src 'self'",
    "worker-src 'self' blob:",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
])


def apply_security_headers(resp):
    resp.headers.setdefault("Content-Security-Policy", CSP)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    resp.headers.setdefault("Permissions-Policy", "camera=(self), microphone=(), geolocation=()")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    elif not request.path.startswith("/static/vendor/"):
        # Pages, CSS and JS: always check for a newer copy (cheap, uses ETags),
        # so a `git pull` never leaves the browser running a mix of old and new files.
        resp.headers["Cache-Control"] = "no-cache"
    return resp
