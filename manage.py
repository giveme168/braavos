# db Migrate Manager
from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager
from app import app
from libs.db import db
from models.user import User, Team
from models.client import Client, Agent
from models.comment import Comment
from models.item import AdItem, AdSchedule
from models.material import Material
from models.medium import Medium, AdSize, AdUnit, AdPosition
from models.order import Order
from models.delivery import Delivery

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
