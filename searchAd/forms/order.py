#-*- coding: UTF-8 -*-
from wtforms import (TextField, validators, SelectField, SelectMultipleField,
                     IntegerField, TextAreaField, DateField,FloatField)
from libs.wtf import Form

from ..models.client import searchAdClient, searchAdAgent
from ..models.medium import searchAdMedium
from ..models.order import DISCOUNT_SALE
from ..models.client_order import CONTRACT_TYPE_CN, RESOURCE_TYPE_CN, SALE_TYPE_CN, AD_PROMOTION_TYPE_CN
from ..models.framework_order import searchAdFrameworkOrder

from models.user import User
from models.user import (TEAM_TYPE_DESIGNER, TEAM_TYPE_PLANNER,
                         TEAM_TYPE_OPERATER, TEAM_TYPE_OPERATER_LEADER)


class ClientOrderForm(Form):
    framework_order_id = SelectField(u'所属框架合同', coerce=int)
    agent = SelectField(u'代理/直客(甲方全称)', coerce=int)
    client = SelectField(u'客户名称', coerce=int)
    campaign = TextField(u'Campaign名称', [validators.Required(u"请输入活动名字.")])
    money = FloatField(u'合同金额(元)', default=0)
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    reminde_date = DateField(u'最迟回款日期')
    direct_sales = SelectMultipleField(u'销售', coerce=int)
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)
    resource_type = SelectField(u'推广类型', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    sale_type = SelectField(u'代理/直客', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ClientOrderForm, self).__init__(*args, **kwargs)
        self.framework_order_id.choices = [(0, u'无框架')] + [(f.id, f.name) for f in searchAdFrameworkOrder.all()]
        self.agent.choices = [(m.id, m.name) for m in searchAdAgent.all()]
        self.client.choices = [(c.id, c.name) for c in searchAdClient.all()]
        self.direct_sales.choices = [(m.id, m.name) for m in User.searchAd_sales()]
        self.agent_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.contract_type.choices = CONTRACT_TYPE_CN.items()
        self.resource_type.choices = AD_PROMOTION_TYPE_CN.items()
        self.sale_type.choices = SALE_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if any(self.direct_sales.data + self.agent_sales.data):
                return True
            else:
                self.direct_sales.errors.append(u"销售不能全为空")
                return False
        return False


class MediumOrderForm(Form):
    medium = SelectField(u'媒体/供应商', coerce=int, description=u"提交后不可修改")
    channel_type = SelectField(u'最终推广渠道', coerce=int)
    sale_money = FloatField(u'客户下单金额(元)', default=0, description=u"无利润未分成")
    medium_money2 = FloatField(u'给供应商下单金额(元)', default=0, description=u"已利润未分成")
    medium_money = FloatField(u'分成金额(元)', default=0, description=u"已利润已分成, 实际给媒体分成金额")  # hidden
    sale_CPM = IntegerField(u'预估量(CPM)', default=0)
    medium_CPM = IntegerField(u'实际量(CPM)', default=0, description=u"结项后由执行填写")
    medium_start = DateField(u'执行开始')
    medium_end = DateField(u'执行结束')
    operaters = SelectMultipleField(u'执行人员', coerce=int)
    designers = SelectMultipleField(u'设计人员', coerce=int)
    planers = SelectMultipleField(u'策划人员', coerce=int)
    discount = SelectField(u'折扣', coerce=int)

    def __init__(self, *args, **kwargs):
        super(MediumOrderForm, self).__init__(*args, **kwargs)
        self.medium.choices = [(m.id, m.name) for m in searchAdMedium.all()]
        self.channel_type.choices = [(0, u'其他'), (1, u'360'), (2, u'百度'), (3, u'小米')]
        operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
        self.operaters.choices = [(m.id, m.name) for m in operaters]
        self.designers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_DESIGNER)]
        self.planers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_PLANNER)]
        self.discount.choices = DISCOUNT_SALE.items()


class FrameworkOrderForm(Form):
    agent = SelectField(u'代理/直客', coerce=int)
    client_id = SelectField(u'客户', coerce=int)
    description = TextAreaField(u'备注', description=u"请填写返点政策/配送政策等信息")
    money = FloatField(u'合同金额(元)', default=0)
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    reminde_date = DateField(u'最迟回款日期')
    sales = SelectMultipleField(u'销售', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    rebate = FloatField(u'返点信息', default=0, description="%")

    def __init__(self, *args, **kwargs):
        super(FrameworkOrderForm, self).__init__(*args, **kwargs)
        self.agent.choices = [(a.id, a.name) for a in searchAdAgent.all()]
        self.client_id.choices = [(0, u'无客户')]
        self.client_id.choices += [(a.id, a.name) for a in searchAdClient.all()]
        self.sales.choices = [(m.id, m.name) for m in User.searchAd_sales()]
        self.contract_type.choices = CONTRACT_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if any(self.sales.data):
                return True
            else:
                self.sales.errors.append(u"销售不能为空")
                return False
        return False


class ClientOrderBackMoneyForm(Form):
    client_order = SelectField(u'客户', coerce=int)
    money = FloatField(u'合同金额(元)', default=0)
    back_time = DateField(u'回款日期')

    def __init__(self, *args, **kwargs):
        super(ClientOrderBackMoneyForm, self).__init__(*args, **kwargs)


class RebateOrderBackMoneyForm(Form):
    rebate_order = SelectField(u'客户', coerce=int)
    money = FloatField(u'合同金额(元)', default=0)
    back_time = DateField(u'回款日期')

    def __init__(self, *args, **kwargs):
        super(RebateOrderBackMoneyForm, self).__init__(*args, **kwargs)


class RebateOrderForm(Form):
    agent = SelectField(u'代理/直客(甲方全称)', coerce=int)
    client = SelectField(u'客户名称', coerce=int)
    campaign = TextField(u'Campaign名称', [validators.Required(u"请输入活动名字.")])
    money = FloatField(u'合同金额(元)', default=0)
    sale_CPM = IntegerField(u'预估量(CPM)', default=0)
    medium_CPM = IntegerField(u'实际量(CPM)', default=0, description=u"结项后由执行填写")
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    reminde_date = DateField(u'最迟回款日期')
    sales = SelectMultipleField(u'销售', coerce=int)
    operaters = SelectMultipleField(u'执行人员', coerce=int)
    designers = SelectMultipleField(u'设计人员', coerce=int)
    planers = SelectMultipleField(u'策划人员', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    resource_type = SelectField(u'售卖类型', coerce=int)
    sale_type = SelectField(u'代理/直客', coerce=int)

    def __init__(self, *args, **kwargs):
        super(RebateOrderForm, self).__init__(*args, **kwargs)
        self.agent.choices = [(m.id, m.name) for m in searchAdAgent.all()]
        self.client.choices = [(c.id, c.name) for c in searchAdClient.all()]
        self.sales.choices = [(m.id, m.name) for m in User.searchAd_sales()]
        operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
        self.operaters.choices = [(m.id, m.name) for m in operaters]
        self.designers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_DESIGNER)]
        self.planers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_PLANNER)]
        self.contract_type.choices = CONTRACT_TYPE_CN.items()
        self.resource_type.choices = RESOURCE_TYPE_CN.items()
        self.sale_type.choices = SALE_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if any(self.sales.data):
                return True
            else:
                self.sales.errors.append(u"销售不能全为空")
                return False
        return False
