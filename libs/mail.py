#-*- coding: UTF-8 -*-
import os
import mimetypes
import smtplib
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
如有任何疑问, 请咨询 z@inad.com
"""
    with mail.app.app_context():
        mail.send_message(subject, recipients=recipients, body=body)


@async
def send_html_mail(subject, recipients, body=''):
    if not recipients:
        return
    with mail.app.app_context():
        mail.send_message(subject, recipients=recipients, body='', html=body)


@async
def send_attach_mail(subject, recipients, body='', file_paths=None):
    if not recipients:
        return
    body += u"""

--------
本邮件由系统代发, 如有任何疑问, 请咨询 z@inad.com
"""
    with mail.app.app_context():
        msg = Message(subject, recipients=recipients, body=body)
        if file_paths:
            for fp in file_paths:
                with open(fp, 'r') as f:
                    ctype, encoding = mimetypes.guess_type(f.name)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    msg.attach(os.path.basename(f.name).encode('gb2312'), ctype, f.read(), 'attachment')
        mail.send(msg)


def check_auth_by_mail(username, password):
    host = "smtp.exmail.qq.com"
    smtp = smtplib.SMTP(host)
    try:
        ret = smtp.login(username, password)
        smtp.close()
        if ret[0] == 235:
            return True
    except:
        pass
    return False
