import datetime as dt
import os
import secrets
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory

from .db import close_db, init_db
from .security import apply_security_headers, check_csrf
from .validation import ValidationError

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PAGES = {"", "login", "register", "dashboard", "session", "history", "analytics",
         "schedule", "research", "settings"}


def _secret_key(instance):
    env = os.environ.get("NEUROFOCUS_SECRET_KEY")
    if env:
        return env
    path = instance / "secret_key"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_hex(32), encoding="utf-8")
        path.chmod(0o600)
    return path.read_text(encoding="utf-8").strip()


def create_app(test_config=None):
    instance = ROOT / "instance"
    app = Flask(__name__, static_folder=None)
    app.config.update(
        DATABASE=str(instance / "neurofocus.sqlite3"),
        SECRET_KEY=None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("NEUROFOCUS_SECURE_COOKIES") == "1",
        PERMANENT_SESSION_LIFETIME=dt.timedelta(days=14),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"]:
        app.config["SECRET_KEY"] = _secret_key(instance)
    init_db(app.config["DATABASE"])

    from . import auth, sessions_api, schedule_api, analytics_api, research_api
    for mod in (auth, sessions_api, schedule_api, analytics_api, research_api):
        app.register_blueprint(mod.bp)

    app.before_request(check_csrf)
    app.after_request(apply_security_headers)
    app.teardown_appcontext(close_db)

    @app.errorhandler(ValidationError)
    def _bad(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(404)
    def _nf(e):
        return jsonify(error="Not found."), 404

    @app.errorhandler(413)
    def _big(e):
        return jsonify(error="Request too large."), 413

    @app.get("/api/health")
    def health():
        return jsonify(ok=True)

    @app.get("/")
    @app.get("/<page>")
    def page(page=""):
        if page not in PAGES:
            abort(404)
        return send_from_directory(FRONTEND, f"{page or 'index'}.html")

    @app.get("/static/<path:path>")
    def static_files(path):
        return send_from_directory(FRONTEND, path)

    return app
