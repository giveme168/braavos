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
    bank_id = db.Column(db.String(50))  # 银行账号
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
        return self.create_time.strftime("%Y-%m-%d")

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


# 媒体返点发票(媒体给inad打钱, inad给媒体开发票)
class MediumRebateInvoice(db.Model, BaseModelMixin):

    __tablename__ = 'bra_medium_rebate_invoice'

    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'ClientOrder', backref=db.backref("mediumrebateinvoices", lazy='dynamic'))
    medium_group_id = db.Column(db.Integer, db.ForeignKey('medium_group.id'))
    medium_group = db.relationship('MediumGroup', backref=db.backref('mediumgrouprebateinvoices', lazy='dynamic'))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship(
        'Medium', backref=db.backref('mediumrebateinvoices', lazy='dynamic'))
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'))
    media = db.relationship(
        'Media', backref=db.backref('mediarebateinvoices', lazy='dynamic'))

    # common part of *Invoice classes
    ###########################################################################
    company = db.Column(db.String(100))  # 公司名称
    tax_id = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(120))  # 公司地址
    phone = db.Column(db.String(80))  # 联系电话
    bank_id = db.Column(db.String(50))  # 银行账号
    bank = db.Column(db.String(100))  # 开户行
    detail = db.Column(db.String(200))  # 发票内容
    money = db.Column(db.Float)  # 发票金额
    invoice_type = db.Column(db.Integer)  # 发票类型
    invoice_status = db.Column(db.Integer)  # 发表状态
    invoice_num = db.Column(db.String(200), default='')  # 发票号
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_medium_rebate_invoice',
                                   lazy='dynamic'))
    create_time = db.Column(db.DateTime)
    ###########################################################################
    back_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_order, media, medium_group, company="", tax_id="", address="",
                 phone="", bank_id="", bank="", detail="", invoice_num="",
                 money=0.0, invoice_type=INVOICE_STATUS_NORMAL,
                 invoice_status=INVOICE_STATUS_NORMAL, creator=None,
                 create_time=None, back_time=None):
        self.client_order = client_order
        self.medium_id = 1
        self.media = media
        self.medium_group = medium_group
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
        self.invoice_num = invoice_num
        self.creator = creator
        self.create_time = create_time or datetime.date.today()
        self.back_time = back_time or datetime.date.today()

    def __repr__(self):
        return '<MediumRebateInvoice: %s>' % self.id

    @property
    def create_time_cn(self):
        return self.create_time.strftime('%Y-%m-%d')

    @property
    def back_time_cn(self):
        if self.back_time:
            return self.back_time.strftime('%Y-%m-%d')
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

    @property
    def search_invoice_info(self):
        return ''.join([self.client_order.client.name, self.client_order.agent.name,
                        self.client_order.campaign, self.client_order.contract,
                        self.invoice_num, self.company, self.medium.name])


MEDIUM_INVOICE_BOOL_INVOICE_FALSE = 'False'
MEDIUM_INVOICE_BOOL_INVOICE_TRUE = 'True'
MEDIUM_INVOICE_BOOL_INVOICE_CN = {
    MEDIUM_INVOICE_BOOL_INVOICE_FALSE: u'未收发票',
    MEDIUM_INVOICE_BOOL_INVOICE_TRUE: u'已收发票',
}

MEDIUM_INVOICE_BOOL_PAY_FALSE = 'False'
MEDIUM_INVOICE_BOOL_PAY_TRUE = 'True'
MEDIUM_INVOICE_BOOL_PAY_CN = {
    MEDIUM_INVOICE_BOOL_PAY_FALSE: u'未打款',
    MEDIUM_INVOICE_BOOL_PAY_TRUE: u'已打款',
}

MEDIUM_INVOICE_STATUS_PASS = 0          # 已打款
MEDIUM_INVOICE_STATUS_NORMAL = 1        # 待申请的打款
MEDIUM_INVOICE_STATUS_APPLY = 2         # 申请打款中
MEDIUM_INVOICE_STATUS_F_AGREE = 3       # 副总裁确认
MEDIUM_INVOICE_STATUS_AGREE = 4         # 总裁确认

MEDIUM_INVOICE_STATUS_CN = {
    MEDIUM_INVOICE_STATUS_PASS: u'已打款',
    MEDIUM_INVOICE_STATUS_NORMAL: u'待申请的打',
    MEDIUM_INVOICE_STATUS_APPLY: u'副总裁请审批',
    MEDIUM_INVOICE_STATUS_F_AGREE: u'总裁审批',
    MEDIUM_INVOICE_STATUS_AGREE: u"同意打款"
}


# 媒体发票
class MediumInvoice(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_invoice'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'ClientOrder', backref=db.backref('mediuminvoices', lazy='dynamic'))
    medium_group_id = db.Column(db.Integer, db.ForeignKey('medium_group.id'))
    medium_group = db.relationship('MediumGroup', backref=db.backref('mediumgroupinvoices', lazy="dynamic"))
    medium_id = db.Column(db.Integer, db.ForeignKey('medium.id'))
    medium = db.relationship('Medium', backref=db.backref('mediuminvoices', lazy="dynamic"))

    company = db.Column(db.String(100))  # 公司名称
    tax_id = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(120))  # 公司地址
    phone = db.Column(db.String(80))  # 联系电话
    bank_id = db.Column(db.String(100))  # 银行账号
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

    def __init__(self, client_order, medium, medium_group, company="", tax_id="",
                 address="", phone="", bank_id="", bank="",
                 detail="", invoice_num="", money=0.0, pay_money=0.0, invoice_type=INVOICE_TYPE_NORMAL,
                 invoice_status=MEDIUM_INVOICE_STATUS_NORMAL, creator=None, create_time=None,
                 add_time=None, pay_time=None, bool_pay=False, bool_invoice=True):
        self.client_order = client_order
        self.medium = medium
        self.medium_group = medium_group
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

    @property
    def invoice_type_cn(self):
        return INVOICE_TYPE_CN[self.invoice_type]

    @classmethod
    def get_medium_invoices_status(cls, status):
        return cls.query.filter_by(invoice_status=status)

    def get_invoice_pas_by_status(self, status):
        return [k for k in MediumInvoicePay.query.filter_by(medium_invoice=self) if k.pay_status == status]

    @property
    def get_pay_money(self):
        return sum([k.money for k in MediumInvoicePay.query.filter_by(medium_invoice=self)
                    if k.pay_status == MEDIUM_INVOICE_STATUS_PASS])

    @property
    def rebate_invoice(self):
        rebate_invoice = MediumRebateInvoice.query.filter_by(client_order_id=self.client_order_id,
                                                             medium_id=self.medium_id)
        return float(sum([i.money for i in rebate_invoice]))

    @property
    def get_unpay_money(self):
        return self.money - self.get_pay_money

    @property
    def get_apply_pay_money(self):
        return sum([k.money for k in MediumInvoicePay.query.filter_by(medium_invoice=self)
                    if k.pay_status in [MEDIUM_INVOICE_STATUS_APPLY, MEDIUM_INVOICE_STATUS_AGREE]])

    @property
    def pay_invoice_money(self):
        return sum([k.money for k in MediumInvoicePay.query.filter_by(medium_invoice=self)])

    @property
    def search_invoice_info(self):
        return ''.join([self.client_order.client.name, self.client_order.agent.name,
                        self.client_order.campaign, self.client_order.contract,
                        self.invoice_num, self.company, self.medium.name])


# 客户订单-媒体发票
class MediumInvoicePay(db.Model, BaseModelMixin):
    __tablename__ = 'bra_medium_invoice_pay'
    id = db.Column(db.Integer, primary_key=True)
    medium_invoice_id = db.Column(
        db.Integer, db.ForeignKey('bra_medium_invoice.id'))  # 客户发票
    medium_invoice = db.relationship(
        'MediumInvoice', backref=db.backref('medium_invoice_pays', lazy='dynamic'))
    detail = db.Column(db.String(200))  # 留言
    pay_status = db.Column(db.Integer)  # 付款状态
    bank = db.Column(db.String(100))
    bank_num = db.Column(db.String(100))
    company = db.Column(db.String(100))
    money = db.Column(db.Float)  # 打款金额
    pay_time = db.Column(db.DateTime)  # 打款时间
    create_time = db.Column(db.DateTime)  # 添加时间

    def __init__(self, medium_invoice, detail="", pay_status=MEDIUM_INVOICE_STATUS_NORMAL,
                 money=0.0, pay_time=None, bank="", bank_num="", company=""):
        self.medium_invoice = medium_invoice
        self.detail = detail
        self.pay_status = pay_status
        self.money = money
        self.bank = bank
        self.bank_num = bank_num
        self.company = company
        self.create_time = datetime.date.today()
        self.pay_time = pay_time or datetime.date.today()

    @property
    def pay_time_cn(self):
        return self.pay_time.strftime("%Y-%m-%d")

    @classmethod
    def get_medium_invoices_status(cls, status):
        return cls.query.filter_by(pay_status=status)

    @property
    def client_order(self):
        return self.medium_invoice.client_order

    @property
    def search_invoice_info(self):
        return self.medium_invoice.search_invoice_info


AGENT_INVOICE_BOOL_INVOICE_FALSE = 'False'
AGENT_INVOICE_BOOL_INVOICE_TRUE = 'True'
AGENT_INVOICE_BOOL_INVOICE_CN = {
    AGENT_INVOICE_BOOL_INVOICE_FALSE: u'没有发票',
    AGENT_INVOICE_BOOL_INVOICE_TRUE: u'发票已开',
}

AGENT_INVOICE_BOOL_PAY_FALSE = 'False'
AGENT_INVOICE_BOOL_PAY_TRUE = 'True'
AGENT_INVOICE_BOOL_PAY_CN = {
    AGENT_INVOICE_BOOL_PAY_FALSE: u'未打款',
    AGENT_INVOICE_BOOL_PAY_TRUE: u'已打款',
}

AGENT_INVOICE_STATUS_PASS = 0          # 已打款
AGENT_INVOICE_STATUS_NORMAL = 1        # 待申请的打款
AGENT_INVOICE_STATUS_APPLY = 2         # 申请打款中
AGENT_INVOICE_STATUS_F_AGREE = 3      # 副总裁确认
AGENT_INVOICE_STATUS_AGREE = 4        # 总裁确认

AGENT_INVOICE_STATUS_CN = {
    AGENT_INVOICE_STATUS_PASS: u'已打款',
    AGENT_INVOICE_STATUS_NORMAL: u'待申请的打款',
    AGENT_INVOICE_STATUS_APPLY: u'副总裁请审批',
    AGENT_INVOICE_STATUS_F_AGREE: u'总裁审批',
    AGENT_INVOICE_STATUS_AGREE: u'同意打款'
}


# 给代理/直客(甲方的全称)开的发票
class AgentInvoice(db.Model, BaseModelMixin):
    __tablename__ = 'bra_agent_invoice'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'ClientOrder', backref=db.backref('agentinvoices', lazy='dynamic'))

    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    agent = db.relationship(
        'Agent', backref=db.backref('agentinvoices', lazy="dynamic"))

    company = db.Column(db.String(100))  # 公司名称
    tax_id = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(120))  # 公司地址
    phone = db.Column(db.String(80))  # 联系电话
    bank_id = db.Column(db.String(100))  # 银行账号
    bank = db.Column(db.String(100))  # 开户行
    detail = db.Column(db.String(200))  # 发票内容
    money = db.Column(db.Float)  # 发票金额
    pay_money = db.Column(db.Float)  # 打款金额
    invoice_type = db.Column(db.Integer)  # 发票类型
    invoice_status = db.Column(db.Integer)  # 发票状态
    invoice_num = db.Column(db.String(200), default='')  # 发票号
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_agent_invoice', lazy='dynamic'))

    add_time = db.Column(db.DateTime)  # 开具发票时间
    pay_time = db.Column(db.DateTime)  # 打款时间
    create_time = db.Column(db.DateTime)  # 添加时间
    bool_pay = db.Column(db.Boolean)  # 是否已打款
    bool_invoice = db.Column(db.Boolean)  # 是否开具发票
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_order, agent, company="", tax_id="",
                 address="", phone="", bank_id="", bank="",
                 detail="", invoice_num="", money=0.0, pay_money=0.0, invoice_type=INVOICE_TYPE_NORMAL,
                 invoice_status=AGENT_INVOICE_STATUS_NORMAL, creator=None, create_time=None,
                 add_time=None, pay_time=None, bool_pay=False, bool_invoice=True):
        self.client_order = client_order
        self.agent = agent
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

    @property
    def invoice_type_cn(self):
        return INVOICE_TYPE_CN[self.invoice_type]

    @classmethod
    def get_agent_invoices_status(cls, status):
        return cls.query.filter_by(invoice_status=status)

    def get_invoice_pas_by_status(self, status):
        return [k for k in AgentInvoicePay.query.filter_by(agent_invoice=self) if k.pay_status == status]

    @property
    def get_pay_money(self):
        return sum([k.money for k in AgentInvoicePay.query.filter_by(agent_invoice=self)
                    if k.pay_status == AGENT_INVOICE_STATUS_PASS])

    @property
    def get_unpay_money(self):
        return self.money - self.get_pay_money

    @property
    def get_apply_pay_money(self):
        return sum([k.money for k in AgentInvoicePay.query.filter_by(agent_invoice=self)
                    if k.pay_status in [AGENT_INVOICE_STATUS_APPLY, AGENT_INVOICE_STATUS_AGREE]])

    @property
    def pay_invoice_money(self):
        return sum([k.money for k in AgentInvoicePay.query.filter_by(agent_invoice=self)])


# inad付款给代理/直客(甲方的全称)的金额
class AgentInvoicePay(db.Model, BaseModelMixin):
    __tablename__ = 'bra_agent_invoice_pay'
    id = db.Column(db.Integer, primary_key=True)
    agent_invoice_id = db.Column(
        db.Integer, db.ForeignKey('bra_agent_invoice.id'))  # 客户发票
    agent_invoice = db.relationship(
        'AgentInvoice', backref=db.backref('agent_invoice_pays', lazy='dynamic'))
    detail = db.Column(db.String(200))  # 留言
    pay_status = db.Column(db.Integer)  # 付款状态
    bank = db.Column(db.String(100))
    bank_num = db.Column(db.String(100))
    company = db.Column(db.String(100))
    money = db.Column(db.Float)  # 打款金额
    pay_time = db.Column(db.DateTime)  # 打款时间
    create_time = db.Column(db.DateTime)  # 添加时间

    def __init__(self, agent_invoice, detail="", pay_status=AGENT_INVOICE_STATUS_NORMAL,
                 money=0.0, pay_time=None, bank="", bank_num="", company=""):
        self.agent_invoice = agent_invoice
        self.detail = detail
        self.pay_status = pay_status
        self.money = money
        self.bank = bank
        self.bank_num = bank_num
        self.company = company
        self.create_time = datetime.date.today()
        self.pay_time = pay_time or datetime.date.today()

    @property
    def pay_time_cn(self):
        return self.pay_time.strftime("%Y-%m-%d")

    @classmethod
    def get_agent_invoices_pay_status(cls, status):
        return cls.query.filter_by(pay_status=status)

    @property
    def client_order(self):
        return self.agent_invoice.client_order


class OutsourceInvoice(db.Model, BaseModelMixin):
    __tablename__ = 'bra_outsource_invoice'
    id = db.Column(db.Integer, primary_key=True)
    client_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_order.id'))  # 客户合同
    client_order = db.relationship(
        'ClientOrder', backref=db.backref('client_order_outsource_invoice', lazy='dynamic'))
    company = db.Column(db.String(100))  # 公司名称
    money = db.Column(db.Float)  # 发票金额
    ex_money = db.Column(db.Float)  # 拆分金额
    invoice_num = db.Column(db.String(100))  # 发票号
    add_time = db.Column(db.DateTime)  # 开具发票时间
    create_time = db.Column(db.DateTime)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('outsource_invoice_creator', lazy='dynamic'))

    def __init__(self, client_order, company, money, ex_money, invoice_num, creator, add_time=None, create_time=None):
        self.client_order = client_order
        self.company = company
        self.money = money
        self.ex_money = ex_money
        self.invoice_num = invoice_num
        self.creator = creator
        self.add_time = add_time or datetime.date.today()
        self.create_time = create_time or datetime.date.today()

    @property
    def add_time_cn(self):
        return self.add_time.strftime('%Y-%m-%d')


class DoubanOutsourceInvoice(db.Model, BaseModelMixin):
    __tablename__ = 'bra_douban_outsource_invoice'
    id = db.Column(db.Integer, primary_key=True)
    douban_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_douban_order.id'))  # 客户合同
    douban_order = db.relationship(
        'DoubanOrder', backref=db.backref('douban_order_outsource_invoice', lazy='dynamic'))
    company = db.Column(db.String(100))  # 公司名称
    money = db.Column(db.Float)  # 发票金额
    ex_money = db.Column(db.Float)  # 拆分金额
    invoice_num = db.Column(db.String(100))  # 发票号
    add_time = db.Column(db.DateTime)  # 开具发票时间
    create_time = db.Column(db.DateTime)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('douban_order_outsource_invoice_creator', lazy='dynamic'))

    def __init__(self, douban_order, company, money, ex_money, invoice_num, creator, add_time=None, create_time=None):
        self.douban_order = douban_order
        self.company = company
        self.money = money
        self.ex_money = ex_money
        self.invoice_num = invoice_num
        self.creator = creator
        self.add_time = add_time or datetime.date.today()
        self.create_time = create_time or datetime.date.today()

    @property
    def add_time_cn(self):
        return self.add_time.strftime('%Y-%m-%d')


class ClientMediumInvoice(db.Model, BaseModelMixin):
    __tablename__ = 'bra_client_medium_invoice'
    id = db.Column(db.Integer, primary_key=True)
    client_medium_order_id = db.Column(
        db.Integer, db.ForeignKey('bra_client_medium_order.id'))  # 客户合同
    client_medium_order = db.relationship(
        'ClientMediumOrder', backref=db.backref('client_medium_invoices', lazy='dynamic'))
    company = db.Column(db.String(100))  # 公司名称
    tax_id = db.Column(db.String(100))  # 税号
    address = db.Column(db.String(120))  # 公司地址
    phone = db.Column(db.String(80))  # 联系电话
    bank_id = db.Column(db.String(50))  # 银行账号
    bank = db.Column(db.String(100))  # 开户行
    detail = db.Column(db.String(200))  # 发票内容
    money = db.Column(db.Float)  # 发票金额
    invoice_type = db.Column(db.Integer)  # 发票类型
    invoice_status = db.Column(db.Integer)  # 发表状态
    invoice_num = db.Column(db.String(200), default='')  # 发票号
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(
        'User', backref=db.backref('created_client_medium_invoice', lazy='dynamic'))
    back_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)
    __mapper_args__ = {'order_by': create_time.desc()}

    def __init__(self, client_medium_order, company="", tax_id="",
                 address="", phone="", bank_id="", bank="",
                 detail="", invoice_num="", money=0.0, invoice_type=INVOICE_TYPE_NORMAL,
                 invoice_status=INVOICE_STATUS_NORMAL, creator=None, create_time=None, back_time=None):
        self.client_medium_order = client_medium_order
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
        return self.create_time.strftime("%Y-%m-%d")

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
