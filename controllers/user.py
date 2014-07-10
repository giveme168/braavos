#-*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, url_for
from flask.ext.mako import render_template as tpl
from flask.ext.login import login_user, login_required, logout_user

user_bp = Blueprint('user', __name__, template_folder='../templates/user')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    from forms.user import LoginForm
    form = LoginForm(request.form)
    if request.method == 'POST':
        user = form.validate()
        if user:
            login_user(user)
            return redirect(request.args.get("next") or url_for("user.teams"))
    return tpl('login.html', form=form)


@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("user.login"))


@user_bp.route('/teams')
@login_required
def teams():
    from models.user import Team
    teams = Team.query.all()
    return tpl('teams.html', teams=teams)


@user_bp.route('/users')
@login_required
def users():
    from models.user import User
    users = User.query.all()
    return tpl('users.html', users=users)
