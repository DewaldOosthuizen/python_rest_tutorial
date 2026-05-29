# Proposal: Add automated tests covering all API endpoints

## Problem

The repository contains zero test files. As an educational Flask + Flask-RESTful project it should
demonstrate test-driven practices. Without tests, regressions go undetected and the project
signals that testing is optional — which is the wrong lesson.

Four resources exist: Hello, Register, Retrieve, Save. None are tested.

## Root cause of the rejected attempt

The previous spec configured `mock_users.find_one.return_value` to control user-existence checks.
This is wrong. The helpers in `web/app.py` use `users.find(...)` exclusively — never
`find_one`. The three helpers and their actual call patterns are:

  user_exist (line 23-24):
    users.find({"Username": username}).count() > 0
    => mock must set find().count() return value

  verify_user (lines 27-34):
    users.find({"Username": username})[0]["Password"]
    => mock cursor must be subscriptable (support __getitem__)

  get_user_messages (lines 38-41):
    users.find({"Username": username})[0]["Messages"]
    => same subscriptable cursor requirement

Configuring find_one has zero effect on any of these paths.

## Solution

### 1. Correct mock cursor pattern

Every test that needs to simulate a user existing must build a cursor mock that satisfies all
three consumers simultaneously:

```python
import bcrypt
from unittest.mock import MagicMock, patch

def make_user_cursor(username="alice", password="secret", messages=None):
    """Return a MagicMock cursor that satisfies find().count() and find()[0]."""
    hashed = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
    user_doc = {
        "Username": username,
        "Password": hashed,
        "Messages": messages or [],
    }
    cursor = MagicMock()
    cursor.count.return_value = 1          # user_exist: find().count() > 0
    cursor.__getitem__.return_value = user_doc  # verify_user / get_user_messages: find()[0]
    return cursor
```

For a non-existent user:
```python
def make_empty_cursor():
    cursor = MagicMock()
    cursor.count.return_value = 0
    return cursor
```

### 2. Patching strategy

Patch the module-level `users` collection object in `app`, not the MongoClient import:

```python
@patch("app.users")
def test_something(mock_users):
    mock_users.find.return_value = make_user_cursor()
    ...
```

This is the minimal, correct patch point. All three helpers read from `app.users` directly.

### 3. Missing body / KeyError — known defect

`Register.post`, `Retrieve.post`, and `Save.post` access `data["username"]` and `data["password"]`
directly without guard clauses. If the body is missing or incomplete, Python raises a `KeyError`
which Flask surfaces as a 500. This is a defect in the tutorial code.

The test must document this as a known defect, not assert it as desired behaviour:

```python
def test_register_missing_body_returns_500_known_defect(client):
    # KNOWN DEFECT: no input validation; KeyError propagates as HTTP 500.
    # A correct implementation should return 400. Fix input validation before changing this test.
    rv = client.post("/register", json={})
    assert rv.status_code == 500  # documents current (broken) behaviour
```

### 4. File changes

#### web/requirements.txt — before
```
Flask==1.0.2
flask-restful
pymongo
bcrypt
```

#### web/requirements.txt — after (add at end)
```
Flask==1.0.2
flask-restful
pymongo
bcrypt
# dev / test
pytest>=7.0
```

Note: mongomock is not used — we patch `app.users` directly, so no MongoDB driver is needed
during tests.

#### NEW: pytest.ini (repository root)
```ini
[pytest]
testpaths = web/tests
```

#### NEW: web/tests/__init__.py
Empty file to make the directory a package.

#### NEW: web/tests/test_app.py
Full test module. Structure below — the implementer must write the actual code exactly as
described; do not deviate from the mock strategy in this proposal.

```python
"""
Tests for web/app.py — Flask REST tutorial.

Patching strategy
-----------------
All three helpers (user_exist, verify_user, get_user_messages) call
    app.users.find({"Username": ...})
and then either .count() or [0][field].  We therefore patch `app.users`
and configure the returned cursor with both count() and __getitem__.

We NEVER use find_one — it is not called anywhere in app.py.
"""
import bcrypt
import pytest
from unittest.mock import MagicMock, patch
from app import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user_cursor(username="alice", password="secret", messages=None):
    hashed = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
    user_doc = {
        "Username": username,
        "Password": hashed,
        "Messages": messages or [],
    }
    cursor = MagicMock()
    cursor.count.return_value = 1
    cursor.__getitem__.return_value = user_doc
    return cursor


def make_empty_cursor():
    cursor = MagicMock()
    cursor.count.return_value = 0
    return cursor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Hello
# ---------------------------------------------------------------------------

def test_hello_returns_200(client):
    rv = client.get("/hello")
    assert rv.status_code == 200


def test_hello_returns_hello_world(client):
    rv = client.get("/hello")
    assert b"Hello World" in rv.data


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@patch("app.users")
def test_register_new_user_returns_200(mock_users, client):
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/register", json={"username": "alice", "password": "secret"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == 200


@patch("app.users")
def test_register_existing_user_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_user_cursor()
    rv = client.post("/register", json={"username": "alice", "password": "secret"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == 301  # invalid_user_json


def test_register_missing_body_returns_500_known_defect(client):
    # KNOWN DEFECT: no input validation guard; KeyError propagates as HTTP 500.
    # A correct implementation should return 400. Fix Register.post before changing this test.
    rv = client.post("/register", json={})
    assert rv.status_code == 500


# ---------------------------------------------------------------------------
# Retrieve
# ---------------------------------------------------------------------------

@patch("app.users")
def test_retrieve_unknown_user_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/retrieve", json={"username": "ghost", "password": "x"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == 301


@patch("app.users")
def test_retrieve_wrong_password_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_user_cursor(password="correct")
    rv = client.post("/retrieve", json={"username": "alice", "password": "wrong"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == 302  # invalid_password_json


@patch("app.users")
def test_retrieve_valid_credentials_returns_messages(mock_users, client):
    mock_users.find.return_value = make_user_cursor(
        password="secret", messages=["hello"]
    )
    rv = client.post("/retrieve", json={"username": "alice", "password": "secret"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == 200
    assert "hello" in data["obj"]


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

@patch("app.users")
def test_save_unknown_user_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/save", json={"username": "ghost", "password": "x", "message": "hi"})
    assert rv.status_code == 200
    assert rv.get_json()["status"] == 301


@patch("app.users")
def test_save_wrong_password_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_user_cursor(password="correct")
    rv = client.post("/save", json={"username": "alice", "password": "wrong", "message": "hi"})
    assert rv.status_code == 200
    assert rv.get_json()["status"] == 302


@patch("app.users")
def test_save_valid_request_returns_200(mock_users, client):
    mock_users.find.return_value = make_user_cursor(password="secret", messages=[])
    rv = client.post("/save", json={"username": "alice", "password": "secret", "message": "hello"})
    assert rv.status_code == 200
    assert rv.get_json()["status"] == 200
```

#### NEW: .github/workflows/test.yml
```yaml
name: Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: ["**"]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r web/requirements.txt
      - name: Run tests
        run: pytest
```

#### README.md — add section "Running the tests"
After the existing Docker instructions, add:

```markdown
## Running the tests

```bash
cd web
pip install -r requirements.txt
pytest
```
```

## Acceptance criteria (from issue)

- [ ] web/tests/ directory exists with test_app.py
- [ ] All four endpoints have at least one happy-path and one error-path test
- [ ] Tests pass with `pytest` from the repository root (testpaths configured in pytest.ini)
- [ ] CI workflow runs on every push and pull request
- [ ] README documents how to run the test suite
- [ ] Mock strategy uses find().count() and find()[0] — never find_one
- [ ] Missing-body tests document the KeyError defect explicitly, not silently accept it
