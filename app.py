#-*- coding: UTF-8 -*-
from flask import Flask, g, request, url_for
from flask.ext.login import LoginManager, current_user
from config import DEBUG, SECRET_KEY, SQLALCHEMY_DATABASE_URI
from urls import register_blueprint

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY

# login manager
login_manager = LoginManager()
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
    elif url_for('user.login') != request.path and not request.path.startswith(u'/static/'):
        return login_manager.unauthorized()

# urls
register_blueprint(app)


if __name__ == '__main__':
    app.debug = DEBUG
    app.run(host='0.0.0.0', port=8000)
