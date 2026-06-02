# python_rest_tutorial

[![Tests](https://github.com/DewaldOosthuizen/python_rest_tutorial/actions/workflows/test.yml/badge.svg)](https://github.com/DewaldOosthuizen/python_rest_tutorial/actions/workflows/test.yml)

This is a comprehensive guide and implementation to help developers learn how to create RESTful APIs using Python, Flask, Docker and MongoDB. It demonstrates best practices for 
building scalable and efficient APIs, leveraging Python's capabilities alongside Docker for containerization. The repository serves as an educational 
resource for both beginners and experienced developers looking to refine their skills in REST API development.

Here is an article you can follow to create this project from the beginning:
<https://www.dvt.co.za/news-insights/insights/item/355-restful-web-services-using-python-flask-docker-and-mongodb>

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RVJC5VUM5ZEW8&source=url)
[![License](http://img.shields.io/badge/Licence-MIT-brightgreen.svg)](LICENSE.md)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/53014a434fb340f2afde9853e2314a8a)](https://www.codacy.com/gh/DewaldOosthuizen/python_rest_tutorial/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DewaldOosthuizen/python_rest_tutorial&amp;utm_campaign=Badge_Grade)

## Docker and docker-compose

Inside the root project you can run

```shell
sudo docker-compose build
```

and then run the folowing to start the container and expose the API:

```shell
sudo docker-compose up
```

Once the container is running, you can access it by opening your browser and typing in localhost:5000/hello. This should
display a "Hello World!" message.

There are also other endpoints to test with, and can be found in the article mentioned at the top.

## Using postman

When using postman to test your rest endpoints, be sure to add content-type: application/json to your headers.

If you don't want to specify content type in the header then you can use
request.get_json(force=True) inside your endpoint when fetching the data from the request
to force the data to be read as JSON.

For reference have a look at <https://github.com/DewaldOosthuizen/python_rest_tutorial/issues/1>

## Environment Variables

The application is configured via environment variables. Copy the example file to get started:

```shell
cp .env.example .env
```

| Variable   | Default                   | Description                                                                      |
|------------|---------------------------|----------------------------------------------------------------------------------|
| MONGO_URI  | mongodb://my_db:27017/    | MongoDB connection string. Override with credentials for remote/secured instances.|
| JWT_SECRET | *(required)*              | Secret key used to sign and verify JWT tokens. Must be a long random string. Never hardcode or commit this value. |


## Authentication

The API uses JWT (JSON Web Token) bearer authentication.

### 1. Obtain a token — POST /login

Send your credentials once to receive a signed token:

```shell
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}'
```

Response (200 OK):

```json
{"status": 200, "token": "<signed-jwt>"}
```

On invalid credentials the endpoint returns 401 with `{"status": 401, "msg": "Invalid credentials"}`.

### 2. Call protected endpoints — Authorization: Bearer

Pass the token in the `Authorization` header on every call to `/retrieve` and `/save`:

```shell
# Retrieve messages
curl -X POST http://localhost:5000/retrieve \
  -H "Authorization: Bearer <token>"

# Save a message
curl -X POST http://localhost:5000/save \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

Missing, expired, or tampered tokens return 401 Unauthorized.


## Running the tests

```bash
cd web
pip install -r requirements.txt
pytest
```

## Dependencies

All runtime and development dependencies are pinned to exact versions in web/requirements.txt
to ensure reproducible builds and avoid unexpected breakage from upstream changes.

| Package        | Version        | Role               |
|----------------|----------------|--------------------|
| Flask          | 2.2.5          | Web framework      |
| Werkzeug       | 2.3.7          | WSGI utilities     |
| flask-restful  | 0.3.10         | REST API helpers   |
| pymongo        | 4.6.3          | MongoDB driver     |
| bcrypt         | 4.0.1          | Password hashing   |
| PyJWT          | >=2.8.0        | JWT authentication |
| pytest         | 9.0.3          | Test runner (dev)  |

Rationale: Floating version specifiers (>=) allow pip to silently pull in
breaking releases. Exact pins (==) guarantee that every environment — local,
CI, and Docker — runs the same code.

Upgrade procedure:
1. Update the version number in web/requirements.txt.
2. Rebuild/reinstall: pip install -r web/requirements.txt
3. Run the full test suite: cd web && pytest
4. If all tests pass, commit the updated requirements.txt.
