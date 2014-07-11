#-*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, url_for, abort
from flask import render_template as tpl
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


@user_bp.route('/new_team', methods=['GET', 'POST'])
@login_required
def new_team():
    from forms.user import NewTeamForm
    from models.user import Team
    form = NewTeamForm(request.form)
    if request.method == 'POST':
        if form.validate():
            team = Team(form.name.data, form.type.data)
            team.add()
            return redirect(url_for("user.teams"))
    return tpl('new_team.html', form=form)


@user_bp.route('/team_detail/<team_id>', methods=['GET', 'POST'])
@login_required
def team_detail(team_id):
    from forms.user import NewTeamForm
    from models.user import Team
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
@login_required
def new_user():
    from forms.user import NewUserForm
    from models.user import User, Team
    form = NewUserForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User(form.name.data, form.email.data, 'pwd123', form.phone.data, Team.get(form.team.data), form.status.data)
            user.add()
            return redirect(url_for("user.users"))
    return tpl('new_user.html', form=form)


@user_bp.route('/user_detail/<user_id>', methods=['GET', 'POST'])
@login_required
def user_detail(user_id):
    from forms.user import NewUserForm
    from models.user import User, Team
    user = User.get(user_id)
    if not user:
        abort(404)
    form = NewUserForm(request.form)
    if request.method == 'POST':
        if form.validate(vali_email=False):
            user.name = form.name.data
            user.email = form.email.data
            user.phone = form.phone.data
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
