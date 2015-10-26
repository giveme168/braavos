#-*- coding: UTF-8 -*-
from wtforms import TextField, IntegerField, FloatField, TextAreaField, SelectField, validators, DateField

from libs.wtf import Form
from models.planning import Bref, BUDGET_TYPE_CN, IS_TEMP_CN, AGENT_YTPE_CN, USE_TYPE_CN, LEVEL_TYPE_CN


class BrefForm(Form):
    title = TextField(
        u'名称', [validators.Required(u"请输入名称.")], description=u'必填')
    agent = TextField(u'代理公司/直客', [validators.Required(u"请输入代理公司/直客.")], description=u'必填')
    brand = TextField(u'品牌', [validators.Required(u"请输入品牌.")], description=u'必填')
    product = TextField(u'产品', [validators.Required(u"请输入产品.")], description=u'必填')
    target = TextField(u'目标受众', [validators.Required(u"请输入目标受众.")], description=u'必填')
    background = TextField(u'背景', [validators.Required(u"请输入背景.")], description=u'必填')
    push_target = TextField(u'推广目的', [validators.Required(u"请输入推广目的.")], description=u'必填')
    push_theme = TextField(u'推广主题', [validators.Required(u"请输入推广主题.")], description=u'必填')
    push_time = TextField(u'推广周期', [validators.Required(u"请输入推广周期.")], description=u'必填')
    budget = SelectField(u'推广预算', coerce=int, default=1)
    is_temp = SelectField(u'有无模板', coerce=int, default=0)

    agent_type = SelectField(u'下单需求方', coerce=int, default=1)
    use_type = SelectField(u'应用场景', coerce=int, default=1)
    level = SelectField(u'项目等级', coerce=int, default=1)

    intent_medium = TextField(u'补充说明', description=u'视与客户沟通情况选填')
    suggest = TextField(u'建议', description=u'视与客户沟通情况选填')
    desc = TextAreaField(u'备注')

    def __init__(self, *args, **kwargs):
        super(BrefForm, self).__init__(*args, **kwargs)
        self.budget.choices = BUDGET_TYPE_CN.items()
        self.is_temp.choices = IS_TEMP_CN.items()
        self.agent_type.choices = AGENT_YTPE_CN.items()
        self.use_type.choices = USE_TYPE_CN.items()
        self.level.choices = LEVEL_TYPE_CN.items()