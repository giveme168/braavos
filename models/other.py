# -*- coding: UTF-8 -*-
import datetime
from . import db, BaseModelMixin


class NianHui(db.Model, BaseModelMixin):
    __tablename__ = 'other_nianhui'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('nianhui_user', lazy='dynamic'))
    create_time = db.Column(db.DateTime)     # 创建时间
    ids = db.Column(db.String(100))          # 节目编号

    def __init__(self, user, ids, create_time=None):
        self.user = user
        self.ids = ids
        self.create_time = create_time or datetime.datetime.now()
