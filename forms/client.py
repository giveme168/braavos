#-*- coding: UTF-8 -*-
from wtforms import TextField, validators, SelectField

from libs.wtf import Form
from models.client import Group, CLIENT_INDUSTRY_CN


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
    group = SelectField(u'所属集团', coerce=int)

    def __init__(self, *args, **kwargs):
        super(NewAgentForm, self).__init__(*args, **kwargs)
        self.group.choices = [(g.id, g.name) for g in Group.all()]


class NewGroupForm(Form):
    name = TextField(u'集团名称',
                     [validators.Required(u"请输入名字.")],
                     description=u"新建之前请确认是否已存在，不要重复创建")
