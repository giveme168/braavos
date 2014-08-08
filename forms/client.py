#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, validators, SelectField

from models.client import CLIENT_INDUSTRY_CN


class NewClientForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    industry = SelectField(u'行业', coerce=int)

    def __init__(self, *args, **kwargs):
        super(NewClientForm, self).__init__(*args, **kwargs)
        self.industry.choices = CLIENT_INDUSTRY_CN.items()


class NewAgentForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])

    def __init__(self, *args, **kwargs):
        super(NewAgentForm, self).__init__(*args, **kwargs)
