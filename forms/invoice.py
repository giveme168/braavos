#-*- coding: UTF-8 -*-
from wtforms import TextField, IntegerField, FloatField, TextAreaField, SelectField, validators

from libs.wtf import Form
from models.invoice import INVOICE_TYPE_CN


class InvoiceForm(Form):
    client_order = SelectField(u'客户', coerce=int, default=0)
    company = TextField(u'公司名称', [validators.Required(u"请输入公司名称.")])
    tax_id = TextField(u'税号', [validators.Required(u"请输入税号.")])
    address = TextField(u'公司地址', [validators.Required(u"请输入公司地址.")])
    phone = TextField(u'联系电话', [validators.Required(u"请输入联系电话.")])
    bank_id = TextField(u'银行账号', [validators.Required(u"请输入银行账号.")])
    bank = TextField(u'开户行', [validators.Required(u"请输入开户行.")])
    detail = TextField(u'发票内容', [validators.Required(u"发票内容.")])
    money = FloatField(u'发票金额(元)', [validators.Required(u"请输入发票金额.")], default=0.0)
    invoice_type = SelectField(u'发票类型', coerce=int, default=0)
    
    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.invoice_type.choices = INVOICE_TYPE_CN.items()