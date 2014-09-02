DEFAULT_PASSWORD = 'default_password'


class Config(object):
    SECRET_KEY = 'your key'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://vagrant:vagrant@localhost/braavos'

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'your name'
    MAIL_PASSWORD = 'your password'
    DEFAULT_MAIL_SENDER = 'your email'
    MAIL_DEBUG = DEBUG
    MAIL_SUPPRESS_SEND = DEBUG

    SENTRY_DSN = ''
    DOMAIN = 'http://z.inad.com'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class DevelopmentConfig(object):
    """Use local_config overwrite this"""
    pass

config_object = 'config.DevelopmentConfig'

try:
    from local_config import *
except ImportError:
    pass
