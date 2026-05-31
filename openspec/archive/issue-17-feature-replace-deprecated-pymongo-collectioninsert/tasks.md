# Tasks: Issue #17

## Verification

- [ ] Run the full test suite against PyMongo 4.x to confirm `users.insert_one` and `users.update_one` work correctly and no `AttributeError` is raised.
- [ ] Confirm `web/app.py` line 99 uses `insert_one` (not legacy `insert`).
- [ ] Confirm `web/app.py` lines 153–159 use `update_one` (not legacy `update`).

## Dependency Upgrades

- [ ] Bump `pymongo` pin in `web/requirements.txt` from `4.6.3` to `4.7.2`.
- [ ] Evaluate bumping `Flask` from `2.2.5` to `3.0.3` — check for breaking changes in Flask 3.x affecting route registration, `jsonify`, and `request` usage in `web/app.py`.
- [ ] Evaluate bumping `bcrypt` from `4.0.1` to `4.1.3` — verify password hashing and verification calls remain compatible.
- [ ] Confirm `Werkzeug` version remains compatible with the chosen Flask version after upgrade.
- [ ] Run full test suite after each dependency bump to catch regressions early.

## Docker

- [ ] Decide whether to upgrade `web/Dockerfile` base image from `python:3.11-slim` to `python:3.12-slim` (optional, non-critical).
- [ ] If upgrading to 3.12-slim, rebuild and smoke-test the Docker image end-to-end.

## Documentation & Closure

- [ ] Update `web/requirements.txt` with final pinned versions.
- [ ] Close issue #17 acceptance criteria with test evidence (CI output or local run log).
