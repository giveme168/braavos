#-*- coding: UTF-8 -*-
from flask import Flask, request
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as tpl
from config import DEBUG, SECRET_KEY, SQLALCHEMY_DATABASE_URI

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAKO_DEFAULT_FILTERS'] = ['decode.utf_8', 'h']
app.config['MAKO_TRANSLATE_EXCEPTIONS'] = False
mako = MakoTemplates(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    from models.user import User
    from forms.login import LoginForm
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        return u"登录成功"
    return tpl('login.html', form=form)


if __name__ == '__main__':
    app.debug = DEBUG
    app.run(host='0.0.0.0', port=8000)
