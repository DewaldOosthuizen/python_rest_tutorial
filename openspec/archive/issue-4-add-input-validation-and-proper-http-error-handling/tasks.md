# Tasks: Add Input Validation and Proper HTTP Error Handling to All Endpoints

## Input Validation — Register endpoint

- [ ] Guard `Register.post()`: call `request.get_json()` and return HTTP 400 if result is `None` (file: `web/app.py`, line 66)
- [ ] Replace `data["username"]` and `data["password"]` bracket access with `.get()` in `Register.post()` (file: `web/app.py`, lines 68–69)
- [ ] Return HTTP 400 with message "username and password are required" if either field is falsy in `Register.post()` (file: `web/app.py`)
- [ ] Return HTTP 400 (not HTTP 200) when the user already exists in `Register.post()` (file: `web/app.py`, line 73)
- [ ] Return explicit HTTP 200 tuple on successful registration in `Register.post()` (file: `web/app.py`, line 90)

## Input Validation — Retrieve endpoint

- [ ] Guard `Retrieve.post()`: return HTTP 400 if `request.get_json()` is `None` (file: `web/app.py`, line 100)
- [ ] Replace `data["username"]` and `data["password"]` bracket access with `.get()` in `Retrieve.post()` (file: `web/app.py`, lines 103–104)
- [ ] Return HTTP 400 with message "username and password are required" if either field is falsy in `Retrieve.post()` (file: `web/app.py`)
- [ ] Return HTTP 401 (not HTTP 200) when user does not exist in `Retrieve.post()` (file: `web/app.py`, line 108)
- [ ] Return HTTP 401 (not HTTP 200) when password verification fails in `Retrieve.post()` (file: `web/app.py`, line 113)
- [ ] Use a single "Invalid credentials" message for both user-not-found and wrong-password to prevent user enumeration (file: `web/app.py`)
- [ ] Return explicit HTTP 200 tuple on successful retrieval in `Retrieve.post()` (file: `web/app.py`, line 124)

## Input Validation — Save endpoint

- [ ] Guard `Save.post()`: return HTTP 400 if `request.get_json()` is `None` (file: `web/app.py`, line 135)
- [ ] Replace `data["username"]`, `data["password"]`, and `data["message"]` bracket access with `.get()` in `Save.post()` (file: `web/app.py`, lines 138–140)
- [ ] Return HTTP 400 with message "username and password are required" if either credential field is falsy in `Save.post()` (file: `web/app.py`)
- [ ] Return HTTP 400 with message "message is required" if `message` is falsy in `Save.post()` (file: `web/app.py`)
- [ ] Return HTTP 401 (not HTTP 200) when user does not exist in `Save.post()` (file: `web/app.py`, line 144)
- [ ] Return HTTP 401 (not HTTP 200) when password verification fails in `Save.post()` (file: `web/app.py`, line 149)
- [ ] Remove the status 303 response for empty message — replace with HTTP 400 (file: `web/app.py`, lines 152–156)
- [ ] Return explicit HTTP 200 tuple on successful save in `Save.post()` (file: `web/app.py`, line 178)

## Shared Error Constants Cleanup

- [ ] Remove or replace `invalid_user_json` module-level constant with inline response tuples at all call sites (file: `web/app.py`)
- [ ] Remove or replace `invalid_password_json` module-level constant with inline response tuples at all call sites (file: `web/app.py`)

## HTTP Semantics

- [ ] Ensure all error responses include an explicit HTTP status code as the second element of the return tuple (file: `web/app.py`)
- [ ] Ensure all success responses return HTTP 200 explicitly (file: `web/app.py`)
- [ ] Verify no endpoint can fall through to an unhandled exception path that returns a raw stack trace

## Testing

- [ ] Write a test: POST `/register` with no body returns HTTP 400
- [ ] Write a test: POST `/register` with missing `username` returns HTTP 400
- [ ] Write a test: POST `/register` with missing `password` returns HTTP 400
- [ ] Write a test: POST `/retrieve` with no body returns HTTP 400
- [ ] Write a test: POST `/retrieve` with invalid credentials returns HTTP 401 (not 200)
- [ ] Write a test: POST `/save` with no body returns HTTP 400
- [ ] Write a test: POST `/save` with missing `message` returns HTTP 400
- [ ] Write a test: POST `/save` with invalid credentials returns HTTP 401
- [ ] Write a test: successful register/retrieve/save flows each return HTTP 200
