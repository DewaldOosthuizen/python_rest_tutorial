import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add web directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

@pytest.fixture
def client():
    with patch('pymongo.MongoClient'):
        import importlib
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config['TESTING'] = True
        with app_module.app.test_client() as c:
            yield c, app_module


# ---- Register tests ----

def test_register_no_body(client):
    c, _ = client
    response = c.post('/register')
    assert response.status_code == 400

def test_register_missing_username(client):
    c, _ = client
    response = c.post('/register', json={"password": "pass123"})
    assert response.status_code == 400

def test_register_missing_password(client):
    c, _ = client
    response = c.post('/register', json={"username": "testuser"})
    assert response.status_code == 400

def test_register_duplicate_user(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=True):
        response = c.post('/register', json={"username": "existing", "password": "pass"})
        assert response.status_code == 400

def test_register_success(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=False), \
         patch.object(app_module, 'users') as mock_users:
        mock_users.insert_one = MagicMock()
        response = c.post('/register', json={"username": "newuser", "password": "pass"})
        assert response.status_code == 200


# ---- Retrieve tests ----

def test_retrieve_no_body(client):
    c, _ = client
    response = c.post('/retrieve')
    assert response.status_code == 400

def test_retrieve_invalid_credentials_no_user(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=False):
        response = c.post('/retrieve', json={"username": "nobody", "password": "wrong"})
        assert response.status_code == 401

def test_retrieve_invalid_credentials_wrong_password(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=True), \
         patch.object(app_module, 'verify_user', return_value=False):
        response = c.post('/retrieve', json={"username": "user", "password": "wrong"})
        assert response.status_code == 401

def test_retrieve_success(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=True), \
         patch.object(app_module, 'verify_user', return_value=True), \
         patch.object(app_module, 'get_user_messages', return_value=["hello"]):
        response = c.post('/retrieve', json={"username": "user", "password": "pass"})
        assert response.status_code == 200


# ---- Save tests ----

def test_save_no_body(client):
    c, _ = client
    response = c.post('/save')
    assert response.status_code == 400

def test_save_missing_message(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=True), \
         patch.object(app_module, 'verify_user', return_value=True):
        response = c.post('/save', json={"username": "user", "password": "pass"})
        assert response.status_code == 400

def test_save_invalid_credentials(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=False):
        response = c.post('/save', json={"username": "nobody", "password": "wrong", "message": "hi"})
        assert response.status_code == 401

def test_save_success(client):
    c, app_module = client
    with patch.object(app_module, 'user_exist', return_value=True), \
         patch.object(app_module, 'verify_user', return_value=True), \
         patch.object(app_module, 'get_user_messages', return_value=[]), \
         patch.object(app_module, 'users') as mock_users:
        mock_users.update_one = MagicMock()
        response = c.post('/save', json={"username": "user", "password": "pass", "message": "hello"})
        assert response.status_code == 200
