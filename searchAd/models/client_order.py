# -*- coding: UTF-8 -*-
import datetime
from flask import url_for, g, json
from models import db, BaseModelMixin
from models.mixin.comment import CommentMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT
from models.item import ITEM_STATUS_LEADER_ACTIONS
from models.user import TEAM_LOCATION_CN
from models.consts import DATE_FORMAT
from ..models.framework_order import searchAdFrameworkOrder

from libs.mail import mail
from libs.date_helpers import get_monthes_pre_days

from .invoice import searchAdInvoice, searchAdMediumInvoice, searchAdMediumInvoicePay, searchAdAgentInvoice, \
    searchAdAgentInvoicePay, searchAdMediumRebateInvoice


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

# for searchAd
AD_PROMOTION_TYPE_CN = {
    0: u'无线助手CPT',
    1: u'无线助手CPC',
    2: u'360搜索CPC',
    3: u'360导航猜你喜欢',
    4: u'360导航CPT',
    5: 'CPA',
    6: 'CPT',
    7: 'CPC',
    8: 'CPD',
    9: 'CPM',
    10: 'CPS',
    99: u'其他'
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
CONTRACT_STATUS_CHECKCONTRACT = 10
CONTRACT_STATUS_PRE_FINISH = 19
CONTRACT_STATUS_FINISH = 20
CONTRACT_STATUS_CN = {
    CONTRACT_STATUS_NEW: u"新建",
    CONTRACT_STATUS_APPLYCONTRACT: u"申请审批中...",
    CONTRACT_STATUS_APPLYPASS: u"审批通过，等待合同审批结果",
    CONTRACT_STATUS_APPLYREJECT: u"审批未通过",
    CONTRACT_STATUS_MEDIA: u"利润分配中...",
    CONTRACT_STATUS_APPLYPRINT: u"申请打印中...",
    CONTRACT_STATUS_PRINTED: u"打印完毕",
    CONTRACT_STATUS_DELETEAPPLY: u'撤单申请中...',
    CONTRACT_STATUS_DELETEAGREE: u'确认撤单',
    CONTRACT_STATUS_DELETEPASS: u'同意撤单',
    CONTRACT_STATUS_PRE_FINISH: u'项目归档（预）',
    CONTRACT_STATUS_FINISH: u'项目归档（确认）',
    CONTRACT_STATUS_CHECKCONTRACT: u'审批合同通过'
}

STATUS_DEL = 0
STATUS_ON = 1
STATUS_CN = {
    STATUS_DEL: u'删除',
    STATUS_ON: u'正常',
}

BACK_MONEY_STATUS_END = 0
BACK_MONEY_STATUS_NOW = 1
BACK_MONEY_STATUS_CN = {
    BACK_MONEY_STATUS_END: u'回款完成',
    BACK_MONEY_STATUS_NOW: u'正在回款',
}

ECPM_CONTRACT_STATUS_LIST = [2, 4, 5]

direct_sales = db.Table('searchAd_client_order_direct_sales',
                        db.Column(
                            'sale_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column(
                            'client_order_id', db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))
                        )
agent_sales = db.Table('searchAd_client_order_agent_sales',
                       db.Column(
                           'agent_sale_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column(
                           'client_order_id', db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))
                       )
table_medium_orders = db.Table('searchAd_client_order_medium_orders',
                               db.Column(
                                   'order_id', db.Integer, db.ForeignKey('searchAd_bra_order.id')),
                               db.Column(
                                   'client_order_id', db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))
                               )


class searchAdClientOrder(db.Model, BaseModelMixin, CommentMixin, AttachmentMixin):
    __tablename__ = 'searchAd_bra_client_order'

    id = db.Column(db.Integer, primary_key=True)
    framework_order_id = db.Column(
        db.Integer, server_default='0', nullable=False)  # 客户合同甲方
    agent_id = db.Column(
        db.Integer, db.ForeignKey('searchAd_agent.id'))  # 客户合同甲方
    agent = db.relationship(
        'searchAdAgent', backref=db.backref('client_orders', lazy='dynamic'))
    client_id = db.Column(db.Integer, db.ForeignKey('searchAd_client.id'))  # 客户
    client = db.relationship(
        'searchAdClient', backref=db.backref('client_orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称

    contract = db.Column(db.String(100))  # 客户合同号
    money = db.Column(db.Float())  # 客户合同金额
    contract_type = db.Column(db.Integer)  # 合同类型： 标准，非标准
    client_start = db.Column(db.Date)
    client_end = db.Column(db.Date)
    client_start_year = db.Column(db.Integer, index=True)
    client_end_year = db.Column(db.Integer, index=True)
    reminde_date = db.Column(db.Date)  # 最迟回款日期
    resource_type = db.Column(db.Integer)  # 推广形式
    sale_type = db.Column(db.Integer)  # 资源形式

    direct_sales = db.relationship('User', secondary=direct_sales)
    agent_sales = db.relationship('User', secondary=agent_sales)

    medium_orders = db.relationship(
        'searchAdOrder', secondary=table_medium_orders)
    contract_status = db.Column(db.Integer)  # 合同审批状态
    status = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('searchAd_created_client_orders', lazy='dynamic'))
    create_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)   # 合同归档时间
    back_money_status = db.Column(db.Integer)
    self_agent_rebate = db.Column(db.String(20))  # 单笔返点
    contract_generate = True
    media_apply = True
    kind = "searchAd-client-order"
    __mapper_args__ = {'order_by': contract.desc()}

    def __init__(self, agent, client, campaign, medium_orders=None, status=STATUS_ON,
                 back_money_status=BACK_MONEY_STATUS_NOW, self_agent_rebate='0-0',
                 contract="", money=0, contract_type=CONTRACT_TYPE_NORMAL, sale_type=SALE_TYPE_AGENT,
                 client_start=None, client_end=None, reminde_date=None, resource_type=RESOURCE_TYPE_AD,
                 direct_sales=None, agent_sales=None, framework_order_id=0,
                 creator=None, create_time=None, contract_status=CONTRACT_STATUS_NEW):
        self.agent = agent
        self.client = client
        self.campaign = campaign
        self.medium_orders = medium_orders or []

        self.contract = contract
        self.money = money
        self.contract_type = contract_type
        self.sale_type = sale_type

        self.client_start = client_start or datetime.date.today()
        self.client_end = client_end or datetime.date.today()
        self.client_start_year = int(self.client_start.year)
        self.client_end_year = int(self.client_end.year)
        self.reminde_date = reminde_date or datetime.date.today()
        self.resource_type = resource_type

        self.direct_sales = direct_sales or []
        self.agent_sales = agent_sales or []

        self.creator = creator
        self.status = status
        self.create_time = create_time or datetime.datetime.now()
        self.contract_status = contract_status
        self.back_money_status = back_money_status
        self.framework_order_id = framework_order_id
        self.self_agent_rebate = self_agent_rebate

    @classmethod
    def get_all(cls):
        """查看所有没删除订单"""
        return [o for o in cls.query.all() if o.status in [STATUS_ON, None] and o.contract_status not in [7, 8, 9]]

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
    def mediums(self):
        return [x.medium for x in self.medium_orders]

    @property
    def agents(self):
        return [self.agent]

    @property
    def mediums_money2(self):
        return sum([x.medium_money2 or 0 for x in self.medium_orders])

    def medium_rebate_money(self, year, month, type='profit'):
        rebate_money = 0
        if self.client_start.year == int(year) and self.client_start.month == int(month):
            for medium_order in self.medium_orders:
                rebate = medium_order.medium.rebate_by_year(
                    self.client_start.year)
                if type == 'profit':
                    rebate_money += medium_order.medium_money2 * rebate / 100
                else:
                    rebate_money += medium_order.medium_money2 * \
                        (1 - rebate / 100)
        return rebate_money

    @property
    def agent_rebate(self):
        return self.agent.inad_rebate_by_year(self.client_start.year)

    def rebate_agent_by_month(self, year, month):
        rebate = self.agent.inad_rebate_by_year(year)
        ex_money = self.executive_report(g.user, year, [month], 'normal')[0]
        return round(ex_money * rebate / 100, 2)

    def rebate_money(self, year, month, type='profit'):
        rebate_money = 0
        if self.client_start.year == int(year) and self.client_start.month == int(month):
            rebate = self.agent.inad_rebate_by_year(self.client_start.year)
            if type == 'profit':
                rebate_money += self.money * (1 - rebate / 100)
            else:
                rebate_money += self.money * rebate / 100
        return rebate_money

    def sum_rebate_medium_by_month(self, year, month):
        return sum([k.rebate_medium_by_month(year, month) for k in self.medium_orders])

    def sum_medium_money_by_month(self, year, month, type):
        return sum([k.get_executive_report_medium_money_by_month(year, month, 'normal')[type]
                    for k in self.medium_orders])

    def profit_money(self, year, month):
        return self.sum_medium_money_by_month(year, month, 'sale_money') - self.sum_medium_money_by_month(year, month, 'medium_money2')

    @property
    def mediums_rebate_money(self):
        return sum([medium_order.get_medium_rebate_money() for medium_order in self.medium_orders])

    def get_medium_rebate_money(self, medium):
        for medium_order in self.medium_orders:
            if medium_order.medium == medium:
                return medium_order.get_medium_rebate_money()
        return 0.0

    @property
    def agent_money(self):
        inad_rebate = self.agent.inad_rebate_by_year(year=self.start_date.year)
        return round(float(inad_rebate) * self.money / 100, 2)

    @property
    def agents_rebate_money(self):
        return self.agent_money

    @property
    def mediums_invoice_sum(self):
        return sum([k.money for k in searchAdMediumInvoice.query.filter_by(client_order_id=self.id)])

    @property
    def agents_invoice_sum(self):  # 一个ClientOrder实例只有一个agent
        return sum([k.money for k in searchAdAgentInvoice.query.filter_by(client_order_id=self.id)])

    @property
    def mediums_invoice_apply_sum(self):
        invoices = searchAdMediumInvoice.query.filter_by(
            client_order_id=self.id)
        return sum([k.money for k in searchAdMediumInvoicePay.all() if k.pay_status == 3 and k.medium_invoice in invoices])

    @property
    def agents_invoice_apply_sum(self):
        invoices = searchAdAgentInvoice.query.filter_by(client_order_id=self.id)
        return sum([k.money for k in searchAdAgentInvoicePay.all() if k.pay_status == 3 and k.agent_invoice in invoices])

    @property
    def mediums_invoice_pass_sum(self):
        invoices = searchAdMediumInvoice.query.filter_by(
            client_order_id=self.id)
        return sum([k.money for k in searchAdMediumInvoicePay.all() if k.pay_status == 0 and k.medium_invoice in invoices])

    @property
    def agent_invoice_pass_sum(self):
        money = 0.0
        invoices = searchAdAgentInvoice.query.filter_by(client_order_id=self.id)
        for invoice in invoices:
            for invoice_pay in searchAdAgentInvoicePay.query.filter_by(pay_status=0, agent_invoice=invoice):
                money += invoice_pay.money
        return money

    @property
    def agents_invoice_pass_sum(self):
        return self.agent_invoice_pass_sum

    def get_invoice_by_status(self, type):
        return [invoice for invoice in self.invoices if invoice.invoice_status == type]

    def get_medium_rebate_invoice_by_status(self, invoice_status):
        return [medium_rebate_invoice for medium_rebate_invoice in self.mediumrebateinvoices
                if medium_rebate_invoice.invoice_status == invoice_status]

    def get_medium_invoice_pay_by_status(self, type):
        return [k for k in searchAdMediumInvoicePay.all()
                if k.pay_status == int(type) and k.medium_invoice in self.mediuminvoices]

    def get_agent_invoice_pay_by_status(self, type):
        return [k for k in searchAdAgentInvoicePay.all()
                if isinstance(k.pay_status, int) and k.agent_invoice in self.agentinvoices]

    def get_medium_rebate_invoice_pass_money(self):
        return sum([invoice.money for invoice in searchAdMediumRebateInvoice.query.filter_by(client_order_id=self.id,
                                                                                     invoice_status=0)])
        
    @property
    def medium_ids(self):
        return [x.medium.id for x in self.medium_orders]

    @property
    def outsources(self):
        return [o for mo in self.medium_orders for o in mo.outsources]

    def get_outsources_by_status(self, outsource_status):
        return [o for o in self.outsources if o.status == outsource_status]

    def get_outsource_status_cn(self, status):
        from models.outsource import OUTSOURCE_STATUS_CN
        return OUTSOURCE_STATUS_CN[status]

    @property
    def outsources_sum(self):
        return sum([o.pay_num or 0 for o in self.outsources if o.status != 0]) if self.outsources else 0

    def apply_outsources(self):
        return [o for o in self.outsources if o.status != 0]

    @property
    def outsources_paied_sum(self):
        return sum([o.pay_num for o in self.outsources if o.status == 4]) if self.outsources else 0

    @property
    def outsources_percent(self):
        if self.money:
            return "%.2f" % (self.outsources_sum * 100 / float(self.money)) if self.money else "0"
        else:
            return "%.2f" % (self.outsources_sum * 100 / 1)

    @property
    def invoice_apply_sum(self):
        return sum([k.money for k in searchAdInvoice.query.filter_by(client_order_id=self.id)
                    if k.invoice_status == 3])

    @property
    def mediums_rebate_invoice_apply_sum(self):
        return sum([invoice.money for invoice in searchAdMediumRebateInvoice.query.filter_by(client_order_id=self.id)
                    if invoice.invoice_status == 3])

    def get_medium_rebate_invoice_apply_sum(self, medium):
        return sum([invoice.money for invoice in searchAdMediumRebateInvoice.query.filter_by(client_order_id=self.id,
                                                                                             invoice_status=3, medium=medium)])

    @property
    def invoice_pass_sum(self):
        return sum([k.money for k in searchAdInvoice.query.filter_by(client_order_id=self.id)
                    if k.invoice_status == 0])

    @property
    def mediums_rebate_invoice_pass_sum(self):
        return sum([invoice.money for invoice in searchAdMediumRebateInvoice.query.filter_by(client_order_id=self.id)
                    if invoice.invoice_status == 0])

    def get_medium_rebate_invoice_pass_sum(self, medium):
        return sum([invoice.money for invoice in searchAdMediumRebateInvoice.query.filter_by(client_order_id=self.id,
                                                                                             invoice_status=0, medium=medium)])

    @property
    def invoice_percent(self):
        return "%.1f" % (self.invoice_pass_sum * 100 / float(self.money)) if self.money else "0"

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
        return AD_PROMOTION_TYPE_CN.get(self.resource_type)

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
        if self.medium_orders:
            return ",".join([u.name for u in self.medium_orders[0].operaters])
        else:
            return ''

    @property
    def operater_ids(self):
        if self.medium_orders:
            return ",".join([str(u.id) for u in self.medium_orders[0].operaters])
        else:
            return ''

    @property
    def operater_users(self):
        if self.medium_orders:
            return [u for u in self.medium_orders[0].operaters]
        else:
            return []

    @property
    def leaders(self):
        return list(set([l for u in self.direct_sales + self.agent_sales
                         for l in u.user_leaders]))

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.direct_sales + self.agent_sales + [self.creator]
        return user.is_searchad_leader() or user.is_contract() or user.is_searchad_leader() or user in admin_users or user.is_super_leader()

    def can_action(self, user, action):
        """是否拥有leader操作"""
        if action in ITEM_STATUS_LEADER_ACTIONS:
            return user.is_admin() or user.is_leader()
        else:
            return self.can_admin(user)

    def can_edit_status(self):
        return [CONTRACT_STATUS_NEW, CONTRACT_STATUS_APPLYCONTRACT,
                CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYREJECT, CONTRACT_STATUS_MEDIA]

    def have_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales + self.agent_sales +\
            [self.creator] + self.operater_users
        return user.is_admin() or user in owner

    def order_agent_owner(self, user):
        """是否可以查看该订单"""
        owner = self.agent_sales
        return user in owner

    def order_direct_owner(self, user):
        """是否可以查看该订单"""
        owner = self.direct_sales
        return user in owner

    @classmethod
    def get_order_by_user(cls, user):
        """一个用户可以查看的所有订单"""
        return [o for o in cls.all() if o.have_owner(user) and o.status in [STATUS_ON, None]]

    def path(self):
        return self.info_path()

    @property
    def search_info(self):
        return (self.client.name + self.agent.name +
                self.campaign + self.contract +
                "".join([mo.medium.name + mo.medium_contract for mo in self.medium_orders]))

    @property
    def search_invoice_info(self):
        search_info = self.search_info
        search_info += ''.join(
            [k.invoice_num for k in searchAdInvoice.query.filter_by(client_order=self)])
        search_info += ''.join(
            [k.invoice_num for k in searchAdMediumRebateInvoice.query.filter_by(client_order=self)])
        search_info += ''.join(
            [k.invoice_num for k in searchAdMediumInvoice.query.filter_by(client_order=self)])
        search_info += ''.join(
            [k.invoice_num for k in searchAdAgentInvoice.query.filter_by(client_order=self)])
        return search_info

    @property
    def email_info(self):
        return u"""
    类型:效果业务订单
    客户订单:

        客户: %s
        代理/直客: %s
        Campaign: %s
        金额: %s
        销售: %s

    媒体订单:
%s""" % (self.client.name, self.agent.name, self.campaign, self.money,
         self.direct_sales_names,
         "\n".join([o.email_info for o in self.medium_orders]))

    @property
    def outsource_info(self):
        return u"""
        客户订单总额:   %s 元
        外包应付总金额: %s 元
        外包占比:   %s %%""" % (self.money, self.outsources_sum, self.outsources_percent)

    @property
    def start_date(self):
        return self.client_start

    @property
    def end_date(self):
        return self.client_end

    @property
    def create_time_cn(self):
        return self.create_time.strftime(DATE_FORMAT)

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

    def attachment_path(self):
        return url_for('files.searchAd_client_order_files', order_id=self.id)

    def info_path(self):
        return url_for("searchAd_order.order_info", order_id=self.id, tab_id=1)

    def contract_path(self):
        return url_for("searchAd_order.client_order_contract", order_id=self.id)

    def saler_invoice_path(self):
        return url_for("searchAd_saler_client_order_invoice.index", order_id=self.id)

    def finance_invoice_path(self):
        return url_for("searchAd_finance_client_order_invoice.info", order_id=self.id)

    def attach_status_confirm_path(self, attachment):
        return url_for('searchAd_order.client_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_PASSED)

    def attach_status_reject_path(self, attachment):
        return url_for('searchAd_order.client_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_REJECT)

    def saler_medium_invoice_path(self):
        return url_for("searchAd_saler_client_order_medium_invoice.index", order_id=self.id)

    def finance_medium_invoice_path(self):
        return url_for("finance_client_order_medium_pay.info", order_id=self.id)

    def saler_agent_invoice_path(self):
        return url_for("searchAd_saler_client_order_agent_invoice.index", order_id=self.id)

    def finance_agent_invoice_path(self):
        return url_for("finance_client_order_agent_pay.info", order_id=self.id)

    def saler_medium_rebate_invoice_path(self):
        return url_for("searchAd_saler_client_order_medium_rebate_invoice.index", order_id=self.id)

    @classmethod
    def contract_exist(cls, contract):
        is_exist = cls.query.filter_by(contract=contract).count() > 0
        return is_exist

    def get_default_contract(self):
        return contract_generator(self.agent.current_framework, self.id)

    def delete(self):
        self.delete_comments()
        self.delete_attachments()
        for mo in self.medium_orders:
            mo.delete()
        db.session.delete(self)
        db.session.commit()

    @property
    def back_moneys(self):
        return sum([k.money for k in self.backmoneys] + [k.money for k in self.back_invoice_rebate_list])

    @property
    def client_back_moneys(self):
        return sum([k.money for k in self.backmoneys])

    @property
    def back_money_status_cn(self):
        if self.back_money_status == 0:
            return BACK_MONEY_STATUS_CN[BACK_MONEY_STATUS_END]
        else:
            return BACK_MONEY_STATUS_CN[self.back_money_status or 1]

    @property
    def back_money_percent(self):
        if self.back_money_status == 0:
            return 100
        else:
            return int(float(self.back_moneys) / self.money * 100) if self.money else 0

    @property
    def back_money_list(self):
        return self.backmoneys

    @property
    def back_invoice_rebate_list(self):
        return self.backinvoicerebates

    @property
    def back_invoice_rebate_money(self):
        return sum([k.money for k in self.backinvoicerebates])

    @property
    def jiafang_name(self):
        return self.agent.name

    def outsource_operater_info_path(self):
        return url_for("outsource.client_orders")

    def outsource_info_path(self):
        return url_for("outsource.client_outsources", order_id=self.id)

    def outsource_distribute_email_info(self, title):
        body = u"""
Dear %s:

%s

【客户订单项目详情】
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
""" % (self.operater_names, title, self.agent.name,
            self.campaign, self.client.name, self.contract,
            self.start_date_cn, self.end_date_cn, self.money,
            self.direct_sales_names, self.agent_sales_names,
            self.operater_names,
            mail.app.config['DOMAIN'] + self.outsource_info_path(), g.user.name)
        return body

    def outsource_email_info(self, to_user, title, o_info, url, msg):
        body = u"""

%s

【客户订单项目详情】
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
""" % (title, self.jiafang_name,
            self.campaign, self.client.name, self.contract,
            self.start_date_cn, self.end_date_cn, self.money,
            self.outsources_percent, o_info,
            self.direct_sales_names, self.agent_sales_names,
            self.operater_names, msg, url, g.user.name)
        return body

    def pre_month_money(self):
        if self.money:
            pre_money = float(self.money) / \
                ((self.client_end - self.client_start).days + 1)
        else:
            pre_money = 0
        pre_month_days = get_monthes_pre_days(datetime.datetime.strptime(self.start_date_cn, '%Y-%m-%d'),
                                              datetime.datetime.strptime(self.end_date_cn, '%Y-%m-%d'))
        pre_month_money_data = []
        for k in pre_month_days:
            pre_month_money_data.append(
                {'money': '%.2f' % (pre_money * k['days']), 'month': k['month'], 'days': k['days']})
        return pre_month_money_data

    def is_executive_report(self):
        return searchAdClientOrderExecutiveReport.query.filter_by(client_order=self).count() > 0

    def executive_report(self, user, now_year, monthes, sale_type):
        if sale_type == 'agent':
            count = len(self.agent_sales)
        else:
            count = len(self.direct_sales)
        if user.team.location == 3:
            count = len(set(self.agent_sales + self.direct_sales))
        if sale_type == 'normal':
            count = 1
        pre_reports = searchAdClientOrderExecutiveReport.query.filter_by(
            client_order=self)
        moneys = []
        for j in monthes:
            try:
                pre_report = pre_reports.filter_by(
                    month_day=datetime.datetime(int(now_year), int(j), 1).date()).first()
            except:
                pre_report = None
            try:
                pre_money = pre_report.money
            except:
                pre_money = 0
            try:
                moneys.append(round(pre_money / count, 2))
            except:
                moneys.append(0)
        return moneys

    def get_executive_report_medium_money_by_month(self, year, month, sale_type):
        if sale_type == 'agent':
            count = len(self.agent_sales)
            user = self.agent_sales[0]
        else:
            count = len(self.direct_sales)
            user = self.direct_sales[0]
        if user.team.location == 3:
            count = len(set(self.agent_sales + self.direct_sales))
        if sale_type == 'normal':
            count = 1
        from .order import searchAdMediumOrderExecutiveReport
        day_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
        executive_reports = searchAdMediumOrderExecutiveReport.query.filter_by(
            client_order=self, month_day=day_month)
        if executive_reports:
            medium_money = sum([k.medium_money for k in executive_reports])
            medium_money2 = sum([k.medium_money2 for k in executive_reports])
            sale_money = sum([k.sale_money for k in executive_reports])
            return {'medium_money': medium_money / count,
                    'medium_money2': medium_money2 / count,
                    'sale_money': sale_money / count}
        else:
            return {'medium_money': 0, 'medium_money2': 0, 'sale_money': 0}

    def get_saler_leaders(self):
        leaders = []
        for user in self.agent_sales + self.direct_sales:
            leaders += user.team_leaders
        return leaders

    def insert_reject_time(self):
        client_order_reject = searchAdClientOrderReject.query.filter_by(
            client_order=self, reject_time=datetime.date.today()).first()
        if client_order_reject:
            client_order_reject.reject_time = datetime.date.today()
        else:
            searchAdClientOrderReject.add(
                client_order=self, reject_time=datetime.date.today())

    def zhixing_money(self, sale_type):
        if sale_type == 'agent':
            count = len(self.agent_sales)
            user = self.agent_sales[0]
        else:
            count = len(self.direct_sales)
            user = self.direct_sales[0]
        if user.team.location == 3:
            count = len(set(self.agent_sales + self.direct_sales))
        return self.money / count

    def zhixing_medium_money2(self, sale_type):
        if sale_type == 'agent':
            count = len(self.agent_sales)
            user = self.agent_sales[0]
        else:
            count = len(self.direct_sales)
            user = self.direct_sales[0]
        if user.team.location == 3:
            count = len(set(self.agent_sales + self.direct_sales))
        return self.mediums_money2 / count

    @property
    def order_path(self):
        return url_for('searchAd_order.order_info', order_id=self.id, tab_id=1)

    def can_edit_contract_time(self, now_date=None):
        if not now_date:
            now_date = datetime.date.today()
        if self.client_start.month > now_date.month:
            return True
        else:
            return False

    @property
    def framework_order(self):
        try:
            framework = searchAdFrameworkOrder.get(self.framework_order_id)
            return {'id': framework.id, 'name': framework.name}
        except:
            return {'id': 0, 'name': u'无框架'}

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


class searchAdConfirmMoney(db.Model, BaseModelMixin):
    __tablename__ = 'searchad_bra_client_order_confirm_money'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'searchAdClientOrder', backref=db.backref('searchad_confirm_client_order', lazy='dynamic'))
    order_id = db.Column(
        db.Integer, db.ForeignKey('searchAd_bra_order.id'))  # 客户合同
    order = db.relationship(
        'searchAdOrder', backref=db.backref('searchad_confirm_order', lazy='dynamic'))
    money = db.Column(db.Float())
    rebate = db.Column(db.Float())
    year = db.Column(db.Integer)
    Q = db.Column(db.String(2))
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': year.desc()}

    def __init__(self, client_order, year, Q, order, money=0.0, rebate=0.0, create_time=None):
        self.client_order = client_order
        self.order = order
        self.money = money
        self.rebate = rebate
        self.year = year
        self.Q = Q
        self.create_time = create_time or datetime.date.today()

    @property
    def time(self):
        return str(self.year) + str(self.Q)


class searchAdBackMoney(db.Model, BaseModelMixin):
    __tablename__ = 'searchAd_bra_client_order_back_money'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'searchAdClientOrder', backref=db.backref('backmoneys', lazy='dynamic'))
    money = db.Column(db.Float())
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_order, money=0.0, create_time=None, back_time=None):
        self.client_order = client_order
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
    def real_back_money_diff_time(self):
        return (self.back_time.date() - self.client_order.reminde_date).days


# 客户返点发票
class searchAdBackInvoiceRebate(db.Model, BaseModelMixin):
    __tablename__ = 'searchAd_bra_client_order_back_invoice_rebate'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'searchAdClientOrder', backref=db.backref('backinvoicerebates', lazy='dynamic'))
    num = db.Column(db.String(100))  # 发票号
    money = db.Column(db.Float())
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_order, num='', money=0.0, create_time=None, back_time=None):
        self.client_order = client_order
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


class searchAdClientOrderExecutiveReport(db.Model, BaseModelMixin):
    __tablename__ = 'searchAd_bra_client_order_executive_report'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'searchAdClientOrder', backref=db.backref('executive_reports', lazy='dynamic'))
    money = db.Column(db.Float())
    month_day = db.Column(db.DateTime)
    days = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    # 合同文件打包
    order_json = db.Column(db.Text(), default=json.dumps({}))
    status = db.Column(db.Integer, index=True)
    contract_status = db.Column(db.Integer, index=True)
    __table_args__ = (db.UniqueConstraint(
        'client_order_id', 'month_day', name='_searchAd_client_order_month_day'),)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_order, money=0, month_day=None, days=0, create_time=None):
        self.client_order = client_order
        self.money = money
        self.month_day = month_day or datetime.date.today()
        self.days = days
        self.create_time = create_time or datetime.date.today()
        # 合同文件打包
        self.status = client_order.status
        self.contract_status = client_order.contract_status
        # 获取相应合同字段
        dict_order = {}
        dict_order['client_name'] = client_order.client.name
        dict_order['agent_name'] = client_order.agent.name
        dict_order['contract'] = client_order.contract
        dict_order['campaign'] = client_order.campaign
        dict_order['industry_cn'] = client_order.client.industry_cn
        dict_order['locations'] = client_order.locations
        dict_order['sales'] = [
            {'id': k.id, 'name': k.name, 'location': k.team.location}for k in client_order.direct_sales]
        dict_order['salers_ids'] = [k['id'] for k in dict_order['sales']]
        dict_order['get_saler_leaders'] = [
            k.id for k in client_order.get_saler_leaders()]
        dict_order['resource_type_cn'] = client_order.resource_type_cn
        dict_order['operater_users'] = [
            {'id': k.id, 'name': k.name}for k in client_order.operater_users]
        dict_order['client_start'] = client_order.client_start.strftime(
            '%Y-%m-%d')
        dict_order['client_end'] = client_order.client_end.strftime('%Y-%m-%d')
        self.order_json = json.dumps(dict_order)

    @property
    def month_cn(self):
        return self.month_day.strftime('%Y-%m') + u'月'


class searchAdClientOrderReject(db.Model, BaseModelMixin):
    __tablename__ = 'searchAd_bra_client_order_reject'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('searchAd_bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'searchAdClientOrder', backref=db.backref('client_order_reject_id', lazy='dynamic'))
    reject_time = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint(
        'client_order_id', 'reject_time', name='_searchAd_client_order_reject_time'),)
    __mapper_args__ = {'order_by': reject_time.desc()}

    def __init__(self, client_order, reject_time=None):
        self.client_order = client_order
        self.reject_time = reject_time or datetime.date.today()

    @property
    def reject_time_cn(self):
        return self.reject_time.strftime('%Y-%m') + u'月'


def contract_generator(framework, num):
    code = "%s-%03x" % (framework, num % 1000)
    code = code.upper()
    return code


# for searchAd
BILL_RESOURCE_TYPE_CN = {
    5: 'CPA',
    6: 'CPT',
    7: 'CPC',
    8: 'CPD',
    9: 'CPM',
    10: 'CPS',
    99: u'其他'
}


class searchAdClientOrderBill(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'searchad_bra_client_order_bill'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100))
    client_id = db.Column(db.Integer, db.ForeignKey('searchAd_client.id'))
    client = db.relationship('searchAdClient', backref=db.backref('searchad_bra_client_bill', lazy='dynamic'))
    medium_id = db.Column(db.Integer, db.ForeignKey('searchAd_medium.id'))
    medium = db.relationship('searchAdMedium', backref=db.backref('searchad_bra_medium_bill', lazy='dynamic'))
    resource_type = db.Column(db.Integer)  # 推广形式
    money = db.Column(db.Float(), default=0.0)
    rebate_money = db.Column(db.Float(), default=0.0)
    start = db.Column(db.Date)
    end = db.Column(db.Date)

    def __init__(self, company, client, medium, resource_type, money, rebate_money, start=None, end=None):
        self.company = company
        self.client = client
        self.medium = medium
        self.resource_type = resource_type
        self.money = money or 0.0
        self.rebate_money = rebate_money or 0.0
        self.start = start or datetime.date.today()
        self.end = end or datetime.date.today()

    @property
    def resource_type_cn(self):
        return BILL_RESOURCE_TYPE_CN.get(self.resource_type)
