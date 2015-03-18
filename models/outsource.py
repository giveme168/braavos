# -*- coding: UTF-8 -*-
from flask import url_for
from . import db, BaseModelMixin
from models.mixin.comment import CommentMixin


TARGET_TYPE_FLASH = 1
TARGET_TYPE_KOL = 2
TARGET_TYPE_OTHER = 3
TARGET_TYPE_BETTER = 4
TARGET_TYPE_CN = {
    TARGET_TYPE_FLASH: u"Flash外包商",
    TARGET_TYPE_KOL: u"KOL",
    TARGET_TYPE_BETTER: u"效果优化",
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


OUTSOURCE_TYPE_GIFT = 1
OUTSOURCE_TYPE_FLASH = 2
OUTSOURCE_TYPE_KOL = 3
OUTSOURCE_TYPE_BETTER = 4
OUTSOURCE_TYPE_OTHER = 5
OUTSOURCE_TYPE_CN = {
    OUTSOURCE_TYPE_GIFT: u"奖品",
    OUTSOURCE_TYPE_FLASH: u"Flash",
    OUTSOURCE_TYPE_KOL: u"劳务(KOL、线下活动等)",
    OUTSOURCE_TYPE_BETTER: u"效果优化",
    OUTSOURCE_TYPE_OTHER: u"其他(视频等)"
}

OUTSOURCE_SUBTYPE_NOFLASH = 1
OUTSOURCE_SUBTYPE_BOCAI = 2
OUTSOURCE_SUBTYPE_TUWEN = 3
OUTSOURCE_SUBTYPE_FENSI = 4
OUTSOURCE_SUBTYPE_FM = 5
OUTSOURCE_SUBTYPE_FORM = 6
OUTSOURCE_SUBTYPE_TEST = 7
OUTSOURCE_SUBTYPE_TUYA = 8
OUTSOURCE_SUBTYPE_MAP = 9
OUTSOURCE_SUBTYPE_GAME = 10
OUTSOURCE_SUBTYPE_GUESS = 11
OUTSOURCE_SUBTYPE_FACE = 12
OUTSOURCE_SUBTYPE_OTHER = 13
OUTSOURCE_SUBTYPE_CN = {
    OUTSOURCE_SUBTYPE_NOFLASH: u"非FLASH",
    OUTSOURCE_SUBTYPE_BOCAI: u"抽奖博彩",
    OUTSOURCE_SUBTYPE_TUWEN: u"图文拼贴组合（单格图文UGC，多格漫画）",
    OUTSOURCE_SUBTYPE_FENSI: u"粉丝日记创作分享",
    OUTSOURCE_SUBTYPE_FM: u"豆瓣电台互动",
    OUTSOURCE_SUBTYPE_FORM: u"问卷测试",
    OUTSOURCE_SUBTYPE_TEST: u"豆瓣用户数据测试",
    OUTSOURCE_SUBTYPE_TUYA: u"涂鸦",
    OUTSOURCE_SUBTYPE_MAP: u"地图互动",
    OUTSOURCE_SUBTYPE_GAME: u"纯游戏",
    OUTSOURCE_SUBTYPE_GUESS: u"猜图",
    OUTSOURCE_SUBTYPE_FACE: u"面部识别及信息合成",
    OUTSOURCE_SUBTYPE_OTHER: u"其他",
}

OUTSOURCE_STATUS_NEW = 0
OUTSOURCE_STATUS_APPLY_LEADER = 1
OUTSOURCE_STATUS_PASS = 2
OUTSOURCE_STATUS_APPLY_MONEY = 3
OUTSOURCE_STATUS_PAIED = 4
OUTSOURCE_STATUS_CN = {
    OUTSOURCE_STATUS_NEW: u"待申请",
    OUTSOURCE_STATUS_APPLY_LEADER: u"申请审批中...",
    OUTSOURCE_STATUS_PASS: u"审批通过",
    OUTSOURCE_STATUS_APPLY_MONEY: u"请款中...",
    OUTSOURCE_STATUS_PAIED: u"已打款"
}


class OutSource(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'out_source'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('out_source_target.id'))
    target = db.relationship('OutSourceTarget', backref=db.backref('outsources', lazy='dynamic'))
    medium_order_id = db.Column(db.Integer, db.ForeignKey('bra_order.id'))
    medium_order = db.relationship('Order', backref=db.backref('outsources', lazy='dynamic'))
    num = db.Column(db.Integer)
    type = db.Column(db.Integer)
    subtype = db.Column(db.Integer)
    invoice = db.Column(db.Boolean)  # 发票
    paid = db.Column(db.Boolean)  # 付款
    remark = db.Column(db.String(1000))
    status = db.Column(db.Integer)

    def __init__(self, target, medium_order, num, type, subtype, invoice=False, paid=False, remark=None, status=0):
        self.target = target
        self.medium_order = medium_order
        self.num = num
        self.type = type
        self.subtype = subtype
        self.invoice = invoice
        self.paid = paid
        self.remark = remark or ""
        self.status = status

    @property
    def name(self):
        return "%s-%s-%s" % (self.medium_order.medium.name,
                             self.target.name,
                             self.type_cn)

    @property
    def client_order(self):
        return self.medium_order.client_order

    def edit_path(self):
        return url_for('outsource.outsource', outsource_id=self.id)

    def info_path(self):
        return url_for("outsource.client_outsources",
                       order_id=self.client_order.id)

    @property
    def type_cn(self):
        return OUTSOURCE_TYPE_CN[self.type]

    @property
    def subtype_cn(self):
        return OUTSOURCE_SUBTYPE_CN[self.subtype]

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.medium_order.operaters
        return user.is_admin() or user in admin_users

    @property
    def form(self):
        from forms.outsource import OutsourceForm
        form = OutsourceForm()
        form.medium_order.choices = [(mo.id, mo.medium.name)
                                     for mo in self.client_order.medium_orders]
        form.medium_order.data = self.medium_order.id
        form.target.data = self.target.id
        form.num.data = self.num
        form.type.data = self.type
        form.subtype.data = self.subtype
        form.remark.data = self.remark
        return form

    @property
    def outsource_info(self):
        return u"""
        投放媒体: %s
        外包方: %s
        外包金额: %s
        外包类别: %s
        子分类: %s
        备注: %s""" % (self.medium_order.medium.name, self.target.name,
                         self.num, self.type_cn, self.subtype_cn, self.remark)
