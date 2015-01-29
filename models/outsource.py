# -*- coding: UTF-8 -*-
from . import db, BaseModelMixin


TARGET_TYPE_FLASH = 1
TARGET_TYPE_KOL = 2
TARGET_TYPE_OTHER = 3
TARGET_TYPE_CN = {
    TARGET_TYPE_FLASH: u"Flash外包商",
    TARGET_TYPE_KOL: u"KOL",
    TARGET_TYPE_OTHER: u"其他"
}


class OutSourceTarget(db.Model, BaseModelMixin):
    __tablename__ = 'out_source_target'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    bank = db.Column(db.String(100))
    card = db.Column(db.String(100))
    alipay = db.Column(db.String(100))
    contract = db.Column(db.String(1000))
    remark = db.Column(db.String(1000))
    type = db.Column(db.Integer)

    def __init__(self, name, bank, card, alipay, contract, remark, type):
        self.name = name
        self.bank = bank
        self.card = card
        self.alipay = alipay
        self.contract = contract
        self.remark = remark
        self.type = type

    @property
    def type_cn(self):
        return TARGET_TYPE_CN[self.type]

"""
class OutSource(db.Model, BaseModelMixin):
    __tablename__ = 'out_source'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('out_source_target.id'))
    target = db.relationship('Team', backref=db.backref('outsources', lazy='dynamic'))
    medium_order_id = db.Column(db.Integer, db.ForeignKey('bra_order.id'))
    medium_order = db.relationship('Order', backref=db.backref('outsources', lazy='dynamic'))
    num = db.Column(db.Integer)
    invoice = db.Column(db.Boolean)
    paid = db.Column(db.Boolean)
    type = db.Column(db.Integer)
    remark = db.Column(db.String(1000))

    def __init__(self, target, medium_order, num, invoice, paid, type, remark):
        self.target = target
        self.medium_order = medium_order
        self.num = num
        self.invoice = invoice
        self.paid = paid
        self.type = type
        self.remark = remark
"""
