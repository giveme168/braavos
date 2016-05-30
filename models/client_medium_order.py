# -*- coding: UTF-8 -*-
import datetime
from flask import url_for

from . import db, BaseModelMixin
from .user import User, TEAM_LOCATION_CN
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
    SALE_TYPE_DIRECT: u"直客",
}

RESOURCE_TYPE_AD = 0
RESOURCE_TYPE_CAMPAIGN = 1
RESOURCE_TYPE_FRAME = 2
RESOURCE_TYPE_OTHER = 4
RESOURCE_TYPE_CN = {
    RESOURCE_TYPE_AD: u"硬广",
    RESOURCE_TYPE_CAMPAIGN: u"互动",
    # RESOURCE_TYPE_FRAME: u"框架",
    RESOURCE_TYPE_OTHER: u"其他"
}

CONTRACT_STATUS_NEW = 0
CONTRACT_STATUS_APPLYCONTRACT = 1
CONTRACT_STATUS_APPLYPASS = 2
CONTRACT_STATUS_APPLYREJECT = 3
CONTRACT_STATUS_APPLYPRINT = 4
CONTRACT_STATUS_PRINTED = 5
CONTRACT_STATUS_MEDIA = 6
CONTRACT_STATUS_DELETEAPPLY = 7
CONTRACT_STATUS_DELETEAGREE = 8
CONTRACT_STATUS_DELETEPASS = 9
CONTRACT_STATUS_PRE_FINISH = 19
CONTRACT_STATUS_FINISH = 20
CONTRACT_STATUS_CN = {
    CONTRACT_STATUS_NEW: u"新建",
    CONTRACT_STATUS_APPLYCONTRACT: u"申请审批中...",
    CONTRACT_STATUS_APPLYPASS: u"审批通过",
    CONTRACT_STATUS_APPLYREJECT: u"审批未通过",
    CONTRACT_STATUS_MEDIA: u"利润分配中...",
    CONTRACT_STATUS_APPLYPRINT: u"申请打印中...",
    CONTRACT_STATUS_PRINTED: u"打印完毕",
    CONTRACT_STATUS_DELETEAPPLY: u'撤单申请中...',
    CONTRACT_STATUS_DELETEAGREE: u'确认撤单',
    CONTRACT_STATUS_DELETEPASS: u'同意撤单',
    CONTRACT_STATUS_PRE_FINISH: u'项目归档（预）',
    CONTRACT_STATUS_FINISH: u'项目归档（确认）'
}


STATUS_DEL = 0
STATUS_ON = 1
STATUS_CN = {
    STATUS_DEL: u'删除',
    STATUS_ON: u'正常',
}

BACK_MONEY_STATUS_BREAK = -1
BACK_MONEY_STATUS_END = 0
BACK_MONEY_STATUS_NOW = 1
BACK_MONEY_STATUS_CN = {
    BACK_MONEY_STATUS_END: u'回款完成',
    BACK_MONEY_STATUS_NOW: u'正在回款',
    BACK_MONEY_STATUS_BREAK: u'坏账'
}

direct_sales = db.Table('client_medium_order_direct_sales',
                        db.Column(
                            'direct_sale_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column(
                            'order_id', db.Integer, db.ForeignKey('bra_client_medium_order.id'))
                        )
agent_sales = db.Table('client_medium_order_agent_sales',
                       db.Column(
                           'agent_sale_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column(
                           'order_id', db.Integer, db.ForeignKey('bra_client_medium_order.id'))
                       )

replace_sales = db.Table('client_medium_order_replace_sales',
                         db.Column(
                             'replace_sale_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column(
                             'order_id', db.Integer, db.ForeignKey('bra_client_medium_order.id'))
                         )

assistant_sales = db.Table('client_medium_order_assistant_sales',
                           db.Column(
                               'assistant_sale_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column(
                               'order_id', db.Integer, db.ForeignKey('bra_client_medium_order.id'))
                           )

operater_users = db.Table('client_medium_order_users_operater',
                          db.Column(
                              'user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column(
                              'order_id', db.Integer, db.ForeignKey('bra_client_medium_order.id'))
                          )
designer_users = db.Table('client_medium_order_users_designerer',
                          db.Column(
                              'user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column(
                              'order_id', db.Integer, db.ForeignKey('bra_client_medium_order.id'))
                          )
planer_users = db.Table('client_medium_order_users_planer',
                        db.Column(
                            'user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column(
                            'order_id', db.Integer, db.ForeignKey('bra_client_medium_order.id'))
                        )


class ClientMediumOrder(db.Model, BaseModelMixin, CommentMixin, AttachmentMixin):
    __tablename__ = 'bra_client_medium_order'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 客户合同甲方
    agent = db.relationship(
        'Agent', backref=db.backref('client_medium_agent', lazy='dynamic'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))  # 客户
    client = db.relationship(
        'Client', backref=db.backref('client_medium_client', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称
    contract = db.Column(db.String(100))  # 客户合同号
    money = db.Column(db.Float())  # 客户合同金额
    medium_CPM = db.Column(db.Integer)  # 实际CPM
    sale_CPM = db.Column(db.Integer)  # 下单CPM
    contract_type = db.Column(db.Integer)  # 合同类型： 标准，非标准
    client_start = db.Column(db.Date)
    client_end = db.Column(db.Date)
    client_start_year = db.Column(db.Integer, index=True)
    client_end_year = db.Column(db.Integer, index=True)
    reminde_date = db.Column(db.Date)  # 最迟回款日期
    direct_sales = db.relationship('User', secondary=direct_sales)
    agent_sales = db.relationship('User', secondary=agent_sales)
    replace_sales = db.relationship('User', secondary=replace_sales)
    assistant_sales = db.relationship('User', secondary=assistant_sales)
    operaters = db.relationship('User', secondary=operater_users)
    designers = db.relationship('User', secondary=designer_users)
    planers = db.relationship('User', secondary=planer_users)
    contract_status = db.Column(db.Integer)  # 合同审批状态
    status = db.Column(db.Integer)
    resource_type = db.Column(db.Integer)  # 资源形式
    sale_type = db.Column(db.Integer)  # 资源形式
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_client_mediumorder', lazy='dynamic'))
    create_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)   # 合同归档时间
    back_money_status = db.Column(db.Integer)
    self_agent_rebate = db.Column(db.String(20))  # 单笔返点

    # 媒体合同信息
    medium = db.relationship(
        'Medium', backref=db.backref('client_medium', lazy='dynamic'))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))  # 媒体
    medium_money = db.Column(db.Float())  # 媒体合同金额
    contract_generate = True
    media_apply = True
    kind = "client-medium-order"
    __mapper_args__ = {'order_by': contract.desc()}

    def __init__(self, agent, client, campaign, status=STATUS_ON,
                 contract="", money=0, contract_type=CONTRACT_TYPE_NORMAL,
                 medium_CPM=0, sale_CPM=0, finish_time=None,
                 back_money_status=BACK_MONEY_STATUS_NOW, self_agent_rebate='0-0',
                 client_start=None, client_end=None, reminde_date=None,
                 direct_sales=None, agent_sales=None, replace_sales=[], assistant_sales=[],
                 operaters=None, designers=None, planers=None,
                 resource_type=RESOURCE_TYPE_AD, sale_type=SALE_TYPE_AGENT,
                 creator=None, create_time=None, contract_status=CONTRACT_STATUS_NEW,
                 medium=None, medium_money=0):
        self.agent = agent
        self.client = client
        self.campaign = campaign

        self.contract = contract
        self.money = money
        self.contract_type = contract_type
        self.medium_CPM = medium_CPM
        self.sale_CPM = sale_CPM

        self.client_start = client_start or datetime.date.today()
        self.client_end = client_end or datetime.date.today()
        self.client_start_year = int(self.client_start.year)
        self.client_end_year = int(self.client_end.year)
        self.reminde_date = reminde_date or datetime.date.today()

        self.direct_sales = direct_sales or []
        self.agent_sales = agent_sales or []
        self.replace_sales = replace_sales
        self.assistant_sales = assistant_sales

        self.operaters = operaters or []
        self.designers = designers or []
        self.planers = planers or []

        self.resource_type = resource_type
        self.sale_type = sale_type

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()
        self.finish_time = finish_time or datetime.datetime.now()
        self.contract_status = contract_status
        self.status = status
        self.back_money_status = back_money_status
        self.self_agent_rebate = self_agent_rebate
        self.medium = medium
        self.medium_money = medium_money or 0

    @property
    def salers(self):
        return list(set(self.direct_sales + self.agent_sales))

    @classmethod
    def get_all(cls):
        """查看所有没删除订单"""
        return [o for o in cls.query.all() if o.status in [STATUS_ON, None] and o.contract_status not in [9]]

    @classmethod
    def all(cls):
        return cls.get_all()

    @classmethod
    def delete_all(cls):
        return [o for o in cls.query.all() if o.status == STATUS_DEL]

    @property
    def name(self):
        return u"%s-%s" % (self.client.name, self.campaign)

    @property
    def jiafang_name(self):
        return self.agent.name

    @property
    def sale_ECPM(self):
        return (self.money / self.sale_CPM) if self.sale_CPM else 0

    @property
    def locations(self):
        return list(set([u.location for u in self.direct_sales + self.agent_sales]))

    @property
    def locations_cn(self):
        return ",".join([TEAM_LOCATION_CN[l] for l in self.locations])

    @property
    def contract_type_cn(self):
        return CONTRACT_TYPE_CN[self.contract_type]

    @property
    def resource_type_cn(self):
        return RESOURCE_TYPE_CN.get(self.resource_type)

    @property
    def sale_type_cn(self):
        return SALE_TYPE_CN.get(self.sale_type)

    @property
    def direct_sales_names(self):
        return ",".join([u.name for u in self.direct_sales])

    @property
    def agent_sales_names(self):
        return ",".join([u.name for u in self.agent_sales])

    @property
    def replace_sales_names(self):
        return ",".join([u.name for u in self.replace_sales])

    @property
    def assistant_sales_names(self):
        return ",".join([u.name for u in self.assistant_sales])

    @property
    def operater_names(self):
        return ",".join([u.name for u in self.operaters])

    @property
    def designers_names(self):
        return ",".join([u.name for u in self.designers])

    @property
    def planers_names(self):
        return ",".join([u.name for u in self.planers])

    @property
    def leaders(self):
        return list(set([l for u in self.direct_sales + self.agent_sales + self.replace_sales + self.assistant_sales
                         for l in u.user_leaders] + User.super_leaders()))

    @property
    def operater_users(self):
        return [u for u in self.operaters]

    def can_admin(self, user):
        """是否可以修改该订单"""
        salers = self.direct_sales + self.agent_sales + self.replace_sales + self.assistant_sales
        leaders = []
        for k in salers:
            leaders += k.team_leaders
        admin_users = salers + [self.creator] + list(set(leaders))
        return user.is_leader() or user.is_contract() or user.is_media() or\
            user.is_media_leader() or user in admin_users

    def can_media_leader_action(self, user):
        return False

    def path(self):
        return self.info_path()

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
    def reminde_date_cn(self):
        return self.reminde_date.strftime(DATE_FORMAT)

    @property
    def contract_status_cn(self):
        return CONTRACT_STATUS_CN[self.contract_status]

    @property
    def search_info(self):
        return (self.client.name + self.agent.name +
                self.campaign + self.contract + self.medium.name)

    @property
    def search_invoice_info(self):
        return self.search_info

    def attachment_path(self):
        return url_for('files.client_medium_order_files', order_id=self.id)

    def info_path(self):
        return url_for("order.client_medium_order_info", order_id=self.id)

    def attach_status_confirm_path(self, attachment):
        return url_for('order.client_medium_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_PASSED)

    def attach_status_reject_path(self, attachment):
        return url_for('order.client_medium_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_REJECT)

    def delete(self):
        self.delete_comments()
        self.delete_attachments()
        db.session.delete(self)
        db.session.commit()

    @property
    def operater_ids(self):
        return ",".join([str(u.id) for u in self.operaters])

    def have_owner(self, user):
        """是否可以查看该订单"""
        salers = self.direct_sales + self.agent_sales + self.replace_sales + self.assistant_sales
        leaders = []
        for k in salers:
            leaders += k.team_leaders
        owner = salers + [self.creator] + \
            self.operater_users + list(set(leaders))
        return user.is_admin() or user in owner

    @classmethod
    def get_order_by_user(cls, user):
        """一个用户可以查看的所有订单"""
        return [o for o in cls.all() if o.have_owner(user) and o.status in [STATUS_ON, None]]

    def order_agent_owner(self, user):
        """是否可以查看该订单"""
        owner = self.agent_sales
        return user in owner

    def order_direct_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales
        return user in owner

    def get_saler_leaders(self):
        leaders = []
        for user in self.agent_sales + self.direct_sales:
            leaders += user.team_leaders
        return leaders

    @property
    def order_path(self):
        return url_for('order.douban_order_info', order_id=self.id)

    def can_edit_contract_time(self, now_date=None):
        if not now_date:
            now_date = datetime.date.today()
        if self.client_start.month > now_date.month:
            return True
        else:
            return False

    @property
    def finish_time_cn(self):
        try:
            return self.finish_time.date()
        except:
            return ''

    @property
    def self_agent_rebate_value(self):
        if self.self_agent_rebate:
            p_self_agent_rebate = self.self_agent_rebate.split('-')
        else:
            p_self_agent_rebate = ['0', '0.0']
        return {'status': p_self_agent_rebate[0],
                'value': p_self_agent_rebate[1]}

    @property
    def payable_time(self):
        if self.back_money_status == 0:
            return 0
        now_date = datetime.date.today()
        return (now_date - self.client_end).days + 1

    def get_default_contract(self):
        return contract_generator(self.medium.direct_framework, self.id)

    def contract_path(self):
        return url_for("order.client_medium_order_contract", order_id=self.id)

    @property
    def email_info(self):
        return u"""
        类型: 直签媒体订单
        客户: %s
        代理/直客: %s
        Campaign: %s
        金额: %s
        预估CPM: %s
        直客销售: %s
        渠道销售: %s
        执行: %s
        执行开始时间: %s
        执行结束时间: %s
        合同号: %s
        所属媒体: %s
        媒体金额: %s
        """ % (self.client.name, self.agent.name, self.campaign, self.money,
               self.sale_CPM or 0, self.direct_sales_names,
               self.agent_sales_names, self.operater_names,
               self.start_date_cn, self.end_date_cn, self.contract,
               self.medium.name, self.medium_money)


class BackMoney(db.Model, BaseModelMixin):
    __tablename__ = 'bra_client_medium_order_back_money'
    id = db.Column(db.Integer, primary_key=True)
    client_medium_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_medium_order.id'))  # 客户合同
    client_medium_order = db.relationship(
        'ClientMediumOrder', backref=db.backref('client_medium_order_back_money', lazy='dynamic'))
    money = db.Column(db.Float())
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_medium_order, money=0.0, create_time=None, back_time=None):
        self.client_medium_order = client_medium_order
        self.money = money
        self.create_time = create_time or datetime.date.today()
        self.back_time = back_time or datetime.date.today()

    @property
    def back_time_cn(self):
        return self.back_time.strftime(DATE_FORMAT)

    @property
    def create_time_cn(self):
        return self.create_time.strftime(DATE_FORMAT)

    @property
    def order(self):
        return self.client_medium_order

    @property
    def real_back_money_diff_time(self):
        return (self.back_time.date() - self.client_medium_order.reminde_date).days


class BackInvoiceRebate(db.Model, BaseModelMixin):
    __tablename__ = 'bra_cleint_medium_order_back_invoice_rebate'
    id = db.Column(db.Integer, primary_key=True)
    client_medium_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_medium_order.id'))  # 客户合同
    client_medium_order = db.relationship(
        'ClientMediumOrder', backref=db.backref('client_medium_order_back_invoice', lazy='dynamic'))
    num = db.Column(db.String(100))  # 发票号
    money = db.Column(db.Float())
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_medium_order, num='', money=0.0, create_time=None, back_time=None):
        self.client_medium_order = client_medium_order
        self.num = num
        self.money = money
        self.create_time = create_time or datetime.date.today()
        self.back_time = back_time or datetime.date.today()

    @property
    def back_time_cn(self):
        return self.back_time.strftime(DATE_FORMAT)

    @property
    def create_time_cn(self):
        return self.create_time.strftime(DATE_FORMAT)

    @property
    def order(self):
        return self.client_medium_order


def contract_generator(framework, num):
    code = "%s-%03x" % (framework, num % 1000)
    code = code.upper()
    return code
