# -*- coding: UTF-8 -*-
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import app
from libs.db import db
db.create_all()

from models.user import (User, Team, TEAM_TYPE_SUPER_ADMIN, TEAM_TYPE_MEDIUM,
                         TEAM_TYPE_LEADER, TEAM_TYPE_DIRECT_SELLER)
from models.medium import Medium, MediumGroup
from models.client import Client, Agent, Group
from models.order import Order
from config import DEFAULT_PASSWORD

admin_team = Team.add(u'管理员', type=TEAM_TYPE_SUPER_ADMIN)
medium_team = Team.add(u'媒体', type=TEAM_TYPE_MEDIUM)
leader_team = Team.add('ledaer', type=TEAM_TYPE_LEADER)
sale_team = Team.add('ledaer', type=TEAM_TYPE_DIRECT_SELLER)


user = User.add(name="admin", email="test0@inad.com", password=DEFAULT_PASSWORD, team=admin_team)
leader = User.add(name="leader", email="test1@inad.com", password=DEFAULT_PASSWORD, team=leader_team)
saler = User.add(name="saler", email="test2@inad.com", password=DEFAULT_PASSWORD, team=sale_team)

medium_group = MediumGroup.add(name='测试媒体供应商', tax_num="", address="",
                               phone_num="", bank="", bank_num="", level=100)
medium = Medium.add(medium_group, u"测试媒体", owner=medium_team)

client = Client.add(u"测试客户", 0)

group = Group.add(u'测试代理集团')

agent = Agent.add(u"测试代理", group=group)
