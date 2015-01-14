# -*- coding: UTF-8 -*-
import datetime
from flask import url_for

from . import db, BaseModelMixin
from models.mixin.comment import CommentMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT
from consts import DATE_FORMAT


CONTRACT_TYPE_NORMAL = 0
CONTRACT_TYPE_SPECIAL = 1
CONTRACT_TYPE_CN = {
    CONTRACT_TYPE_NORMAL: u"标准",
    CONTRACT_TYPE_SPECIAL: u"非标"
}

SALE_TYPE_AGENT = 0
SALE_TYPE_DIRECT = 1
SALE_TYPE_CN = {
    SALE_TYPE_AGENT: u"代理",
    SALE_TYPE_DIRECT: u"直签",
}

RESOURCE_TYPE_AD = 0
RESOURCE_TYPE_CAMPAIGN = 1
RESOURCE_TYPE_FRAME = 2
RESOURCE_TYPE_OTHER = 4
RESOURCE_TYPE_CN = {
    RESOURCE_TYPE_AD: u"硬广",
    RESOURCE_TYPE_CAMPAIGN: u"互动",
    #RESOURCE_TYPE_FRAME: u"框架",
    RESOURCE_TYPE_OTHER: u"其他"
}

CONTRACT_STATUS_NEW = 0
CONTRACT_STATUS_APPLYCONTRACT = 1
CONTRACT_STATUS_APPLYPASS = 2
CONTRACT_STATUS_APPLYREJECT = 3
CONTRACT_STATUS_APPLYPRINT = 4
CONTRACT_STATUS_PRINTED = 5
CONTRACT_STATUS_CN = {
    CONTRACT_STATUS_NEW: u"新建",
    CONTRACT_STATUS_APPLYCONTRACT: u"申请合同号中...",
    CONTRACT_STATUS_APPLYPASS: u"申请合同号通过",
    CONTRACT_STATUS_APPLYREJECT: u"申请合同号未通过",
    CONTRACT_STATUS_APPLYPRINT: u"申请打印中...",
    CONTRACT_STATUS_PRINTED: u"打印完毕"
}


direct_sales = db.Table('douban_order_direct_sales',
                        db.Column('direct_sale_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('douban_order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                        )
agent_sales = db.Table('douban_order_agent_sales',
                       db.Column('agent_sale_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('douban_order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                       )

operater_users = db.Table('douban_order_users_operater',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                          )
designer_users = db.Table('douban_order_users_designerer',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                          )
planer_users = db.Table('douban_order_users_planer',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                        )


class DoubanOrder(db.Model, BaseModelMixin, CommentMixin, AttachmentMixin):
    __tablename__ = 'bra_douban_order'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 客户合同甲方
    agent = db.relationship('Agent', backref=db.backref('douban_orders', lazy='dynamic'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))  # 客户
    client = db.relationship('Client', backref=db.backref('douban_orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称

    contract = db.Column(db.String(100))  # 豆瓣合同号
    money = db.Column(db.Integer)  # 客户合同金额
    contract_type = db.Column(db.Integer)  # 合同类型： 标准，非标准
    client_start = db.Column(db.Date)
    client_end = db.Column(db.Date)
    reminde_date = db.Column(db.Date)  # 最迟回款日期

    direct_sales = db.relationship('User', secondary=direct_sales)
    agent_sales = db.relationship('User', secondary=agent_sales)

    operaters = db.relationship('User', secondary=operater_users)
    designers = db.relationship('User', secondary=designer_users)
    planers = db.relationship('User', secondary=planer_users)

    contract_status = db.Column(db.Integer)  # 合同审批状态

    resource_type = db.Column(db.Integer)  # 资源形式
    sale_type = db.Column(db.Integer)  # 资源形式

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_douban_orders', lazy='dynamic'))
    create_time = db.Column(db.DateTime)

    contract_generate = False

    def __init__(self, agent, client, campaign,
                 contract="", money=0, contract_type=CONTRACT_TYPE_NORMAL,
                 client_start=None, client_end=None, reminde_date=None,
                 direct_sales=None, agent_sales=None,
                 operaters=None, designers=None, planers=None,
                 resource_type=RESOURCE_TYPE_AD, sale_type=SALE_TYPE_AGENT,
                 creator=None, create_time=None, contract_status=CONTRACT_STATUS_NEW):
        self.agent = agent
        self.client = client
        self.campaign = campaign

        self.contract = contract
        self.money = money
        self.contract_type = contract_type

        self.client_start = client_start or datetime.date.today()
        self.client_end = client_end or datetime.date.today()
        self.reminde_date = reminde_date or datetime.date.today()

        self.direct_sales = direct_sales or []
        self.agent_sales = agent_sales or []

        self.operaters = operaters or []
        self.designers = designers or []
        self.planers = planers or []

        self.resource_type = resource_type
        self.sale_type = sale_type

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()
        self.contract_status = contract_status

    @property
    def name(self):
        return u"%s-%s" % (self.client.name, self.campaign)

    @property
    def jiafang_name(self):
        return self.agent.name

    @property
    def direct_sales_names(self):
        return ",".join([u.name for u in self.direct_sales])

    @property
    def agent_sales_names(self):
        return ",".join([u.name for u in self.agent_sales])

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.direct_sales + self.agent_sales + [self.creator]
        return user.is_admin() or user in admin_users

    def have_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales + self.agent_sales + [self.creator]
        return user.is_admin() or user in owner

    @classmethod
    def get_order_by_user(cls, user):
        """一个用户可以查看的所有订单"""
        return [o for o in cls.all() if o.have_owner(user)]

    def path(self):
        return url_for('order.order_info', order_id=self.id)

    @property
    def start_date(self):
        return self.client_start

    @property
    def end_date(self):
        return self.client_end

    @property
    def start_date_cn(self):
        return self.start_date.strftime(DATE_FORMAT)

    @property
    def end_date_cn(self):
        return self.end_date.strftime(DATE_FORMAT)

    @property
    def contract_status_cn(self):
        return CONTRACT_STATUS_CN[self.contract_status]

    @property
    def sale_type_cn(self):
        return SALE_TYPE_CN.get(self.sale_type)

    def attachment_path(self):
        return url_for('files.douban_order_files', order_id=self.id)

    def info_path(self):
        return url_for("order.douban_order_info", order_id=self.id)

    def contract_path(self):
        return url_for("order.douban_order_contract", order_id=self.id)

    def attach_status_confirm_path(self, attachment):
        return url_for('order.douban_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_PASSED)

    def attach_status_reject_path(self, attachment):
        return url_for('order.douban_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_REJECT)

    def douban_contract_apply_path(self):
        return url_for("contract.douban_apply", order_id=self.id)