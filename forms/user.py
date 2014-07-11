#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField, SelectField


class LoginForm(Form):
    email = TextField(u'邮箱', [validators.Required(u"请输入邮箱地址."),
                                  validators.Email(u"请输入正确的邮箱地址.")])
    password = PasswordField(u'密码', [validators.Required(u"请输入您的密码.")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        from models.user import User
        user = User.get_by_email(email=self.email.data.lower())
        if user and user.check_password(self.password.data):
            return user
        else:
            self.email.errors.append(u"用户名或者密码错误.")
            return False


class NewTeamForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    type = SelectField(u'类型', coerce=int)

    def __init__(self, *args, **kwargs):
        from models.user import TEAM_TYPE_CN
        Form.__init__(self, *args, **kwargs)
        self.type.choices = TEAM_TYPE_CN.items()

    def validate(self):
        return Form.validate(self)


class NewUserForm(Form):
    name = TextField(u'名字', [validators.Required(u"请输入名字.")])
    email = TextField(u'邮箱', [validators.Required(u"请输入邮箱."),
                                  validators.Email(u"请输入正确的邮箱地址.")])
    phone = TextField(u'手机', [validators.Required(u"请输入手机号.")])
    status = SelectField(u'状态', coerce=int)
    team = SelectField(u'Team', coerce=int)

    def __init__(self, *args, **kwargs):
        from models.user import Team, USER_STATUS_CN
        Form.__init__(self, *args, **kwargs)
        self.status.choices = USER_STATUS_CN.items()
        self.team.choices = [(t.id, t.name) for t in Team.all()]

    def validate(self, vali_email=True):
        if not Form.validate(self):
            return False
        from models.user import User
        user = User.get_by_email(email=self.email.data.lower())
        if vali_email and user:
            self.email.errors.append(u' 该邮箱用户已存在')
            return False
        return True
