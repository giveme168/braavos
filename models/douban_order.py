# -*- coding: UTF-8 -*-
import datetime
from flask import url_for, g

from . import db, BaseModelMixin
from .user import User, TEAM_LOCATION_CN
from models.mixin.comment import CommentMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT
from consts import DATE_FORMAT
from libs.mail import mail

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
CONTRACT_STATUS_CN = {
    CONTRACT_STATUS_NEW: u"新建",
    CONTRACT_STATUS_APPLYCONTRACT: u"申请合同号中...",
    CONTRACT_STATUS_APPLYPASS: u"申请合同号通过",
    CONTRACT_STATUS_APPLYREJECT: u"申请合同号未通过",
    CONTRACT_STATUS_APPLYPRINT: u"申请打印中...",
    CONTRACT_STATUS_PRINTED: u"打印完毕"
}

STATUS_DEL = 0
STATUS_ON = 1
STATUS_CN = {
    STATUS_DEL: u'删除',
    STATUS_ON: u'正常',
}

direct_sales = db.Table('douban_order_direct_sales',
                        db.Column(
                            'direct_sale_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column(
                            'douban_order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                        )
agent_sales = db.Table('douban_order_agent_sales',
                       db.Column(
                           'agent_sale_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column(
                           'douban_order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                       )

operater_users = db.Table('douban_order_users_operater',
                          db.Column(
                              'user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column(
                              'order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                          )
designer_users = db.Table('douban_order_users_designerer',
                          db.Column(
                              'user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column(
                              'order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                          )
planer_users = db.Table('douban_order_users_planer',
                        db.Column(
                            'user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column(
                            'order_id', db.Integer, db.ForeignKey('bra_douban_order.id'))
                        )


class DoubanOrder(db.Model, BaseModelMixin, CommentMixin, AttachmentMixin):
    __tablename__ = 'bra_douban_order'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 客户合同甲方
    agent = db.relationship(
        'Agent', backref=db.backref('douban_orders', lazy='dynamic'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))  # 客户
    client = db.relationship(
        'Client', backref=db.backref('douban_orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称

    contract = db.Column(db.String(100))  # 豆瓣合同号
    money = db.Column(db.Integer)  # 客户合同金额
    medium_CPM = db.Column(db.Integer)  # 实际CPM
    sale_CPM = db.Column(db.Integer)  # 下单CPM
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
    status = db.Column(db.Integer)

    resource_type = db.Column(db.Integer)  # 资源形式
    sale_type = db.Column(db.Integer)  # 资源形式

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_douban_orders', lazy='dynamic'))
    create_time = db.Column(db.DateTime)

    contract_generate = False
    media_apply = False
    kind = "douban-order"
    __mapper_args__ = {'order_by': contract.desc()}

    def __init__(self, agent, client, campaign, status=STATUS_ON,
                 contract="", money=0, contract_type=CONTRACT_TYPE_NORMAL,
                 medium_CPM=0, sale_CPM=0,
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
        self.medium_CPM = medium_CPM
        self.sale_CPM = sale_CPM

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
        self.status = status

    @classmethod
    def get_all(cls):
        """查看所有没删除订单"""
        return [o for o in cls.query.all() if o.status in [STATUS_ON, None]]

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
        return list(set([l for u in self.direct_sales + self.agent_sales
                         for l in u.user_leaders] + User.super_leaders()))

    @property
    def operater_users(self):
        return [u for u in self.operaters]

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.direct_sales + self.agent_sales + [self.creator]
        return user.is_admin() or user in admin_users

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
    def email_info(self):
        return u"""
        类型: 直签豆瓣订单
        客户: %s
        代理/直客: %s
        Campaign: %s
        金额: %s
        预估CPM: %s
        直客销售: %s
        渠道销售: %s
        执行: %s
        """ % (self.client.name, self.agent.name, self.campaign, self.money,
               self.sale_CPM or 0, self.direct_sales_names,
               self.agent_sales_names, self.operater_names)

    @property
    def search_info(self):
        return (self.client.name + self.agent.name +
                self.campaign + self.contract)

    def attachment_path(self):
        return url_for('files.douban_order_files', order_id=self.id)

    def info_path(self):
        return url_for("order.douban_order_info", order_id=self.id)

    def outsource_operater_info_path(self):
        return url_for("outsource.douban_orders")

    def outsource_info_path(self):
        return url_for("outsource.douban_outsources", order_id=self.id)

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

    @property
    def outsources(self):
        return [o for o in self.douban_outsources]

    def get_outsources_by_status(self, outsource_status):
        return [o for o in self.douban_outsources if o.status == outsource_status]

    def get_outsource_status_cn(self, status):
        from models.outsource import OUTSOURCE_STATUS_CN
        return OUTSOURCE_STATUS_CN[status]

    @property
    def outsources_sum(self):
        return sum([o.pay_num for o in self.douban_outsources if o.status != 0]) if self.douban_outsources else 0

    @property
    def outsources_percent(self):
        return "%.1f" % (self.outsources_sum * 100 / float(self.money)) if self.money else "0"

    def delete(self):
        self.delete_comments()
        self.delete_attachments()
        db.session.delete(self)
        db.session.commit()

    def douban_contract_email_info(self, title):
        body = u"""
Dear %s:

%s

项目: %s
客户: %s
代理: %s
直客销售: %s
渠道销售: %s
时间: %s : %s
金额: %s

附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (','.join([x.name for x in User.douban_contracts()]), title, self.campaign,
            self.client.name, self.jiafang_name,
            self.direct_sales_names, self.agent_sales_names,
            self.start_date_cn, self.end_date_cn,
            self.money, mail.app.config['DOMAIN'] + self.info_path(), g.user.name)
        return body

    @property
    def operater_ids(self):
        return ",".join([str(u.id) for u in self.operaters])

    def have_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales + self.agent_sales + [self.creator] + [k for k in self.operaters]
        return user.is_admin() or user in owner

    @classmethod
    def get_order_by_user(cls, user):
        """一个用户可以查看的所有订单"""
        return [o for o in cls.all() if o.have_owner(user) and o.status in [STATUS_ON, None]]

    def outsource_path(self):
        return url_for("outsource.douban_outsources", order_id=self.id)

    @property
    def outsource_info(self):
        return u"""
        客户订单总额:   %s 元
        外包应付总金额: %s 元
        外包占比:   %s %%""" % (self.money, self.outsources_sum, self.outsources_percent)

    def finance_outsource_path(self):
        return url_for("finance_pay.douban_info", order_id=self.id)

    def outsource_distribute_email_info(self, title):
        body = u"""
Dear %s:

%s

【直签豆瓣订单项目详情】
甲方: %s
项目: %s
客户: %s
合同号: %s
时间: %s : %s
金额: %s

【项目相关人员】
直客销售: %s
渠道销售: %s
运营: %s

附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (self.operater_names, title, self.jiafang_name,
            self.campaign, self.client.name, self.contract,
            self.start_date_cn, self.end_date_cn, self.money,
            self.direct_sales_names, self.agent_sales_names,
            self.operater_names,
            mail.app.config['DOMAIN'] + self.outsource_info_path(), g.user.name)
        return body

    def outsource_email_info(self, to_user, title, o_info, url, msg):
        body = u"""
Dear %s:

%s

【直签豆瓣订单项目详情】
甲方: %s
项目: %s
客户: %s
合同号: %s
时间: %s : %s
金额: %s
外包占比: %s %%

【外包组成】
%s

【项目相关人员】
直客销售: %s
渠道销售: %s
运营: %s

留言:
%s


附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (to_user, title, self.jiafang_name,
            self.campaign, self.client.name, self.contract,
            self.start_date_cn, self.end_date_cn, self.money,
            self.outsources_percent, o_info,
            self.direct_sales_names, self.agent_sales_names,
            self.operater_names, msg, url, g.user.name)
        return body
