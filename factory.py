from flask import Flask
from braavos.libs.db import db


def create_app(config_object='braavos.config.DevelopmentConfig'):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_object)
    db.init_app(app)
    return app
