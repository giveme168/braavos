# -*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin
from libs.files import get_attachment_path


class Attachment(db.Model, BaseModelMixin):
    __tablename__ = 'bra_attachment'
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    filename = db.Column(db.String(500))
    attachment_type = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, target_type, target_id, filename, attachment_type,
                 creator, create_time=None):
        self.target_type = target_type
        self.target_id = target_id
        self.filename = filename
        self.attachment_type = attachment_type
        self.creator = creator
        self.create_time = create_time

    @property
    def path(self):
        return get_attachment_path(self.filename)

    @property
    def target(self):
        from .order import Order
        from .client_order import ClientOrder

        TARGET_DICT = {
            'Order': Order,
            'ClientOrder': ClientOrder,
        }

        return TARGET_DICT[self.target_type].get(self.target_id)
