#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SelectField, RadioField

from models.item import SALE_TYPE_CN


class ItemForm(Form):
    order = TextField(u'所属订单')
    sale_type = SelectField(u'售卖类型', coerce=int)
    special_sale = RadioField(u'定向/特殊投放', coerce=int, default=0)
    description = TextAreaField(u'描述')

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        self.sale_type.choices = SALE_TYPE_CN.items()
        self.special_sale.choices = [(0, u"否"), (1, u"是")]

    def validate(self):
        if Form.validate(self):
            return True
        return False


class ItemDetailForm(ItemForm):

    creator = TextField(u'创建者')

    def __init__(self, *args, **kwargs):
        super(ItemDetailForm, self).__init__(*args, **kwargs)
