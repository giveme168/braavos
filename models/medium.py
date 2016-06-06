# -*- coding: utf-8 -*-
import itertools
import datetime
from datetime import timedelta

from flask import json, url_for

from . import db, BaseModelMixin
from .consts import STATUS_CN, DATE_FORMAT
from models.mixin.delivery import DeliveryMixin
from models.item import OCCUPY_RESOURCE_STATUS, ITEM_STATUS_ORDER
from models.order import Order, MediumOrderExecutiveReport
from models.mixin.attachment import AttachmentMixin
from models.mixin.comment import CommentMixin


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

ad_position_unit_table = db.Table('ad_position_unit',
                                  db.Column(
                                      'position_id', db.Integer, db.ForeignKey('ad_position.id')),
                                  db.Column(
                                      'unit_id', db.Integer, db.ForeignKey('ad_unit.id'))
                                  )

LEVEL_S = 1
LEVEL_A = 2
LEVEL_B = 3
LEVEL_C = 4
LEVEL_OTHER = 100
LEVEL_CN = {
    LEVEL_S: u"S级",
    LEVEL_A: u"A级",
    LEVEL_B: u"B级",
    LEVEL_C: u"C级",
    LEVEL_OTHER: u"其他"
}


class Medium(db.Model, BaseModelMixin, CommentMixin, AttachmentMixin):
    __tablename__ = 'medium'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    abbreviation = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    owner = db.relationship(
        'Team', backref=db.backref('mediums', lazy='dynamic'))
    level = db.Column(db.Integer)
    tax_num = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(100))  # 地址
    phone_num = db.Column(db.String(100))  # 电话
    bank = db.Column(db.String(100))  # 银行
    bank_num = db.Column(db.String(100))  # 银行号
    rebates = db.relationship('MediumRebate')
    __mapper_args__ = {'order_by': id.desc()}

    def __init__(self, name, owner, level=100, abbreviation=None, tax_num="",
                 address="", phone_num="", bank="", bank_num=""):
        self.name = name
        self.owner = owner
        self.level = level
        self.abbreviation = abbreviation or ""
        self.tax_num = tax_num
        self.address = address
        self.phone_num = phone_num
        self.bank = bank
        self.bank_num = bank_num

    def positions_info_by_date(self):
        return positions_info(self.positions)

    @classmethod
    def name_exist(cls, name):
        is_exist = Medium.query.filter_by(name=name).count() > 0
        return is_exist

    @property
    def current_framework(self):
        return framework_generator(self.id)

    @property
    def direct_framework(self):
        return direct_generator(self.id)

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
        return sum([k.sale_money for k in MediumOrderExecutiveReport.query.join(Order).filter(
            Order.medium_id == self.id, MediumOrderExecutiveReport.month_day == month_day) if k.status == 1])

    def sale_money_report_by_year(self):
        start_month_day = datetime.datetime.now().replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_month_day = start_month_day.replace(
            month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum([k.sale_money for k in MediumOrderExecutiveReport.query.join(Order).filter(
            Order.medium_id == self.id, MediumOrderExecutiveReport.month_day >= start_month_day,
            MediumOrderExecutiveReport.month_day <= end_month_day) if k.status == 1])

    def medium_money2_report_by_month(self, month):
        month_day = datetime.datetime.now().replace(
            month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum([k.medium_money2 for k in MediumOrderExecutiveReport.query.join(Order).filter(
            Order.medium_id == self.id, MediumOrderExecutiveReport.month_day == month_day) if k.status == 1])

    def medium_money2_report_by_year(self):
        start_month_day = datetime.datetime.now().replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_month_day = start_month_day.replace(
            month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum([k.medium_money2 for k in MediumOrderExecutiveReport.query.join(Order).filter(
            Order.medium_id == self.id, MediumOrderExecutiveReport.month_day >= start_month_day,
            MediumOrderExecutiveReport.month_day <= end_month_day) if k.status == 1])

    def rebate_by_year(self, year):
        rebate = [k for k in self.rebates if k.year.year == int(year)]
        if len(rebate) > 0:
            return rebate[0].rebate
        return 0

    @property
    def files_update_time(self):
        all_files = list(self.get_medium_files())
        if all_files:
            update_time = all_files[
                0].create_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            update_time = ''
        return update_time

    @property
    def level_cn(self):
        return LEVEL_CN[self.level or 100]

    def medium_path(self):
        return url_for('client.medium_detail', medium_id=self.id)


class MediumRebate(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_rebate'

    id = db.Column(db.Integer, primary_key=True)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))  # 媒体id
    medium = db.relationship(
        'Medium', backref=db.backref('mediumrebate', lazy='dynamic'))
    rebate = db.Column(db.Float)
    year = db.Column(db.Date)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_medium_rebate', lazy='dynamic'))
    create_time = db.Column(db.DateTime)   # 添加时间
    __table_args__ = (
        db.UniqueConstraint('medium_id', 'year', name='_medium_rebate_year'),)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, medium, rebate=0.0, year=None, creator=None, create_time=None):
        self.medium = medium
        self.rebate = rebate
        self.year = year or datetime.date.today()
        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    def __repr__(self):
        return '<MediumRebate %s>' % (self.id)

    @property
    def create_time_cn(self):
        return self.create_time.strftime("%Y-%m-%d")


def framework_generator(num):
    code = "ZQM%s%03x" % (datetime.datetime.now().strftime('%Y%m'), num % 1000)
    code = code.upper()
    return code


def direct_generator(num):
    code = "ZQD%s%03x" % (datetime.datetime.now().strftime('%Y%m'), num % 1000)
    code = code.upper()
    return code


COOPERATION_TYPE_ONLY = 1
COOPERATION_TYPE_NO_ONLY = 0
COOPERATION_TYPE_CN = {
    COOPERATION_TYPE_ONLY: u'独家',
    COOPERATION_TYPE_NO_ONLY: u'非独家',
}


class MediumProductPC(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_product_pc'
    id = db.Column(db.Integer, primary_key=True)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('medium_product_pc', lazy='dynamic'))
    name = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    register_count = db.Column(db.Integer, default=0)
    alone_count_by_day = db.Column(db.Integer, default=0)
    active_count_by_day = db.Column(db.Integer, default=0)
    alone_count_by_month = db.Column(db.Integer, default=0)
    active_count_by_month = db.Column(db.Integer, default=0)
    pv_by_day = db.Column(db.Integer, default=0)
    pv_by_month = db.Column(db.Integer, default=0)
    access_time = db.Column(db.Integer, default=0)           # 访问时长
    ugc_count = db.Column(db.Integer, default=0)
    cooperation_type = db.Column(db.Integer, default=1)      # 合作方式
    divide_into = db.Column(db.Float, default=0)           # 分成比例
    policies = db.Column(db.Float, default=0)              # 折扣政策
    delivery = db.Column(db.String(255), default="")         # 配送政策
    special = db.Column(db.String(255), default="")          # 特殊情况说明
    sex_distributed = db.Column(db.String(255), default="")  # 性别分布
    age_distributed = db.Column(db.String(255), default="")  # 年龄分布
    area_distributed = db.Column(db.String(255), default="")  # 地域分布
    education_distributed = db.Column(db.String(255), default="")  # 学历分布
    income_distributed = db.Column(db.String(255), default="")     # 收入分布
    product_position = db.Column(db.String(255), default="")       # 产品定位
    body = db.Column(db.Text(), default=json.dumps([]))
    __table_args__ = (db.UniqueConstraint(
        'medium_id', 'name', name='_medium_product_pc_id_name_unique'),)
    __mapper_args__ = {'order_by': update_time.desc()}

    def __init__(self, medium, name, create_time, update_time, register_count, alone_count_by_day,
                 active_count_by_day, alone_count_by_month, active_count_by_month, pv_by_day,
                 pv_by_month, access_time, ugc_count, cooperation_type, divide_into, policies,
                 delivery, special, sex_distributed, age_distributed, area_distributed,
                 education_distributed, income_distributed, product_position, body=None):
        self.medium = medium
        self.name = name
        self.create_time = create_time or datetime.datetime.now()
        self.update_time = update_time or datetime.datetime.now()
        self.register_count = register_count
        self.alone_count_by_day = alone_count_by_day
        self.active_count_by_day = active_count_by_day
        self.alone_count_by_month = alone_count_by_month
        self.active_count_by_month = active_count_by_month
        self.pv_by_day = pv_by_day
        self.pv_by_month = pv_by_month
        self.access_time = access_time
        self.ugc_count = ugc_count
        self.cooperation_type = cooperation_type
        self.divide_into = divide_into
        self.delivery = delivery
        self.special = special
        self.sex_distributed = sex_distributed
        self.area_distributed = area_distributed
        self.age_distributed = age_distributed
        self.education_distributed = education_distributed
        self.income_distributed = income_distributed
        self.product_position = product_position
        self.policies = policies
        self.body = body or json.dumps([])

    @property
    def update_time_cn(self):
        return self.update_time.strftime(DATE_FORMAT)

    @property
    def cooperation_type_cn(self):
        if self.cooperation_type:
            return u'独家'
        else:
            return u'非独家'


class MediumProductApp(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_product_app'
    id = db.Column(db.Integer, primary_key=True)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('medium_product_app', lazy='dynamic'))
    name = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    install_count = db.Column(db.Integer, default=0)          # 安装量
    activation_count = db.Column(db.Integer, default=0)       # 激活量
    register_count = db.Column(db.Integer, default=0)
    active_count_by_day = db.Column(db.Integer, default=0)    # 日活用户
    active_count_by_month = db.Column(db.Integer, default=0)  # 月活用户
    pv_by_day = db.Column(db.Integer, default=0)
    pv_by_month = db.Column(db.Integer, default=0)
    open_rate_by_day = db.Column(db.Float, default=0)         # 日打开率
    access_time = db.Column(db.Float, default=0)              # 访问时长
    sex_distributed = db.Column(db.String(255), default="")   # 性别分布
    age_distributed = db.Column(db.String(255), default="")   # 年龄分布
    area_distributed = db.Column(db.String(255), default="")  # 地域分布
    education_distributed = db.Column(db.String(255), default="")  # 学历分布
    income_distributed = db.Column(db.String(255), default="")     # 收入分布
    ugc_count = db.Column(db.Integer, default=0)
    cooperation_type = db.Column(db.Integer, default=1)      # 合作方式
    divide_into = db.Column(db.Float, default=0)           # 分成比例
    policies = db.Column(db.Float, default=0)              # 折扣政策
    delivery = db.Column(db.String(255), default="")         # 配送政策
    special = db.Column(db.String(255), default="")          # 特殊情况说明
    product_position = db.Column(db.String(255), default="")       # 产品定位
    body = db.Column(db.Text(), default=json.dumps([]))
    __table_args__ = (db.UniqueConstraint(
        'medium_id', 'name', name='_medium_product_app_id_name_unique'),)
    __mapper_args__ = {'order_by': update_time.desc()}

    def __init__(self, medium, name, create_time, update_time, register_count, install_count,
                 active_count_by_day, active_count_by_month, pv_by_day, activation_count,
                 pv_by_month, access_time, ugc_count, cooperation_type, divide_into, policies,
                 delivery, special, sex_distributed, age_distributed, area_distributed,
                 education_distributed, income_distributed, product_position, open_rate_by_day,
                 body=None):
        self.medium = medium
        self.name = name
        self.create_time = create_time or datetime.datetime.now()
        self.update_time = update_time or datetime.datetime.now()
        self.register_count = register_count
        self.install_count = install_count
        self.activation_count = activation_count
        self.active_count_by_day = active_count_by_day
        self.active_count_by_month = active_count_by_month
        self.pv_by_day = pv_by_day
        self.pv_by_month = pv_by_month
        self.open_rate_by_day = open_rate_by_day
        self.access_time = access_time
        self.ugc_count = ugc_count
        self.cooperation_type = cooperation_type
        self.divide_into = divide_into
        self.delivery = delivery
        self.special = special
        self.sex_distributed = sex_distributed
        self.area_distributed = area_distributed
        self.age_distributed = age_distributed
        self.education_distributed = education_distributed
        self.income_distributed = income_distributed
        self.product_position = product_position
        self.policies = policies
        self.body = body or json.dumps([])

    @property
    def update_time_cn(self):
        return self.update_time.strftime(DATE_FORMAT)

    @property
    def cooperation_type_cn(self):
        if self.cooperation_type:
            return u'独家'
        else:
            return u'非独家'


class MediumProductDown(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_product_down'
    id = db.Column(db.Integer, primary_key=True)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('medium_product_down', lazy='dynamic'))
    name = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(100))  # 举办地点
    subject = db.Column(db.String(255))  # 主题
    before_year_count = db.Column(db.Integer, default=0)           # 往年人数
    now_year_count = db.Column(db.Integer, default=0)              # 今年人数
    sex_distributed = db.Column(db.String(255), default="")        # 性别分布
    age_distributed = db.Column(db.String(255), default="")        # 年龄分布
    area_distributed = db.Column(db.String(255), default="")       # 地域分布
    education_distributed = db.Column(db.String(255), default="")  # 学历分布
    income_distributed = db.Column(db.String(255), default="")     # 收入分布
    cooperation_type = db.Column(db.Integer, default=1)      # 合作方式
    divide_into = db.Column(db.Float, default=0)           # 分成比例
    policies = db.Column(db.Float, default=0)              # 折扣政策
    delivery = db.Column(db.String(255), default="")         # 配送政策
    special = db.Column(db.String(255), default="")          # 特殊情况说明
    product_position = db.Column(db.String(255), default="")       # 产品定位
    business_start_time = db.Column(db.DateTime)
    business_end_time = db.Column(db.DateTime)
    body = db.Column(db.Text(), default=json.dumps([]))
    __table_args__ = (db.UniqueConstraint(
        'medium_id', 'name', name='_medium_product_down_id_name_unique'),)
    __mapper_args__ = {'order_by': update_time.desc()}

    def __init__(self, medium, name, create_time, update_time, start_time, end_time, location,
                 subject, before_year_count, now_year_count, sex_distributed, age_distributed,
                 area_distributed, education_distributed, income_distributed, cooperation_type,
                 divide_into, policies, delivery, special, product_position, business_start_time,
                 business_end_time, body=None):
        self.name = name
        self.medium = medium
        self.create_time = create_time
        self.update_time = update_time
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.subject = subject
        self.before_year_count = before_year_count
        self.now_year_count = now_year_count
        self.sex_distributed = sex_distributed
        self.age_distributed = age_distributed
        self.area_distributed = area_distributed
        self.education_distributed = education_distributed
        self.income_distributed = income_distributed
        self.cooperation_type = cooperation_type
        self.divide_into = divide_into
        self.policies = policies
        self.delivery = delivery
        self.special = special
        self.product_position = product_position
        self.business_end_time = business_end_time
        self.business_start_time = business_start_time
        self.body = body or json.dumps([])

    @property
    def update_time_cn(self):
        return self.update_time.strftime(DATE_FORMAT)

    @property
    def cooperation_type_cn(self):
        if self.cooperation_type:
            return u'独家'
        else:
            return u'非独家'

    @property
    def start_time_cn(self):
        return self.start_time.strftime('%Y-%m-%d %H:%M')

    @property
    def end_time_cn(self):
        return self.end_time.strftime('%Y-%m-%d %H:%M')

    @property
    def business_start_time_cn(self):
        return self.business_start_time.strftime('%Y-%m-%d %H:%M')

    @property
    def business_end_time_cn(self):
        return self.business_end_time.strftime('%Y-%m-%d %H:%M')


MEDIUM_RESOURCE_TYPE_PC = 1
MEDIUM_RESOURCE_TYPE_APP = 2
MEDIUM_RESOURCE_TYPE_DOWN = 3
MEDIUM_RESOURCE_TYPE_CN = {
    MEDIUM_RESOURCE_TYPE_PC: u'PC端',
    MEDIUM_RESOURCE_TYPE_APP: u'移动端',
    MEDIUM_RESOURCE_TYPE_DOWN: u'线下活动',
}

MEDIUM_RESOURCE_TYPE_INT = {
    'pc': 1,
    'app': 2,
    'down': 3,
}


SHAP_INTERNET = 1
SHAP_CN = {
    SHAP_INTERNET: u'互联网'
}

RESOURCE_TYPE_AD = 1
RESOURCE_TYPE_CAMPAIGN = 2
RESOURCE_TYPE_SPECIAL = 3
RESOURCE_TYPE_OTHER = 4
RESOURCE_TYPE_CN = {
    RESOURCE_TYPE_AD: u"硬广",
    RESOURCE_TYPE_CAMPAIGN: u"互动",
    RESOURCE_TYPE_SPECIAL: u"特殊",
    RESOURCE_TYPE_OTHER: u"其他"
}

BUY_UNIT_NONE = 0
BUY_UNIT_CPM = 1
BUY_UNIT_THOUSAND_WEEK = 2
BUY_UNIT_PHASE = 3
BUY_UNIT_THOUSAND = 4
BUY_UNIT_DAY = 5


BUY_UNIT_CN = {
    BUY_UNIT_NONE: u'无',
    BUY_UNIT_CPM: u'CPM',
    BUY_UNIT_THOUSAND_WEEK: u'千份（周）',
    BUY_UNIT_PHASE: u'期',
    BUY_UNIT_THOUSAND: u'千份',
    BUY_UNIT_DAY: u'天',
}

DIRECTIONAL_TYPE_NONE = 0
DIRECTIONAL_TYPE_AREA = 1
DIRECTIONAL_TYPE_TOPIC = 2
DIRECTIONAL_TYPE_TOPIC_AND_AREA = 3
DIRECTIONAL_TYPE_OTHER = 10
DIRECTIONAL_TYPE_CN = {
    DIRECTIONAL_TYPE_NONE: u'无',
    DIRECTIONAL_TYPE_AREA: u'地域',
    DIRECTIONAL_TYPE_TOPIC: u'话题',
    DIRECTIONAL_TYPE_TOPIC_AND_AREA: u'地域、话题',
    DIRECTIONAL_TYPE_OTHER: u'其他',
}


LESS_BUY_NONE = 0
LESS_BUY_1000 = 1
LESS_BUY_CN = {
    LESS_BUY_NONE: u'无限制',
    LESS_BUY_1000: u'不低于1000CPM',
}

B_FALSE = 0
B_TURE = 1
B_CN = {
    B_FALSE: u'否',
    B_TURE: u'是',
}


class MediumResource(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_resource'
    id = db.Column(db.Integer, primary_key=True)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('medium_resource', lazy='dynamic'))
    type = db.Column(db.Integer, default=1)       # 资源类型
    number = db.Column(db.String(20), default="")     # 编号
    shape = db.Column(db.Integer, default=1)      # 形态
    product = db.Column(db.Integer, default=0)    # 所属产品
    resource_type = db.Column(db.Integer)         # 资源形式
    page_postion = db.Column(db.String(450))      # 页面位置
    ad_position = db.Column(db.String(450))       # 广告位置
    cpm = db.Column(db.Float)
    b_click = db.Column(db.Integer, default=1)    # 是否可点击
    click_rate = db.Column(db.Float, default=0)   # 点击率
    buy_unit = db.Column(db.Integer, default=1)   # 购买单位
    buy_threshold = db.Column(db.String(450), default="")   # 购买门槛
    money = db.Column(db.Float, default=0)        # 刊例单价
    b_directional = db.Column(db.Integer, default=1)        # 是否可定向
    directional_type = db.Column(db.Integer, default=1)     # 定向类型
    directional_money = db.Column(db.Float, default=0)      # 定向价格
    discount = db.Column(db.Float, default=0)     # 折扣
    ad_size = db.Column(db.String(450))           # 广告尺寸
    materiel_format = db.Column(db.String(450))   # 物料格式
    less_buy = db.Column(db.Integer, default=0)   # 最小购买值
    b_give = db.Column(db.Integer, default=0)     # 是否可配送
    give_desc = db.Column(db.String(450))         # 配送门槛
    b_check_exposure = db.Column(db.Integer, default=0)     # 是否可监测曝光
    b_check_click = db.Column(db.Integer, default=0)        # 是否个监测点击
    b_out_link = db.Column(db.Integer, default=0)           # 是否可外链
    b_in_link = db.Column(db.Integer, default=0)            # 是否可内链
    description = db.Column(db.String(450))       # 描述
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    body = db.Column(db.Text(), default=json.dumps([]))
    __mapper_args__ = {'order_by': update_time.desc()}

    def __init__(self, medium, type, number, shape, product, resource_type, page_postion,
                 ad_position, cpm, b_click, click_rate, buy_unit, buy_threshold, money,
                 b_directional, directional_type, directional_money, discount, ad_size,
                 materiel_format, less_buy, b_give, give_desc, b_check_exposure, description,
                 b_check_click, b_out_link, b_in_link, create_time, update_time, body):
        self.medium = medium
        self.type = type
        self.number = number
        self.shape = shape
        self.product = product
        self.resource_type = resource_type
        self.page_postion = page_postion
        self.ad_position = ad_position
        self.cpm = cpm
        self.b_click = b_click
        self.click_rate = click_rate
        self.buy_unit = buy_unit
        self.buy_threshold = buy_threshold
        self.money = money
        self.b_directional = b_directional
        self.directional_type = directional_type
        self.directional_money = directional_money
        self.discount = discount
        self.ad_size = ad_size
        self.materiel_format = materiel_format
        self.less_buy = less_buy
        self.b_give = b_give
        self.give_desc = give_desc
        self.b_check_exposure = b_check_exposure
        self.description = description
        self.b_check_click = b_check_click
        self.b_out_link = b_out_link
        self.b_in_link = b_in_link
        self.create_time = create_time
        self.update_time = update_time
        self.body = body or json.dumps([])

    @property
    def type_cn(self):
        return MEDIUM_RESOURCE_TYPE_CN[self.type]

    @property
    def shape_cn(self):
        return SHAP_CN[self.shape]

    @property
    def resource_type_cn(self):
        return RESOURCE_TYPE_CN[self.resource_type]

    @property
    def b_click_cn(self):
        return B_CN[self.b_click]

    @property
    def buy_unit_cn(self):
        return BUY_UNIT_CN[self.buy_unit]

    @property
    def b_directional_cn(self):
        return B_CN[self.b_directional]

    @property
    def less_buy_cn(self):
        return LESS_BUY_CN[self.less_buy]

    @property
    def b_give_cn(self):
        return B_CN[self.b_give]

    @property
    def b_check_exposure_cn(self):
        return B_CN[self.b_check_exposure]

    @property
    def b_check_click_cn(self):
        return B_CN[self.b_check_click]

    @property
    def b_out_link_cn(self):
        return B_CN[self.b_out_link]

    @property
    def b_in_link_cn(self):
        return B_CN[self.b_in_link]

    @property
    def directional_type_cn(self):
        return DIRECTIONAL_TYPE_CN[self.directional_type]


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

    def __eq__(self, other):
        return self.width == other.width and self.height == other.height

    @property
    def name(self):
        return "%s x %s" % (self.width, self.height)


class AdUnit(db.Model, BaseModelMixin, DeliveryMixin):
    __tablename__ = 'ad_unit'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    size_id = db.Column(db.Integer, db.ForeignKey('ad_size.id'))
    size = db.relationship(
        'AdSize', backref=db.backref('adUnits', lazy='dynamic'))
    margin = db.Column(db.String(50))
    target = db.Column(db.Integer)
    status = db.Column(db.Integer)
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('units', lazy='dynamic'))
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
    def target_cn(self):
        return TARGET_CN[self.target]

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
        return int(round(sum([x.schedule_num(date) * (float(self.estimate_num) / x.estimate_num)
                              for x in self.positions])))

    def retain_num(self, date):
        retain_num = self.estimate_num - self.schedule_num(date)
        return max(retain_num, 0)

    def schedule_nums_by_dates(self, dates_list):
        position_s_nums = [
            (p.schedule_nums_by_dates(dates_list), p.estimate_num) for p in self.positions]
        # 每个位置在时间段内每天分配到当前unit的预订量
        position_to_nuit_nums = []
        for nums, e_num in position_s_nums:
            position_to_nuit_nums.append(
                [num * (float(self.estimate_num) / e_num) for num in nums])
        temp = map(list, itertools.izip(*position_to_nuit_nums))
        return [int(round(sum(num))) for num in temp]

    def retain_nums_by_dates(self, dates_list):
        schedule_nums = self.schedule_nums_by_dates(dates_list)
        return [self.estimate_num - num for num in schedule_nums]

    @property
    def order_items(self):
        """所有关联的订单项"""
        _items = []
        for p in self.positions:
            for i in p.order_items:
                _items.append(i)
        return _items

    def online_order_items_by_date(self, _date):
        return [i for i in self.order_items if i.is_online_by_date(_date)]


class AdPosition(db.Model, BaseModelMixin):
    __tablename__ = 'ad_position'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    size_id = db.Column(db.Integer, db.ForeignKey('ad_size.id'))
    size = db.relationship(
        'AdSize', backref=db.backref('adPositions', lazy='dynamic'))
    standard = db.Column(db.String(100))
    status = db.Column(db.Integer)
    level = db.Column(db.Integer)
    units = db.relationship('AdUnit', secondary=ad_position_unit_table,
                            backref=db.backref('positions', lazy='dynamic'))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('positions', lazy='dynamic'))
    ad_type = db.Column(db.Integer)
    cpd_num = db.Column(db.Integer)
    max_order_num = db.Column(db.Integer)
    price = db.Column(db.Integer)
    launch_strategy = db.Column(db.Integer)

    def __init__(self, name, description, size, standard, status, medium,
                 level=POSITION_LEVEL_A1, ad_type=AD_TYPE_NORMAL, launch_strategy=1, price=0, max_order_num=0):
        self.name = name
        self.description = description
        self.size = size
        self.standard = standard
        self.status = status
        self.medium = medium
        self.level = level
        self.ad_type = ad_type
        self.price = price
        self.max_order_num = max_order_num
        self.launch_strategy = launch_strategy

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

    @property
    def standard_cn(self):
        return "%s-%s" % (self.size.name, self.standard)

    def schedules_by_date(self, _date):
        return [x.schedule_by_date(_date)
                for x in self.order_items if x.schedule_by_date(_date)]

    def schedule_num(self, _date):
        """
        该位置的已经预订的量,
        通过所有预订这个位置的订单项的这一天的量计算
        """
        schedules = self.schedules_by_date(_date)
        return sum([s.num for s in schedules if s.item.item_status in OCCUPY_RESOURCE_STATUS])

    def schedule_nums_by_dates(self, dates_list):
        # 每个item在时间段内每天的已预订量
        item_nums = [
            i.schedule_sums_by_dates(dates_list) for i in self.order_items
            if i.item_status in OCCUPY_RESOURCE_STATUS]
        if not item_nums:
            return [0] * len(dates_list)
        temp = map(list, itertools.izip(*item_nums))
        return [sum(d) for d in temp]

    def ordered_num(self, _date):
        """该位置的已经下单的量"""
        schedules = self.schedules_by_date(_date)
        return sum([s.num for s in schedules if s.item.item_status == ITEM_STATUS_ORDER])

    @property
    def suitable_units(self):
        return AdUnit.query.filter_by(medium_id=self.medium.id, size=self.size)

    def retain_num(self, date):
        """剩余量, 所有广告单元的剩余量"""
        return sum([x.retain_num(date) for x in self.units])

    def can_order_num(self, date):
        """可预订量"""
        return min(self.max_order_num, self.retain_num(date))

    def check_order_num(self, date, num):
        return num <= self.can_order_num(date)

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

    def storage_percent_cn(self, percent):
        if percent == EMPTY:
            return OCCUPY_RESOURCE_PRECENT_CN[EMPTY]
        elif percent <= TWENTY_FIVE:
            return OCCUPY_RESOURCE_PRECENT_CN[TWENTY_FIVE]
        elif percent <= FIFTY:
            return OCCUPY_RESOURCE_PRECENT_CN[FIFTY]
        elif percent <= SEVENTY_FIVE:
            return OCCUPY_RESOURCE_PRECENT_CN[SEVENTY_FIVE]
        elif percent <= HUNDERD:
            return OCCUPY_RESOURCE_PRECENT_CN[HUNDERD]
        else:
            return OCCUPY_RESOURCE_PRECENT_CN[ERROR]

    def storage_percent_info(self, start_date, last):
        """得到一个（预订百分比区间，日期）的列表"""
        dates_list = []
        for x in range(0, last):
            current = start_date + timedelta(days=x)
            dates_list.append(current)
        current_nums = self.schedule_nums_by_dates(dates_list)
        units_retains = [u.retain_nums_by_dates(
            dates_list) for u in self.units]
        temp = map(list, itertools.izip(*units_retains))
        retain_nums = [sum(d) for d in temp]
        storage_info = []
        for i in range(0, last):
            min_num = 1 if current_nums[i] > 0 else 0
            percent = max(
                [current_nums[i] * 100 / (retain_nums[i] + current_nums[i]), min_num])
            storage_info.append(
                (self.storage_percent_cn(percent), dates_list[i]))
        return storage_info

    def get_storage_info(self, date):
        ret = {"position": self.id,
               "estimate_num": self.estimate_num,
               "ordered_num": self.ordered_num(date),
               "per_ordered_num": self.schedule_num(date) - self.ordered_num(date),
               "remain_num": self.retain_num(date)}
        ret['orders'] = [order_info(o, self, date)
                         for o in self.get_orders_by_date(date)]
        return ret

    def get_orders_by_date(self, date):
        orders = [
            i.order for i in self.order_items if i.schedule_by_date(date)]
        return list(set(orders))

    @classmethod
    def all_positions_info_by_date(cls):
        return positions_info(cls.all())


def positions_info(positions):
    positions_info = []
    level_dict = sorted(POSITION_LEVEL_CN.iteritems(), key=lambda d: d[0])
    for v, level_cn in level_dict:
        temp_positions = [p for p in positions if p.level == v]
        positions_info.append((v, POSITION_LEVEL_CN[v], temp_positions))
    return positions_info


def schdule_info(date, num):
    return (date.strftime(DATE_FORMAT), num, date.isoweekday())


def order_info(order, position, date):
    order_info_dic = {}
    order_info_dic["name"] = order.name
    order_info_dic["URL"] = order.path()
    order_info_dic["occupy_num"] = order.occupy_num_by_date_position(
        date, position)
    order_info_dic["state_cn"] = "&".join(order.items_status_cn)
    order_info_dic["date_cn"] = u"%s至%s" % (
        order.start_date_cn, order.end_date_cn)
    order_info_dic["special_sale"] = u"是" if order.special_sale_in_position(
        position) else u"否"
    order_info_dic["creator"] = order.creator.name
    return order_info_dic


# 案例标签
class Tag(db.Model, BaseModelMixin):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name


# 案列标签关联表
class TagCase(db.Model, BaseModelMixin):
    __tablename__ = 'bra_tag_case'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    tag = db.relationship(
        'Tag', backref=db.backref('tag_case', lazy='dynamic'))
    case_id = db.Column(db.Integer, db.ForeignKey('bra_case.id'))
    case = db.relationship(
        'Case', backref=db.backref('case_tag', lazy='dynamic'))

CASE_TYPE_CASE = 1
CASE_TYPE_PACKING = 2
CASE_TYPE_CLOSE = 3

CASE_TYPE_CN = {
    CASE_TYPE_CASE: u"策划案",
    CASE_TYPE_PACKING: u"包装案例",
    CASE_TYPE_CLOSE: u"结案报告",
}


case_mediums = db.Table('case_mediums',
                        db.Column(
                            'medium_id', db.Integer, db.ForeignKey('medium.id')),
                        db.Column(
                            'case_id', db.Integer, db.ForeignKey('bra_case.id'))
                        )


# 策划案例
class Case(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'bra_case'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=1)
    name = db.Column(db.String(100))
    url = db.Column(db.String(300))  # 网盘链接
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('case_medium', lazy='dynamic'))  # 这个字段已经废掉了
    mediums = db.relationship('Medium', secondary=case_mediums)
    brand = db.Column(db.String(100))  # 品牌
    industry = db.Column(db.String(100))  # 行业
    create_time = db.Column(db.DateTime)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('case_user', lazy='dynamic'))
    desc = db.Column(db.String(300))
    is_win = db.Column(db.Integer, default=0)
    pwd = db.Column(db.String(20))
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, name, url, type, medium, brand, industry, creator,
                 desc, mediums, pwd=None, create_time=None, is_win=0):
        self.name = name
        self.url = url
        self.type = type
        self.medium = medium
        self.mediums = mediums or []
        self.brand = brand
        self.industry = industry
        self.creator = creator
        self.desc = desc
        self.is_win = is_win
        self.pwd = pwd or ''
        self.create_time = create_time or datetime.datetime.now()

    @property
    def type_cn(self):
        return CASE_TYPE_CN[self.type]

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d')

    @property
    def info(self):
        return '%s%s%s' % (self.name, self.brand, self.desc)

    @property
    def tag_ids(self):
        return [k.tag_id for k in self.case_tag]

    @property
    def tags(self):
        return ','.join([k.tag.name for k in self.case_tag])

    @property
    def mediums_name(self):
        return ','.join([k.name for k in self.mediums])

    @property
    def mediums_id(self):
        return [k.id for k in self.mediums]
