# -*- coding: UTF-8 -*-
import os
import datetime
from flask import current_app as app

from . import db, BaseModelMixin
from libs.files import get_attachment_path, get_medium_path, get_full_path, get_all_file_path

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
ATTACHMENT_TYPE_OUTSOURCE = 3
ATTACHMENT_TYPE_OTHERS = 4
ATTACHMENT_TYPE_MEDIUM_INTRODUCE = 5
ATTACHMENT_TYPE_MEDIUM_PRODUCT = 6
ATTACHMENT_TYPE_MEDIUM_DATA = 7
ATTACHMENT_TYPE_MEDIUM_NEW_PRODUCT = 8
ATTACHMENT_TYPE_AGENT = 9
ATTACHMENT_TYPE_FINISH = 10
ATTACHMENT_TYPE_USER_PIC = 11
ATTACHMENT_TYPE_MEDIUM = 12
ATTACHMENT_TYPE_MEDIUM_GROUP = 13
ATTACHMENT_TYPE_BILL = 14

ATTACHMENT_TYPE = {
    ATTACHMENT_TYPE_CONTRACT: u"合同",
    ATTACHMENT_TYPE_SCHEDULE: u"排期",
    ATTACHMENT_TYPE_FRAMEWORK: u"框架",
    ATTACHMENT_TYPE_OUTSOURCE: u"外包资料",
    ATTACHMENT_TYPE_OTHERS: u"其他资料",
    ATTACHMENT_TYPE_MEDIUM_INTRODUCE: u"媒体介绍",
    ATTACHMENT_TYPE_MEDIUM_PRODUCT: u"媒体刊列",
    ATTACHMENT_TYPE_MEDIUM_DATA: u"媒体数据",
    ATTACHMENT_TYPE_MEDIUM_NEW_PRODUCT: u"媒体新资源",
    ATTACHMENT_TYPE_AGENT: u'代理/甲方资料',
    ATTACHMENT_TYPE_FINISH: u'合同扫描件',
    ATTACHMENT_TYPE_USER_PIC: u'用户头像',
    ATTACHMENT_TYPE_MEDIUM: u'媒体资质',
    ATTACHMENT_TYPE_MEDIUM_GROUP: u'一级媒体资质',
    ATTACHMENT_TYPE_BILL: u'结算单'
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
    def medium_path(self):
        return get_medium_path(self.filename)

    @property
    def all_file_path(self):
        return get_all_file_path(self.filename)

    @property
    def agent_path(self):
        return get_full_path(self.filename)

    @property
    def client_path(self):
        return get_full_path(self.filename)

    @property
    def path(self):
        return get_attachment_path(self.filename)

    @property
    def real_path(self):
        return os.path.join(app.upload_set_config.get('attachment').destination, self.filename)

    @property
    def full_path(self):
        return get_attachment_path(self.filename, True)

    @property
    def status_cn(self):
        return ATTACHMENT_STATUS.get(self.attachment_status, u"新上传")

    def is_passed(self):
        return self.attachment_status == ATTACHMENT_STATUS_PASSED

    @property
    def type_cn(self):
        return ATTACHMENT_TYPE[self.attachment_type]

    @property
    def target(self):
        from .order import Order
        from .client_order import ClientOrder
        from .framework_order import FrameworkOrder
        from .douban_order import DoubanOrder
        from .associated_douban_order import AssociatedDoubanOrder
        from .client import Agent
        from .user import User
        from .medium import Medium, MediumGroup

        # add for searchAd team
        from searchAd.models.order import searchAdOrder
        from searchAd.models.client_order import searchAdClientOrder
        from searchAd.models.framework_order import searchAdFrameworkOrder

        TARGET_DICT = {
            'Order': Order,
            'ClientOrder': ClientOrder,
            'FrameworkOrder': FrameworkOrder,
            'DoubanOrder': DoubanOrder,
            'AssociatedDoubanOrder': AssociatedDoubanOrder,
            'searchAdOrder': searchAdOrder,
            'searchAdClientOrder': searchAdClientOrder,
            'searchAdFrameworkOrder': searchAdFrameworkOrder,
            'Agent': Agent,
            'User': User,
            'Medium': Medium,
            'MediumGroup': MediumGroup
        }
        return TARGET_DICT[self.target_type].get(self.target_id)
