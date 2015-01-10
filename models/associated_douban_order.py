# -*- coding: UTF-8 -*-
import datetime
from flask import url_for

from . import db, BaseModelMixin
from models.mixin.attachment import AttachmentMixin
from models.attachment import ATTACHMENT_STATUS_PASSED, ATTACHMENT_STATUS_REJECT


class AssociatedDoubanOrder(db.Model, BaseModelMixin, AttachmentMixin):
    __tablename__ = 'bra_associated_douban_order'

    id = db.Column(db.Integer, primary_key=True)
    medium_order_id = db.Column(db.Integer, db.ForeignKey('agent.id'))  # 客户合同甲方
    medium_order = db.relationship('Agent', backref=db.backref('client_orders', lazy='dynamic'))

    contract = db.Column(db.String(100))  # 豆瓣合同号

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_client_orders', lazy='dynamic'))
    create_time = db.Column(db.DateTime)

    contract_generate = False

    def __init__(self, medium_order, contract="", creator=None, create_time=None):
        self.medium_order = medium_order
        self.contract = contract

        self.creator = creator
        self.create_time = create_time or datetime.datetime.now()

    @property
    def name(self):
        return u"%s-豆瓣" % (self.medium_order.name)

    def path(self):
        return url_for('order.order_info', order_id=self.id)

    def attachment_path(self):
        return url_for('files.client_order_files', order_id=self.id)

    def info_path(self):
        return url_for("order.order_info", order_id=self.id)

    def contract_path(self):
        return url_for("order.client_order_contract", order_id=self.id)

    def attach_status_confirm_path(self, attachment):
        return url_for('order.client_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_PASSED)

    def attach_status_reject_path(self, attachment):
        return url_for('order.client_attach_status',
                       order_id=self.id,
                       attachment_id=attachment.id,
                       status=ATTACHMENT_STATUS_REJECT)
