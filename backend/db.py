import datetime as dt
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = Path(__file__).with_name("schema.sql")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA.read_text())
    con.execute("PRAGMA journal_mode = WAL")
    con.close()


def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def row_dict(row):
    return dict(row) if row is not None else None
