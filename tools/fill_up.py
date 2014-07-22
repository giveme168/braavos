#-*- coding: UTF-8 -*-
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import app
from libs.db import db
db.create_all()

from models.user import User, Team, TEAM_TYPE_SUPER_ADMIN
from models.medium import Medium, AdSize, AdUnit, AdPosition, TARGET_BLANK, STATUS_ON
from models.client import Client, Agent

team = Team('管理员', type=TEAM_TYPE_SUPER_ADMIN)
team.add()

for x in range(5):
    email = "test%s@inad.com" % x
    password = 'pwd123'
    phone = '1234567890%s' % x
    user = User(email, email, password, phone, team)
    user.add()

medium = Medium("测试媒体", owner=team)
medium.add()

size = AdSize(200, 70)
size.add()

unit = AdUnit("测试广告单元", "测试", size, "0px 0px 0px 0px",
              TARGET_BLANK, STATUS_ON, medium)
unit.add()

position = AdPosition("测试展示位置", "测试", size, STATUS_ON, medium)
position.add()

client = Client("测试客户", 0)
client.add()

agent = Agent("测试代理")
agent.add()
