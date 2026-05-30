# Pin All Dependency Versions

## Overview

`web/requirements.txt` mixes exact pins, a range pin (`bcrypt>=4.0`), and a
loose dev-only range (`pytest>=7.0`). `web/Dockerfile` pulls an unversioned
`python:3` base image. Together these make builds non-deterministic: a fresh
`docker-compose build` on a new machine or in CI may silently install different
versions, causing runtime failures. The most acute risk is `pymongo`: the code
uses the deprecated `Collection.insert()` and `Collection.update()` APIs (removed
in pymongo 4.x), so any bump past 3.x breaks registration and messaging at
runtime. All version specifiers must be pinned to exact known-good values, and
the base image must be replaced with a pinned slim variant.

## Issues

### Issue 1 — bcrypt pinned with a range instead of an exact version

**File:** `web/requirements.txt` (line 5)
**Problem:** `bcrypt>=4.0` allows any future major release. A bcrypt 5.x breaking
change would silently break password hashing.
**Fix:**
```
# Before
bcrypt>=4.0

# After
bcrypt==4.0.1
```

### Issue 2 — pytest pinned with a range instead of an exact version

**File:** `web/requirements.txt` (line 7)
**Problem:** `pytest>=7.0` allows any future major release. A pytest 9.x API
change could break the test suite without warning.
**Fix:**
```
# Before
pytest>=7.0

# After
pytest==7.4.4
```

### Issue 3 — Unpinned Python base image in Dockerfile

**File:** `web/Dockerfile` (line 2)
**Problem:** `FROM python:3` resolves to the latest Python 3.x at build time.
Minor or patch-level Python releases can change stdlib behaviour, SSL defaults,
or pip resolver logic, making builds non-reproducible.
**Fix:**
```dockerfile
# Before
FROM python:3

# After
FROM python:3.11-slim
```

Using the `-slim` variant also reduces image size by ~60 % compared to the
full Debian-based image.

### Issue 4 — Deprecated pymongo Collection.insert() call

**File:** `web/app.py` (line 79)
**Problem:** `Collection.insert()` was removed in pymongo 4.x. With the current
exact pin of `pymongo==3.12.3` the code works, but any accidental upgrade (e.g.
a developer running `pip install pymongo` without pinning) silently breaks
registration. The API should be migrated to `insert_one()` now so a future
controlled upgrade to pymongo 4.x does not require a separate emergency patch.
**Fix:**
```python
# Before
users.insert({
    "Username": username,
    "Password": hashed_pw,
    "Messages": []
})

# After
users.insert_one({
    "Username": username,
    "Password": hashed_pw,
    "Messages": []
})
```

### Issue 5 — Deprecated pymongo Collection.update() call

**File:** `web/app.py` (line 138)
**Problem:** `Collection.update()` was removed in pymongo 4.x for the same
reason as `insert()`. Same risk and same migration rationale as Issue 4.
**Fix:**
```python
# Before
users.update({
    "Username": username
}, {
    "$set": {
        "Messages": messages
    }
})

# After
users.update_one({
    "Username": username
}, {
    "$set": {
        "Messages": messages
    }
})
```

### Issue 6 — README does not document pinned versions or upgrade procedure

**File:** `README.md`
**Problem:** New contributors have no guidance on which versions are in use or
how to update them safely. Without this, the typical reaction to a "pip install"
failure is to remove version pins rather than perform a deliberate upgrade.
**Fix:** Add a "Dependencies" section to `README.md` that lists the pinned
versions, explains why they are pinned, and describes the upgrade procedure
(edit `requirements.txt`, run tests, rebuild Docker image).
