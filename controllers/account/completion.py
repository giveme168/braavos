# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, redirect, url_for, g, abort, jsonify
from flask import render_template as tpl, flash

from models.user import User, TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN
from models.account.saler import Completion, CompletionIncrement


account_completion_bp = Blueprint(
    'account_completion', __name__, template_folder='../../templates/account/completion/')


@account_completion_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    users = [u for u in User.all() if u.is_out_saler]
    huabei_users = [u for u in users if u.location == TEAM_LOCATION_HUABEI]
    huadong_users = [u for u in users if u.location == TEAM_LOCATION_HUADONG]
    huanan_users = [u for u in users if u.location == TEAM_LOCATION_HUANAN]
    return tpl('/account/completion/self/index.html', huabei_users=huabei_users,
               huadong_users=huadong_users, huanan_users=huanan_users)


@account_completion_bp.route('/increment', methods=['GET'])
def increment_index():
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    users = [u for u in User.all() if u.is_out_saler]
    huabei_users = [u for u in users if u.location == TEAM_LOCATION_HUABEI]
    huadong_users = [u for u in users if u.location == TEAM_LOCATION_HUADONG]
    huanan_users = [u for u in users if u.location == TEAM_LOCATION_HUANAN]
    return tpl('/account/completion/increment/index.html', huabei_users=huabei_users,
               huadong_users=huadong_users, huanan_users=huanan_users)


@account_completion_bp.route('/<user_id>/info', methods=['GET'])
def info(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    user = User.get(user_id)
    comp = Completion.query.filter_by(user_id=user_id)
    return tpl('/account/completion/self/info.html', user=user, comp=comp)


@account_completion_bp.route('/<user_id>/increment/info', methods=['GET'])
def increment_info(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    user = User.get(user_id)
    comp = CompletionIncrement.query.filter_by(user_id=user_id)
    return tpl('/account/completion/increment/info.html', user=user, comp=comp)


@account_completion_bp.route('/<user_id>/create', methods=['GET', 'POST'])
def create(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    user = User.get(user_id)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = str(request.values.get('year', datetime.datetime.now().year))
        Q = str(request.values.get('Q', 'Q1'))
        try:
            completion = Completion.add(
                user=user,
                creator=g.user,
                rate=rate,
                time=year + Q)
            if completion:
                flash(u'添加提成信息成功', 'success')
                return redirect(url_for('account_completion.info', user_id=user_id))
            else:
                flash(u'该年度已存在返点信息', 'danger')
                return redirect(url_for('account_completion.create', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
    return tpl('/account/completion/self/create.html', user=user)


@account_completion_bp.route('/<user_id>/increment/create', methods=['GET', 'POST'])
def increment_create(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    user = User.get(user_id)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = str(request.values.get('year', datetime.datetime.now().year))
        Q = str(request.values.get('Q', 'Q1'))
        try:
            completion = CompletionIncrement.add(
                user=user,
                creator=g.user,
                rate=rate,
                time=year + Q)
            if completion:
                flash(u'添加提成信息成功', 'success')
                return redirect(url_for('account_completion.increment_info', user_id=user_id))
            else:
                flash(u'该年度已存在返点信息', 'danger')
                return redirect(url_for('account_completion.increment_create', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
    return tpl('/account/completion/increment/create.html', user=user)


@account_completion_bp.route('/<user_id>/<mid>/update', methods=['GET', 'POST'])
def update(user_id, mid):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    completion = Completion.get(mid)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = str(request.values.get('year', datetime.datetime.now().year))
        Q = str(request.values.get('Q', 'Q1'))
        try:
            completion.time = year + Q
            completion.rate = rate
            completion.save()
            flash(u'修改提成信息成功', 'success')
            return redirect(url_for('account_completion.info', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
            return redirect(url_for('account_completion.update', user_id=user_id, mid=mid))
    return tpl('/account/completion/self/update.html', completion=completion)


@account_completion_bp.route('/<user_id>/<mid>/increment/update', methods=['GET', 'POST'])
def increment_update(user_id, mid):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    completion = CompletionIncrement.get(mid)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = str(request.values.get('year', datetime.datetime.now().year))
        Q = str(request.values.get('Q', 'Q1'))
        try:
            completion.time = year + Q
            completion.rate = rate
            completion.save()
            flash(u'修改提成信息成功', 'success')
            return redirect(url_for('account_completion.increment_info', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
            return redirect(url_for('account_completion.increment_update', user_id=user_id, mid=mid))
    return tpl('/account/completion/increment/update.html', completion=completion)


@account_completion_bp.route('/<user_id>/<mid>/delete', methods=['GET'])
def delete(user_id, mid):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    completion = Completion.get(mid)
    completion.delete()
    return jsonify({'id': mid})


@account_completion_bp.route('/<user_id>/<mid>/increment/delete', methods=['GET'])
def increment_delete(user_id, mid):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    completion = CompletionIncrement.get(mid)
    completion.delete()
    return jsonify({'id': mid})
