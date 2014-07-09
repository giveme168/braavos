import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from models.user import User

for x in range(5):
    email = "test%s@inad.com" % x
    password = 'pwd123'
    user = User(email, email, password)
    user.add()
