# -*- coding: UTF-8 -*-
import datetime

from . import db, BaseModelMixin


INVOICE_TYPE_NORMAL = 0         # 一般纳税人增值税专用发票
INVOICE_TYPE_COMMON = 1         # 一般纳税人增值税普通发票


INVOICE_TYPE_CN = {
    INVOICE_TYPE_NORMAL: u"一般纳税人增值税专用发票",
    INVOICE_TYPE_COMMON: u"一般纳税人增值税普通发票",
}

INVOICE_STATUS_PASS = 0          # 发票已开
INVOICE_STATUS_NORMAL = 1        # 待申请发票
INVOICE_STATUS_APPLY = 2         # 发票开具申请
INVOICE_STATUS_APPLYPASS = 3     # 批准开发票
INVOICE_STATUS_FAIL = 4          # 审批未通过

INVOICE_STATUS_CN = {
    INVOICE_STATUS_PASS: u'发票已开',
    INVOICE_STATUS_NORMAL: u'待申请发票',
    INVOICE_STATUS_APPLY: u'发票开具申请中',
    INVOICE_STATUS_APPLYPASS: u'已批准开发票',
    INVOICE_STATUS_FAIL: u'审批未通过',
}


class Invoice(db.Model, BaseModelMixin):
    __tablename__ = 'bra_invoice'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'ClientOrder', backref=db.backref('invoices', lazy='dynamic'))
    company = db.Column(db.String(100))  # 公司名称
    tax_id = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(120))  # 公司地址
    phone = db.Column(db.String(80))  # 联系电话
    bank_id = db.Column(db.String(20))  # 银行账号
    bank = db.Column(db.String(100))  # 开户行
    detail = db.Column(db.String(200))  # 发票内容
    money = db.Column(db.Float)  # 发票金额
    invoice_type = db.Column(db.Integer)  # 发票类型
    invoice_status = db.Column(db.Integer)  # 发表状态
    invoice_num = db.Column(db.String(200), default='')  # 发票号
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_invoice', lazy='dynamic'))
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_order, company="", tax_id="",
                 address="", phone="", bank_id="", bank="",
                 detail="", invoice_num="", money=0.0, invoice_type=INVOICE_TYPE_NORMAL,
                 invoice_status=INVOICE_STATUS_NORMAL, creator=None, create_time=None, back_time=None):
        self.client_order = client_order
        self.company = company
        self.tax_id = tax_id
        self.address = address
        self.phone = phone
        self.bank_id = bank_id
        self.bank = bank
        self.detail = detail
        self.money = money
        self.invoice_type = invoice_type
        self.invoice_status = invoice_status
        self.creator = creator
        self.create_time = create_time or datetime.date.today()
        self.back_time = back_time or datetime.date.today()
        self.invoice_num = invoice_num

    def __repr__(self):
        return '<Invoice %s>' % (self.id)

    @property
    def create_time_cn(self):
        return self.create_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def back_time_cn(self):
        if self.back_time:
            return self.back_time.strftime("%Y-%m-%d")
        else:
            return ""

    @property
    def invoice_type_cn(self):
        return INVOICE_TYPE_CN[self.invoice_type]

    @property
    def invoice_status_cn(self):
        return INVOICE_STATUS_CN[self.invoice_status]

    @classmethod
    def get_invoices_status(cls, status):
        return cls.query.filter_by(invoice_status=status)


MEDIUM_INVOICE_BOOL_INVOICE_FALSE = 'False'
MEDIUM_INVOICE_BOOL_INVOICE_TRUE = 'True'
MEDIUM_INVOICE_BOOL_INVOICE_CN = {
    MEDIUM_INVOICE_BOOL_INVOICE_FALSE: u'没有发票',
    MEDIUM_INVOICE_BOOL_INVOICE_TRUE: u'发票已开',
}

MEDIUM_INVOICE_BOOL_PAY_FALSE = 'False'
MEDIUM_INVOICE_BOOL_PAY_TRUE = 'True'
MEDIUM_INVOICE_BOOL_PAY_CN = {
    MEDIUM_INVOICE_BOOL_PAY_FALSE: u'未打款',
    MEDIUM_INVOICE_BOOL_PAY_TRUE: u'已打款',
}

MEDIUM_INVOICE_STATUS_PASS = 0          # 已打款的发票
MEDIUM_INVOICE_STATUS_NORMAL = 1        # 待申请的打款的发票
MEDIUM_INVOICE_STATUS_APPLY = 2         # 申请打款中

MEDIUM_INVOICE_STATUS_CN = {
    MEDIUM_INVOICE_STATUS_PASS: u'已打款的发票',
    MEDIUM_INVOICE_STATUS_NORMAL: u'待申请的打款的发票',
    MEDIUM_INVOICE_STATUS_APPLY: u'申请打款中',
}


# 客户订单-媒体发票及打款
class MediumInvoice(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_invoice'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'ClientOrder', backref=db.backref('mediuminvoices', lazy='dynamic'))

    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('mediuminvoices', lazy="dynamic"))

    company = db.Column(db.String(100))  # 公司名称
    tax_id = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(120))  # 公司地址
    phone = db.Column(db.String(80))  # 联系电话
    bank_id = db.Column(db.String(20))  # 银行账号
    bank = db.Column(db.String(100))  # 开户行
    detail = db.Column(db.String(200))  # 发票内容
    money = db.Column(db.Float)  # 发票金额
    pay_money = db.Column(db.Float)  # 打款金额
    invoice_type = db.Column(db.Integer)  # 发票类型
    invoice_status = db.Column(db.Integer)  # 发票状态
    invoice_num = db.Column(db.String(200), default='')  # 发票号
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_medium_invoice', lazy='dynamic'))

    add_time = db.Column(db.DateTime)  # 开具发票时间
    pay_time = db.Column(db.DateTime)  # 打款时间
    create_time = db.Column(db.DateTime)  # 添加时间
    bool_pay = db.Column(db.Boolean)  # 是否已打款
    bool_invoice = db.Column(db.Boolean)  # 是否开具发票
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_order, medium, company="", tax_id="",
                 address="", phone="", bank_id="", bank="",
                 detail="", invoice_num="", money=0.0, pay_money=0.0, invoice_type=INVOICE_TYPE_NORMAL,
                 invoice_status=MEDIUM_INVOICE_STATUS_NORMAL, creator=None, create_time=None,
                 add_time=None, pay_time=None, bool_pay=False, bool_invoice=True):
        self.client_order = client_order
        self.medium = medium
        self.company = company
        self.tax_id = tax_id
        self.address = address
        self.phone = phone
        self.bank_id = bank_id
        self.bank = bank
        self.detail = detail
        self.money = money
        self.pay_money = pay_money
        self.invoice_type = invoice_type
        self.invoice_status = invoice_status
        self.creator = creator
        self.create_time = create_time or datetime.date.today()
        self.add_time = add_time or datetime.date.today()
        self.pay_time = pay_time or datetime.date.today()
        self.bool_pay = bool_pay
        self.bool_invoice = bool_invoice
        self.invoice_num = invoice_num

    def __repr__(self):
        return '<Invoice %s>' % (self.id)

    @property
    def create_time_cn(self):
        return self.create_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def add_time_cn(self):
        return self.add_time.strftime("%Y-%m-%d")

    @property
    def pay_time_cn(self):
        return self.pay_time.strftime("%Y-%m-%d")

    @classmethod
    def get_medium_invoices_status(cls, status):
        return cls.query.filter_by(invoice_status=status)
