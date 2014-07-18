#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, validators, SelectField

from models.user import Team


class NewMediumForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    owner = SelectField(u'管理组', coerce=int)

    def __init__(self, *args, **kwargs):
        super(NewMediumForm, self).__init__(*args, **kwargs)
        self.owner.choices = [(t.id, t.name) for t in Team.all() if t.is_medium()]

    def validate(self):
        return Form.validate(self)
