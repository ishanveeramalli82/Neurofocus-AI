import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app import create_app  # noqa: E402
from backend.security import login_limiter  # noqa: E402


@pytest.fixture
def app(tmp_path):
    login_limiter._hits.clear()
    return create_app({"DATABASE": str(tmp_path / "test.sqlite3"), "SECRET_KEY": "test", "TESTING": True})


class Api:
    def __init__(self, client):
        self.c = client
        self.csrf = client.get("/api/auth/csrf").get_json()["csrf"]

    def _do(self, method, url, json=None):
        r = getattr(self.c, method)(url, json=json, headers={"X-CSRF-Token": self.csrf})
        body = r.get_json(silent=True) or {}
        if "csrf" in body:
            self.csrf = body["csrf"]
        return r

    def get(self, url):
        return self.c.get(url)

    def post(self, url, json=None):
        return self._do("post", url, json)

    def put(self, url, json=None):
        return self._do("put", url, json)

    def patch(self, url, json=None):
        return self._do("patch", url, json)

    def delete(self, url, json=None):
        return self._do("delete", url, json)


@pytest.fixture
def api(app):
    return Api(app.test_client())


@pytest.fixture
def user(api):
    r = api.post("/api/auth/register", {"email": "student@example.com", "password": "correct-horse-9",
                                         "display_name": "Test Student"})
    assert r.status_code == 201, r.get_json()
    return api
