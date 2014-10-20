# -*- coding: UTF-8 -*-
from wtforms import TextField, TextAreaField, SelectField, IntegerField

from libs.wtf import Form
from models.item import SALE_TYPE_CN, AD_TYPE_CN, ITEM_STATUS_CN, PRIORITY_CN, SPEED_CN
from models.consts import STATUS_CN


class ItemForm(Form):
    order = TextField(u'所属订单')
    sale_type = SelectField(u'售卖类型', coerce=int)
    special_sale = SelectField(u'定向/特殊投放', coerce=int, default=0)
    position = TextField(u'展示位置')
    description = TextAreaField(u'描述')

    ad_type = SelectField(u'广告类型', coerce=int, default=0)
    price = IntegerField(u'价钱')
    priority = SelectField(u'优先级', coerce=int, default=0)
    speed = SelectField(u'投放速度', coerce=int, default=0)
    item_status = SelectField(u'订单状态', coerce=int, default=0)
    status = SelectField(u'状态', coerce=int, default=0)
    creator = TextField(u'创建者')

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        self.sale_type.choices = SALE_TYPE_CN.items()
        self.special_sale.choices = [(0, u"否"), (1, u"是")]
        self.ad_type.choices = AD_TYPE_CN.items()
        self.priority.choices = PRIORITY_CN.items()
        self.speed.choices = SPEED_CN.items()
        self.item_status.choices = ITEM_STATUS_CN.items()
        self.status.choices = STATUS_CN.items()
