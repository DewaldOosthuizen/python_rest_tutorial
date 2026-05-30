# Proposal: Replace Per-Request Plaintext Password Auth with JWT Token Auth

## Problem

Every authenticated endpoint (`/retrieve`, `/save`) requires the caller to send
the user's plaintext password in the JSON body on every single request.

This is a critical authentication design flaw (OWASP API Security Top 10 — API2:
Broken Authentication) for several reasons:

1. The raw password travels over the wire on every business request — not just at
   login time. Any logging middleware, proxy, or accidental debug output will
   capture it in plaintext.
2. `verify_user()` is tightly coupled to every business operation. Adding a new
   protected endpoint means copy-pasting the same password extraction and
   verification block.
3. There is no concept of a session or token revocation — a compromised credential
   cannot be invalidated without changing the password.

### Affected Code

File: web/app.py

Lines 27-35 — `verify_user()` helper (credential verification coupled to each request):

    def verify_user(username, password):
        if not user_exist(username):
            return False
        user_hashed_pw = users.find({"Username": username})[0]["Password"]
        return bcrypt.checkpw(password.encode('utf8'), user_hashed_pw)

Lines 92-108 — `Retrieve.post()` — extracts `password` from the request body
and calls `verify_user()` before serving the business response:

    def post(self):
        data = request.get_json(silent=True, force=True)
        ...
        username = data.get("username")
        password = data.get("password")            # <-- plaintext password on every request
        if not verify_user(username, password):
            return {"status": 401, "msg": "Invalid credentials"}, 401
        messages = get_user_messages(username)
        return {"status": 200, "obj": messages}, 200

Lines 115-146 — `Save.post()` — identical pattern: extracts `password` from body,
calls `verify_user()`, then performs the business operation.

---

## Solution

### Architecture

1. Add a `/login` endpoint. It accepts `username` + `password` (the one and only
   place credentials travel over the wire), verifies them via the existing
   `verify_user()` helper, and returns a signed JWT containing `{"sub": username}`.

2. Add a `requires_auth` decorator. It reads the `Authorization: Bearer ***`
   header, decodes and validates the JWT, and attaches `request.username` for use
   by the view. Any missing, expired, or tampered token returns 401 immediately.

3. Remove `password` (and `username` where it can be sourced from the token) from
   the request bodies of `/retrieve` and `/save`. Protect those endpoints with
   `@requires_auth`.

4. Add `PyJWT>=2.8.0` to `web/requirements.txt`.

5. Source `JWT_SECRET` from `os.environ["JWT_SECRET"]` — never hardcode it.

---

### Before / After

#### web/requirements.txt

Before:
    Flask==2.2.5
    Werkzeug==2.3.7
    flask-restful==0.3.10
    pymongo==3.12.3
    bcrypt>=4.0
    pytest>=7.0

After (add PyJWT):
    Flask==2.2.5
    Werkzeug==2.3.7
    flask-restful==0.3.10
    pymongo==3.12.3
    bcrypt>=4.0
    PyJWT>=2.8.0
    pytest>=7.0

---

#### web/app.py — imports (top of file, lines 1-7)

Before:
    import os
    import bcrypt
    from flask import Flask, jsonify, request
    from flask_restful import Api, Resource
    from pymongo import MongoClient

After (add jwt and datetime imports):
    import os
    import datetime
    import bcrypt
    import jwt
    from flask import Flask, jsonify, request
    from flask_restful import Api, Resource
    from pymongo import MongoClient

---

#### web/app.py — JWT_SECRET constant (after MONGO_URI block, ~line 16)

Before:
    (nothing)

After (insert after db/users setup):
    SECRET = os.environ["JWT_SECRET"]

---

#### web/app.py — `requires_auth` decorator (new, insert after helper functions ~line 44)

Before:
    (nothing — no auth decorator exists)

After:
    from functools import wraps

    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.removeprefix("Bearer ").strip()
            if not token:
                return jsonify({"status": 401, "msg": "Unauthorized"}), 401
            try:
                payload = jwt.decode(token, SECRET, algorithms=["HS256"])
                request.username = payload["sub"]
            except jwt.PyJWTError:
                return jsonify({"status": 401, "msg": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated

---

#### web/app.py — new `Login` Resource (insert before `Retrieve` class, ~line 87)

Before:
    (no Login resource)

After:
    class Login(Resource):
        """
        Issues a signed JWT on valid credentials.
        POST /login  {username, password}  ->  {status: 200, token: "<jwt>"}
        """

        def post(self):
            data = request.get_json(silent=True, force=True)
            if not data:
                return {"status": 400, "msg": "Request body must be valid JSON"}, 400
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                return {"status": 400, "msg": "username and password are required"}, 400
            if not verify_user(username, password):
                return {"status": 401, "msg": "Invalid credentials"}, 401
            token = jwt.encode(
                {
                    "sub": username,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                SECRET,
                algorithm="HS256",
            )
            return {"status": 200, "token": token}, 200

---

#### web/app.py — `Retrieve.post()` (lines 92-108)

Before:
    def post(self):
        data = request.get_json(silent=True, force=True)
        if not data:
            return {"status": 400, "msg": "Request body must be valid JSON"}, 400
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": 400, "msg": "username and password are required"}, 400
        if not user_exist(username):
            return {"status": 401, "msg": "Invalid credentials"}, 401
        if not verify_user(username, password):
            return {"status": 401, "msg": "Invalid credentials"}, 401
        messages = get_user_messages(username)
        return {"status": 200, "obj": messages}, 200

After (decorator + username from token, no password in body):
    @requires_auth
    def post(self):
        messages = get_user_messages(request.username)
        return {"status": 200, "obj": messages}, 200

---

#### web/app.py — `Save.post()` (lines 115-146)

Before:
    def post(self):
        data = request.get_json(silent=True, force=True)
        if not data:
            return {"status": 400, "msg": "Request body must be valid JSON"}, 400
        username = data.get("username")
        password = data.get("password")
        message = data.get("message")
        if not username or not password:
            return {"status": 400, "msg": "username and password are required"}, 400
        if not message:
            return {"status": 400, "msg": "message is required"}, 400
        if not user_exist(username):
            return {"status": 401, "msg": "Invalid credentials"}, 401
        if not verify_user(username, password):
            return {"status": 401, "msg": "Invalid credentials"}, 401
        messages = get_user_messages(username)
        messages.append(message)
        users.update({"Username": username}, {"$set": {"Messages": messages}})
        return {"status": 200, "msg": "Message has been saved successfully"}, 200

After (decorator + username from token, only message in body):
    @requires_auth
    def post(self):
        data = request.get_json(silent=True, force=True)
        if not data:
            return {"status": 400, "msg": "Request body must be valid JSON"}, 400
        message = data.get("message")
        if not message:
            return {"status": 400, "msg": "message is required"}, 400
        username = request.username
        messages = get_user_messages(username)
        messages.append(message)
        users.update({"Username": username}, {"$set": {"Messages": messages}})
        return {"status": 200, "msg": "Message has been saved successfully"}, 200

---

#### web/app.py — api.add_resource registration (~line 149)

Before:
    api.add_resource(Hello, '/hello')
    api.add_resource(Register, '/register')
    api.add_resource(Retrieve, '/retrieve')
    api.add_resource(Save, '/save')

After (add Login):
    api.add_resource(Hello, '/hello')
    api.add_resource(Register, '/register')
    api.add_resource(Login, '/login')
    api.add_resource(Retrieve, '/retrieve')
    api.add_resource(Save, '/save')
