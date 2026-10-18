"""Smoke tests against a running server (default http://localhost:8000).

Run:  python3 tests/smoke.py
Expects the server from `uvicorn app.main:app --port 8000` to be up.
Uses only the standard library.
"""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8000"
passed = failed = 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except AssertionError as e:
        print(f"  FAIL  {name}: {e}")
        failed += 1


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def get(path, headers=None):
    req = urllib.request.Request(BASE + path, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


valid = {
    "name": "Test Client",
    "email": "client@example.com",
    "service": "Web Development",
    "message": "Please build us a landing page for our new product launch.",
    "source_page": "contact",
}


def t_health():
    s, b = get("/api/health")
    assert s == 200 and b.get("ok") is True, b


def t_valid_submit():
    s, b = post("/api/inquiries", valid)
    assert s == 201, (s, b)
    assert b.get("ok") is True and isinstance(b.get("id"), int), b


def t_bad_email():
    s, b = post("/api/inquiries", {**valid, "email": "not-an-email"})
    assert s == 422, (s, b)


def t_bad_service():
    s, b = post("/api/inquiries", {**valid, "service": "Time Travel"})
    assert s == 422, (s, b)


def t_short_message():
    s, b = post("/api/inquiries", {**valid, "message": "hi"})
    assert s == 422, (s, b)


def t_admin_forbidden():
    s, _ = get("/api/inquiries")
    assert s == 403, s


print("Rizz Edits Studio API — smoke tests")
for name, fn in [
    ("health check", t_health),
    ("valid inquiry accepted", t_valid_submit),
    ("invalid email rejected (422)", t_bad_email),
    ("invalid service rejected (422)", t_bad_service),
    ("short message rejected (422)", t_short_message),
    ("admin list without key forbidden (403)", t_admin_forbidden),
]:
    check(name, fn)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
