# -*- coding: UTF-8 -*-
import datetime
from wtforms import TextField, DateField, validators, PasswordField, SelectField, SelectMultipleField, TextAreaField

from libs.wtf import Form
from models.user import (User, Team,
                         TEAM_TYPE_CN, TEAM_LOCATION_CN, USER_STATUS_CN, TEAM_TYPE_MEDIUM,
                         TEAM_LOCATION_DEFAULT, LEAVE_TYPE_CN, DEFAULT_BIRTHDAY, DEFAULT_RECRUITED_DATE,
                         OKR_P_OBJECTIVE_CN, OKR_P_KEY_RESULT)


class LoginForm(Form):
    email = TextField(u'邮箱', [validators.Required(u"请输入邮箱地址."),
                              validators.Email(u"请输入正确的邮箱地址.")])
    password = PasswordField(u'密码', [validators.Required(u"请输入您的密码.")])

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.get_by_email(email=self.email.data.lower())
        if user and user.check_password(self.password.data):
            return user
        else:
            self.email.errors.append(u"用户名或者密码错误.")
            return False

    def error_msg(self, msg):
        self.email.errors.append(msg)


class PwdChangeForm(Form):
    old_password = PasswordField(u'原密码', [validators.Required(u"请输入原密码.")])
    password = PasswordField(u'密码', [validators.Required(u"请输入您的密码.")])
    confirm = PasswordField(u'再次输入新密码', [validators.Required(u"请再次输入您的密码.")])

    def validate(self, user):
        if not Form.validate(self):
            return False
        if not user.check_password(self.old_password.data):
            self.old_password.errors.append(u"原密码错误.")
            return False
        return True


class NewTeamForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    type = SelectField(u'类型', coerce=int, default=TEAM_TYPE_MEDIUM)
    location = SelectField(u'区域', coerce=int, default=TEAM_LOCATION_DEFAULT)
    admins = SelectMultipleField(u'团队管理员', coerce=int)

    def __init__(self, *args, **kwargs):
        super(NewTeamForm, self).__init__(*args, **kwargs)
        self.type.choices = TEAM_TYPE_CN.items()
        self.location.choices = TEAM_LOCATION_CN.items()
        self.admins.choices = [(m.id, m.name) for m in User.all()]


class NewUserForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    email = TextField(u'邮箱', [validators.Required(u"请输入邮箱."),
                              validators.Email(u"请输入正确的邮箱地址.")])
    status = SelectField(u'状态', coerce=int, default=1)
    team = SelectField(u'角色', coerce=int)
    team_leaders = SelectMultipleField(u'直属领导', coerce=int)
    birthday = DateField(u'生日日期', default=DEFAULT_BIRTHDAY)
    recruited_date = DateField(u'入职日期', default=DEFAULT_RECRUITED_DATE)
    positive_date = DateField(u'转正日期', default=DEFAULT_RECRUITED_DATE)
    quit_date = DateField(u'离职日期', default=DEFAULT_RECRUITED_DATE)
    cellphone = TextField(u'手机号', default='')
    position = TextField(u'职位', default='')
    sn = TextField(u'员工编号', default='')

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.status.choices = USER_STATUS_CN.items()
        self.team.choices = [(t.id, t.name) for t in Team.all()]
        self.team_leaders.choices = [(m.id, m.name) for m in User.all()]

    def validate(self, vali_email=True):
        if not Form.validate(self):
            return False
        user = User.get_by_email(email=self.email.data.lower())
        if vali_email and user:
            self.email.errors.append(u' 该邮箱用户已存在')
            return False
        return True


class UserLeaveForm(Form):
    type = SelectField(u'类型', coerce=int, default=1)
    reason = TextAreaField(u'原因')
    senders = SelectMultipleField(u'抄送人', coerce=int)

    def __init__(self, *args, **kwargs):
        super(UserLeaveForm, self).__init__(*args, **kwargs)
        self.type.choices = LEAVE_TYPE_CN.items()
        self.senders.choices = [(m.id, m.name) for m in User.all()]


class OkrForm(Form):
    #type = TextAreaField(u'目标')
    objective = TextAreaField(u'目标')
    p_objective = SelectField(u'目标优先级', coerce=int, default=1)
    key_result = TextAreaField(u'主要成绩')
    p_key_result = SelectField(u'成绩优先级', coerce=int, default=1)

    def __init__(self, *args, **kwargs):
        super(OkrForm, self).__init__(*args, **kwargs)
        self.p_objective.choices = OKR_P_OBJECTIVE_CN.items()
        self.p_key_result.choices = OKR_P_KEY_RESULT.items()
