# -*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin


class Comment(db.Model, BaseModelMixin):
    __tablename__ = 'bra_comment'
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    msg_channel = db.Column(db.Integer, default=0)
    msg = db.Column(db.String(1000))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, target_type, target_id, msg, creator,
                 create_time=None, msg_channel=0):
        self.target_type = target_type
        self.target_id = target_id
        self.msg = msg
        self.creator = creator
        self.create_time = create_time
        self.msg_channel = msg_channel

    def __repr__(self):
        return '<Comment %s, target:%s-%s>' % (self.id, self.target_type, self.target_id)

    @property
    def target(self):
        from .order import Order
        from .client_order import ClientOrder
        from .douban_order import DoubanOrder
        from .framework_order import FrameworkOrder
        from .item import AdItem
        from .material import Material

        TARGET_DICT = {
            'Order': Order,
            'DoubanOrder': DoubanOrder,
            'ClientOrder': ClientOrder,
            'FrameworkOrder': FrameworkOrder,
            'AdItem': AdItem,
            'Material': Material,
        }

        return TARGET_DICT[self.target_type].get(self.target_id)
