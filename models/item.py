#-*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin

SALE_TYPE_NORMAL = 0         # 标准, 购买
SALE_TYPE_GIFT = 1           # 配送
SALE_TYPE_REMNANT = 2         # 补量
SALE_TYPE_CPC = 3            # CPC

SALE_TYPE_CN = {
    SALE_TYPE_NORMAL: u"标准/购买",
    SALE_TYPE_GIFT: u"配送",
    SALE_TYPE_REMNANT: u"补量",
    SALE_TYPE_CPC: u"CPC",
}

AD_TYPE_NORMAL = 0
AD_TYPE_CPD = 1
AD_TYPE_REMNANT = 2

AD_TYPE_CN = {
    AD_TYPE_NORMAL: u"标准/CPM",
    AD_TYPE_CPD: u"CPD",
    AD_TYPE_REMNANT: u"补余",
}


class AdItem(db.Model, BaseModelMixin):
    __tablename__ = 'bra_item'
    # 基础
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('bra_order.id'))
    order = db.relationship('Order', backref=db.backref('items', lazy='dynamic'))
    description = db.Column(db.String(500))
    # 排期
    sale_type = db.Column(db.Integer)  # 售卖类型: 购买, 配送, 补量, CPC
    position_id = db.Column(db.Integer, db.ForeignKey('ad_position.id'))
    position = db.relationship('AdPosition', backref=db.backref('order_items', lazy='dynamic'))
    special_sale = db.Column(db.Boolean)  # 特殊投放
    price = db.Column(db.Integer)
    # 投放
    ad_type = db.Column(db.Integer)  # 广告类型: 标准, CPD, 补余
    priority = db.Column(db.Integer)  # 优先级
    speed = db.Column(db.Integer)  # 投放速度
    # 创建者
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_items', lazy='dynamic'))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, order, sale_type, special_sale, position, creator, create_time):
        self.order = order
        self.sale_type = sale_type
        self.special_sale = special_sale
        self.position = position
        self.creator = creator
        self.create_time = create_time

    def __repr__(self):
        return '<Order %s>' % (self.name)

    @property
    def name(self):
        return "%s-%s" % (self.position.name, self.description or "")

    @property
    def sale_type_cn(self):
        return SALE_TYPE_CN[self.sale_type]
