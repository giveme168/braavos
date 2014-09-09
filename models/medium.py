# -*- coding: UTF-8 -*-
from datetime import timedelta

from . import db, BaseModelMixin
from .consts import STATUS_CN, DATE_FORMAT

TARGET_TOP = 1
TARGET_BLANK = 0
TARGET_CN = {
    TARGET_TOP: u"_top",
    TARGET_BLANK: u"_blank"
}

POSITION_LEVEL_A1 = 11
POSITION_LEVEL_A2 = 12
POSITION_LEVEL_B = 21
POSITION_LEVEL_C = 31
POSITION_LEVEL_Y = 41
POSITION_LEVEL_APP = 51
POSITION_LEVEL_CN = {
    POSITION_LEVEL_A1: u"A1",
    POSITION_LEVEL_A2: u"A2",
    POSITION_LEVEL_B: u"B",
    POSITION_LEVEL_C: u"C",
    POSITION_LEVEL_Y: u"软性资源",
    POSITION_LEVEL_APP: u"APP",
}

AD_TYPE_NORMAL = 0
AD_TYPE_CPD = 1
AD_TYPE_REMNANT = 2

AD_TYPE_CN = {
    AD_TYPE_NORMAL: u"标准/CPM",
    AD_TYPE_CPD: u"CPD",
}

ad_position_unit_table = db.Table('ad_position_unit',
                                  db.Column('position_id', db.Integer, db.ForeignKey('ad_position.id')),
                                  db.Column('unit_id', db.Integer, db.ForeignKey('ad_unit.id'))
                                  )


class Medium(db.Model, BaseModelMixin):
    __tablename__ = 'medium'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    owner = db.relationship('Team', backref=db.backref('mediums', lazy='dynamic'))

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def __repr__(self):
        return '<Medium %s>' % (self.name)


class AdSize(db.Model, BaseModelMixin):
    __tablename__ = 'ad_size'
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __repr__(self):
        return "<AdSize %sx%s>" % (self.width, self.height)

    @property
    def name(self):
        return "%s x %s" % (self.width, self.height)


class AdUnit(db.Model, BaseModelMixin):
    __tablename__ = 'ad_unit'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    size_id = db.Column(db.Integer, db.ForeignKey('ad_size.id'))
    size = db.relationship('AdSize', backref=db.backref('adUnits', lazy='dynamic'))
    margin = db.Column(db.String(50))
    target = db.Column(db.Integer)
    status = db.Column(db.Integer)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship('Medium', backref=db.backref('units', lazy='dynamic'))
    estimate_num = db.Column(db.Integer)

    def __init__(self, name, description, size, margin, target, status, medium, estimate_num=0):
        self.name = name
        self.description = description
        self.size = size
        self.margin = margin
        self.target = target
        self.status = status
        self.medium = medium
        self.estimate_num = estimate_num

    def __repr__(self):
        return '<AdUnit %s>' % (self.name)

    @property
    def status_cn(self):
        return STATUS_CN[self.status]

    @property
    def display_name(self):
        return "%s(%s)" % (self.name, self.medium.name)

    def schedule_num(self, date):
        """
        每个展示位置的的预订量按照比例分配到所拥有的广告单元上,
        再加和计算该单元的预订量
        """
        return int(sum([x.schedule_num(date) * (float(self.estimate_num) / x.estimate_num)
                        for x in self.positions]))

    def retain_num(self, date):
        retain_num = self.estimate_num - self.schedule_num(date)
        return max(retain_num, 0)


class AdPosition(db.Model, BaseModelMixin):
    __tablename__ = 'ad_position'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    size_id = db.Column(db.Integer, db.ForeignKey('ad_size.id'))
    size = db.relationship('AdSize', backref=db.backref('adPositions', lazy='dynamic'))
    status = db.Column(db.Integer)
    level = db.Column(db.Integer)
    units = db.relationship('AdUnit', secondary=ad_position_unit_table,
                            backref=db.backref('positions', lazy='dynamic'))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship('Medium', backref=db.backref('positions', lazy='dynamic'))
    ad_type = db.Column(db.Integer)
    cpd_num = db.Column(db.Integer)
    max_order_num = db.Column(db.Integer)
    price = db.Column(db.Integer)

    def __init__(self, name, description, size, status, medium,
                 level=POSITION_LEVEL_A1, ad_type=AD_TYPE_NORMAL,
                 cpd_num=1, max_order_num=0, price=0):
        self.name = name
        self.description = description
        self.size = size
        self.status = status
        self.medium = medium
        self.level = level
        self.ad_type = ad_type
        self.cpd_num = cpd_num
        self.max_order_num = max_order_num
        self.price = price

    def __repr__(self):
        return '<AdPosition %s>' % (self.name)

    @property
    def status_cn(self):
        return STATUS_CN[self.status]

    @property
    def display_name(self):
        return "%s-%s-%s" % (self.name, self.level_cn, self.medium.name)

    @property
    def level_cn(self):
        return POSITION_LEVEL_CN[self.level]

    @property
    def ad_type_cn(self):
        return AD_TYPE_CN[self.ad_type]

    def is_cpd(self):
        return self.ad_type == AD_TYPE_CPD

    @property
    def estimate_num(self):
        """
        预估量是所有广告单元一天预估量的和, 表示这个位置最大投放量,
        所以拥有同相同广告单元的位置不能同时预订, 否则可能会超
        所以每个展示位置需要制定一个最大预订值
        """
        return sum([x.estimate_num for x in self.units])

    @property
    def estimate_num_per_cpd(self):
        """
        平均每个CPD的预估量
        """
        return self.estimate_num / self.cpd_num if self.cpd_num > 1 else self.estimate_num

    def schedules_by_date(self, _date):
        return [x.schedule_by_date(_date)
                for x in self.order_items if x.schedule_by_date(_date)]

    def schedule_num(self, _date):
        """
        该位置的已经预订的量,
        通过所有预订这个位置的订单项的这一天的量计算
        """
        schedules = self.schedules_by_date(_date)
        return sum([s.num for s in schedules])

    def retain_num(self, date):
        """剩余量, 所有广告单元的剩余量"""
        return sum([x.retain_num(date) for x in self.units])

    def can_order_num(self, date):
        """可预订量"""
        return min(self.max_order_num, self.retain_num(date))

    def check_order_num(self, date, num):
        return num <= self.order_num(date)

    def can_order_num_schedule(self, start_date, end_date):
        """在start和end之间可以预订的量"""
        days = (end_date - start_date).days + 1
        schedules = [(start_date + timedelta(days=n), self.can_order_num(start_date + timedelta(days=n)))
                     for n in range(days)]
        return schedules

    def get_schedule(self, start_date, end_date):
        """格式化预订量"""
        ret = {"position": self.id,
               "name": self.display_name,
               "start": start_date.strftime(DATE_FORMAT),
               "end": end_date.strftime(DATE_FORMAT)}
        ret['schedules'] = [schdule_info(_date, num)
                            for _date, num in self.can_order_num_schedule(start_date, end_date)]
        return ret


def schdule_info(date, num):
    return (date.strftime(DATE_FORMAT), num, date.isoweekday())
