#-*- coding: UTF-8 -*-
from wtforms import TextField, IntegerField, FloatField, TextAreaField, SelectField, validators, DateField

from libs.wtf import Form
from models.invoice import INVOICE_TYPE_CN,MEDIUM_INVOICE_BOOL_PAY_CN,MEDIUM_INVOICE_BOOL_INVOICE_CN, \
    AGENT_INVOICE_BOOL_PAY_CN, AGENT_INVOICE_BOOL_INVOICE_CN


class InvoiceForm(Form):
    client_order = SelectField(u'客户', coerce=int, default=0)
    company = TextField(u'公司名称', [validators.Required(u"请输入公司名称.")])
    tax_id = TextField(u'税号', [validators.Required(u"请输入税号.")])
    address = TextField(u'公司地址', [validators.Required(u"请输入公司地址.")])
    phone = TextField(u'联系电话', [validators.Required(u"请输入联系电话.")])
    bank_id = TextField(u'银行账号', [validators.Required(u"请输入银行账号.")])
    bank = TextField(u'开户行', [validators.Required(u"请输入开户行.")])
    detail = TextField(u'发票内容', [validators.Required(u"请输入发票内容.")])
    money = FloatField(
        u'发票金额(元)', [validators.Required(u"请输入发票金额.")], default=0.0)
    invoice_type = SelectField(u'发票类型', coerce=int, default=0)
    invoice_num = TextField(u'发票号', default='')
    back_time = DateField(u'回款时间')

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.invoice_type.choices = INVOICE_TYPE_CN.items()

class MediumRebateInvoiceForm(Form):
    client_order = SelectField(u'客户', coerce=int, default=0)
    medium = SelectField(u'媒体', coerce=int, default=0)
    company = TextField(u'公司名称', [validators.Required(u"请输入公司名称.")])
    tax_id = TextField(u'税号', [validators.Required(u"请输入税号.")])
    address = TextField(u'公司地址', [validators.Required(u"请输入公司地址.")])
    phone = TextField(u'联系电话', [validators.Required(u"请输入联系电话.")])
    bank_id = TextField(u'银行账号', [validators.Required(u"请输入银行账号.")])
    bank = TextField(u'开户行', [validators.Required(u"请输入开户行.")])
    detail = TextField(u'发票内容', [validators.Required(u"请输入发票内容.")])
    money = FloatField(
        u'发票金额(元)', [validators.Required(u"请输入发票金额.")], default=0.0)
    invoice_type = SelectField(u'发票类型', coerce=int, default=0)
    invoice_num = TextField(u'发票号', default='')
    back_time = DateField(u'回款时间')

    def __init__(self, *args, **kwargs):
        super(MediumRebateInvoiceForm, self).__init__(*args, **kwargs)
        self.invoice_type.choices = INVOICE_TYPE_CN.items()


class MediumInvoiceForm(Form):
    client_order = SelectField(u'客户', coerce=int, default=0)
    medium = SelectField(u'媒体',coerce=int, default=0)
    company = TextField(u'公司名称', [validators.Required(u"请输入公司名称.")])
    tax_id = TextField(u'税号', [validators.Required(u"请输入税号.")])
    address = TextField(u'公司地址', [validators.Required(u"请输入公司地址.")])
    phone = TextField(u'联系电话', [validators.Required(u"请输入联系电话.")])
    bank_id = TextField(u'银行账号', [validators.Required(u"请输入银行账号.")])
    bank = TextField(u'开户行', [validators.Required(u"请输入开户行.")])
    detail = TextField(u'发票内容', [validators.Required(u"请输入发票内容.")])
    money = FloatField(
        u'发票金额(元)', [validators.Required(u"请输入发票金额.")], default=0.0)
    invoice_type = SelectField(u'发票类型', coerce=int, default=0)
    invoice_num = TextField(u'发票号', default='')

    add_time = DateField(u'开具发票时间')  
    pay_time = DateField(u'打款时间')  
    bool_pay = SelectField(u'是否打款',default=False)  # 是否已打款
    bool_invoice = SelectField(u'是否开发票',default=True)   # 是否开具发票

    def __init__(self, *args, **kwargs):
        super(MediumInvoiceForm, self).__init__(*args, **kwargs)
        self.invoice_type.choices = INVOICE_TYPE_CN.items()
        self.bool_pay.choices = MEDIUM_INVOICE_BOOL_PAY_CN.items()
        self.bool_invoice.choices = MEDIUM_INVOICE_BOOL_INVOICE_CN.items()


class AgentInvoiceForm(Form):
    client_order = SelectField(u'客户', coerce=int, default=0)
    agent = SelectField(u'代理\直客(甲方全称)',coerce=int, default=0)
    company = TextField(u'公司名称', [validators.Required(u"请输入公司名称.")])
    tax_id = TextField(u'税号', [validators.Required(u"请输入税号.")])
    address = TextField(u'公司地址', [validators.Required(u"请输入公司地址.")])
    phone = TextField(u'联系电话', [validators.Required(u"请输入联系电话.")])
    bank_id = TextField(u'银行账号', [validators.Required(u"请输入银行账号.")])
    bank = TextField(u'开户行', [validators.Required(u"请输入开户行.")])
    detail = TextField(u'发票内容', [validators.Required(u"请输入发票内容.")])
    money = FloatField(
        u'发票金额(元)', [validators.Required(u"请输入发票金额.")], default=0.0)
    invoice_type = SelectField(u'发票类型', coerce=int, default=0)
    invoice_num = TextField(u'发票号', default='')

    add_time = DateField(u'开具发票时间')  
    pay_time = DateField(u'打款时间')  
    bool_pay = SelectField(u'是否打款',default=False)  # 是否已打款
    bool_invoice = SelectField(u'是否开发票',default=True)   # 是否开具发票

    def __init__(self, *args, **kwargs):
        super(AgentInvoiceForm, self).__init__(*args, **kwargs)
        self.invoice_type.choices = INVOICE_TYPE_CN.items()
        self.bool_pay.choices = AGENT_INVOICE_BOOL_PAY_CN.items()
        self.bool_invoice.choices = AGENT_INVOICE_BOOL_INVOICE_CN.items()
