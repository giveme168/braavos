#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField
from models.user import User


class LoginForm(Form):
    email = TextField(u'邮箱', [validators.Required(u"请输入邮箱地址."),
                                  validators.Email(u"请输入正确的邮箱地址.")])
    password = PasswordField(u'密码', [validators.Required(u"请输入您的密码.")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return user
        else:
            self.email.errors.append(u"用户名或者密码错误.")
            return False
