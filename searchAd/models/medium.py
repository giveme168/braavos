# -*- coding: utf-8 -*-
import datetime

from flask import url_for

from models import db, BaseModelMixin
from models.mixin.attachment import AttachmentMixin
from models.mixin.comment import CommentMixin
from .order import searchAdOrder, searchAdMediumOrderExecutiveReport

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
LAUNCH_STRATEGY_A = 0
LAUNCH_STRATEGY_B = 1
LAUNCH_STRATEGY = {
    LAUNCH_STRATEGY_A: u"不可定向",
    LAUNCH_STRATEGY_B: u"定向/定投(地域/精准)"
}
AD_TYPE_NORMAL = 0
AD_TYPE_CPD = 1
AD_TYPE_REMNANT = 2

AD_TYPE_CN = {
    AD_TYPE_NORMAL: u"标准/CPM",
    AD_TYPE_CPD: u"CPD",
}

EMPTY = 0
TWENTY_FIVE = 25
FIFTY = 50
SEVENTY_FIVE = 75
HUNDERD = 100
ERROR = 101

OCCUPY_RESOURCE_PRECENT_CN = {
    EMPTY: "",
    TWENTY_FIVE: "twenty-five",
    FIFTY: "fifty",
    SEVENTY_FIVE: "seventy-five",
    HUNDERD: "hundred",
    ERROR: "error"
}

ad_position_unit_table = db.Table('searchAd_ad_position_unit',
                                  db.Column(
                                      'position_id', db.Integer, db.ForeignKey('ad_position.id')),
                                  db.Column(
                                      'unit_id', db.Integer, db.ForeignKey('ad_unit.id'))
                                  )


class searchAdMedium(db.Model, BaseModelMixin, AttachmentMixin, CommentMixin):
    __tablename__ = 'searchAd_medium'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    abbreviation = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    owner = db.relationship(
        'Team', backref=db.backref('searchAd_mediums', lazy='dynamic'))
    tax_num = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(100))  # 地址
    phone_num = db.Column(db.String(100))  # 电话
    bank = db.Column(db.String(100))  # 银行
    bank_num = db.Column(db.String(100))  # 银行号
    rebates = db.relationship('searchAdMediumRebate')
    __mapper_args__ = {'order_by': id.desc()}

    def __init__(self, name, owner, abbreviation=None, tax_num="",
                 address="", phone_num="", bank="", bank_num=""):
        self.name = name
        self.owner = owner
        self.abbreviation = abbreviation or ""
        self.tax_num = tax_num
        self.address = address
        self.phone_num = phone_num
        self.bank = bank
        self.bank_num = bank_num

    @classmethod
    def name_exist(cls, name):
        is_exist = searchAdMedium.query.filter_by(name=name).count() > 0
        return is_exist

    @property
    def current_framework(self):
        return framework_generator(self.id)

    @property
    def tax_info(self):
        return {'tax_num': self.tax_num or '',
                'address': self.address or '',
                'phone_num': self.phone_num or '',
                'bank': self.bank or '',
                'bank_num': self.bank_num or '',
                'abbreviation': self.abbreviation or ''}

    def sale_money_report_by_month(self, month):
        month_day = datetime.datetime.now().replace(
            month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum([k.sale_money for k in searchAdMediumOrderExecutiveReport.query.join(Order).filter(
            searchAdOrder.medium_id == self.id, searchAdMediumOrderExecutiveReport.month_day == month_day) if k.status == 1])

    def sale_money_report_by_year(self):
        start_month_day = datetime.datetime.now().replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_month_day = start_month_day.replace(
            month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum([k.sale_money for k in searchAdMediumOrderExecutiveReport.query.join(Order).filter(
            searchAdOrder.medium_id == self.id, searchAdMediumOrderExecutiveReport.month_day >= start_month_day,
            searchAdMediumOrderExecutiveReport.month_day <= end_month_day) if k.status == 1])

    def medium_money2_report_by_month(self, month):
        month_day = datetime.datetime.now().replace(
            month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum([k.medium_money2 for k in searchAdMediumOrderExecutiveReport.query.join(Order).filter(
            searchAdOrder.medium_id == self.id, searchAdMediumOrderExecutiveReport.month_day == month_day) if k.status == 1])

    def medium_money2_report_by_year(self):
        start_month_day = datetime.datetime.now().replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_month_day = start_month_day.replace(
            month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum([k.medium_money2 for k in searchAdMediumOrderExecutiveReport.query.join(Order).filter(
            searchAdOrder.medium_id == self.id, searchAdMediumOrderExecutiveReport.month_day >= start_month_day,
            searchAdMediumOrderExecutiveReport.month_day <= end_month_day) if k.status == 1])

    def rebate_by_year(self, year):
        rebate = [k for k in self.rebates if k.year.year == int(year)]
        if len(rebate) > 0:
            return rebate[0].rebate
        return 0

    def medium_path(self):
        return url_for('searchAd_client.medium_detail', medium_id=self.id)


class searchAdMediumRebate(db.Model, BaseModelMixin):
    __tablename__ = 'searchAd_bra_medium_rebate'

    id = db.Column(db.Integer, primary_key=True)
    medium_id = db.Column(db.Integer, db.ForeignKey('searchAd_medium.id'))  # 媒体id
    medium = db.relationship(
        'searchAdMedium', backref=db.backref('mediumrebate', lazy='dynamic'))
    rebate = db.Column(db.Float)
    year = db.Column(db.Date)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('searchAd_created_medium_rebate', lazy='dynamic'))
    create_time = db.Column(db.DateTime)   # 添加时间
    __table_args__ = (
        db.UniqueConstraint('medium_id', 'year', name='_searchAd_medium_rebate_year'),)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, medium, rebate=0.0, year=None, creator=None, create_time=None):
        self.medium = medium
        self.rebate = rebate
        self.year = year or datetime.date.today()
        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    def __repr__(self):
        return '<searchAdMediumRebate %s>' % (self.id)

    @property
    def create_time_cn(self):
        return self.create_time.strftime("%Y-%m-%d")


def framework_generator(num):
    code = "ZQSM%s%03x" % (datetime.datetime.now().strftime('%Y%m'), num % 1000)
    code = code.upper()
    return code
