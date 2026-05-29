# Tasks: Issue 5 — Add automated tests covering all API endpoints

## Dependencies

- [ ] DEP-1: Confirm Python 3.9+ is the target runtime (affects pytest version pin)

## Test infrastructure

- [ ] INFRA-1: Add `pytest>=7.0` to `web/requirements.txt` (no mongomock needed — we patch app.users directly)
- [ ] INFRA-2: Create `pytest.ini` at repository root with `testpaths = web/tests`
- [ ] INFRA-3: Create empty `web/tests/__init__.py`

## Test implementation — web/tests/test_app.py

Follow the mock strategy in proposal.md exactly. Never use find_one.

### Cursor helper functions

- [ ] TEST-1: Implement `make_user_cursor(username, password, messages)` returning a MagicMock where:
  - `cursor.count.return_value = 1`
  - `cursor.__getitem__.return_value = {"Username": ..., "Password": bcrypt_hash, "Messages": [...]}`
- [ ] TEST-2: Implement `make_empty_cursor()` returning a MagicMock where `cursor.count.return_value = 0`

### Fixtures

- [ ] TEST-3: Implement `client` pytest fixture — sets `app.config["TESTING"] = True`, yields `app.test_client()`

### Hello endpoint tests

- [ ] TEST-4: `test_hello_returns_200` — GET /hello, assert status_code == 200
- [ ] TEST-5: `test_hello_returns_hello_world` — GET /hello, assert b"Hello World" in rv.data

### Register endpoint tests

- [ ] TEST-6: `test_register_new_user_returns_200` — patch app.users, find returns empty cursor, POST /register with valid JSON, assert status 200 and response body status == 200
- [ ] TEST-7: `test_register_existing_user_returns_invalid` — patch app.users, find returns user cursor, POST /register, assert response body status == 301
- [ ] TEST-8: `test_register_missing_body_returns_500_known_defect` — POST /register with empty JSON {}, assert status_code == 500; add comment: "KNOWN DEFECT: no input validation guard; fix Register.post before changing this assertion"

### Retrieve endpoint tests

- [ ] TEST-9:  `test_retrieve_unknown_user_returns_invalid` — empty cursor, POST /retrieve, assert body status == 301
- [ ] TEST-10: `test_retrieve_wrong_password_returns_invalid` — user cursor with password="correct", POST with password="wrong", assert body status == 302
- [ ] TEST-11: `test_retrieve_valid_credentials_returns_messages` — user cursor with messages=["hello"], POST with correct credentials, assert body status == 200 and "hello" in body["obj"]

### Save endpoint tests

- [ ] TEST-12: `test_save_unknown_user_returns_invalid` — empty cursor, POST /save, assert body status == 301
- [ ] TEST-13: `test_save_wrong_password_returns_invalid` — user cursor with wrong password, POST /save, assert body status == 302
- [ ] TEST-14: `test_save_valid_request_returns_200` — user cursor with correct password, POST /save with message, assert body status == 200

## CI / GitHub Actions

- [ ] CI-1: Create `.github/workflows/test.yml` triggering on push and pull_request for all branches
- [ ] CI-2: Workflow steps: checkout → setup-python 3.11 → `pip install -r web/requirements.txt` → `pytest`

## Documentation

- [ ] DOC-1: Add "Running the tests" section to README.md showing `cd web && pip install -r requirements.txt && pytest`

## Known defect tracking (do not close without addressing)

- [ ] DEFECT-1: `Register.post`, `Retrieve.post`, `Save.post` have no input validation — missing/malformed body raises KeyError → HTTP 500. Tests TEST-8 documents this. A separate issue or follow-up PR should add proper guard clauses and change the assertion to 400.
