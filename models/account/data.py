# -*- coding: UTF-8 -*-
import datetime
from flask import json

from models import db, BaseModelMixin


class Notice(db.Model, BaseModelMixin):
    __tablename__ = 'notice'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    emails = db.Column(db.Text(), default=json.dumps([]))
    content = db.Column(db.Text(), default="")
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('notice_creator', lazy='dynamic'),
        foreign_keys=[creator_id])
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, title, emails, content, creator, create_time=None):
        self.title = title
        self.emails = emails
        self.content = content
        self.creator = creator
        self.create_time = create_time or datetime.date.today()

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d %H:%M')
