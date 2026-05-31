# Proposal: Issue #15 — Add Unit and Integration Test Suite

## Overview

The repository has zero test coverage: no `tests/` directory exists, no pytest configuration is
present, and `pytest` is absent from `requirements.txt`. All five Flask-RESTful endpoints
(`/hello`, `/register`, `/login`, `/retrieve`, `/save`) are exercised only by running the full
Docker stack manually. The fix introduces `web/tests/test_app.py` with a comprehensive pytest
suite that patches `app.users` via `unittest.mock.patch` (no live MongoDB required), adds
`pytest` and `pytest-cov` to `web/requirements.txt`, and optionally adds a `pytest.ini` /
`pyproject.toml` section so pytest can discover tests from `web/` without manual configuration.

## Issues

### Issue 1

**File:** `web/requirements.txt`
**Problem:** `pytest` (and optionally `pytest-cov`) are not listed. Running `pytest` in CI would
fail immediately with a missing-command error.
**Fix:** Append `pytest>=7.4` (and `pytest-cov>=4.1` for coverage reporting) to
`web/requirements.txt`. A separate `requirements-dev.txt` is an equally valid alternative.

Before:
```
flask
flask-restful
pymongo
bcrypt
pyjwt
```

After:
```
flask
flask-restful
pymongo
bcrypt
pyjwt
pytest>=7.4
pytest-cov>=4.1
```

### Issue 2

**File:** `web/tests/__init__.py` (virtual — does not exist)
**Problem:** Without an `__init__.py` in `web/tests/`, pytest import-mode `prepend` may fail to
resolve `from app import app` when pytest is invoked from `web/`.
**Fix:** Create an empty `web/tests/__init__.py` to mark the directory as a package and ensure
consistent import resolution.

### Issue 3

**File:** `web/tests/test_app.py` (virtual — does not exist)
**Problem:** No test file exists. Regressions in any of the five endpoints go undetected, and
learners have no reference for testing Flask/MongoDB applications without a live database.
**Fix:** Create `web/tests/test_app.py` with pytest tests covering every acceptance criterion:

- `/hello` GET — assert HTTP 200.
- `/register` happy path — assert HTTP 200 and `{"status": 200}`.
- `/register` duplicate user — assert HTTP 400.
- `/register` missing fields — assert HTTP 400.
- `/login` happy path — assert HTTP 200 and `token` present in response.
- `/login` wrong password — assert HTTP 401.
- `/login` missing fields — assert HTTP 400.
- `/retrieve` no Authorization header — assert HTTP 401.
- `/retrieve` expired JWT — assert HTTP 401.
- `/retrieve` tampered JWT — assert HTTP 401.
- `/retrieve` valid JWT — assert HTTP 200 and messages returned.
- `/save` no Authorization header — assert HTTP 401.
- `/save` expired JWT — assert HTTP 401.
- `/save` happy path — assert HTTP 200.
- `/save` missing `message` field — assert HTTP 400.
- `Register` calls `users.insert_one` (not deprecated `insert`).
- `Save` calls `users.update_one` (not deprecated `update`).

Patching strategy: patch the module-level `app.users` collection object with
`@patch("app.users")`. Configure the mock cursor returned by `users.find(...)` with both
`.count()` and `.__getitem__()` because `user_exist`, `verify_user`, and `get_user_messages`
all call `users.find({"Username": ...})` and then index or count the result. Never use
`find_one` — it is not called anywhere in `app.py`.

Key implementation note: set `os.environ["JWT_SECRET"] = "testsecret"` before importing
`app`, because `SECRET = os.environ.get("JWT_SECRET", ...)` is evaluated at import time.
