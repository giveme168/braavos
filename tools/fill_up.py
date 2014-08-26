#-*- coding: UTF-8 -*-
import os
import sys
import datetime
sys.path.insert(0, os.path.abspath('.'))

from app import app
from libs.db import db
db.create_all()

from models.user import User, Team, TEAM_TYPE_SUPER_ADMIN
from models.medium import Medium, AdSize, AdUnit, AdPosition, TARGET_BLANK
from models.consts import STATUS_ON
from models.client import Client, Agent
from models.order import Order

team = Team.add('管理员', type=TEAM_TYPE_SUPER_ADMIN)

medium_team = Team.add('管理员', type=TEAM_TYPE_SUPER_ADMIN)


for x in range(5):
    email = "test%s@inad.com" % x
    password = 'pwd123'
    phone = '1234567890%s' % x
    user = User.add(email, email, password, phone, team)

medium = Medium.add("测试媒体", owner=medium_team)

size = AdSize.add(200, 70)

unit = AdUnit.add("测试广告单元", "测试", size, "0px 0px 0px 0px",
                  TARGET_BLANK, STATUS_ON, medium, 10000)

unit2 = AdUnit.add("测试广告单元2", "测试", size, "0px 0px 0px 0px",
                   TARGET_BLANK, STATUS_ON, medium, 10000)

unit3 = AdUnit.add("测试广告单元3", "测试", size, "0px 0px 0px 0px",
                   TARGET_BLANK, STATUS_ON, medium, 10000)

position = AdPosition.add("测试展示位置", "测试", size, STATUS_ON, medium, max_order_num=700)
position.units = [unit, unit2]

position2 = AdPosition.add("测试展示位置2", "测试", size, STATUS_ON, medium, max_order_num=800)
position2.units = [unit2, unit3]


client = Client.add("测试客户", 0)

agent = Agent.add("测试代理")

order = Order.add(client, "测试活动", medium, 0, "", 1000,
              agent, [user], [], [], [], [], user, datetime.datetime.now())
