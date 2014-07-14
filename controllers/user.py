#-*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, url_for, abort, g
from flask import render_template as tpl
from flask.ext.login import login_user, logout_user, current_user

from . import admin_required
from models.user import Team, User
from forms.user import LoginForm, PwdChangeForm, NewTeamForm, NewUserForm

user_bp = Blueprint('user', __name__, template_folder='../templates/user')
DEFAULT_PASSWORD = 'pwd123'


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
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


@user_bp.route('/password_change', methods=['GET', 'POST'])
def pwd_change():
    form = PwdChangeForm(request.form)
    if request.method == 'POST':
        user = current_user
        if form.validate(user):
            user.set_password(form.password.data)
            logout_user()
            return redirect(url_for('user.login'))
    return tpl('pwd_change.html', form=form)


@user_bp.route('/teams')
@admin_required
def teams():
    teams = Team.all()
    return tpl('teams.html', teams=teams)


@user_bp.route('/users')
@admin_required
def users():
    users = User.all()
    return tpl('users.html', users=users)


@user_bp.route('/new_team', methods=['GET', 'POST'])
@admin_required
def new_team():
    form = NewTeamForm(request.form)
    if request.method == 'POST':
        if form.validate():
            team = Team(form.name.data, form.type.data)
            team.add()
            return redirect(url_for("user.teams"))
    return tpl('new_team.html', form=form)


@user_bp.route('/team_detail/<team_id>', methods=['GET', 'POST'])
@admin_required
def team_detail(team_id):
    team = Team.get(team_id)
    if not team:
        abort(404)
    form = NewTeamForm(request.form)
    if request.method == 'POST':
        if form.validate():
            team.name = form.name.data
            team.type = form.type.data
            team.save()
    else:
        form.name.data = team.name
        form.type.data = team.type
    return tpl('team_detail.html', team=team, form=form)


@user_bp.route('/new_user', methods=['GET', 'POST'])
@admin_required
def new_user():
    form = NewUserForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User(form.name.data, form.email.data, DEFAULT_PASSWORD, form.phone.data, Team.get(form.team.data), form.status.data)
            user.add()
            return redirect(url_for("user.users"))
    return tpl('new_user.html', form=form)


@user_bp.route('/user_detail/<user_id>', methods=['GET', 'POST'])
def user_detail(user_id):
    user = User.get(user_id)
    if not user:
        abort(404)
    form = NewUserForm(request.form)
    if request.method == 'POST':
        if form.validate(vali_email=False):
            user.name = form.name.data
            user.phone = form.phone.data
            if g.user.team.is_admin():  #   只有管理员才有权限修改 email team status
                user.email = form.email.data
                user.team = Team.get(form.team.data)
                user.status = form.status.data
            user.save()
    else:
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.team.data = user.team
        form.status.data = user.status
    return tpl('user_detail.html', user=user, form=form)


@user_bp.route('/mine')
def mine():
    return redirect(url_for('user.user_detail', user_id=g.user.id))


@user_bp.route('/pwd_reset/<user_id>')
@admin_required
def pwd_reset(user_id):
    user = User.get(user_id)
    if not user:
        abort(404)
    user.set_password(DEFAULT_PASSWORD)
    user.save()
    return redirect(url_for('user.users'))
