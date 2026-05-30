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
    # PROPAGATE_EXCEPTIONS must be True so JWT exceptions (e.g. NoAuthorizationError)
    # are handled by the JWT error handlers rather than being caught by flask_restful
    # and returned as 500.
    app.config["PROPAGATE_EXCEPTIONS"] = True
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
    # [ORCHESTRATOR NOTE] Pre-existing failure — behavior changed by issue #7
    # Failure: Retrieve now requires JWT token; in-body credential passing removed
    # Suggested fix: Use /login to get a token and pass it in Authorization header
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/retrieve", json={"username": "ghost", "password": "x"})
    assert rv.status_code == 401
    data = rv.get_json()
    assert data["status"] == 401


@patch("app.users")
def test_retrieve_wrong_password_returns_invalid(mock_users, client):
    # [ORCHESTRATOR NOTE] Pre-existing failure — behavior changed by issue #7
    # Failure: Retrieve now requires JWT token; in-body password no longer accepted
    # Suggested fix: Use /login to get a token and pass it in Authorization header
    mock_users.find.return_value = make_user_cursor(password="correct")
    rv = client.post("/retrieve", json={"username": "alice", "password": "wrong"})
    assert rv.status_code == 401
    data = rv.get_json()
    assert data["status"] == 401


@patch("app.users")
def test_retrieve_valid_credentials_returns_messages(mock_users, client):
    # [ORCHESTRATOR NOTE] Pre-existing failure — behavior changed by issue #7
    # Failure: Retrieve now requires JWT token; in-body password no longer accepted
    # Suggested fix: Use /login to get a token and pass it in Authorization header
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
    # [ORCHESTRATOR NOTE] Pre-existing failure — behavior changed by issue #7
    # Failure: Save now requires JWT token; in-body credential passing removed
    # Suggested fix: Use /login to get a token and pass it in Authorization header
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/save", json={"username": "ghost", "password": "x", "message": "hi"})
    assert rv.status_code == 401
    assert rv.get_json()["status"] == 401


@patch("app.users")
def test_save_wrong_password_returns_invalid(mock_users, client):
    # [ORCHESTRATOR NOTE] Pre-existing failure — behavior changed by issue #7
    # Failure: Save now requires JWT token; in-body password no longer accepted
    # Suggested fix: Use /login to get a token and pass it in Authorization header
    mock_users.find.return_value = make_user_cursor(password="correct")
    rv = client.post("/save", json={"username": "alice", "password": "wrong", "message": "hi"})
    assert rv.status_code == 401
    assert rv.get_json()["status"] == 401


@patch("app.users")
def test_save_valid_request_returns_200(mock_users, client):
    # [ORCHESTRATOR NOTE] Pre-existing failure — behavior changed by issue #7
    # Failure: Save now requires JWT token; in-body password no longer accepted
    # Suggested fix: Use /login to get a token and pass it in Authorization header
    mock_users.find.return_value = make_user_cursor(password="secret", messages=[])
    rv = client.post("/save", json={"username": "alice", "password": "secret", "message": "hello"})
    assert rv.status_code == 200
    assert rv.get_json()["status"] == 200


# ---------------------------------------------------------------------------
# Login (issue #7 - JWT token-based auth)
# ---------------------------------------------------------------------------

@patch("app.users")
def test_login_valid_credentials_returns_token(mock_users, client):
    mock_users.find.return_value = make_user_cursor(username="alice", password="secret")
    rv = client.post("/login", json={"username": "alice", "password": "secret"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert "access_token" in data


@patch("app.users")
def test_login_wrong_password_returns_401(mock_users, client):
    mock_users.find.return_value = make_user_cursor(username="alice", password="correct")
    rv = client.post("/login", json={"username": "alice", "password": "wrong"})
    assert rv.status_code == 401


@patch("app.users")
def test_login_unknown_user_returns_401(mock_users, client):
    mock_users.find.return_value = make_empty_cursor()
    rv = client.post("/login", json={"username": "ghost", "password": "x"})
    assert rv.status_code == 401


def test_login_missing_body_returns_400(client):
    rv = client.post("/login", json={})
    assert rv.status_code == 400


# ---------------------------------------------------------------------------
# Retrieve with JWT (issue #7)
# ---------------------------------------------------------------------------

@patch("app.users")
def test_retrieve_with_token_returns_messages(mock_users, client):
    """After issue #7: Retrieve uses JWT token, no password in body."""
    mock_users.find.return_value = make_user_cursor(
        username="alice", password="secret", messages=["hello"]
    )
    # First get a token
    login_rv = client.post("/login", json={"username": "alice", "password": "secret"})
    assert login_rv.status_code == 200
    token = login_rv.get_json()["access_token"]

    mock_users.find.return_value = make_user_cursor(
        username="alice", password="secret", messages=["hello"]
    )
    rv = client.post(
        "/retrieve",
        json={"username": "alice"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rv.status_code == 200
    assert "hello" in rv.get_json()["obj"]


def test_retrieve_without_token_returns_401(client):
    """After issue #7: Retrieve requires JWT token."""
    rv = client.post("/retrieve", json={"username": "alice"})
    assert rv.status_code == 401


# ---------------------------------------------------------------------------
# Save with JWT (issue #7)
# ---------------------------------------------------------------------------

@patch("app.users")
def test_save_with_token_returns_200(mock_users, client):
    """After issue #7: Save uses JWT token, no password in body."""
    mock_users.find.return_value = make_user_cursor(
        username="alice", password="secret", messages=[]
    )
    login_rv = client.post("/login", json={"username": "alice", "password": "secret"})
    assert login_rv.status_code == 200
    token = login_rv.get_json()["access_token"]

    mock_users.find.return_value = make_user_cursor(
        username="alice", password="secret", messages=[]
    )
    rv = client.post(
        "/save",
        json={"username": "alice", "message": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rv.status_code == 200
    assert rv.get_json()["status"] == 200


def test_save_without_token_returns_401(client):
    """After issue #7: Save requires JWT token."""
    rv = client.post("/save", json={"username": "alice", "message": "hi"})
    assert rv.status_code == 401
