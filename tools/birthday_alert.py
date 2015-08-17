# encoding: utf-8
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import app
from models.user import User
from libs.mail import send_simple_mail


def get_all_today_is_birthday():
    users = User.get_all_today_is_birthday()
    to_emails = [user.email for user in users]
    send_simple_mail(u'祝你生日快乐',
            recipients=to_emails,
            body=u'今天是你的生日,祝你生日快乐!'
            )
    

if __name__ == '__main__':
    get_all_today_is_birthday()
