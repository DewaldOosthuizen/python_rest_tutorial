# Tasks: Replace In-Request Credential Passing with Token-Based Authentication

## Dependencies

- [ ] Add `Flask-JWT-Extended>=4.5` to `web/requirements.txt`

## Application Wiring

- [ ] Import `JWTManager`, `create_access_token`, `jwt_required`, `get_jwt_identity` from `flask_jwt_extended` in `web/app.py`
- [ ] Set `app.config["JWT_SECRET_KEY"]` from `os.environ.get("JWT_SECRET_KEY", "change-me-in-production")` in `web/app.py` (after `app = Flask(__name__)`)
- [ ] Instantiate `JWTManager(app)` in `web/app.py` (after setting `JWT_SECRET_KEY`)

## New Login Endpoint

- [ ] Add `Login(Resource)` class with `post()` method that validates credentials via `verify_user()` and returns a JWT via `create_access_token()` (file: `web/app.py`)
- [ ] Register `Login` resource at `/login` route via `api.add_resource(Login, '/login')` (file: `web/app.py`)

## Protect Existing Resources

- [ ] Decorate `Retrieve.post()` with `@jwt_required()` (file: `web/app.py`, line ~92)
- [ ] Remove `username` and `password` extraction from `Retrieve.post()` request body; obtain identity via `get_jwt_identity()` (file: `web/app.py`)
- [ ] Remove inline `verify_user()` call and related credential validation from `Retrieve.post()` (file: `web/app.py`)
- [ ] Decorate `Save.post()` with `@jwt_required()` (file: `web/app.py`, line ~115)
- [ ] Remove `username` and `password` extraction from `Save.post()` request body; obtain identity via `get_jwt_identity()` (file: `web/app.py`)
- [ ] Remove inline `verify_user()` call and related credential validation from `Save.post()` (file: `web/app.py`)

## Cleanup

- [ ] Verify `verify_user()` helper is still used only by `Login.post()` after the refactor; remove it only if the helper is fully superseded (file: `web/app.py`)

## Documentation

- [ ] Add "Authentication" section to `README.md` documenting: register, login (obtain token), and call protected endpoints with Bearer token
- [ ] Include curl examples for `/register`, `/login`, `/retrieve`, and `/save` in `README.md`

## Tests

- [ ] Update existing tests for `/retrieve` to POST with `Authorization: Bearer <token>` header instead of password in body (file: `web/tests/` or wherever test suite lives)
- [ ] Update existing tests for `/save` to POST with `Authorization: Bearer <token>` header instead of password in body
- [ ] Add test for `POST /login` with valid credentials — expects 200 and `access_token` in response
- [ ] Add test for `POST /login` with invalid credentials — expects 401
- [ ] Add test for `POST /retrieve` with missing/invalid token — expects 401 (JWT error response)
- [ ] Add test for `POST /save` with missing/invalid token — expects 401 (JWT error response)
