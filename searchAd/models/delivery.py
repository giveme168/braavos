# -*- coding: UTF-8 -*-
from . import db, BaseModelMixin

DELIVERY_TYPE_MONITOR = 0
DELIVERY_TYPE_CLICK = 1


class Delivery(db.Model, BaseModelMixin):
    """Delivery 主要用来做统计用的
        Storm那边统计的每天的素材, 广告单元, 订单项的展示, 点击
        按照天来统计
    """
    __tablename__ = 'searchAd_delivery'

    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    value = db.Column(db.Integer)
    delivery_type = db.Column(db.Integer)

    def __init__(self, target_type, target_id, date, delivery_type, value):
        self.target_type = target_type
        self.target_id = target_id
        self.date = date
        self.value = value
        self.delivery_type = delivery_type

    def __repr__(self):
        return '<Delivery %s, %s=%s>' % (self.id, self.target_type, self.target_id)
