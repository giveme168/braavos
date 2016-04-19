# -*- coding: utf-8 -*-
import datetime
import calendar as cal

from flask import Blueprint, request, redirect, url_for, g, abort, jsonify
from flask import render_template as tpl, flash

from models.user import User, TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN
from models.account.saler import Commission
from models.client_order import BackMoney
from models.douban_order import BackMoney as DoubanBackMoney
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q)


account_commission_bp = Blueprint(
    'account_commission', __name__, template_folder='../../templates/account/commission/')


@account_commission_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    if g.user.is_searchad_member() and (not g.user.is_admin()) and (not g.user.is_super_leader()):
        users = [u for u in User.all() if u.is_search_saler and u.is_active()]
    else:
        users = [u for u in User.all() if u.is_out_saler and u.is_active()]
    huabei_users = [u for u in users if u.location == TEAM_LOCATION_HUABEI]
    huadong_users = [u for u in users if u.location == TEAM_LOCATION_HUADONG]
    huanan_users = [u for u in users if u.location == TEAM_LOCATION_HUANAN]
    return tpl('/account/commission/index.html', huabei_users=huabei_users,
               huadong_users=huadong_users, huanan_users=huanan_users)


@account_commission_bp.route('/<user_id>/info', methods=['GET'])
def info(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    user = User.get(user_id)
    comms = Commission.query.filter_by(user_id=user_id)
    return tpl('/account/commission/info.html', user=user, comms=comms)


@account_commission_bp.route('/<user_id>/create', methods=['GET', 'POST'])
def create(user_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
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
    if not (g.user.is_super_leader() or g.user.is_finance()):
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
    if not (g.user.is_super_leader() or g.user.is_finance()):
        return abort(404)
    commission = Commission.get(mid)
    commission.delete()
    return jsonify({'id': mid})


# 格式化回款
def _dict_back_money(back_money):
    dict_back_money = {}
    dict_back_money['money'] = back_money.money
    dict_back_money['back_time'] = back_money.back_time
    order = back_money.order
    dict_back_money['order'] = order
    dict_back_money['order_id'] = back_money.order.id
    dict_back_money['order_start'] = order.client_start
    dict_back_money['order_end'] = order.client_end
    return dict_back_money


# 销售提成
@account_commission_bp.route('/saler', methods=['GET'])
def saler():
    now_year = request.values.get('year', '')
    now_Q = request.values.get('Q', '')
    location_id = int(request.values.get('location_id', 0))
    if not now_year and not now_Q:
        now_date = datetime.date.today()
        now_year = now_date.strftime('%Y')
        now_month = now_date.strftime('%m')
        now_Q = check_month_get_Q(now_month)
    Q_monthes = check_Q_get_monthes(now_Q)
    start_Q_month = datetime.datetime(int(now_year), int(Q_monthes[0]), 1)
    # 获取下季度的第一天为本季度的结束时间
    d = cal.monthrange(int(now_year), int(Q_monthes[-1]))
    end_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[-1]), d[1]) + datetime.timedelta(days=1)
    # 获取该季度所有回款
    client_back_moneys = [_dict_back_money(k) for k in BackMoney.query.filter(
        BackMoney.back_time >= start_Q_month, BackMoney.back_time < end_Q_month)]
    douban_back_moneys = [_dict_back_money(k) for k in DoubanBackMoney.query.filter(
        BackMoney.back_time >= start_Q_month, BackMoney.back_time < end_Q_month)]
    # 回去当季度回款的所有合同
    client_orders = list(set([k['order'] for k in client_back_moneys]))
    douban_orders = list(set([k['order'] for k in douban_back_moneys]))
    return tpl('/account/commission/saler.html', Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, location_id=location_id, client_orders=client_orders,
               douban_orders=douban_orders)
