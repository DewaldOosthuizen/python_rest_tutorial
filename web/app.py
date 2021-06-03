import bcrypt
import functools

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
# print = functools.partial(print, flush=True)

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://my_db:27017")
db = client.projectDB
users = db["Users"]
invalid_user_json = { "status": 301, "msg": "Invalid Username" }
invalid_password_json = { "status": 302, "msg": "Invalid password" }

"""
HELPER FUNCTIONS
"""


def user_exist(username):
    return users.find({"Username": username}).count() > 0;


def verify_user(username, password):
    if not user_exist(username):
        return False

    user_hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    return bcrypt.checkpw(password.encode('utf8'), user_hashed_pw);


def get_user_messages(username):
    # get the messages
    return users.find({
        "Username": username,
    })[0]["Messages"]


"""
RESOURCES
"""

@api.representation('application/json')
class Hello(Resource):
    """
    This is the Hello resource class
    """

    def get(self):
        return "Hello World!"

@api.representation('application/json')
class Register(Resource):
    """
    This is the Register resource class
    """

    def post(self):
        # Get posted data from request
        data = request.get_json()

        username = data["username"]
        password = data["password"]

        # check if user exists
        if user_exist(username):
            return jsonify(invalid_user_json)

        # encrypt password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Insert record
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Messages": []
        })

        # Return successful result
        ret_json = {
            "status": 200,
            "msg": "Registration successful"
        }
        return jsonify(ret_json)

@api.representation('application/json')
class Retrieve(Resource):
    """
    This is the Retrieve resource class
    """

    def post(self):
         # Get posted data from request
        data = request.get_json()

        # get data
        username = data["username"]
        password = data["password"]

        # check if user exists
        if not user_exist(username):
            return jsonify(invalid_user_json)

        # check password
        correct_pw = verify_user(username, password)
        if not correct_pw:
            return jsonify(invalid_password_json)

        # get the messages
        messages = get_user_messages(username)

        # Build successful response
        ret_json = {
            "status": 200,
            "obj": messages
        }

        return jsonify(ret_json)

@api.representation('application/json')
class Save(Resource):
    """
    This is the Save resource class
    """

    def post(self):

         # Get posted data from request
        data = request.get_json()

        # get data
        username = data["username"]
        password = data["password"]
        message = data["message"]

        # check if user exists
        if not user_exist(username):
            return jsonify(invalid_user_json)

        # check password
        correct_pw = verify_user(username, password)
        if not correct_pw:
            return jsonify(invalid_password_json)

        if not message:
            ret_json = {
                "status": 303,
                "msg": "Please supply a valid message"
            }
            return jsonify(ret_json)

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

        ret_json = {
            "status": 200,
            "msg": "Message has been saved successfully"
        }

        return jsonify(ret_json)


api.add_resource(Hello, '/hello')
api.add_resource(Register, '/register')
api.add_resource(Retrieve, '/retrieve')
api.add_resource(Save, '/save')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
