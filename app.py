#-*- coding: utf-8 -*-
from flask import g, request, url_for, redirect
from flask.ext.login import LoginManager, current_user

from factory import create_app
from urls import register_blueprint
from config import config_object


app = create_app(config_object)

login_manager = LoginManager()
login_manager.login_message = None
login_manager.init_app(app)
login_manager.login_view = "user.login"


@login_manager.user_loader
def load_user(userid):
    from models.user import User
    return User.get(userid)


@app.before_request
def request_user():
    if current_user and current_user.is_authenticated():
        g.user = current_user
    elif url_for('user.login') != request.path and \
            not request.path.startswith(u'/static/'):
        return login_manager.unauthorized()


@app.route('/')
def index():
    return redirect(url_for('order.index'))

# urls
register_blueprint(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
