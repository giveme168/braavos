#-*- coding: UTF-8 -*-
from threading import Thread
from flask_mail import Mail, Message

mail = Mail()


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


@async
def send_async_mail(msg):
    with mail.app.app_context():
        mail.send(msg)


def send_sync_mail(msg):
    with mail.app.app_context():
        mail.send(msg)


@async
def send_mail(*args, **kwargs):
    with mail.app.app_context():
        mail.send_message(*args, **kwargs)


@async
def send_simple_mail(subject, recipients, body=''):
    if not recipients:
        return
    body += u"""

--------
本邮件由系统代发, 请不要直接回复
如有任何疑问, 请咨询 promotion@inad.com
"""
    with mail.app.app_context():
        mail.send_message(subject, recipients=recipients, body=body)
