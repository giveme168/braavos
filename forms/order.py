#-*- coding: UTF-8 -*-
from wtforms import TextField, validators, SelectField, SelectMultipleField, IntegerField

from libs.wtf import Form
from models.client import Client, Agent
from models.medium import Medium
from models.order import DISCOUNT_SALE, DISCOUNT_SELECT
from models.user import User
from models.user import (TEAM_TYPE_DESIGNER, TEAM_TYPE_PLANNER,
                         TEAM_TYPE_OPERATER, TEAM_TYPE_AGENT_SELLER,
                         TEAM_TYPE_DIRECT_SELLER)


class ClientOrderForm(Form):
    agent = SelectField(u'甲方全称', coerce=int)
    client = SelectField(u'客户名称', coerce=int)
    campaign = TextField(u'Campaign名称', [validators.Required(u"请输入活动名字.")])
    medium = SelectField(u'投放媒体', coerce=int, description=u"提交后不可修改")
    money = IntegerField(u'合同金额(人民币元)', default=0)
    direct_sales = SelectMultipleField(u'直客销售', coerce=int)
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ClientOrderForm, self).__init__(*args, **kwargs)
        self.agent.choices = [(m.id, m.name) for m in Agent.all()]
        self.client.choices = [(c.id, c.name) for c in Client.all()]
        self.medium.choices = [(m.id, m.name) for m in Medium.all()]
        self.direct_sales.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_DIRECT_SELLER)]
        self.agent_sales.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_AGENT_SELLER)]

    def validate(self):
        if Form.validate(self):
            if any(self.direct_sales.data + self.agent_sales.data):
                return True
            else:
                self.direct_sales.errors.append(u"直接销售和渠道销售不能全为空")
                return False
        return False


class MediumOrderForm(Form):
    #medium_money = IntegerField(u'合同金额(人民币元)', default=0)
    operaters = SelectMultipleField(u'执行', coerce=int)
    designers = SelectMultipleField(u'设计', coerce=int)
    planers = SelectMultipleField(u'策划', coerce=int)
    discount = SelectField(u'折扣', coerce=int)

    def __init__(self, *args, **kwargs):
        super(MediumOrderForm, self).__init__(*args, **kwargs)
        self.operaters.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_OPERATER)]
        self.designers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_DESIGNER)]
        self.planers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_PLANNER)]
        self.discount.choices = DISCOUNT_SALE.items()

    def validate(self):
        if Form.validate(self):
            if self.discount.data != DISCOUNT_SELECT:
                return True
            else:
                self.discount.errors.append(u"请选择折扣")
                return False
        return False
