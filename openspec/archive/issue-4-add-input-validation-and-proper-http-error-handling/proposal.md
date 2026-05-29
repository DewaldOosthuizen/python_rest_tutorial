# Add Input Validation and Proper HTTP Error Handling to All Endpoints

## Overview

All three business endpoints (`/register`, `/retrieve`, `/save`) in `web/app.py`
access `request.get_json()` keys directly via bracket notation with no null or
type guards. A missing or malformed JSON body, or any absent required field,
raises an unhandled `KeyError` or `TypeError`, resulting in a raw HTTP 500
response that leaks a Python stack trace to the client. In addition, all current
error responses return HTTP 200 with a non-200 `status` field in the body — a
violation of HTTP semantics. As an educational codebase, these patterns actively
teach incorrect practices. The fix standardises input validation, maps failures
to correct HTTP status codes (400, 401), and ensures no Python tracebacks ever
reach the client.

---

## Issues

### Issue 1 — Register.post() has no JSON body or field validation

**File:** `web/app.py` (lines 64–90)

**Problem:** `data = request.get_json()` can return `None` if the body is
missing or the `Content-Type` header is not `application/json`. The subsequent
direct key access `data["username"]` and `data["password"]` then raises
`TypeError` (NoneType not subscriptable) or `KeyError`, both of which produce
an HTTP 500 with a stack trace. The existing error response for a duplicate user
also returns HTTP 200.

**Fix:**
```python
# Before
def post(self):
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    if user_exist(username):
        return jsonify(invalid_user_json)  # HTTP 200, status 301 in body
    ...
    return jsonify(ret_json)  # HTTP 200

# After
def post(self):
    data = request.get_json()
    if not data:
        return jsonify({"status": 400, "msg": "Request body must be valid JSON"}), 400
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": 400, "msg": "username and password are required"}), 400
    if user_exist(username):
        return jsonify({"status": 400, "msg": "User already exists"}), 400
    ...
    return jsonify({"status": 200, "msg": "Registration successful"}), 200
```

---

### Issue 2 — Retrieve.post() has no JSON body or field validation

**File:** `web/app.py` (lines 98–124)

**Problem:** Same bracket-access pattern as Register. Additionally,
`invalid_user_json` and `invalid_password_json` are returned with HTTP 200.
Authentication failures (wrong user or wrong password) must return HTTP 401,
not 200.

**Fix:**
```python
# Before
def post(self):
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    if not user_exist(username):
        return jsonify(invalid_user_json)   # HTTP 200
    if not correct_pw:
        return jsonify(invalid_password_json)  # HTTP 200
    ...

# After
def post(self):
    data = request.get_json()
    if not data:
        return jsonify({"status": 400, "msg": "Request body must be valid JSON"}), 400
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": 400, "msg": "username and password are required"}), 400
    if not user_exist(username):
        return jsonify({"status": 401, "msg": "Invalid credentials"}), 401
    if not verify_user(username, password):
        return jsonify({"status": 401, "msg": "Invalid credentials"}), 401
    ...
    return jsonify({"status": 200, "obj": messages}), 200
```

Note: both "user not found" and "wrong password" must return the same 401
message to prevent user enumeration.

---

### Issue 3 — Save.post() has no JSON body or field validation

**File:** `web/app.py` (lines 132–178)

**Problem:** Same bracket-access crash on missing body or missing fields.
The existing empty-message check returns status 303 (a redirect code) over
HTTP 200, which is semantically incorrect — it should be 400. Authentication
failures again return HTTP 200.

**Fix:**
```python
# Before
def post(self):
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    message = data["message"]
    if not user_exist(username):
        return jsonify(invalid_user_json)   # HTTP 200
    if not correct_pw:
        return jsonify(invalid_password_json)  # HTTP 200
    if not message:
        return jsonify({"status": 303, "msg": "Please supply a valid message"})  # HTTP 200

# After
def post(self):
    data = request.get_json()
    if not data:
        return jsonify({"status": 400, "msg": "Request body must be valid JSON"}), 400
    username = data.get("username")
    password = data.get("password")
    message = data.get("message")
    if not username or not password:
        return jsonify({"status": 400, "msg": "username and password are required"}), 400
    if not message:
        return jsonify({"status": 400, "msg": "message is required"}), 400
    if not user_exist(username):
        return jsonify({"status": 401, "msg": "Invalid credentials"}), 401
    if not verify_user(username, password):
        return jsonify({"status": 401, "msg": "Invalid credentials"}), 401
    ...
    return jsonify({"status": 200, "msg": "Message has been saved successfully"}), 200
```

---

### Issue 4 — Shared error JSON variables do not carry correct HTTP status codes

**File:** `web/app.py` (lines ~14–48, module-level constants)

**Problem:** `invalid_user_json` and `invalid_password_json` are defined as
module-level dicts and returned with `jsonify(...)` but no explicit HTTP status
tuple, so Flask defaults to 200. These constants must either be removed in
favour of inline responses (recommended) or extended to include the HTTP status
as a second return value. Using inline responses per endpoint is cleaner and
makes each endpoint self-documenting.

**Fix:** Remove `invalid_user_json` and `invalid_password_json` module-level
constants and replace all usages with explicit inline `return jsonify({...}), STATUS`
tuples as shown in Issues 1–3 above.
