# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, redirect, url_for, g, abort, jsonify
from flask import render_template as tpl, flash

from models.user import User, TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN
from models.account.saler import Commission


account_commission_bp = Blueprint(
    'account_commission', __name__, template_folder='../../templates/account/commission/')


@account_commission_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_super_leader():
        return abort(404)
    users = [u for u in User.all() if u.is_out_saler and u.is_active()]
    huabei_users = [u for u in users if u.location == TEAM_LOCATION_HUABEI]
    huadong_users = [u for u in users if u.location == TEAM_LOCATION_HUADONG]
    huanan_users = [u for u in users if u.location == TEAM_LOCATION_HUANAN]
    return tpl('/account/commission/index.html', huabei_users=huabei_users,
               huadong_users=huadong_users, huanan_users=huanan_users)


@account_commission_bp.route('/<user_id>/info', methods=['GET'])
def info(user_id):
    if not g.user.is_super_leader():
        return abort(404)
    user = User.get(user_id)
    comms = Commission.query.filter_by(user_id=user_id)
    return tpl('/account/commission/info.html', user=user, comms=comms)


@account_commission_bp.route('/<user_id>/create', methods=['GET', 'POST'])
def create(user_id):
    if not g.user.is_super_leader():
        return abort(404)
    user = User.get(user_id)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = int(request.values.get('year', datetime.datetime.now().year))
        try:
            commission = Commission.add(
                user=user,
                creator=g.user,
                rate=rate,
                year=year)
            if commission:
                flash(u'添加提成信息成功', 'success')
                return redirect(url_for('account_commission.info', user_id=user_id))
            else:
                flash(u'该年度已存在返点信息', 'danger')
                return redirect(url_for('account_commission.create', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
    return tpl('/account/commission/create.html', user=user)


@account_commission_bp.route('/<user_id>/<mid>/update', methods=['GET', 'POST'])
def update(user_id, mid):
    if not g.user.is_super_leader():
        return abort(404)
    commission = Commission.get(mid)
    if request.method == 'POST':
        rate = float(request.values.get('rate', 0))
        year = int(request.values.get('year', datetime.datetime.now().year))
        try:
            commission.year = year
            commission.rate = rate
            commission.save()
            flash(u'修改提成信息成功', 'success')
            return redirect(url_for('account_commission.info', user_id=user_id))
        except:
            flash(u'该年度已存在返点信息', 'danger')
            return redirect(url_for('account_commission.update', user_id=user_id, mid=mid))
    return tpl('/account/commission/update.html', commission=commission)


@account_commission_bp.route('/<user_id>/<mid>/delete', methods=['GET'])
def delete(user_id, mid):
    if not g.user.is_super_leader():
        return abort(404)
    commission = Commission.get(mid)
    commission.delete()
    return jsonify({'id': mid})
