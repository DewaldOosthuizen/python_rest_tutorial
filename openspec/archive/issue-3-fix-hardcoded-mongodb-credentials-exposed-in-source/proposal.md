# Fix Hardcoded MongoDB Credentials Exposed in Source Code

## Overview

`web/app.py` constructs a `MongoClient` with a connection string literal baked
directly into source code. Even though the current URI does not include a
password (the redacted form in the issue description suggests a prior iteration
did), shipping any infrastructure URI as a literal is a CWE-798 violation and
teaches dangerous habits to learners of this tutorial repository.  The fix
replaces the hardcoded URI with an `os.environ` lookup, wires the variable into
`docker-compose.yml`, and adds supporting hygiene files (`.env.example`,
`.gitignore`, README update) so the environment-variable pattern is
self-documenting.

---

## Issues

### Issue 1 — Hardcoded MongoDB URI in web/app.py

**File:** `web/app.py` (line 12)

**Problem:** The MongoDB connection string is a string literal. Any credentials
embedded now or in future commits are permanently visible in version history to
anyone with read access, violating the principle of least exposure.

**Fix:**

```python
# Before (line 12)
client = MongoClient("mongodb://my_db:27017")

# After
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://my_db:27017/")
client = MongoClient(MONGO_URI)
```

`os.environ.get` keeps a safe default so the app still starts in plain
`docker-compose` mode without a `.env` file, while allowing credentials to be
injected via environment in any other deployment.

---

### Issue 2 — No environment variable plumbing in docker-compose.yml

**File:** `docker-compose.yml` (lines 1–11 — `web` service block)

**Problem:** The `web` service has no `environment:` section, so there is no
documented or working mechanism to pass `MONGO_URI` into the container at
runtime.

**Fix:**

```yaml
# Before
services:
  web:
    build: "./web"
    ports:
      - "5000:5000"
    links:
      - my_db

# After
services:
  web:
    build: "./web"
    ports:
      - "5000:5000"
    links:
      - my_db
    environment:
      - MONGO_URI=mongodb://my_db:27017/
```

The default value mirrors the `os.environ.get` fallback in `app.py`, so the
compose stack works out of the box without a `.env` file.

---

### Issue 3 — No .env.example documenting required variables

**File:** `.env.example` (new file, project root)

**Problem:** No canonical list of runtime environment variables exists. New
contributors have no reference for what needs to be set.

**Fix:** Create `.env.example` at the project root:

```dotenv
# MongoDB connection string.
# For local docker-compose usage the default is sufficient.
# Override with credentials for remote or secured MongoDB instances.
MONGO_URI=mongodb://my_db:27017/
```

---

### Issue 4 — No .gitignore; .env files would be committed accidentally

**File:** `.gitignore` (new file, project root)

**Problem:** The repository has no `.gitignore`. If a developer creates a `.env`
file with real credentials for local testing, there is nothing preventing an
accidental `git add .` from committing it.

**Fix:** Create `.gitignore` at the project root with at minimum:

```gitignore
# Environment files — never commit real credentials
.env
.env.local
.env.*.local

# Python artifacts
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
```

---

### Issue 5 — README does not explain environment variable setup

**File:** `README.md` (or equivalent top-level readme)

**Problem:** Learners following the tutorial have no guidance on how to
configure `MONGO_URI`, what `.env.example` is for, or how to run the stack with
custom credentials.

**Fix:** Add an "Environment Variables" section to the README:

```markdown
## Environment Variables

| Variable    | Default                   | Description                          |
|-------------|---------------------------|--------------------------------------|
| `MONGO_URI` | `mongodb://my_db:27017/`  | Full MongoDB connection string.      |

Copy `.env.example` to `.env` and adjust values before running:

    cp .env.example .env
    # edit .env as needed
    docker-compose up
```
