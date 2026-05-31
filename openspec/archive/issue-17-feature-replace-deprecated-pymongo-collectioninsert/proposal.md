# Proposal: Issue #17 — Replace Deprecated PyMongo collection.insert() and collection.update() Calls

## Overview

PyMongo 4.x removed the legacy `Collection.insert()` and `Collection.update()` methods. Any
application using these calls against a modern PyMongo installation raises `AttributeError` at
runtime. A code audit of `web/app.py` confirms that **both deprecated calls have already been
replaced** with their modern equivalents (`insert_one` and `update_one`) in the current working
tree. However, the `requirements.txt` version pin for pymongo (`4.6.3`) is slightly behind the
latest stable `4.7.2` recommended by the issue, and `web/Dockerfile` already uses `python:3.11-slim`
(a pinned minor version). This spec documents the remaining gap and confirms the implementation
state so the acceptance criteria can be formally closed.

## Issues

### Issue 1

**File:** `web/app.py` (line 99)
**Problem:** Issue #17 reported `users.insert({...})` at line 79 (legacy PyMongo 3.x API). This
call raises `AttributeError` under PyMongo 4.x.
**Fix:** Already resolved in the current working tree — the call reads `users.insert_one({...})`
at line 99. No code change required; verify via test run against PyMongo 4.x to formally close
this criterion.

### Issue 2

**File:** `web/app.py` (lines 153–159)
**Problem:** Issue #17 reported `users.update({...}, {"$set": {...}})` at lines 165–171 (legacy
PyMongo 3.x API). This call raises `AttributeError` under PyMongo 4.x.
**Fix:** Already resolved in the current working tree — the call reads `users.update_one({...},
{"$set": {...}})` at lines 153–159. No code change required; verify via test run.

### Issue 3

**File:** `web/requirements.txt`
**Problem:** `pymongo==4.6.3` is pinned but is behind the recommended `4.7.2`. All other
direct dependencies (`Flask==2.2.5`, `Werkzeug==2.3.7`, `bcrypt==4.0.1`) are pinned to older
stable versions. The issue recommends aligning to: `pymongo==4.7.2`, `bcrypt==4.1.3`,
`Flask==3.0.3`, `flask-restful==0.3.10`.
**Fix:** Bump pinned versions in `requirements.txt` to match the recommended set. Verify no
breaking changes are introduced — Flask 3.x has minor API changes vs Flask 2.x that should be
validated against the existing route and resource classes.

### Issue 4

**File:** `web/Dockerfile`
**Problem:** Issue #17 flagged an unpinned `FROM python:3` base image. The current Dockerfile
already uses `FROM python:3.11-slim`, which satisfies the pinning requirement at the minor
version level.
**Fix:** No change required. Optionally upgrade to `python:3.12-slim` for alignment with the
issue's recommendation, but this is non-critical and carries upgrade risk.
