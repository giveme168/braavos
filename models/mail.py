# -*- coding: UTF-8 -*-
import datetime
from . import db, BaseModelMixin


class Mail(db.Model, BaseModelMixin):
    """Mail 用来做邮件发送记录
    """
    __tablename__ = 'mail'

    id = db.Column(db.Integer, primary_key=True)
    recipients = db.Column(db.String(1000))
    subject = db.Column(db.String(1000))
    body = db.Column(db.String(1000))
    files = db.Column(db.String(1000))
    remark = db.Column(db.String(1000))

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_mails', lazy='dynamic'))
    create_time = db.Column(db.DateTime)

    def __init__(self, recipients, subject, body, files, creator, create_time=None, remark=None):
        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.files = files
        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()
        self.remark = remark or ""
