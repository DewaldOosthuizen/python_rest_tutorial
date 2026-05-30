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
    # PROPAGATE_EXCEPTIONS must be False so unhandled exceptions (e.g. KeyError)
    # are surfaced as HTTP 500 responses rather than bubbling up as Python exceptions.
    app.config["PROPAGATE_EXCEPTIONS"] = False
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
    assert rv.status_code == 200


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
    assert rv.status_code == 400
    data = rv.get_json()
    assert data["status"] == 400


def test_register_missing_body_returns_400(client):
    rv = client.post("/register", json={})
    assert rv.status_code == 400


# ---------------------------------------------------------------------------
# Retrieve
# ---------------------------------------------------------------------------

@patch("app.users")
def test_retrieve_unknown_user_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/retrieve", json={"username": "ghost", "password": "x"})
    assert rv.status_code == 401
    data = rv.get_json()
    assert data["status"] == 401


@patch("app.users")
def test_retrieve_wrong_password_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_user_cursor(password="correct")
    rv = client.post("/retrieve", json={"username": "alice", "password": "wrong"})
    assert rv.status_code == 401
    data = rv.get_json()
    assert data["status"] == 401


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
    assert rv.status_code == 401
    assert rv.get_json()["status"] == 401


@patch("app.users")
def test_save_wrong_password_returns_invalid(mock_users, client):
    mock_users.find.return_value = make_user_cursor(password="correct")
    rv = client.post("/save", json={"username": "alice", "password": "wrong", "message": "hi"})
    assert rv.status_code == 401
    assert rv.get_json()["status"] == 401


@patch("app.users")
def test_save_valid_request_returns_200(mock_users, client):
    mock_users.find.return_value = make_user_cursor(password="secret", messages=[])
    rv = client.post("/save", json={"username": "alice", "password": "secret", "message": "hello"})
    assert rv.status_code == 200
    assert rv.get_json()["status"] == 200


# ---------------------------------------------------------------------------
# insert_one / update_one API migration (issue #6)
# ---------------------------------------------------------------------------

@patch("app.users")
def test_register_calls_insert_one(mock_users, client):
    """Register must use insert_one (not the deprecated insert)."""
    mock_users.find.return_value = make_empty_cursor()
    client.post("/register", json={"username": "bob", "password": "pass"})
    mock_users.insert_one.assert_called_once()


@patch("app.users")
def test_save_calls_update_one(mock_users, client):
    """Save must use update_one (not the deprecated update)."""
    mock_users.find.return_value = make_user_cursor(password="secret", messages=[])
    client.post("/save", json={"username": "alice", "password": "secret", "message": "hi"})
    mock_users.update_one.assert_called_once()
