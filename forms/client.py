#-*- coding: UTF-8 -*-
from wtforms import TextField, validators, SelectField

from libs.wtf import Form
from models.client import CLIENT_INDUSTRY_CN


class NewClientForm(Form):
    name = TextField(u'客户名字',
                     [validators.Required(u"请输入名字.")],
                     description=u"新建之前请确认是否已存在，不要重复创建")
    industry = SelectField(u'行业', coerce=int)

    def __init__(self, *args, **kwargs):
        super(NewClientForm, self).__init__(*args, **kwargs)
        self.industry.choices = CLIENT_INDUSTRY_CN.items()


class NewAgentForm(Form):
    name = TextField(u'甲方全称',
                     [validators.Required(u"请输入名字.")],
                     description=u"新建之前请确认是否已存在，不要重复创建")
    framework = TextField(u'今年框架号')
