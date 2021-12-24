from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import mongo, login
from bson.objectid import ObjectId

userlogin = mongo.db.userlogin             # collection of users and their login details

# User Login Database
class UserLogin(UserMixin):

    def __init__(self, username):
            userName = userlogin.find_one({"username": username})
            # print(userName)
            if userName != None:
                self.username = userName["username"]
                self.password_hash = userName["password"]
                self.id = userName['_id']
            else:
                self.username = ""
                self.password_hash = ""

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    if userlogin.find_one({"_id": ObjectId(id)}) != None:
        # print(id, userlogin.find_one({"_id": ObjectId(id)}), UserLogin(userlogin.find_one({"_id": ObjectId(id)})["username"]))
        return UserLogin(username=userlogin.find_one({"_id": ObjectId(id)})["username"])