#-*- coding: utf-8 -*-
from wtforms import IntegerField, TextField, validators, SelectField, TextAreaField, SelectMultipleField, FloatField

from libs.wtf import Form
from models.user import Team
from models.medium import (AdSize, AdPosition, AdUnit, Medium,
                           STATUS_CN, TARGET_CN, POSITION_LEVEL_CN, AD_TYPE_CN,
                           AD_TYPE_NORMAL, AD_TYPE_CPD, LAUNCH_STRATEGY)


class NewMediumForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    abbreviation = TextField(u'公司全称', [validators.Required(u"请输入媒体全称.")])
    owner = SelectField(u'管理团队', coerce=int)
    tax_num = TextField(u'公司税号')
    address = TextField(u'公司地址')
    phone_num = TextField(u'公司电话')
    bank = TextField(u'公司开户银行')
    bank_num = TextField(u'公司银行账号')
    
    def __init__(self, *args, **kwargs):
        super(NewMediumForm, self).__init__(*args, **kwargs)
        self.owner.choices = [(t.id, t.name) for t in Team.all() if t.is_medium()]


class NewMediumProductPC(Form):
    name = TextField(u'产品名称', [validators.Required(u'请输入产品')])
    medium = SelectField(u'所属媒体', coerce=int, default=1)
    register_count = IntegerField(u'注册用户数', default=0)
    alone_count_by_day = IntegerField(u'日独用户数', default=0)
    active_count_by_day = IntegerField(u'日活用户数', default=0)
    alone_count_by_month = IntegerField(u'月独用户数', default=0)
    active_count_by_month = IntegerField(u'月活用户数', default=0)
    pv_by_day = IntegerField(u'日PV', default=0)
    pv_by_month = IntegerField(u'月PV', default=0)
    access_time = IntegerField(u'访问时长（秒）', default=0)
    ugc_count = IntegerField(u'UGC生产数量', default=0)
    cooperation_type = SelectField(u'是否是独家', coerce=int, default=1)
    divide_into = FloatField(u'分成比例（%）', default=20)
    policies = SelectField(u'折扣政策', coerce=int, default=1)
    delivery = TextAreaField(u'配送政策')
    special = TextAreaField(u'特殊情况说明')
    sex_distributed = TextAreaField(u'性别分布')
    age_distributed = TextAreaField(u'年龄分布')
    area_distributed = TextAreaField(u'区域分布')
    education_distributed = TextAreaField(u'学历分布')
    income_distributed = TextAreaField(u'收入分布')
    product_position = TextAreaField(u'产品定位')

    def __init__(self, *args, **kwargs):
        super(NewMediumProductPC, self).__init__(*args, **kwargs)
        self.medium.choices = [(k.id, k.name) for k in Medium.all()]
        self.cooperation_type.choices = [(0, u'否'), (1, u'是')]
        self.policies.choices = [(k, str(k)+u'折') for k in range(1,10)]


class NewMediumProductApp(Form):
    name = TextField(u'产品名称', [validators.Required(u'请输入产品')])
    medium = SelectField(u'所属媒体', coerce=int, default=1)
    install_count = IntegerField(u'安装量', default=0)
    activation_count = IntegerField(u'激活量', default=0)
    register_count = IntegerField(u'注册用户数', default=0)
    active_count_by_day = IntegerField(u'日活用户数', default=0)
    active_count_by_month = IntegerField(u'月活用户数', default=0)
    pv_by_day = IntegerField(u'日PV', default=0)
    pv_by_month = IntegerField(u'月PV', default=0)
    open_rate_by_day = FloatField(u'日打开率', default=0)
    access_time = IntegerField(u'访问时长（秒）', default=0)
    ugc_count = IntegerField(u'UGC生产数量', default=0)
    cooperation_type = SelectField(u'是否是独家', coerce=int, default=1)
    divide_into = FloatField(u'分成比例（%）', default=20)
    policies = SelectField(u'折扣政策', coerce=int, default=1)
    delivery = TextAreaField(u'配送政策')
    special = TextAreaField(u'特殊情况说明')
    sex_distributed = TextAreaField(u'性别分布')
    age_distributed = TextAreaField(u'年龄分布')
    area_distributed = TextAreaField(u'区域分布')
    education_distributed = TextAreaField(u'学历分布')
    income_distributed = TextAreaField(u'收入分布')
    product_position = TextAreaField(u'产品定位')

    def __init__(self, *args, **kwargs):
        super(NewMediumProductApp, self).__init__(*args, **kwargs)
        self.medium.choices = [(k.id, k.name) for k in Medium.all()]
        self.cooperation_type.choices = [(0, u'否'), (1, u'是')]
        self.policies.choices = [(k, str(k)+u'折') for k in range(1,10)]


class NewMediumProductDown(Form):
    name = TextField(u'产品名称', [validators.Required(u'请输入产品')])
    medium = SelectField(u'所属媒体', coerce=int, default=1)
    location = TextField(u'举办地点')
    subject = TextAreaField(u'主题')
    before_year_count = IntegerField(u'往年人数', default=0)
    now_year_count = IntegerField(u'今年预计人数', default=0)
    cooperation_type = SelectField(u'是否是独家', coerce=int, default=1)
    divide_into = FloatField(u'分成比例（%）', default=20)
    policies = SelectField(u'折扣政策', coerce=int, default=1)
    delivery = TextAreaField(u'配送政策')
    special = TextAreaField(u'特殊情况说明')
    sex_distributed = TextAreaField(u'性别分布')
    age_distributed = TextAreaField(u'年龄分布')
    area_distributed = TextAreaField(u'区域分布')
    education_distributed = TextAreaField(u'学历分布')
    income_distributed = TextAreaField(u'收入分布')
    product_position = TextAreaField(u'产品定位')

    def __init__(self, *args, **kwargs):
        super(NewMediumProductDown, self).__init__(*args, **kwargs)
        self.medium.choices = [(k.id, k.name) for k in Medium.all()]
        self.cooperation_type.choices = [(0, u'否'), (1, u'是')]
        self.policies.choices = [(k, str(k)+u'折') for k in range(1,10)]
        

class SizeForm(Form):
    width = IntegerField(u'Width', [validators.Required(u"请输入宽度.")])
    height = IntegerField(u'Height', [validators.Required(u"请输入高度.")])


class UnitForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    description = TextAreaField(u'描述', [validators.Required(u"请输入描述.")])
    size = SelectField(u'尺寸', coerce=int)
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

    def validate(self):
        if Form.validate(self):
            positions = AdPosition.gets(self.positions.data)
            medium = Medium.get(self.medium.data)
            for p in positions:
                if p.medium != medium:
                    self.positions.errors.append(u"%s不属于%s" % (p.display_name, medium.name))
                    return False
            return True
        else:
            return False


class PositionForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    description = TextAreaField(u'描述', [validators.Required(u"请输入描述.")])
    size = SelectField(u'尺寸', coerce=int)
    standard = TextField(u'广告标准', [validators.Required(u"请输入广告标准.")])
    status = SelectField(u'状态', coerce=int, default=1)
    units = SelectMultipleField(u'包含以下广告单元', coerce=int)
    medium = SelectField(u'所属媒体', coerce=int)
    level = SelectField(u'资源类别', coerce=int)
    ad_type = SelectField(u'投放类型', coerce=int)
    cpd_num = IntegerField(u'CPD量(CPD有效)', default=0)
    estimate_num = IntegerField(u'预估量(自动计算)', default=0)
    max_order_num = IntegerField(u'最大预订(CPM有效)', default=0)
    launch_strategy = SelectField(u'投放策略', coerce=int, default=1)
    price = IntegerField(u'单价(元)', default=0)

    def __init__(self, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)
        self.status.choices = STATUS_CN.items()
        self.size.choices = [(x.id, x.name) for x in AdSize.all()]
        self.medium.choices = [(x.id, x.name) for x in Medium.all()]
        self.level.choices = POSITION_LEVEL_CN.items()
        self.ad_type.choices = AD_TYPE_CN.items()
        self.units.choices = [(x.id, x.display_name) for x in AdUnit.all()]
        self.estimate_num.readonly = True
        self.estimate_num.hidden = False
        self.launch_strategy.choices = LAUNCH_STRATEGY.items()

    def validate(self):
        if Form.validate(self):
            if not self.estimate_num.hidden:
                if self.ad_type.data == AD_TYPE_NORMAL:
                    if self.max_order_num.data > self.estimate_num.data:
                        self.max_order_num.errors.append(u"最大预订不能大于预估量(如果新添加了广告单元, 请先保存, 然后根据计算所得调整)")
                        return False
                elif self.ad_type.data == AD_TYPE_CPD:
                    if self.cpd_num.data > self.estimate_num.data:
                        self.cpd_num.errors.append(u"CPD量不能大于预估量")
                        return False
            units = AdUnit.gets(self.units.data)
            medium = Medium.get(self.medium.data)
            if not units:
                self.units.errors.append(u"所含广告单元不能为空")
                return False
            for u in units:
                if u.medium != medium:
                    self.units.errors.append(u"%s不属于%s" % (u.display_name, medium.name))
                    return False
            return True
        else:
            return False
