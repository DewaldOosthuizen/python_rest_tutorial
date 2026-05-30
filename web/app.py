# import functools
import os
import bcrypt

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
# print = functools.partial(print, flush=True)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "change-me-in-production-32chars!!")
jwt = JWTManager(app)
api = Api(app)


@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return {"status": 401, "msg": reason}, 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return {"status": 401, "msg": reason}, 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return {"status": 401, "msg": "Token has expired"}, 401

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://my_db:27017/")
client = MongoClient(MONGO_URI)
db = client.projectDB
users = db["Users"]

"""
HELPER FUNCTIONS
"""


def user_exist(username):
    return users.find({"Username": username}).count() > 0


def verify_user(username, password):
    if not user_exist(username):
        return False

    user_hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    return bcrypt.checkpw(password.encode('utf8'), user_hashed_pw)


def get_user_messages(username):
    # get the messages
    return users.find({
        "Username": username,
    })[0]["Messages"]


"""
RESOURCES
"""


class Hello(Resource):
    """
    This is the Hello resource class
    """

    def get(self):
        return "Hello World!"

class Register(Resource):
    """
    This is the Register resource class
    """

    def post(self):
        data = request.get_json(silent=True, force=True)
        if not data:
            return {"status": 400, "msg": "Request body must be valid JSON"}, 400
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": 400, "msg": "username and password are required"}, 400
        if user_exist(username):
            return {"status": 400, "msg": "User already exists"}, 400

        # encrypt password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Insert record
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Messages": []
        })

        return {"status": 200, "msg": "Registration successful"}, 200

class Login(Resource):
    """
    This is the Login resource class — issues JWT tokens (issue #7)
    """

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

        access_token = create_access_token(identity=username)
        return {"access_token": access_token}, 200

class Retrieve(Resource):
    """
    This is the Retrieve resource class
    """

    @jwt_required()
    def post(self):
        username = get_jwt_identity()
        if not user_exist(username):
            return {"status": 401, "msg": "Invalid credentials"}, 401

        # get the messages
        messages = get_user_messages(username)

        return {"status": 200, "obj": messages}, 200

class Save(Resource):
    """
    This is the Save resource class
    """

    @jwt_required()
    def post(self):
        data = request.get_json(silent=True, force=True)
        username = get_jwt_identity()
        message = data.get("message") if data else None
        if not message:
            return {"status": 400, "msg": "message is required"}, 400
        if not user_exist(username):
            return {"status": 401, "msg": "Invalid credentials"}, 401

        # get the messages
        messages = get_user_messages(username)

        # add new message
        messages.append(message)

        # save the new user message
        users.update({
            "Username": username
        }, {
            "$set": {
                "Messages": messages
            }
        })

        return {"status": 200, "msg": "Message has been saved successfully"}, 200


api.add_resource(Hello, '/hello')
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Retrieve, '/retrieve')
api.add_resource(Save, '/save')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5000)
