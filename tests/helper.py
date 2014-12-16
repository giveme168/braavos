# -*- coding: utf-8 -*-
from datetime import date, time, datetime

from config import DEFAULT_PASSWORD
from models.user import User, Team
from models.client import Client, Agent
from models.order import Order
from models.medium import Medium, AdSize, AdUnit, AdPosition
from models.item import AdItem, AdSchedule
from models.material import Material, MATERIAL_TYPE_RAW
from .test_consts import TEST_POSITION, TEST_MEDIUM, TEST_DEFAULT_MEDIUM


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
    team = add_team(TEST_DEFAULT_MEDIUM)
    medium = Medium.add(name, team)
    return medium


def add_size(width, height):
    size = AdSize.add(width, height)
    return size


def add_unit(name, estimate_num, medium=None, size=None):
    size = size or add_size(300, 50)
    medium = medium or add_medium(TEST_MEDIUM)
    unit = AdUnit.add(
        name=name, description='', size=size,
        margin='', target=0, status=1, medium=medium,
        estimate_num=estimate_num)
    return unit


def add_position(name, medium=None, size=None):
    size = size or add_size(300, 50)
    medium = medium or add_medium(TEST_MEDIUM)
    position = AdPosition.add(
        name=name, description='', size=size, standard='', status=1, medium=medium)
    return position


def add_client(name):
    client = Client.add(name, 0)
    return client


def add_agent(name):
    agent = Agent.add(name)
    return agent


def add_order():
    user = get_default_user()
    medium = add_medium(TEST_MEDIUM)
    order = Order.add(campaign='testcampaign', medium=medium, order_type=0,
                      creator=user, create_time=datetime.now())
    return order


def add_item(position=None):
    order = add_order()
    position = position or add_position(TEST_POSITION)
    user = get_default_user()
    item = AdItem.add(
        order=order, sale_type=0, special_sale=False,
        position=position, creator=user, create_time=datetime.now())
    return item


def add_schedule(item=None, num=300):
    item = item or add_item()
    today = date.today()
    start = time.min
    end = time.max
    schedule = AdSchedule.add(item=item, num=num, date=today, start=start, end=end)
    return schedule


def add_material(item=None, material_type=MATERIAL_TYPE_RAW, name=None):
    item = item or add_item()
    user = get_default_user()
    name = name or 'test_material'
    material = Material.add(name=name, item=item, creator=user, type=material_type)
    return material


def get_position(name, medium=None):
    medium = medium or add_medium(TEST_MEDIUM)
    position = AdPosition.query.filter_by(name=name).first()
    return position


def get_medium_by_name(name):
    return Medium.query.filter_by(name=name).first()


def get_unit(name):
    return AdUnit.query.filter_by(name=name).first()
