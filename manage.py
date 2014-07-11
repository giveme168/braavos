# db Migrate Manager
from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager
from app import app
from libs.db import db
from models.user import User, Team

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

app.debug = True
manager.run()
