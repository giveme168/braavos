#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import IntegerField, TextField, validators, SelectField, TextAreaField, SelectMultipleField

from models.user import Team
from models.medium import (AdSize, AdPosition, AdUnit, Medium,
                           STATUS_CN, TARGET_CN, POSITION_LEVEL_CN, AD_TYPE_CN,
                           AD_TYPE_NORMAL, AD_TYPE_CPD)


class NewMediumForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    owner = SelectField(u'管理组', coerce=int)

    def __init__(self, *args, **kwargs):
        super(NewMediumForm, self).__init__(*args, **kwargs)
        self.owner.choices = [(t.id, t.name) for t in Team.all() if t.is_medium()]


class SizeForm(Form):
    width = IntegerField(u'Width', [validators.Required(u"请输入宽度.")])
    height = IntegerField(u'Height', [validators.Required(u"请输入高度.")])


class UnitForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    description = TextAreaField(u'描述', [validators.Required(u"请输入描述.")])
    size = SelectField(u'大小', coerce=int)
    margin = TextField(u'外边距', [validators.Required(u"请输入外边距.")], default="0px 0px 0px 0px")
    target = SelectField(u'target', coerce=int)
    status = SelectField(u'状态', coerce=int, default=1)
    positions = SelectMultipleField(u'属于以下展示位置', coerce=int)
    medium = SelectField(u'所属媒体', coerce=int)
    estimate_num = IntegerField(u'预估量', [validators.Required(u"请输入预估量.")])

    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        self.target.choices = TARGET_CN.items()
        self.status.choices = STATUS_CN.items()
        self.size.choices = [(x.id, x.name) for x in AdSize.all()]
        self.positions.choices = [(x.id, x.display_name) for x in AdPosition.all()]
        self.medium.choices = [(x.id, x.name) for x in Medium.all()]


class PositionForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    description = TextAreaField(u'描述', [validators.Required(u"请输入描述.")])
    size = SelectField(u'大小', coerce=int)
    status = SelectField(u'状态', coerce=int, default=1)
    units = SelectMultipleField(u'包含以下广告单元', coerce=int)
    medium = SelectField(u'所属媒体', coerce=int)
    level = SelectField(u'资源类别', coerce=int)
    ad_type = SelectField(u'投放类型', coerce=int)
    cpd_num = IntegerField(u'CPD量(CPD有效)', default=0)
    estimate_num = IntegerField(u'预估量(自动计算)', default=0)
    max_order_num = IntegerField(u'最大预订(CPM有效)', default=0)
    price = IntegerField(u'单价', default=0)

    def __init__(self, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)
        self.status.choices = STATUS_CN.items()
        self.size.choices = [(x.id, x.name) for x in AdSize.all()]
        self.units.choices = [(x.id, x.display_name) for x in AdUnit.all()]
        self.medium.choices = [(x.id, x.name) for x in Medium.all()]
        self.level.choices = POSITION_LEVEL_CN.items()
        self.ad_type.choices = AD_TYPE_CN.items()
        self.estimate_num.readonly = True

    def validate(self):
        if Form.validate(self):
            if self.ad_type.data is AD_TYPE_NORMAL:
                if self.max_order_num.data > self.estimate_num.data:
                    self.max_order_num.errors.append(u"最大预订不能大于预估量")
                    return False
            elif self.ad_type.data is AD_TYPE_CPD:
                if self.cpd_num.data > self.estimate_num.data:
                    self.cpd_num.errors.append(u"CPD量不能大于预估量")
                    return False
            return True
        else:
            return False
