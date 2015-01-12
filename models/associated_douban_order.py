# -*- coding: UTF-8 -*-
import datetime
from flask import url_for

from . import db, BaseModelMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT


class AssociatedDoubanOrder(db.Model, BaseModelMixin, AttachmentMixin):
    __tablename__ = 'bra_associated_douban_order'

    id = db.Column(db.Integer, primary_key=True)
    medium_order_id = db.Column(db.Integer, db.ForeignKey('bra_order.id'))  # 关联媒体订单
    medium_order = db.relationship('Order', backref=db.backref('associated_douban_orders', lazy='dynamic'))
    campaign = db.Column(db.String(100))  # 活动名称
    contract = db.Column(db.String(100))  # 豆瓣合同号

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')
    create_time = db.Column(db.DateTime)

    contract_generate = False

    def __init__(self, medium_order, contract=None, campaign=None, creator=None, create_time=None):
        self.medium_order = medium_order
        self.contract = contract or ""
        self.campaign = campaign or ""

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    @property
    def name(self):
        return u"%s-豆瓣" % (self.medium_order.name)

    @property
    def direct_sales(self):
        return self.medium_order.client_order.direct_sales

    @property
    def agent_sales(self):
        return self.medium_order.client_order.agent_sales

    @property
    def jiafang_name(self):
        return self.medium_order.medium.name

    @property
    def money(self):
        return self.medium_order.medium_money

    def path(self):
        return url_for('order.order_info', order_id=self.id)

    def attachment_path(self):
        return url_for('files.associated_douban_order_files', order_id=self.id)

    def info_path(self):
        return url_for("order.order_info", order_id=self.medium_order.client_order.id)

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
