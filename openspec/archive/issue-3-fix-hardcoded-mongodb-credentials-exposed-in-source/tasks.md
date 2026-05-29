# Tasks: Fix Hardcoded MongoDB Credentials Exposed in Source Code

## Security Fixes

- [ ] Add `import os` at the top of `web/app.py` (file: `web/app.py`)
- [ ] Replace line 12 hardcoded `MongoClient("mongodb://my_db:27017")` with
      `MONGO_URI = os.environ.get("MONGO_URI", "mongodb://my_db:27017/")` and
      `client = MongoClient(MONGO_URI)` (file: `web/app.py`)

## Configuration

- [ ] Add an `environment:` block to the `web` service in `docker-compose.yml`
      with `MONGO_URI=mongodb://my_db:27017/` (file: `docker-compose.yml`)

## Hygiene Files

- [ ] Create `.env.example` at the project root documenting the `MONGO_URI`
      variable with a safe default value and explanatory comment
      (file: `.env.example`)
- [ ] Create `.gitignore` at the project root; include `.env`, `.env.local`,
      `__pycache__/`, `*.pyc`, and common IDE directories
      (file: `.gitignore`)

## Documentation

- [ ] Add an "Environment Variables" section to `README.md` with a table of
      all required variables, their defaults, and a `cp .env.example .env`
      quick-start instruction (file: `README.md`)

## Git History (post-implementation, manual step)

- [ ] Run `git filter-repo --replace-text <(echo "XXXXXXXX==>REDACTED")`
      (or equivalent) to purge any prior commit that contained a real credential
      in the connection string; force-push and rotate any exposed secrets
      (out-of-band — not automated by this changeset)
