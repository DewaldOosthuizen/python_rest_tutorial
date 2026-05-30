# Replace In-Request Credential Passing with Token-Based Authentication

## Overview
Every `/retrieve` and `/save` request currently requires the client to transmit a
plaintext password in the JSON body on each call. This pattern exposes credentials in
request logs, browser history, and network traces on every authenticated operation.
The tutorial targets developers learning REST API best practices; teaching
password-per-request as the default undermines that goal. The fix is to introduce a
dedicated `/login` endpoint that issues a short-lived JWT, then protect `/retrieve`
and `/save` with Bearer token verification via Flask-JWT-Extended — eliminating the
password from every non-login request body.

## Issues

### Issue 1 — Password Transmitted on Every Protected Request

**File:** `web/app.py` (lines 92–108, 115–146)

**Problem:** Both `Retrieve.post()` and `Save.post()` extract `password` from the
request body and call `verify_user()` inline. This means the password travels over the
wire and is processed on every single API call, not just at login time.

**Fix:**
```python
# Before — Retrieve.post() (lines 92-108)
def post(self):
    data = request.get_json(silent=True, force=True)
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return {"status": 400, "msg": "username and password are required"}, 400
    if not verify_user(username, password):
        return {"status": 401, "msg": "Invalid credentials"}, 401
    messages = get_user_messages(username)
    return {"status": 200, "obj": messages}, 200

# After — Retrieve.post()
@jwt_required()
def post(self):
    username = get_jwt_identity()
    messages = get_user_messages(username)
    return {"status": 200, "obj": messages}, 200
```

### Issue 2 — No Login Endpoint Exists

**File:** `web/app.py` (line 149 — resource registration block)

**Problem:** There is no dedicated authentication endpoint. Credentials have no
central validation point; auth logic is duplicated across every protected resource.

**Fix:**
```python
# Before — no Login resource exists

# After — add Login resource
class Login(Resource):
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
        token = create_access_token(identity=username)
        return {"status": 200, "access_token": token}, 200

api.add_resource(Login, '/login')
```

### Issue 3 — JWT Library Missing from requirements.txt

**File:** `web/requirements.txt` (line 7 — end of file)

**Problem:** Flask-JWT-Extended is not listed as a dependency. The application will
fail to start after the code changes if the library is not declared.

**Fix:**
```text
# Before
Flask==2.2.5
flask-restful==0.3.10
pymongo==3.12.3
bcrypt>=4.0

# After (add the following line)
Flask-JWT-Extended>=4.5
```

### Issue 4 — JWT Configuration Not Wired Into App

**File:** `web/app.py` (lines 10–11 — app/api initialisation block)

**Problem:** `JWTManager` is not instantiated and `JWT_SECRET_KEY` is not read from
the environment, so token signing cannot function.

**Fix:**
```python
# Before
app = Flask(__name__)
api = Api(app)

# After
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
jwt = JWTManager(app)
api = Api(app)
```

### Issue 5 — README Does Not Document the Authentication Flow

**File:** `README.md` (entire file — authentication section absent)

**Problem:** The README has no documentation of the login flow or token usage. Learners
following the tutorial will not know how to obtain or use a JWT.

**Fix:** Add an "Authentication" section with curl examples:
```markdown
## Authentication

### 1. Register a user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "s3cr3t"}'

### 2. Log in and obtain a token
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "s3cr3t"}'
# Response: {"status": 200, "access_token": "<JWT>"}

### 3. Call a protected endpoint
curl -X POST http://localhost:5000/retrieve \
  -H "Authorization: Bearer <JWT>"

curl -X POST http://localhost:5000/save \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world"}'
```
