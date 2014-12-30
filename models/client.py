# -*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin
from consts import CLIENT_INDUSTRY_CN


class Client(db.Model, BaseModelMixin):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    industry = db.Column(db.Integer)

    def __init__(self, name, industry):
        self.name = name
        self.industry = industry

    @classmethod
    def name_exist(cls, name):
        is_exist = Client.query.filter_by(name=name).count() > 0
        return is_exist

    @property
    def industry_cn(self):
        return CLIENT_INDUSTRY_CN[self.industry]


class Group(db.Model, BaseModelMixin):
    __tablename__ = 'bra_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    @classmethod
    def name_exist(cls, name):
        is_exist = Group.query.filter_by(name=name).count() > 0
        return is_exist


class Agent(db.Model, BaseModelMixin):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    group_id = db.Column(db.Integer, db.ForeignKey('bra_group.id'))
    group = db.relationship('Group', backref=db.backref('agents', lazy='dynamic'))

    def __init__(self, name, group=None):
        self.name = name
        self.group = group

    @classmethod
    def name_exist(cls, name):
        is_exist = Agent.query.filter_by(name=name).count() > 0
        return is_exist

    @property
    def current_framework(self):
        return framework_generator(self.id)


def framework_generator(num):
    code = "ZQC%s%03x" % (datetime.datetime.now().strftime('%Y%m'), num % 1000)
    code = code.upper()
    return code
