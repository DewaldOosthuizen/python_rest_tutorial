# DewaldOosthuizen/python_rest_tutorial

This file instructs AI agents (Hermes, GitHub Copilot, Codex, etc.) on how
to orient themselves in this repository efficiently.

## Project Overview

A comprehensive educational repository demonstrating how to build RESTful APIs
using Python, Flask, Docker, and MongoDB. Covers best practices for scalable
API design, containerisation, JWT authentication, password hashing, and testing.

Reference article: https://www.dvt.co.za/news-insights/insights/item/355-restful-web-services-using-python-flask-docker-and-mongodb

Stack: Flask 2.2.5, flask-restful, pymongo, bcrypt, PyJWT, pytest, Docker + docker-compose, MongoDB.

## Repository Structure

    web/              Python application source and tests
    web/requirements.txt  Pinned runtime + dev dependencies
    docker-compose.yml    Service definitions (app + MongoDB)
    .env.example          Environment variable template

## Getting Started

Copy environment config:

    cp .env.example .env

Build and start containers:

    sudo docker-compose build
    sudo docker-compose up

Health check — open http://localhost:5000/hello (returns "Hello World!").

## Environment Variables

| Variable   | Default                | Description                                                     |
|------------|------------------------|-----------------------------------------------------------------|
| MONGO_URI  | mongodb://my_db:27017/ | MongoDB connection string.                                      |
| JWT_SECRET | (required)             | Secret key for signing/verifying JWT tokens. Never commit this. |

## Authentication

The API uses JWT bearer tokens.

Obtain a token:

    curl -X POST http://localhost:5000/login \
      -H "Content-Type: application/json" \
      -d '{"username": "alice", "password": "secret"}'

Response: {"status": 200, "token": "<signed-jwt>"}

Pass the token on protected endpoints (/retrieve, /save):

    curl -X POST http://localhost:5000/retrieve \
      -H "Authorization: Bearer <token>"

Missing, expired, or tampered tokens return 401 Unauthorized.

## Running Tests

    cd web
    pip install -r requirements.txt
    pytest

## Postman

Add Content-Type: application/json to request headers, or use
request.get_json(force=True) in endpoints to skip the header requirement.
See https://github.com/DewaldOosthuizen/python_rest_tutorial/issues/1 for context.

## Dependency Management

All dependencies are exact-pinned in web/requirements.txt for reproducible builds.

Upgrade procedure:
1. Update the version in web/requirements.txt.
2. Reinstall: pip install -r web/requirements.txt
3. Run tests: cd web && pytest
4. Commit the updated requirements.txt.

<!-- graph-tools-start -->

## Code Exploration

### understand-anything

.understand-anything/knowledge-graph.json is present.
Use it for layered architecture questions (layers, communities, entry points).

    # Launch the interactive dashboard
    cd ~/.understand-anything-plugin/packages/dashboard
    GRAPH_DIR=$(pwd) npx vite --host 127.0.0.1

For prose questions load the skill:

    skill: understand-chat

### codegraph

.codegraph/ is present. Use it FIRST for symbol lookup, call tracing,
or targeted context gathering before opening source files.

    codegraph context "<task description>" -p .   # focused file+symbol context
    codegraph query "<ClassName or function>" -p . # where is X defined / used
    codegraph affected <changed-files> -p .        # which tests are affected
    codegraph sync .                               # after any code change

Decision order for code tasks:
  1. codegraph context       — which symbols matter?
  2. understand-anything     — where in the architecture does this live?
  3. Read raw source         — only the 1-2 files that actually matter.

### graphify

graphify-out/ not yet generated for this repo.

<!-- graph-tools-end -->
