# import functools
import bcrypt

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
# print = functools.partial(print, flush=True)

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://my_db:27017")
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

class Retrieve(Resource):
    """
    This is the Retrieve resource class
    """

    def post(self):
        data = request.get_json(silent=True, force=True)
        if not data:
            return {"status": 400, "msg": "Request body must be valid JSON"}, 400
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": 400, "msg": "username and password are required"}, 400
        if not user_exist(username):
            return {"status": 401, "msg": "Invalid credentials"}, 401
        if not verify_user(username, password):
            return {"status": 401, "msg": "Invalid credentials"}, 401

        # get the messages
        messages = get_user_messages(username)

        return {"status": 200, "obj": messages}, 200

class Save(Resource):
    """
    This is the Save resource class
    """

    def post(self):
        data = request.get_json(silent=True, force=True)
        if not data:
            return {"status": 400, "msg": "Request body must be valid JSON"}, 400
        username = data.get("username")
        password = data.get("password")
        message = data.get("message")
        if not username or not password:
            return {"status": 400, "msg": "username and password are required"}, 400
        if not message:
            return {"status": 400, "msg": "message is required"}, 400
        if not user_exist(username):
            return {"status": 401, "msg": "Invalid credentials"}, 401
        if not verify_user(username, password):
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
api.add_resource(Retrieve, '/retrieve')
api.add_resource(Save, '/save')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5000)
