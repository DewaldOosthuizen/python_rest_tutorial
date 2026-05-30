# Tasks: Pin All Dependency Versions

## Dependencies — requirements.txt

- [ ] Pin `bcrypt` to an exact version: change `bcrypt>=4.0` to `bcrypt==4.0.1` (file: `web/requirements.txt` line 5)
- [ ] Pin `pytest` to an exact version: change `pytest>=7.0` to `pytest==7.4.4` (file: `web/requirements.txt` line 7)
- [ ] Verify all other entries (`Flask==2.2.5`, `Werkzeug==2.3.7`, `flask-restful==0.3.10`, `pymongo==3.12.3`) remain exact pins and have not drifted (file: `web/requirements.txt`)

## Docker Base Image

- [ ] Replace `FROM python:3` with `FROM python:3.11-slim` (file: `web/Dockerfile` line 2)
- [ ] Confirm `docker-compose build` completes without error after image change
- [ ] Confirm `docker-compose up && curl localhost:<port>/hello` returns a valid response after the image change

## pymongo API Migration

- [ ] Replace `users.insert({...})` with `users.insert_one({...})` in the Register resource (file: `web/app.py` line 79)
- [ ] Replace `users.update({...}, {...})` with `users.update_one({...}, {...})` in the AddMessage resource (file: `web/app.py` line 138)
- [ ] Verify no other `Collection.insert()`, `Collection.update()`, or `Collection.remove()` calls remain in `web/app.py` (search for deprecated API surface)

## Documentation

- [ ] Add a "Dependencies" section to `README.md` listing the pinned versions
- [ ] Document the rationale for pinning (reproducible builds, pymongo 4.x breaking changes)
- [ ] Document the upgrade procedure: edit `requirements.txt`, run `pytest`, rebuild Docker image with `docker-compose build --no-cache`

## Verification

- [ ] Run `pytest` inside the web container (or locally with a running MongoDB) — all tests pass
- [ ] Run `docker-compose build && docker-compose up` from scratch — no errors
- [ ] Confirm `/hello`, `/register`, and `/addmessage` endpoints respond correctly via manual smoke test or integration test
