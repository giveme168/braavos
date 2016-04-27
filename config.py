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
    MAIL_DEFAULT_SENDER = 'your email'
    MAIL_DEBUG = DEBUG
    MAIL_SUPPRESS_SEND = DEBUG

    SENTRY_DSN = ''
    DOMAIN = 'https://z.inad.com'
    UPLOADED_FILES_DEST = '/tmp/braavos/'
    UPLOADED_FILES_URL = '/files/files/'
    UPLOADED_ATTACHMENT_DEST = '/tmp/attachment/'
    UPLOADED_ATTACHMENT_URL = '/files/attachment/'
    UPLOADED_MEDIUMS_DEST = '/tmp/mediums/'
    UPLOADED_MEDIUMS_URL = '/files/mediums/'

    REDIS_URL = "redis://@localhost:6379/0"


class TestingConfig(Config):
    TESTING = True
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class DevelopmentConfig(object):
    """Use local_config overwrite this"""
    pass

config_object = 'config.DevelopmentConfig'

try:
    from local_config import *
except ImportError:
    pass
