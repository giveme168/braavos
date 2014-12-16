#-*- coding: UTF-8 -*-
from wtforms import TextField, validators, PasswordField, SelectField

from libs.wtf import Form
from models.user import User, Team, TEAM_TYPE_CN, USER_STATUS_CN, TEAM_TYPE_MEDIUM


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


class PwdChangeForm(Form):
    old_password = PasswordField(u'原密码', [validators.Required(u"请输入原密码.")])
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

    def __init__(self, *args, **kwargs):
        super(NewTeamForm, self).__init__(*args, **kwargs)
        self.type.choices = TEAM_TYPE_CN.items()


class NewUserForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    email = TextField(u'邮箱', [validators.Required(u"请输入邮箱."),
                                  validators.Email(u"请输入正确的邮箱地址.")])
    status = SelectField(u'状态', coerce=int, default=1)
    team = SelectField(u'Team', coerce=int)

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.status.choices = USER_STATUS_CN.items()
        self.team.choices = [(t.id, t.name) for t in Team.all()]

    def validate(self, vali_email=True):
        if not Form.validate(self):
            return False
        user = User.get_by_email(email=self.email.data.lower())
        if vali_email and user:
            self.email.errors.append(u' 该邮箱用户已存在')
            return False
        return True
