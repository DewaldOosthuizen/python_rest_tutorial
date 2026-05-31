# Tasks: Issue #15

## Dependencies

- [ ] Add `pytest>=7.4` to `web/requirements.txt`
- [ ] Add `pytest-cov>=4.1` to `web/requirements.txt`

## Test Infrastructure

- [ ] Create empty `web/tests/__init__.py` to ensure correct import resolution
- [ ] Verify `from app import app` resolves correctly when pytest is run from `web/`
- [ ] Set `os.environ["JWT_SECRET"] = "testsecret"` before the `from app import app` import in the test module

## Hello Endpoint Tests

- [ ] `test_hello_returns_200` — GET `/hello` asserts HTTP 200

## Register Endpoint Tests

- [ ] `test_register_new_user_returns_200` — happy path, mock empty cursor, assert status 200
- [ ] `test_register_existing_user_returns_400` — mock populated cursor, assert status 400
- [ ] `test_register_missing_body_returns_400` — send empty JSON `{}`, assert status 400

## Login Endpoint Tests

- [ ] `test_login_valid_credentials_returns_token` — mock user cursor with hashed password, assert status 200 and `token` in response
- [ ] `test_login_wrong_password_returns_401` — mock user with different password, assert status 401
- [ ] `test_login_unknown_user_returns_401` — mock empty cursor, assert status 401
- [ ] `test_login_missing_body_returns_400` — send empty JSON `{}`, assert status 400

## Retrieve Endpoint Tests

- [ ] `test_retrieve_no_auth_header_returns_401` — no Authorization header, assert status 401
- [ ] `test_retrieve_expired_token_returns_401` — token with past `exp`, assert status 401
- [ ] `test_retrieve_tampered_token_returns_401` — malformed Bearer value, assert status 401
- [ ] `test_retrieve_valid_token_returns_messages` — valid JWT, mock user with messages, assert status 200 and correct messages

## Save Endpoint Tests

- [ ] `test_save_no_auth_header_returns_401` — no Authorization header, assert status 401
- [ ] `test_save_expired_token_returns_401` — expired JWT, assert status 401
- [ ] `test_save_valid_token_saves_and_returns_200` — valid JWT, mock user cursor, assert status 200
- [ ] `test_save_missing_message_returns_400` — valid JWT but no `message` field, assert status 400

## API Contract Tests (PyMongo method migration)

- [ ] `test_register_calls_insert_one` — assert `mock_users.insert_one` called exactly once (not deprecated `insert`)
- [ ] `test_save_calls_update_one` — assert `mock_users.update_one` called exactly once (not deprecated `update`)

## CI Verification

- [ ] Run `pytest` from `web/` locally and confirm all tests pass with zero warnings
- [ ] Confirm no `mongomock` dependency is introduced anywhere
