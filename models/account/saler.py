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
    __table_args__ = (
        db.UniqueConstraint('user_id', 'year', name='_commission_user_year'),)
    __mapper_args__ = {'order_by': year.desc()}

    def __init__(self, user, year=None, rate=None, creator=None, create_time=None):
        self.user = user
        self.creator = creator
        self.year = year or datetime.datetime.now().year
        self.rate = rate or 0.0
        self.create_time = datetime.date.today()


TEAM_LOCATION_HUABEI = 1
TEAM_LOCATION_HUADONG = 2
TEAM_LOCATION_HUANAN = 3
TEAM_LOCATION_CN = {
    TEAM_LOCATION_HUABEI: u"华北",
    TEAM_LOCATION_HUADONG: u"华东",
    TEAM_LOCATION_HUANAN: u"华南",
}

PER_STATUS_NEW = 1
PER_STATUS_APPLY = 2
PER_STATUS_SUCCESS = 0
PER_STATUS_CN = {
    PER_STATUS_NEW: u"新建",
    PER_STATUS_APPLY: u"审批中",
    PER_STATUS_SUCCESS: u"审批通过"
}


class Performance(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('performance_creator', lazy='dynamic'))
    status = db.Column(db.Integer)
    year = db.Column(db.Integer)
    q_month = db.Column(db.String(10))
    t_money = db.Column(db.Float)  # 区域销售目标总计
    location = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}
    __table_args__ = (db.UniqueConstraint(
        'location', 'year', 'q_month', name='_performance_location_year_q'),)

    def __init__(self, creator, year, q_month, t_money, location, create_time=None, status=None):
        self.creator = creator
        self.year = year
        self.q_month = q_month
        self.t_money = t_money
        self.location = location
        self.create_time = create_time or datetime.date.today()
        self.status = status or PER_STATUS_NEW

    @property
    def location_cn(self):
        return TEAM_LOCATION_CN[self.location]


class PerformanceUser(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('performance_user', lazy='dynamic'))
    performance = db.relationship(
        'Performance', backref=db.backref('performance_user_money', lazy='dynamic'))
    performance_id = db.Column(db.Integer, db.ForeignKey('performance.id'))
    year = db.Column(db.Integer)
    q_month = db.Column(db.String(10))
    money = db.Column(db.Float)  # 销售目标
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, user, year, q_month, money, create_time, performance):
        self.user = user
        self.year = year
        self.performance = performance
        self.q_month = q_month
        self.money = money
        self.create_time = create_time or datetime.date.today()

    @property
    def status(self):
        return self.performance.status


class Completion(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('completion_user', lazy='dynamic'),
        foreign_keys=[user_id])
    time = db.Column(db.String(7))
    rate = db.Column(db.Float)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('completion_creator', lazy='dynamic'),
        foreign_keys=[creator_id])
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': time.desc()}

    def __init__(self, user, time, rate=None, creator=None, create_time=None):
        self.user = user
        self.creator = creator
        self.time = time
        self.rate = rate or 0.0
        self.create_time = datetime.date.today()
