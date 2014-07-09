from flask.ext.sqlalchemy import SQLAlchemy
from app import app
db = SQLAlchemy(app)
db.init_app(app)
