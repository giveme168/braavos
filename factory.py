from flask import Flask
from raven.contrib.flask import Sentry

from libs.db import db
from libs.mail import mail
from libs.files import uploads_conf
from libs.redis_client import redis
from libs.signals import init_signal
from libs.email_signals import email_init_signal
from filters import register_filter


def create_app(config_object='config.DevelopmentConfig'):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_object)
    app.debug = app.config['DEBUG']
    db.init_app(app)
    db.app = app
    redis.init_app(app)
    init_signal(app)
    email_init_signal(app)
    mail.init_app(app)
    mail.app = app
    register_filter(app)
    if not app.debug:
        Sentry(app)
    uploads_conf(app)
    return app
