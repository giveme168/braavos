# -*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin
from libs.files import get_attachment_path

ATTACHMENT_STATUS_NEW = 0
ATTACHMENT_STATUS_PASSED = 1
ATTACHMENT_STATUS_REJECT = 2
ATTACHMENT_STATUS = {
    ATTACHMENT_STATUS_NEW: u"新上传",
    ATTACHMENT_STATUS_PASSED: u"已确认",
    ATTACHMENT_STATUS_REJECT: u"未通过"
}

ATTACHMENT_TYPE_CONTRACT = 0
ATTACHMENT_TYPE_SCHEDULE = 1
ATTACHMENT_TYPE_FRAMEWORK = 2
ATTACHMENT_TYPE = {
    ATTACHMENT_TYPE_CONTRACT: u"合同",
    ATTACHMENT_TYPE_SCHEDULE: u"排期",
    ATTACHMENT_TYPE_FRAMEWORK: u"框架"
}


class Attachment(db.Model, BaseModelMixin):
    __tablename__ = 'bra_attachment'
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    filename = db.Column(db.String(500))
    attachment_type = db.Column(db.Integer)
    attachment_status = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, target_type, target_id, filename, attachment_type,
                 creator, create_time=None):
        self.target_type = target_type
        self.target_id = target_id
        self.filename = filename
        self.attachment_type = attachment_type
        self.attachment_status = ATTACHMENT_STATUS_NEW
        self.creator = creator
        self.create_time = create_time

    @property
    def path(self):
        return get_attachment_path(self.filename)

    @property
    def status_cn(self):
        return ATTACHMENT_STATUS.get(self.attachment_status, u"新上传")

    @property
    def type_cn(self):
        return ATTACHMENT_TYPE[self.attachment_type]

    @property
    def target(self):
        from .order import Order
        from .client_order import ClientOrder
        from .framework_order import FrameworkOrder

        TARGET_DICT = {
            'Order': Order,
            'ClientOrder': ClientOrder,
            'FrameworkOrder': FrameworkOrder,
        }

        return TARGET_DICT[self.target_type].get(self.target_id)
