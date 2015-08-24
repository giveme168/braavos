# -*- coding: UTF-8 -*-
import datetime

from models import db, BaseModelMixin


class Commission(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('commission_user', lazy='dynamic'),
        foreign_keys=[user_id])
    year = db.Column(db.Integer)
    rate = db.Column(db.Float)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('commission_creator', lazy='dynamic'),
        foreign_keys=[creator_id])
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': year.desc()}

    def __init__(self, user, year=None, rate=None, creator=None, create_time=None):
        self.user = user
        self.creator = creator
        self.year = year or datetime.datetime.now().year
        self.rate = rate or 0.0
        self.create_time = datetime.date.today()
