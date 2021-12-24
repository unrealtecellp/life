import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'do-not-try'
    # MONGO_URI = "mongodb://localhost:27017/lifedb"
    MONGO_URI = "mongodb+srv://analytics:NS5l970EeAJVD4ab@mflix.dadx7.mongodb.net/lifetestapp?retryWrites=true&w=majority"
    
    LOGIN_DISABLED = False