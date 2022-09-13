from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from flask_login import LoginManager
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'

from app.karya_ext.karya import karya_bp
app.register_blueprint(karya_bp, url_prefix='/karyaext')

# lib_name = 'karya_routes'

from app import routes, models, forms

