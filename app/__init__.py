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

from app.lifeques.lifeques import lifeques
app.register_blueprint(lifeques, url_prefix='/lifeques')

from app.lifedata.lifedata import lifedata
app.register_blueprint(lifedata, url_prefix='/lifedata')

from app.lifemodels.lifemodelsroutes import lifemodels
app.register_blueprint(lifemodels, url_prefix='/lifemodels')

from app.easyAnno.easyAnnoroutes import easyAnno
app.register_blueprint(easyAnno, url_prefix='/easyAnno')

from app.lifedownloader.lifedownloaderroutes import ld
app.register_blueprint(ld, url_prefix='/download')

from app import routes, models, forms

