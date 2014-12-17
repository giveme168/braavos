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


class Agent(db.Model, BaseModelMixin):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    framework = db.Column(db.String(100))

    def __init__(self, name, framework=None):
        self.name = name
        self.framework = framework or ""

    def get_default_framework(self):
        return framework_generator(self.id)

    @classmethod
    def name_exist(cls, name):
        is_exist = Agent.query.filter_by(name=name).count() > 0
        return is_exist

    @classmethod
    def fw_exist(cls, framework):
        is_exist = Agent.query.filter_by(framework=framework).count() > 0
        return is_exist

    @classmethod
    def get_new_framework(cls):
        return framework_generator(cls.all().count() + 1)


def framework_generator(num):
    code = "ZQC%s%03x" % (datetime.datetime.now().strftime('%Y%m'), num % 1000)
    code = code.upper()
    if Agent.fw_exist(code):
        return framework_generator(num + 1)
    return code
