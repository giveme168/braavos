# -*- coding: UTF-8 -*-
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

    def __repr__(self):
        return '<Client %s, industry=%s>' % (self.name, self.industry_cn)

    @property
    def industry_cn(self):
        return CLIENT_INDUSTRY_CN[self.industry]


class Agent(db.Model, BaseModelMixin):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Agent %s>' % (self.name)
