#-*- coding: UTF-8 -*-
import requests
from models.mail import Mail

url = "http://sendcloud.sohu.com/webapi/mail.send.json"


def send_simple_mail(sender, subject, recipients, body='', file_paths=None):
    body += u"""


--------
本邮件由系统代发, 请不要直接回复, 不要取消订阅
如有任何疑问, 请咨询 z@inad.com
"""
    if recipients:
        recipients = ";".join(recipients)

        params = {
            "api_user": "inadrobot",
            "api_key": "JZv0peFZg3Bjh9Qt",
            "to": recipients,
            "from": "robot@z.inad.com",
            "fromname": "致趣机器人",
            "subject": subject,
            "html": body.replace("\n", "<br>"),
            "resp_email_id": "true",
        }
        files = {}

        if file_paths:
            for fp in file_paths:
                with open(fp, 'rb') as f:
                    files[f.name] = (f.name, f)

        r = requests.post(url, files=files, data=params)

        Mail.add(recipients=recipients,
                 subject=subject,
                 body=body,
                 files=";".join(file_paths) if file_paths else "",
                 creator=sender,
                 remark=r.text)


def password_changed(sender, user):
    send_simple_mail(sender=sender,
                     subject=u'您的InAd帐号密码重设',
                     recipients=[user.email],
                     body=u'您的InAd帐号密码已经被重新设置, 如果不是您的操作, 请联系广告平台管理员')


def add_comment(sender, comment):
    send_simple_mail(sender=sender,
                     subject=u'InAd新留言提醒[%s]' % comment.target.name,
                     recipients=[
                         u.email for u in comment.target.get_mention_users(except_user=comment.creator)],
                     body=(u'%s的新留言:\n\n %s' % (comment.creator.name, comment.msg)))
