import os

SECRET_KEY = 'b8e2b80a27c64f79b7dc8293c1cc370a'
DEBUG = False
SQLALCHEMY_DATABASE_URI = 'postgresql://vagrant:vagrant@localhost/braavos'

try:
    from local_config import *
except:
    pass
