# -*- coding: UTF-8 -*-
import datetime
from flask import url_for, g

from . import db, BaseModelMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT
from models.client_order import (CONTRACT_STATUS_NEW, CONTRACT_STATUS_APPLYCONTRACT,
                                 CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYREJECT, CONTRACT_STATUS_MEDIA)
from forms.order import AssociatedDoubanOrderForm
from consts import DATE_FORMAT
from models.user import User
from libs.mail import mail


class AssociatedDoubanOrder(db.Model, BaseModelMixin, AttachmentMixin):
    __tablename__ = 'bra_associated_douban_order'

    id = db.Column(db.Integer, primary_key=True)
    medium_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_order.id'))  # 关联媒体订单
    medium_order = db.relationship(
        'Order', backref=db.backref('associated_douban_orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称
    contract = db.Column(db.String(100))  # 豆瓣合同号
    money = db.Column(db.Integer)  # 客户合同金额

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')
    create_time = db.Column(db.DateTime)

    contract_generate = False
    kind = "associated-douban-order"

    def __init__(self, medium_order, contract=None, campaign=None, money=0, creator=None, create_time=None):
        self.medium_order = medium_order
        self.contract = contract or ""
        self.campaign = campaign or ""
        self.money = money

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    @property
    def name(self):
        return u"%s-%s" % (self.medium_order.name, self.campaign)

    @property
    def contract_status(self):
        return self.medium_order.contract_status

    @property
    def client(self):
        return self.medium_order.client_order.client

    @property
    def sale_ECPM(self):
        return (float(self.money) / self.medium_order.sale_CPM) if self.medium_order.sale_CPM else 0

    @property
    def direct_sales(self):
        return self.medium_order.client_order.direct_sales

    @property
    def agent_sales(self):
        return self.medium_order.client_order.agent_sales

    @property
    def leaders(self):
        return self.medium_order.client_order.leaders

    @property
    def direct_sales_names(self):
        return ",".join([u.name for u in self.direct_sales])

    @property
    def agent_sales_names(self):
        return ",".join([u.name for u in self.agent_sales])

    @property
    def jiafang_name(self):
        return self.medium_order.medium.name

    @property
    def start_date(self):
        return self.medium_order.medium_start

    @property
    def end_date(self):
        return self.medium_order.medium_end

    @property
    def start_date_cn(self):
        return self.start_date.strftime(DATE_FORMAT)

    @property
    def end_date_cn(self):
        return self.end_date.strftime(DATE_FORMAT)

    @property
    def email_info(self):
        return u"""
        关联媒体: %s
        Campaign: %s
        金额: %s (元)
        豆瓣合同号: %s
""" % (self.medium_order.medium.name, self.campaign, self.money or 0, self.contract)

    def can_admin(self, user):
        """是否可以修改该订单"""
        return self.medium_order.client_order.can_admin(user)

    def can_edit_status(self):
        return [CONTRACT_STATUS_NEW, CONTRACT_STATUS_APPLYCONTRACT,
                CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYREJECT, CONTRACT_STATUS_MEDIA]

    def path(self):
        return self.info_path()

    def attachment_path(self):
        return url_for('files.associated_douban_order_files', order_id=self.id)

    def info_path(self):
        return self.medium_order.client_order.info_path()

    def edit_path(self):
        return url_for("order.associated_douban_order", order_id=self.id)

    def contract_path(self):
        return url_for("order.associated_douban_order_contract", order_id=self.id)

    def attach_status_confirm_path(self, attachment):
        return url_for('order.associated_douban_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_PASSED)

    def attach_status_reject_path(self, attachment):
        return url_for('order.associated_douban_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_REJECT)

    def douban_contract_apply_path(self):
        return url_for("contract.associated_douban_apply", order_id=self.id)

    @property
    def form(self):
        form = AssociatedDoubanOrderForm()
        form.medium_order.choices = [(mo.id, "%s (%s)" % (mo.name, mo.start_date_cn + '-' + str(mo.sale_money)))
                                     for mo in self.medium_order.client_order.medium_orders]
        form.medium_order.data = self.medium_order.id
        form.campaign.data = self.campaign
        form.money.data = self.money
        return form

    def delete(self):
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
    def operaters(self):
        return self.medium_order.operaters
