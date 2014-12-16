# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, url_for, abort, g
from flask import render_template as tpl, flash
from flask.ext.login import login_user, logout_user, current_user

from . import admin_required
from models.user import Team, User, USER_STATUS_CN
from forms.user import LoginForm, PwdChangeForm, NewTeamForm, NewUserForm
from config import DEFAULT_PASSWORD
from libs.signals import password_changed_signal

user_bp = Blueprint('user', __name__, template_folder='../templates/user')


@user_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('user.teams'))


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        user = form.validate()
        if user:
            login_user(user)
            if user.check_password(DEFAULT_PASSWORD):
                flash(u'您还在使用默认密码, 请及时<a href="%s">修改您的密码!</a>' % url_for('user.pwd_change'), 'danger')
            return redirect(request.args.get("next", "/"))
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
            password_changed_signal.send(user)
            logout_user()
            return redirect('/')
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
    if request.method == 'POST' and form.validate():
        db_team_name = Team.name_exist(form.name.data)
        if not db_team_name:
            team = Team.add(form.name.data, form.type.data)
            flash(u'新建团队(%s)成功!' % team.name, 'success')
        else:
            flash(u'新建团队(%s)失败，团队名称已经存在!' % form.name.data, 'danger')
            return tpl('new_team.html', form=form)
        if request.values.get('next'):
            return redirect(request.values.get('next'))
        return redirect(url_for("user.team_detail", team_id=team.id))
    return tpl('new_team.html', form=form)


@user_bp.route('/team/<team_id>', methods=['GET', 'POST'])
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
            flash(u'保存成功!', 'success')
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
            db_user_name = User.name_exist(form.name.data)
            if not db_user_name:
                user = User.add(form.name.data, form.email.data, DEFAULT_PASSWORD,
                                Team.get(form.team.data), form.status.data)
                flash(u'新建用户(%s)成功!' % user.name, 'success')
            else:
                flash(u'新建用户(%s)失败，用户名已经存在!' % form.name.data, 'danger')
                return tpl('new_user.html', form=form)
            return redirect(url_for("user.users"))
    return tpl('new_user.html', form=form)


@user_bp.route('/user/<user_id>', methods=['GET', 'POST'])
def user_detail(user_id):
    user = User.get(user_id)
    if not user:
        abort(404)
    form = NewUserForm(request.form)
    if request.method == 'POST':
        if form.validate(vali_email=False):
            user.name = form.name.data
            if g.user.team.is_admin():  # 只有管理员才有权限修改 email team status
                user.email = form.email.data
                user.team = Team.get(form.team.data)
                user.status = form.status.data
            user.save()
            flash(u'保存成功!', 'success')
    else:
        form.name.data = user.name
        form.email.data = user.email
        form.team.data = user.team_id
        form.status.data = user.status
    if not g.user.team.is_admin():
        form.email.readonly = True
        form.team.readonly = True
        form.status.readonly = True
        form.status.choices = [(user.status, USER_STATUS_CN[user.status])]
        form.team.choices = [(user.team_id, user.team.name)]
    return tpl('user_detail.html', user=user, form=form, DEFAULT_PASSWORD=DEFAULT_PASSWORD)


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
