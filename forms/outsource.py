#-*- coding: UTF-8 -*-
from wtforms import TextField, TextAreaField, SelectField, validators

from libs.wtf import Form
from models.outsource import TARGET_TYPE_CN


class OutSourceTargetForm(Form):
    name = TextField(u'名称', [validators.Required(u"请输入名字.")])
    type = SelectField(u'类型', coerce=int, default=1)
    bank = TextField(u'开户行')
    card = TextField(u'卡号')
    alipay = TextField(u'支付宝')
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
