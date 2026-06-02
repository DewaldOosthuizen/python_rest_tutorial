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
import datetime
import os
import bcrypt
import pytest
import jwt
from unittest.mock import MagicMock, patch

# Set JWT_SECRET before importing app
os.environ["JWT_SECRET"] = "testsecret"

from app import app


TEST_SECRET = "testsecret"


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


def make_valid_token(username="alice", secret=TEST_SECRET):
    return jwt.encode(
        {"sub": username, "exp": datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)},
        secret,
        algorithm="HS256",
    )


def make_expired_token(username="alice"):
    return jwt.encode(
        {"sub": username, "exp": datetime.datetime.now(timezone.utc) - datetime.timedelta(seconds=1)},
        TEST_SECRET,
        algorithm="HS256",
    )


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
    assert rv.get_json() == "Hello World!"
    assert rv.headers["Content-Type"].startswith("application/json")


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
# Login
# ---------------------------------------------------------------------------

@patch("app.users")
def test_login_valid_credentials_returns_token(mock_users, client):
    mock_users.find.return_value = make_user_cursor(username="alice", password="secret")
    rv = client.post("/login", json={"username": "alice", "password": "secret"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == 200
    assert "token" in data


@patch("app.users")
def test_login_wrong_password_returns_401(mock_users, client):
    mock_users.find.return_value = make_user_cursor(username="alice", password="correct")
    rv = client.post("/login", json={"username": "alice", "password": "wrong"})
    assert rv.status_code == 401
    assert rv.get_json()["status"] == 401


@patch("app.users")
def test_login_unknown_user_returns_401(mock_users, client):
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/login", json={"username": "ghost", "password": "x"})
    assert rv.status_code == 401


def test_login_missing_body_returns_400(client):
    rv = client.post("/login", json={})
    assert rv.status_code == 400


# ---------------------------------------------------------------------------
# Retrieve
# ---------------------------------------------------------------------------

@patch("app.users")
def test_retrieve_no_auth_header_returns_401(mock_users, client):
    rv = client.post("/retrieve")
    assert rv.status_code == 401
    assert rv.get_json()["status"] == 401


@patch("app.users")
def test_retrieve_expired_token_returns_401(mock_users, client):
    token = make_expired_token()
    rv = client.post("/retrieve", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 401


@patch("app.users")
def test_retrieve_tampered_token_returns_401(mock_users, client):
    rv = client.post("/retrieve", headers={"Authorization": "Bearer tampered.token.value"})
    assert rv.status_code == 401


@patch("app.users")
def test_retrieve_valid_token_returns_messages(mock_users, client):
    mock_users.find.return_value = make_user_cursor(username="alice", messages=["hello"])
    token = make_valid_token(username="alice")
    rv = client.post("/retrieve", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == 200
    assert "hello" in data["obj"]


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

@patch("app.users")
def test_save_no_auth_header_returns_401(mock_users, client):
    rv = client.post("/save", json={"message": "hi"})
    assert rv.status_code == 401


@patch("app.users")
def test_save_expired_token_returns_401(mock_users, client):
    token = make_expired_token()
    rv = client.post("/save", json={"message": "hi"}, headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 401


@patch("app.users")
def test_save_valid_token_saves_and_returns_200(mock_users, client):
    mock_users.find.return_value = make_user_cursor(username="alice", messages=[])
    token = make_valid_token(username="alice")
    rv = client.post(
        "/save",
        json={"message": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rv.status_code == 200
    assert rv.get_json()["status"] == 200


@patch("app.users")
def test_save_missing_message_returns_400(mock_users, client):
    token = make_valid_token(username="alice")
    rv = client.post(
        "/save",
        json={},
        headers={"Authorization": "Bearer " + token},
    )
    assert rv.status_code == 400


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
    mock_users.find.return_value = make_user_cursor(username="alice", messages=[])
    token = make_valid_token(username="alice")
    client.post(
        "/save",
        json={"message": "hi"},
        headers={"Authorization": "Bearer " + token},
    )
    mock_users.update_one.assert_called_once()
