#-*- coding: UTF-8 -*-
from . import db, BaseModelMixin
from .consts import STATUS_CN

TARGET_TOP = 1
TARGET_BLANK = 0
TARGET_CN = {
    TARGET_TOP: u"_top",
    TARGET_BLANK: u"_blank"
}

POSITION_LEVEL_A = 11
POSITION_LEVEL_A2 = 12
POSITION_LEVEL_B = 21
POSITION_LEVEL_B2 = 22
POSITION_LEVEL_C = 31
POSITION_LEVEL_CN = {
    POSITION_LEVEL_A: u"A",
    POSITION_LEVEL_A2: u"A2",
    POSITION_LEVEL_B: u"B",
    POSITION_LEVEL_B2: u"B2",
    POSITION_LEVEL_C: u"C",
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
        self.name = name.title()
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
        self.name = name.title()
        self.description = description.title()
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

    @property
    def schedule_num(self):
        """
        每个展示位置的的预订量按照比例分配到所拥有的广告单元上,
        再加和计算该单元的预订量
        """
        return sum([x.schedule_num * (self.estimate_num / x.estimate_num) for x in self.positions])

    @property
    def retain_num(self):
        retain_num = self.estimate_num - self.schedule_num
        return retain_num if retain_num > 0 else 0


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

    def __init__(self, name, description, size, status, medium, level=POSITION_LEVEL_A, ad_type=AD_TYPE_NORMAL, cpd_num=1):
        self.name = name.title()
        self.description = description.title()
        self.size = size
        self.status = status
        self.medium = medium
        self.level = level
        self.ad_type = ad_type
        self.cpd_num = cpd_num

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
        """预估量为所有广告单元的和"""
        return sum([x.estimate_num for x in self.units])

    @property
    def estimate_num_per_cpd(self):
        """每个CPD的预估量"""
        return self.estimate_num / self.cpd_num if self.cpd_num > 0 else self.estimate_num

    @property
    def schedule_num(self):
        """该位置的排期预订量, 通过所有订单项的排期计算"""
        schedules = []
        for x in self.items:
            schedules.extend(x.schedules)
        return sum([x.num for x in list(set(schedules))])

    @property
    def retain_num(self):
        return sum([x.retain_num for x in self.units])
