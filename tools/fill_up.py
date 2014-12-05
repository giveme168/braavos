#-*- coding: UTF-8 -*-
import os
import sys
import datetime
sys.path.insert(0, os.path.abspath('.'))

from app import app
from libs.db import db
db.create_all()

from models.user import (User, Team, TEAM_TYPE_SUPER_ADMIN, TEAM_TYPE_MEDIUM,
                         TEAM_TYPE_LEADER, TEAM_TYPE_DIRECT_SELLER)
from models.medium import Medium, AdSize, AdUnit, AdPosition, TARGET_BLANK
from models.consts import STATUS_ON
from models.client import Client, Agent
from models.order import Order
from config import DEFAULT_PASSWORD

admin_team = Team.add('管理员', type=TEAM_TYPE_SUPER_ADMIN)
medium_team = Team.add('媒体', type=TEAM_TYPE_MEDIUM)
leader_team = Team.add('ledaer', type=TEAM_TYPE_LEADER)
sale_team = Team.add('ledaer', type=TEAM_TYPE_DIRECT_SELLER)


user = User.add(name="admin", email="test0@inad.com", password=DEFAULT_PASSWORD, phone='1234', team=admin_team)
leader = User.add(name="leader", email="test1@inad.com", password=DEFAULT_PASSWORD, phone='12345', team=leader_team)
saler = User.add(name="saler", email="test2@inad.com", password=DEFAULT_PASSWORD, phone='12346', team=sale_team)

medium = Medium.add("测试媒体", owner=medium_team)

size = AdSize.add(180, 180)

unit = AdUnit.add("测试广告单元", "测试", size, "0px 0px 0px 0px",
                  TARGET_BLANK, STATUS_ON, medium, 10000)

unit2 = AdUnit.add("测试广告单元2", "测试", size, "0px 0px 0px 0px",
                   TARGET_BLANK, STATUS_ON, medium, 10000)

unit3 = AdUnit.add("测试广告单元3", "测试", size, "0px 0px 0px 0px",
                   TARGET_BLANK, STATUS_ON, medium, 10000)

position = AdPosition.add("测试展示位置", "测试", size, "测试标准", STATUS_ON, medium)
position.max_order_num = 700
position.units = [unit, unit2]
position.save()

position2 = AdPosition.add("测试展示位置2", "测试", size, "测试标准", STATUS_ON, medium)
position2.max_order_num = 800
position2.units = [unit2, unit3]
position2.save()


client = Client.add("测试客户", 0)

agent = Agent.add("测试代理")

order = Order.add(agent, client, "测试活动", medium, creator=user)
