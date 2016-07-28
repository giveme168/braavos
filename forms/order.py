# -*- coding: UTF-8 -*-
from wtforms import (TextField, validators, SelectField, SelectMultipleField,
                     IntegerField, TextAreaField, DateField, FloatField)
from libs.wtf import Form
from models.client import Client, Group, Agent
from models.medium import Medium, MediumGroup
from models.order import DISCOUNT_SALE
from models.client_order import CONTRACT_TYPE_CN, RESOURCE_TYPE_CN, SALE_TYPE_CN
from models.user import User
from models.user import (TEAM_TYPE_DESIGNER, TEAM_TYPE_PLANNER,
                         TEAM_TYPE_OPERATER, TEAM_TYPE_OPERATER_LEADER)


class ClientOrderForm(Form):
    agent = SelectField(u'代理/直客(甲方全称)', coerce=int)
    client = SelectField(u'客户名称', coerce=int)
    campaign = TextField(u'Campaign名称', [validators.Required(u"请输入活动名字.")])
    money = FloatField(u'合同金额(元)', default=0)
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    reminde_date = DateField(u'最迟回款日期')
    direct_sales = SelectMultipleField(u'直客销售', coerce=int)
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)
    assistant_sales = SelectMultipleField(u'销售助理', coerce=int)
    resource_type = SelectField(u'售卖类型', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    sale_type = SelectField(u'代理/直客', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ClientOrderForm, self).__init__(*args, **kwargs)
        self.agent.choices = [(m.id, m.name) for m in Agent.all()]
        self.client.choices = [(c.id, c.name) for c in Client.all()]
        self.direct_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.agent_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.assistant_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.contract_type.choices = CONTRACT_TYPE_CN.items()
        self.resource_type.choices = RESOURCE_TYPE_CN.items()
        self.sale_type.choices = SALE_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if any(self.direct_sales.data + self.agent_sales.data):
                return True
            else:
                self.direct_sales.errors.append(u"直接销售和渠道销售不能全为空")
                return False
        return False


class MediumOrderForm(Form):
    medium = SelectField(u'投放媒体', coerce=int, description=u"提交后不可修改")
    sale_money = FloatField(u'售卖金额(元)', default=0, description=u"无利润未分成")
    medium_money2 = FloatField(u'媒体金额(元)', default=0, description=u"已利润未分成")
    medium_money = FloatField(u'分成金额(元)', default=0, description=u"已利润已分成, 实际给媒体分成金额")
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
        self.medium.choices = [(m.id, m.name) for m in Medium.all()]
        operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
        self.operaters.choices = [(m.id, m.name) for m in operaters]
        self.designers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_DESIGNER)]
        self.planers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_PLANNER)]
        self.discount.choices = DISCOUNT_SALE.items()


class AssociatedDoubanOrderForm(Form):
    medium_order = SelectField(u'关联媒体订单', coerce=int)
    campaign = TextField(u'Campaign名称', [validators.Required(u"请输入活动名字.")])
    money = FloatField(u'合同金额(元)', default=0)


class FrameworkOrderForm(Form):
    group = SelectField(u'代理集团', coerce=int)
    agents = SelectMultipleField(u'代理/直客', coerce=int)
    description = TextAreaField(u'备注', description=u"返点政策/配送政策等信息")
    money = FloatField(u'合同金额(元)', default=0)
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    reminde_date = DateField(u'最迟回款日期')
    direct_sales = SelectMultipleField(u'直客销售', coerce=int)
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)
    assistant_sales = SelectMultipleField(u'销售助理', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    inad_rebate = FloatField(u'致趣返点信息', default=0, description=u"%,请预估全年最高比例")
    douban_rebate = FloatField(u'豆瓣返点信息', default=0, description=u"%,请预估全年最高比例")

    def __init__(self, *args, **kwargs):
        super(FrameworkOrderForm, self).__init__(*args, **kwargs)
        self.agents.choices = [(a.id, a.name) for a in Agent.all()]
        self.group.choices = [(g.id, g.name) for g in Group.all()]
        self.direct_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.agent_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.assistant_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.contract_type.choices = CONTRACT_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if any(self.direct_sales.data + self.agent_sales.data):
                return True
            else:
                self.direct_sales.errors.append(u"直接销售和渠道销售不能全为空")
                return False
        return False


class MediumFrameworkOrderForm(Form):
    mediums = SelectMultipleField(u'媒体', coerce=int)
    description = TextAreaField(u'备注', description=u"返点政策/配送政策等信息")
    money = FloatField(u'合同金额(元)', default=0)
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    medium_users = SelectMultipleField(u'媒介人员', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    inad_rebate = FloatField(u'致趣返点信息', default=0, description=u"%,请预估全年最高比例")

    def __init__(self, *args, **kwargs):
        super(MediumFrameworkOrderForm, self).__init__(*args, **kwargs)
        self.mediums.choices = [(a.id, a.medium_group.name + '-' + a.name) for a in Medium.all()]
        self.medium_users.choices = [(m.id, m.name) for m in User.medias()]
        self.contract_type.choices = CONTRACT_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if any(self.medium_users.data):
                return True
            else:
                self.medium_users.errors.append(u"直接销售和渠道销售不能全为空")
                return False
        return False


class DoubanOrderForm(Form):
    agent = SelectField(u'代理/直客(甲方全称)', coerce=int)
    client = SelectField(u'客户名称', coerce=int)
    campaign = TextField(u'Campaign名称', [validators.Required(u"请输入活动名字.")])
    money = FloatField(u'合同金额(元)', default=0)
    sale_CPM = IntegerField(u'预估量(CPM)', default=0)
    medium_CPM = IntegerField(u'实际量(CPM)', default=0, description=u"结项后由执行填写")
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    reminde_date = DateField(u'最迟回款日期')
    direct_sales = SelectMultipleField(u'直客销售', coerce=int)
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)
    assistant_sales = SelectMultipleField(u'销售助理', coerce=int)
    operaters = SelectMultipleField(u'执行人员', coerce=int)
    designers = SelectMultipleField(u'设计人员', coerce=int)
    planers = SelectMultipleField(u'策划人员', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    resource_type = SelectField(u'售卖类型', coerce=int)
    sale_type = SelectField(u'代理/直客', coerce=int)

    def __init__(self, *args, **kwargs):
        super(DoubanOrderForm, self).__init__(*args, **kwargs)
        self.agent.choices = [(m.id, m.name) for m in Agent.all()]
        self.client.choices = [(c.id, c.name) for c in Client.all()]
        self.direct_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.agent_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.assistant_sales.choices = [(m.id, m.name) for m in User.sales()]
        operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
        self.operaters.choices = [(m.id, m.name) for m in operaters]
        self.designers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_DESIGNER)]
        self.planers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_PLANNER)]
        self.contract_type.choices = CONTRACT_TYPE_CN.items()
        self.resource_type.choices = RESOURCE_TYPE_CN.items()
        self.sale_type.choices = SALE_TYPE_CN.items()

    def validate(self):
        if Form.validate(self):
            if any(self.direct_sales.data + self.agent_sales.data):
                return True
            else:
                self.direct_sales.errors.append(u"直接销售和渠道销售不能全为空")
                return False
        return False


class ClientOrderBackMoneyForm(Form):
    client_order = SelectField(u'客户', coerce=int)
    money = FloatField(u'合同金额(元)', default=0)
    back_time = DateField(u'回款日期')

    def __init__(self, *args, **kwargs):
        super(DoubanOrderForm, self).__init__(*args, **kwargs)


class ClientMediumOrderForm(Form):
    agent = SelectField(u'代理/直客(甲方全称)', coerce=int)
    client = SelectField(u'客户名称', coerce=int)
    campaign = TextField(u'Campaign名称', [validators.Required(u"请输入活动名字.")])
    money = FloatField(u'合同金额(元)', default=0)
    sale_CPM = IntegerField(u'预估量(CPM)', default=0)
    medium_CPM = IntegerField(u'实际量(CPM)', default=0, description=u"结项后由执行填写")
    client_start = DateField(u'执行开始')
    client_end = DateField(u'执行结束')
    reminde_date = DateField(u'最迟回款日期')
    direct_sales = SelectMultipleField(u'直客销售', coerce=int)
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)
    assistant_sales = SelectMultipleField(u'销售助理', coerce=int)
    operaters = SelectMultipleField(u'执行人员', coerce=int)
    designers = SelectMultipleField(u'设计人员', coerce=int)
    planers = SelectMultipleField(u'策划人员', coerce=int)
    contract_type = SelectField(u'合同模板类型', coerce=int)
    resource_type = SelectField(u'售卖类型', coerce=int)
    sale_type = SelectField(u'代理/直客', coerce=int)
    medium_group = SelectField(u'媒体供应商媒体', coerce=int)
    medium = SelectField(u'投放媒体', coerce=int)
    medium_money = FloatField(u'媒体服务费(元)', default=0)

    def __init__(self, *args, **kwargs):
        super(ClientMediumOrderForm, self).__init__(*args, **kwargs)
        self.agent.choices = [(m.id, m.name) for m in Agent.all()]
        self.client.choices = [(c.id, c.name) for c in Client.all()]
        self.direct_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.agent_sales.choices = [(m.id, m.name) for m in User.sales()]
        self.assistant_sales.choices = [(m.id, m.name) for m in User.sales()]
        operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
        self.operaters.choices = [(m.id, m.name) for m in operaters]
        self.operaters.hidden = True
        self.designers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_DESIGNER)]
        self.designers.hidden = True
        self.planers.choices = [(m.id, m.name) for m in User.gets_by_team_type(TEAM_TYPE_PLANNER)]
        self.planers.hidden = True
        self.sale_CPM.hidden = True
        self.medium_CPM.hidden = True
        self.contract_type.choices = CONTRACT_TYPE_CN.items()
        self.resource_type.choices = RESOURCE_TYPE_CN.items()
        self.sale_type.choices = SALE_TYPE_CN.items()
        self.medium_group.choices = [(m.id, m.name) for m in MediumGroup.all()]
        self.medium.choices = [(m.id, m.name) for m in Medium.all()]

    def validate(self):
        if Form.validate(self):
            if any(self.direct_sales.data + self.agent_sales.data):
                return True
            else:
                self.direct_sales.errors.append(u"直接销售和渠道销售不能全为空")
                return False
        return False
