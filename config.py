DEFAULT_PASSWORD = 'default_password'


class Config(object):
    SECRET_KEY = 'b8e2b80a27c64f79b7dc8293c1cc370a'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://vagrant:vagrant@localhost/braavos'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class DevelopmentConfig(Config):
    pass

config_object = 'config.DevelopmentConfig'

try:
    from local_config import *
except:
    pass
