from datetime import date, time, datetime

from config import DEFAULT_PASSWORD
from models.user import User, Team
from models.client import Client, Agent
from models.order import Order
from models.medium import Medium, AdSize, AdUnit, AdPosition
from models.item import AdItem, AdSchedule
from models.material import Material, MATERIAL_TYPE_RAW


def add_team(name):
    team = Team.add(name)
    return team


def add_user(name, phone, pwd=DEFAULT_PASSWORD):
    team = add_team('testteam1')
    user = User.add(name=name, email=(name + '@inad.com'),
                    password=pwd, phone=phone, team=team)
    return user


def get_default_user():
    name = 'defaultuser'
    email = 'defaultuser@inad.com'
    phone = '7654321'
    user = User.get_by_email(email)
    if user:
        return user
    else:
        return add_user(name, phone)


def add_medium(name):
    team = add_team('testteam')
    medium = Medium.add(name, team)
    return medium


def add_size(width, height):
    size = AdSize.add(width, height)
    return size


def add_unit(name, estimate_num, medium=None):
    size = add_size(300, 50)
    medium = medium or add_medium('testmedium')
    unit = AdUnit.add(name, '', size, '', 0, 1, medium, estimate_num)
    return unit


def add_position(name, medium=None):
    size = add_size(300, 50)
    medium = medium or add_medium('testmedium')
    position = AdPosition.add(name, '', size, '', 1, medium)
    return position


def add_client(name):
    client = Client.add(name, 0)
    return client


def add_agent(name):
    agent = Agent.add(name)
    return agent


def add_order():
    user = get_default_user()
    medium = add_medium('testmedium')
    client = add_client('testclient')
    agent = add_agent('testagent')
    order = Order.add(client, 'testcampaign', medium, 0, 'testcontract', 1000, agent,
                      [user], [], [], [], [], user, datetime.now())
    return order


def add_item(position=None):
    order = add_order()
    position = position or add_position('testposition')
    user = get_default_user()
    item = AdItem.add(order, 0, False, position, user, datetime.now())
    return item


def add_schedule(item=None, num=300):
    item = item or add_item()
    today = date.today()
    start = time.min
    end = time.max
    schedule = AdSchedule.add(item, num, today, start, end)
    return schedule


def add_material(item=None, material_type=MATERIAL_TYPE_RAW, name=None):
    item = item or add_item()
    user = get_default_user()
    name = name or 'test_material'
    material = Material.add(name, item, user, material_type)
    return material
