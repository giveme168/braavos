# db Migrate Manager
from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager
from app import app
from libs.db import db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
