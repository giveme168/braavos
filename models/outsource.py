# -*- coding: UTF-8 -*-
import datetime

from flask import url_for
from . import db, BaseModelMixin
from models.mixin.comment import CommentMixin
from models.user import User

TARGET_TYPE_FLASH = 1
TARGET_TYPE_KOL = 2
TARGET_TYPE_OTHER = 3
TARGET_TYPE_BETTER = 4
TARGET_TYPE_H5 = 5
TARGET_TYPE_CN = {
    TARGET_TYPE_FLASH: u"Flash外包商",
    TARGET_TYPE_KOL: u"KOL",
    TARGET_TYPE_BETTER: u"效果优化",
    TARGET_TYPE_OTHER: u"其他",
    TARGET_TYPE_H5: u"h5外包商",
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

    def client_outsources_by_status(self, status):
        return list(OutSource.query.filter_by(target_id=self.id, status=status))

    def client_outsources_by_paied(self):
        return list(OutSource.query.filter_by(target_id=self.id, status=OUTSOURCE_STATUS_PAIED))

    def douban_outsources_by_status(self, status):
        return list(DoubanOutSource.query.filter_by(target_id=self.id, status=status))

    def douban_outsources_by_paied(self):
        return list(DoubanOutSource.query.filter_by(target_id=self.id, status=OUTSOURCE_STATUS_PAIED))

    def outsource_status_cn(self, status):
        if int(status) == OUTSOURCE_STATUS_PAIED:
            return OUTSOURCE_STATUS_CN[OUTSOURCE_STATUS_PAIED]
        elif int(status) == OUTSOURCE_STATUS_PASS:
            return OUTSOURCE_STATUS_CN[OUTSOURCE_STATUS_PASS]
        else:
            return OUTSOURCE_STATUS_CN[OUTSOURCE_STATUS_APPLY_MONEY]


OUTSOURCE_TYPE_GIFT = 1
OUTSOURCE_TYPE_FLASH = 2
OUTSOURCE_TYPE_KOL = 3
OUTSOURCE_TYPE_BETTER = 4
OUTSOURCE_TYPE_OTHER = 5
OUTSOURCE_TYPE_FLASH_AND_H5 = 6
OUTSOURCE_TYPE_H5 = 7
OUTSOURCE_TYPE_CN = {
    OUTSOURCE_TYPE_GIFT: u"奖品",
    OUTSOURCE_TYPE_FLASH: u"Flash",
    OUTSOURCE_TYPE_KOL: u"劳务(KOL、线下活动等)",
    OUTSOURCE_TYPE_BETTER: u"效果优化",
    OUTSOURCE_TYPE_OTHER: u"其他(视频等)",
    OUTSOURCE_TYPE_FLASH_AND_H5: u'flash&H5开发',
    OUTSOURCE_TYPE_H5: u'H5开发',
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
OUTSOURCE_SUBTYPE_H5 = 14
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
    OUTSOURCE_SUBTYPE_H5: u"展示型H5",
}

OUTSOURCE_STATUS_NEW = 0
OUTSOURCE_STATUS_APPLY_LEADER = 1
OUTSOURCE_STATUS_PASS = 2
OUTSOURCE_STATUS_APPLY_MONEY = 3
OUTSOURCE_STATUS_PAIED = 4
OUTSOURCE_STATUS_EXCEED = 5

OUTSOURCE_STATUS_CN = {
    OUTSOURCE_STATUS_NEW: u"待申请",
    OUTSOURCE_STATUS_APPLY_LEADER: u"申请审批中...",
    OUTSOURCE_STATUS_PASS: u"审批通过",
    OUTSOURCE_STATUS_APPLY_MONEY: u"请款中...",
    OUTSOURCE_STATUS_PAIED: u"已打款",
    OUTSOURCE_STATUS_EXCEED: u'超过2%,申请审批中...'
}

INVOICE_RATE = 0.05    # 发票税点
OUTSOURCE_INVOICE_FALSE = 'False'
OUTSOURCE_INVOICE_TRUE = 'True'
OUTSOURCE_INVOICE_CN = {
    OUTSOURCE_INVOICE_FALSE: u'无',
    OUTSOURCE_INVOICE_TRUE: u'有',
}


table_merger_outsources = db.Table('merget_outsources',
                                   db.Column(
                                       'mergeroutsource_id', db.Integer, db.ForeignKey('merger_out_source.id')),
                                   db.Column(
                                       'outsource_id', db.Integer, db.ForeignKey('out_source.id'))
                                   )


class OutSource(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'out_source'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('out_source_target.id'))
    target = db.relationship(
        'OutSourceTarget', backref=db.backref('outsources', lazy='dynamic'))
    medium_order_id = db.Column(db.Integer, db.ForeignKey('bra_order.id'))
    medium_order = db.relationship(
        'Order', backref=db.backref('outsources', lazy='dynamic'))
    merger_outsources = db.relationship(
        'MergerOutSource', secondary=table_merger_outsources)
    num = db.Column(db.Integer)
    type = db.Column(db.Integer)
    subtype = db.Column(db.Integer)
    invoice = db.Column(db.Boolean)  # 发票
    paid = db.Column(db.Boolean)  # 付款
    pay_num = db.Column(db.Float)
    remark = db.Column(db.String(1000))
    status = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, target, medium_order, num, type, subtype, pay_num=0,
                 invoice=False, paid=False, remark=None, status=0):
        self.target = target
        self.medium_order = medium_order
        self.num = num
        self.pay_num = pay_num
        self.type = type
        self.subtype = subtype
        self.invoice = invoice
        self.paid = paid
        self.remark = remark or ""
        self.status = status
        self.create_time = datetime.date.today()

    @property
    def name(self):
        return "%s-%s-%s-%s" % (self.medium_order.medium.name,
                                self.target.name,
                                self.type_cn,
                                self.num)

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

    @property
    def invoice_cn(self):
        return OUTSOURCE_INVOICE_CN[str(self.invoice)]

    @property
    def invoice_num(self):
        return self.pay_num

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.medium_order.operaters + User.operater_leaders()
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
        form.pay_num.data = self.pay_num
        form.type.data = self.type
        form.subtype.data = self.subtype
        form.remark.data = self.remark
        return form

    @property
    def outsource_info(self):
        medium_name = self.medium_order.medium.name
        contract = self.medium_order.medium_contract
        return u"""
        投放媒体: %s
        合同号:%s
        外包方: %s
        外包金额: %s
        外包类别: %s
        子分类: %s
        备注: %s""" % (medium_name, contract, self.target.name, self.pay_num, self.type_cn, self.subtype_cn, self.remark)

    @classmethod
    def get_apply_money_outsources(cls):
        return cls.query.filter_by(status=OUTSOURCE_STATUS_APPLY_MONEY)

    @classmethod
    def get_outsources_by_target(cls, target_id, status):
        return list(cls.query.filter_by(target_id=target_id, status=status))

    @property
    def create_time_cn(self):
        if self.create_time:
            return self.create_time.strftime('%Y-%m-%d')
        else:
            return ''

    def finance_pay_path(self):
        return url_for('finance_pay.index')

    @property
    def invoice_info(self):
        try:
            return self.merger_outsources[0].remark
        except:
            return ''


table_merger_douban_outsources = db.Table('merget_douban_outsources',
                                          db.Column(
                                              'mergerdoubanoutsource_id', db.Integer,
                                              db.ForeignKey('merger_douban_out_source.id')),
                                          db.Column(
                                              'doubanoutsource_id', db.Integer,
                                              db.ForeignKey('douban_out_source.id'))
                                          )


class DoubanOutSource(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'douban_out_source'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('out_source_target.id'))
    target = db.relationship('OutSourceTarget', backref=db.backref(
        'douban_outsources_target', lazy='dynamic'))
    douban_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_douban_order.id'))
    douban_order = db.relationship(
        'DoubanOrder', backref=db.backref('douban_outsources', lazy='dynamic'))
    merger_outsources = db.relationship(
        'MergerDoubanOutSource', secondary=table_merger_douban_outsources)
    num = db.Column(db.Integer)
    type = db.Column(db.Integer)
    subtype = db.Column(db.Integer)
    invoice = db.Column(db.Boolean)  # 发票
    paid = db.Column(db.Boolean)  # 付款
    pay_num = db.Column(db.Float)
    remark = db.Column(db.String(1000))
    status = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, target, douban_order, num, type, subtype, pay_num=0,
                 invoice=False, paid=False, remark=None, status=0):
        self.target = target
        self.douban_order = douban_order
        self.num = num
        self.pay_num = pay_num
        self.type = type
        self.subtype = subtype
        self.invoice = invoice
        self.paid = paid
        self.remark = remark or ""
        self.status = status
        self.create_time = datetime.date.today()

    @property
    def name(self):
        return "%s-%s-%s-%s" % (self.douban_order.name,
                                self.target.name,
                                self.type_cn,
                                self.num)

    def edit_path(self):
        return url_for('outsource.outsource', outsource_id=self.id)

    def info_path(self):
        return url_for("outsource.douban_outsources",
                       order_id=self.douban_order.id)

    @property
    def type_cn(self):
        return OUTSOURCE_TYPE_CN[self.type]

    @property
    def subtype_cn(self):
        return OUTSOURCE_SUBTYPE_CN[self.subtype]

    @property
    def invoice_cn(self):
        return OUTSOURCE_INVOICE_CN[str(self.invoice)]

    @property
    def invoice_num(self):
        return self.pay_num

    def can_admin(self, user):
        """是否可以修改该订单"""
        admin_users = self.douban_order.operaters + User.operater_leaders()
        return user.is_admin() or user in admin_users

    @property
    def form(self):
        from forms.outsource import DoubanOutsourceForm
        form = DoubanOutsourceForm()
        form.douban_order.choices = [
            (self.douban_order.id, self.douban_order.name)]
        form.douban_order.data = self.douban_order.id
        form.target.data = self.target.id
        form.num.data = self.num
        form.pay_num.data = self.pay_num
        form.type.data = self.type
        form.subtype.data = self.subtype
        form.remark.data = self.remark
        return form

    @property
    def outsource_info(self):
        name = self.douban_order.name
        contract = self.douban_order.contract
        return u"""
        投放媒体: %s
        合同号: %s
        外包方: %s
        外包金额: %s
        外包类别: %s
        子分类: %s
        备注: %s""" % (name, contract, self.target.name, self.num, self.type_cn, self.subtype_cn, self.remark)

    @classmethod
    def get_apply_money_outsources(cls):
        return cls.query.filter_by(status=OUTSOURCE_STATUS_APPLY_MONEY)

    @classmethod
    def get_outsources_by_target(cls, target_id, status):
        return list(cls.query.filter_by(target_id=target_id, status=status))

    @property
    def create_time_cn(self):
        if self.create_time:
            return self.create_time.strftime('%Y-%m-%d')
        else:
            return ''

    def finance_pay_path(self):
        return url_for('finance_pay.douban_index')

    @property
    def invoice_info(self):
        try:
            return self.merger_outsources[0].remark
        except:
            return ''


MERGER_OUTSOURCE_STATUS_PAIED = 0
MERGER_OUTSOURCE_STATUS_APPLY_MONEY = 1

MERGER_OUTSOURCE_STATUS_CN = {
    MERGER_OUTSOURCE_STATUS_PAIED: u"已打款",
    MERGER_OUTSOURCE_STATUS_APPLY_MONEY: u"请款中...",
}


class MergerOutSource(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'merger_out_source'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('out_source_target.id'))
    target = db.relationship('OutSourceTarget', backref=db.backref(
        'merger_outsources_target', lazy='dynamic'))
    outsources = db.relationship('OutSource', secondary=table_merger_outsources)
    invoice = db.Column(db.Boolean)  # 发票
    pay_num = db.Column(db.Float)    # 打款金额
    num = db.Column(db.Float)        # 原始金额
    remark = db.Column(db.String(1000))  # 发票信息
    status = db.Column(db.Integer)      # 状态
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, target, outsources, num, pay_num=0,
                 invoice=False, remark="", status=0):
        self.target = target
        self.outsources = outsources or []
        self.num = num
        self.pay_num = pay_num
        self.invoice = invoice
        self.remark = remark or ""
        self.status = status
        self.create_time = datetime.date.today()

    @classmethod
    def get_outsources_by_status(cls, status):
        return cls.query.filter_by(status=status)

    @property
    def media_info(self):
        return '<br/>'.join([k.outsource_info for k in self.outsources])

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d')


class MergerDoubanOutSource(db.Model, BaseModelMixin, CommentMixin):
    __tablename__ = 'merger_douban_out_source'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('out_source_target.id'))
    target = db.relationship('OutSourceTarget', backref=db.backref(
        'merger_douban_outsources_target', lazy='dynamic'))
    outsources = db.relationship(
        'DoubanOutSource', secondary=table_merger_douban_outsources)
    invoice = db.Column(db.Boolean)  # 发票
    pay_num = db.Column(db.Float)    # 打款金额
    num = db.Column(db.Float)        # 原始金额
    remark = db.Column(db.String(1000))  # 发票信息
    status = db.Column(db.Integer)      # 状态
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, target, outsources, num, pay_num=0,
                 invoice=False, remark="", status=0):
        self.target = target
        self.outsources = outsources or []
        self.num = num
        self.pay_num = pay_num
        self.invoice = invoice
        self.remark = remark or ""
        self.status = status
        self.create_time = datetime.date.today()

    @classmethod
    def get_outsources_by_status(cls, status):
        return cls.query.filter_by(status=status)

    @property
    def media_info(self):
        return '<br/>'.join([k.outsource_info for k in self.outsources])

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d')
