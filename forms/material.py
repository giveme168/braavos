#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, validators, SelectField

from models.consts import STATUS_CN


class RawMaterialForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    status = SelectField(u'状态', coerce=int, default=1)
    code = TextAreaField(u'代码')

    def __init__(self, *args, **kwargs):
        super(RawMaterialForm, self).__init__(*args, **kwargs)
        self.status.choices = STATUS_CN.items()


class ImageMaterialForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    status = SelectField(u'状态', coerce=int, default=1)
    image_link = TextField(u'图片链接', [validators.Required(u"请输入名字."), validators.URL(u"请输入正确的链接")])
    click_link = TextField(u'跳转链接(点击检测)', [validators.Required(u"请输入名字."), validators.URL(u"请输入正确的链接")])
    monitor_link = TextField(u'展示检测')

    def __init__(self, *args, **kwargs):
        super(ImageMaterialForm, self).__init__(*args, **kwargs)
        self.status.choices = STATUS_CN.items()
