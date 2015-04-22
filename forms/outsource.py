#-*- coding: UTF-8 -*-
from wtforms import TextField, IntegerField, TextAreaField, SelectField, validators

from libs.wtf import Form
from models.outsource import OutSourceTarget, TARGET_TYPE_CN, OUTSOURCE_TYPE_CN, OUTSOURCE_SUBTYPE_CN, OUTSOURCE_INVOICE_CN


class OutSourceTargetForm(Form):
    name = TextField(u'名称', [validators.Required(u"请输入名字.")])
    type = SelectField(u'类型', coerce=int, default=1)
    bank = TextField(u'开户行')
    card = TextField(u'银行卡号')
    alipay = TextField(u'支付宝', description=u"支付宝和银行支付两者选一就可以")
    contract = TextAreaField(u'联系方式')
    remark = TextAreaField(u'备注')

    def __init__(self, *args, **kwargs):
        super(OutSourceTargetForm, self).__init__(*args, **kwargs)
        self.type.choices = TARGET_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if self.alipay.data:
                return True
            else:
                if not self.bank.data:
                    self.bank.errors.append(u"开户行和支付宝不能全为空")
                    return False
                elif not self.card.data:
                    self.card.errors.append(u"需提供开户行的银行卡号")
                    return False
                else:
                    return True
        return False


class OutsourceForm(Form):
    medium_order = SelectField(u'投放媒体', coerce=int, description=u"保存后不可修改")
    target = SelectField(u'收款方', coerce=int)
    num = IntegerField(u'金额', default=0)
    pay_num = IntegerField(u'打款金额',default=0)
    type = SelectField(u'外包类别', coerce=int)
    subtype = SelectField(u'Flash功能分类', coerce=int, default=1)
    remark = TextAreaField(u'备注')

    def __init__(self, *args, **kwargs):
        super(OutsourceForm, self).__init__(*args, **kwargs)
        self.target.choices = [(ost.id, ost.name) for ost in OutSourceTarget.all()]
        self.type.choices = OUTSOURCE_TYPE_CN.items()
        self.subtype.choices = OUTSOURCE_SUBTYPE_CN.items()


class DoubanOutsourceForm(Form):
    douban_order = SelectField(u'豆瓣订单', coerce=int, description=u"不可修改")
    target = SelectField(u'收款方', coerce=int)
    num = IntegerField(u'金额', default=0)
    pay_num = IntegerField(u'打款金额',default=0)
    type = SelectField(u'外包类别', coerce=int)
    subtype = SelectField(u'Flash功能分类', coerce=int, default=1)
    remark = TextAreaField(u'备注')

    def __init__(self, *args, **kwargs):
        super(DoubanOutsourceForm, self).__init__(*args, **kwargs)
        self.target.choices = [(ost.id, ost.name) for ost in OutSourceTarget.all()]
        self.type.choices = OUTSOURCE_TYPE_CN.items()
        self.subtype.choices = OUTSOURCE_SUBTYPE_CN.items()


class MergerOutSourceForm(Form):
    num = IntegerField(u'填报金额', default=0)
    pay_num = IntegerField(u'实际打款金额', default=0)
    invoice = SelectField(u'是否有发票', default=False)
    remark = TextAreaField(u'发票信息')

    def __init__(self, *args, **kwargs):
        super(MergerOutSourceForm, self).__init__(*args, **kwargs)
        self.invoice.choices = OUTSOURCE_INVOICE_CN.items()
