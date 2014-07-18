#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, validators, SelectField, SelectMultipleField, IntegerField

from models.client import Client, Agent
from models.medium import Medium
from models.order import ORDER_TYPE_CN
from models.user import User


class OrderForm(Form):
    client = SelectField(u'客户', coerce=int)
    campaign = TextField(u'Campaign活动名', [validators.Required(u"请输入活动名字.")])
    medium = SelectField(u'媒体', coerce=int)
    order_type = SelectField(u'订单类型', coerce=int)
    contract = TextField(u'合同号')
    money = IntegerField(u'合同金额', default=0)
    agent = SelectField(u'代理', coerce=int)
    direct_sales = SelectMultipleField(u'直接销售', coerce=int)
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)
    creator = TextField(u'创建者')

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.client.choices = [(c.id, c.name) for c in Client.all()]
        self.medium.choices = [(m.id, m.name) for m in Medium.all()]
        self.order_type.choices = ORDER_TYPE_CN.items()
        self.agent.choices = [(m.id, m.name) for m in Agent.all()]
        self.direct_sales.choices = [(m.id, m.name) for m in User.all()]
        self.agent_sales.choices = [(m.id, m.name) for m in User.all()]
        self.creator.readonly = True

    def validate(self):
        if Form.validate(self):
            if any(self.direct_sales.data + self.agent_sales.data):
                return True
            else:
                self.direct_sales.errors.append(u"直接销售和渠道销售不能全为空")
                return False
        return False
