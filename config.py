import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'do-not-try'
    MONGO_URI = "mongodb://localhost:27017/lifedb"
    # Flask-Caching related configs
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
    LOGIN_DISABLED = False