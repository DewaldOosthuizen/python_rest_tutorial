# python_rest_tutorial — Copilot Instructions

## Project Overview

Educational REST API built with Python, Flask, Docker, and MongoDB.
Stack: Flask 3.1.3, flask-restful, pymongo 4.7.2, bcrypt, PyJWT, pytest, Ruff, Docker + docker-compose.

Reference article:
https://www.dvt.co.za/news-insights/insights/item/355-restful-web-services-using-python-flask-docker-and-mongodb

## Repository Structure

    web/                  Flask application source (app.py) + Dockerfile
    web/requirements.txt  Pinned runtime and dev dependencies (includes ruff, pytest)
    web/tests/            Unit tests for the Flask app
    tests/                Config-level and API-contract tests
    scripts/lint.sh       Local lint script — mirrors CI exactly
    docker-compose.yml    Service definitions: web app + MongoDB
    .env.example          Environment variable template
    pyproject.toml        Ruff linting and formatting config

## Environment Variables

| Variable   | Default                | Description                                              |
|------------|------------------------|----------------------------------------------------------|
| MONGO_URI  | mongodb://my_db:27017/ | MongoDB connection string                                |
| JWT_SECRET | (required)             | JWT signing secret. Must be long and random. Never commit.|

## Authentication Flow

1. Register:  POST /register  {"username": "...", "password": "..."}
2. Login:     POST /login     {"username": "...", "password": "..."} → returns {"token": "..."}
3. Protected: POST /retrieve or /save with header Authorization: Bearer <token>

Tokens expire after 1 hour. Missing/expired/tampered tokens return 401.

## Running Locally

    cp .env.example .env          # set JWT_SECRET
    sudo docker-compose build
    sudo docker-compose up
    curl http://localhost:5000/hello   # → "Hello World!"

## Running Tests

    pip install -r web/requirements.txt
    pytest -v
    # Runs web/tests/ (unit) and tests/ (config + contract)

## Linting

    ./scripts/lint.sh            # check only — same as CI
    ./scripts/lint.sh --fix      # auto-fix then check

Ruff config is in pyproject.toml. Rules: E, F, I (pycodestyle, Pyflakes, isort).
Line length: 120. Both web/ and tests/ are in scope.

## CI Pipeline

Defined in .github/workflows/ci.yml. Two sequential jobs on every push/PR:

    lint  →  test

lint: ruff check + ruff format --check
test: pytest -v (only runs if lint passes)

## Code Conventions

- All imports must be sorted (ruff I rules enforced in CI).
- Use insert_one / update_one (PyMongo 4.x API — not deprecated insert/update).
- JWT datetime must use timezone-aware datetimes: datetime.datetime.now(timezone.utc).
- Passwords are bcrypt-hashed — never stored in plaintext.
- All endpoints return {"status": <code>, ...} JSON bodies.

## Code Exploration

### codegraph

.codegraph/ is present. Use it first for symbol lookup and call tracing.

    codegraph context "<task description>" -p .
    codegraph query "<ClassName or function>" -p .
    codegraph affected <changed-files> -p .
    codegraph sync .

### understand-anything

.understand-anything/knowledge-graph.json is present. Use for architecture questions.

    skill: understand-chat

Decision order for code tasks:
  1. codegraph context  — which symbols matter?
  2. understand-anything — where in the architecture does this live?
  3. Read raw source — only the 1-2 files that actually matter.
