import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from app import app
from models.user import User, Team, TEAM_TYPE_SUPER_ADMIN

team = Team('Test Admin Team', type=TEAM_TYPE_SUPER_ADMIN)
team.add()

for x in range(5):
    email = "test%s@inad.com" % x
    password = 'pwd123'
    phone = '1234567890%s' % x
    user = User(email, email, password, phone, team)
    user.add()
