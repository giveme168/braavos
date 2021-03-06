# -*- coding: UTF-8 -*-
import datetime
from flask import url_for

from . import db, BaseModelMixin
from models.mixin.attachment import AttachmentMixin
from models.mixin.comment import CommentMixin
from models.client_order import ClientOrder
from models.douban_order import DoubanOrder
from models.framework_order import FrameworkOrder
from models.invoice import AgentInvoice
from consts import CLIENT_INDUSTRY_CN


FILE_TYPE_LICENCE = 100  # 营业执照
FILE_TYPE_F_CERTIFICATE = 101  # 税务登记证
FILE_TYPE_O_CERTIFICATE = 102  # 组织机构代码证
FILE_TYPE_TAX_CERTIFICATE = 103  # 一般纳税人证明
FILE_TYPE_T_INFO = 104  # 盖章的开票信息
FILE_TYPE_A_LICENCE = 105  # 开户许可证

FILE_TYPE_CN = {
    FILE_TYPE_LICENCE: u'营业执照',
    FILE_TYPE_F_CERTIFICATE: u'税务登记证',
    FILE_TYPE_O_CERTIFICATE: u'组织机构代码证',
    FILE_TYPE_TAX_CERTIFICATE: u'一般纳税人证明',
    FILE_TYPE_T_INFO: u'盖章的开票信息',
    FILE_TYPE_A_LICENCE: u'开户许可证'
}


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

    def get_agent_count(self):
        return Agent.query.filter_by(group_id=self.id).count()

    def get_framework_order_count(self):
        return FrameworkOrder.query.filter_by(group_id=self.id).count()

    @classmethod
    def name_exist(cls, name):
        is_exist = Group.query.filter_by(name=name).count() > 0
        return is_exist


class Agent(db.Model, BaseModelMixin, AttachmentMixin, CommentMixin):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    group_id = db.Column(db.Integer, db.ForeignKey('bra_group.id'))
    group = db.relationship('Group', backref=db.backref('agents', lazy='dynamic'))
    tax_num = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(100))  # 地址
    phone_num = db.Column(db.String(100))  # 电话
    bank = db.Column(db.String(100))  # 银行
    bank_num = db.Column(db.String(100))  # 银行号
    contact = db.Column(db.String(50))  # 公司内部联系人
    contact_phone = db.Column(db.String(100))  # 公司内部联系人电话
    rebates = db.relationship('AgentRebate')

    def __init__(self, name, group=None,
                 tax_num="", address="", phone_num="",
                 bank="", bank_num="", contact="", contact_phone=""):
        self.name = name
        self.group = group
        self.tax_num = tax_num
        self.address = address
        self.phone_num = phone_num
        self.bank = bank
        self.bank_num = bank_num
        self.contact = contact
        self.contact_phone = contact_phone

    @classmethod
    def name_exist(cls, name):
        is_exist = Agent.query.filter_by(name=name).count() > 0
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
                'bank_num': self.bank_num or ''}

    def inad_rebate_by_year(self, year):
        rebate = [k for k in self.rebates if k.year.year == int(year)]
        if len(rebate) > 0:
            return rebate[0].inad_rebate
        return 0

    def douban_rebate_by_year(self, year):
        rebate = [k for k in self.rebates if k.year.year == int(year)]
        if len(rebate) > 0:
            return rebate[0].douban_rebate
        return 0

    def get_client_order_count(self):
        return ClientOrder.query.filter_by(agent_id=self.id).count()

    def get_douban_order_count(self):
        return DoubanOrder.query.filter_by(agent_id=self.id).count()

    def get_framework_order_count(self):
        return len([k for k in FrameworkOrder.all() if self in k.agents])

    def get_agent_invoice_count(self):
        return AgentInvoice.query.filter_by(agent_id=self.id).count()

    def agent_path(self):
        return url_for('client.agent_detail', agent_id=self.id)


class AgentRebate(db.Model, BaseModelMixin):
    __tablename__ = 'bra_agent_rebate'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 代理公司id
    agent = db.relationship('Agent', backref=db.backref('agentrebate', lazy='dynamic'))

    inad_rebate = db.Column(db.Float)
    douban_rebate = db.Column(db.Float)
    year = db.Column(db.Date)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_agent_rebate', lazy='dynamic'))
    create_time = db.Column(db.DateTime)  # 添加时间
    __table_args__ = (db.UniqueConstraint('agent_id', 'year', name='_agent_rebate_year'),)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, agent, inad_rebate=0.0, douban_rebate=0.0, year=None, creator=None, create_time=None):
        self.agent = agent
        self.inad_rebate = inad_rebate
        self.douban_rebate = douban_rebate
        self.year = year or datetime.date.tody()
        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    def __repr__(self):
        return '<AgentRebate %s>' % (self.id)

    @property
    def create_time_cn(self):
        return self.create_time.strftime("%Y-%m-%d")


class AgentMediumRebate(db.Model, BaseModelMixin):
    __tablename__ = 'bra_agent_medium_rebate'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 代理公司id
    agent = db.relationship('Agent', backref=db.backref('agent_medium_rebate', lazy='dynamic'))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))  # 媒体 该字段已废除
    medium = db.relationship('Medium', backref=db.backref('medium_agent_rebate', lazy="dynamic"))
    medium_name = db.Column(db.String(100))
    rebate = db.Column(db.Float)
    year = db.Column(db.Date)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_medium_agent_rebate', lazy='dynamic'))
    create_time = db.Column(db.DateTime)  # 添加时间
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, agent, medium, medium_name='', rebate=0.0, year=None, creator=None, create_time=None):
        self.agent = agent
        self.medium = medium
        self.medium_name = medium_name
        self.rebate = rebate
        self.year = year or datetime.date.tody()
        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    @property
    def create_time_cn(self):
        return self.create_time.strftime("%Y-%m-%d")


def framework_generator(num):
    code = "ZQC%s%03x" % (datetime.datetime.now().strftime('%Y%m'), num % 1000)
    code = code.upper()
    return code
