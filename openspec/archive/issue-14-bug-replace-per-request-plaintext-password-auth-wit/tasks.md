# Tasks: Issue #14 — Replace Per-Request Plaintext Password Auth with JWT

## Dependencies

- [ ] Add `PyJWT>=2.8.0` to `web/requirements.txt`
- [ ] Verify `PyJWT` is installable in the Docker/local environment (`pip install PyJWT`)

## Environment

- [ ] Document `JWT_SECRET` environment variable in README or .env.example
- [ ] Ensure `JWT_SECRET` is injected via docker-compose or runtime environment — never committed to source

## web/app.py — Imports and Constants

- [ ] Add `import datetime` at the top of `web/app.py`
- [ ] Add `import jwt` at the top of `web/app.py`
- [ ] Add `from functools import wraps` at the top of `web/app.py`
- [ ] Add `SECRET = os.environ["JWT_SECRET"]` after the MongoDB setup block (~line 16)

## web/app.py — requires_auth Decorator

- [ ] Implement `requires_auth(f)` decorator in `web/app.py` after the helper functions (~line 44)
  - [ ] Extract Bearer token from `Authorization` header
  - [ ] Return 401 if header is missing or empty
  - [ ] Decode token using `jwt.decode(token, SECRET, algorithms=["HS256"])`
  - [ ] Return 401 on any `jwt.PyJWTError` (expired, invalid signature, malformed)
  - [ ] Set `request.username = payload["sub"]` on success

## web/app.py — Login Resource

- [ ] Implement `Login(Resource)` class in `web/app.py` (before `Retrieve` class)
  - [ ] `POST /login` accepts `{"username": str, "password": str}`
  - [ ] Return 400 if body is not valid JSON
  - [ ] Return 400 if `username` or `password` is missing
  - [ ] Return 401 if `verify_user(username, password)` returns False
  - [ ] On success: encode JWT with `{"sub": username, "exp": utcnow + 1 hour}` using HS256
  - [ ] Return `{"status": 200, "token": "<jwt>"}` with HTTP 200
- [ ] Register route: `api.add_resource(Login, '/login')` in the resource registration block

## web/app.py — Retrieve Resource

- [ ] Apply `@requires_auth` decorator to `Retrieve.post()`
- [ ] Remove `data = request.get_json(...)` block (no longer needed)
- [ ] Remove `username = data.get("username")` and `password = data.get("password")`
- [ ] Remove `verify_user()` call and all credential checks
- [ ] Replace `username` references with `request.username` (set by decorator)
- [ ] Ensure only `get_user_messages(request.username)` and the return remain in the method body

## web/app.py — Save Resource

- [ ] Apply `@requires_auth` decorator to `Save.post()`
- [ ] Remove `username = data.get("username")` and `password = data.get("password")`
- [ ] Remove the `if not username or not password` guard and `verify_user()` call
- [ ] Keep `data = request.get_json(...)` block (still needed for `message`)
- [ ] Keep `message = data.get("message")` and its 400 guard
- [ ] Replace `username` references with `request.username` (set by decorator)

## Testing

- [ ] Update any existing tests for `/retrieve` that sent `username`+`password` in the body:
  - [ ] Remove `password` from test request body
  - [ ] Add a valid JWT `Authorization: Bearer ***   header to the test request
- [ ] Update any existing tests for `/save` similarly
- [ ] Add test: `POST /login` with valid credentials returns 200 and a `token` field
- [ ] Add test: `POST /login` with wrong password returns 401
- [ ] Add test: `POST /retrieve` with no Authorization header returns 401
- [ ] Add test: `POST /retrieve` with an expired JWT returns 401
- [ ] Add test: `POST /retrieve` with a tampered/invalid JWT signature returns 401
- [ ] Add test: `POST /save` with a valid JWT saves the message and returns 200
- [ ] Add test: `POST /save` with an expired JWT returns 401

## Cleanup / Final Checks

- [ ] Confirm `verify_user()` helper is still used only by `Login.post()` — remove if orphaned
- [ ] Run full test suite: `pytest` — all tests green
- [ ] Confirm no `password` field appears in `/retrieve` or `/save` request handling
- [ ] Confirm `JWT_SECRET` has no hardcoded fallback value in source code
- [ ] Update README or API docs to document the new `/login` endpoint and Bearer token usage
