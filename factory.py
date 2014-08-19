from flask import Flask
from libs.db import db
from libs.mail import mail


def create_app(config_object='config.DevelopmentConfig'):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_object)
    app.debug = app.config['DEBUG']
    db.init_app(app)
    db.app = app
    mail.init_app(app)
    mail.app = app
    return app
