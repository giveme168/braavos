# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder
from models.douban_order import BackMoney as DoubanBackMoney
from models.douban_order import BackInvoiceRebate as DoubanBackInvoiceRebate
from models.client_order import ClientOrder
from models.client_order import BackMoney as ClientBackMoney
from models.client_order import BackInvoiceRebate as ClientBackInvoiceRebate
from libs.date_helpers import get_monthes_pre_days

data_query_super_leader_back_money_bp = Blueprint(
    'data_query_super_leader_back_money', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_back_money_bp.route('/client_order', methods=['GET'])
def client_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/back_money.html',
               title=u'新媒体订单回款分析（包含返点发票）',
               type='client')


@data_query_super_leader_back_money_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/back_money.html',
               title=u'豆瓣订单回款分析（包含返点发票）',
               type='douban')


# 计算某个合同指定月是否有回款
def _order_executive_reports(order, month_day):
    money, start, end = order.money, order.client_start, order.client_end
    back_moneys = order.backmoneys
    back_invoice = order.backinvoicerebates
    back_total = 0
    # 获取到指定月之前的所有回款
    for k in list(back_moneys) + list(back_invoice):
        back_time = k.back_time.replace(day=1).date()
        if back_time <= month_day:
            back_total += k.money

    if money:
        pre_money = float(money) / ((start - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(datetime.datetime.strptime(start.strftime('%Y-%m-%d'), '%Y-%m-%d'),
                                          datetime.datetime.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d'))
    # pre_month_money_data = []
    for k in pre_month_days:
        # pre_month_money_data.append({'money': pre_money * k['days'], 'month_day': k['month']})
        money = pre_money * k['days']
        month = k['month'].date()
        # 回款逐月递减，减到指定月后，看总回款的剩余情况，计算指定月未回款金额
        back_total -= money
        if month_day == month:
            if back_total <= 0:
                return money
            else:
                if back_total > money:
                    return money
                else:
                    return money - back_total
        else:
            continue
    return 0


# 格式化合同
def _format_client_order(order):
    params = {}
    params['money'] = order.money
    params['reminde_date'] = order.reminde_date.replace(day=1)
    params['order_id'] = order.id
    params['reminde_date'] = order.reminde_date.replace(day=1)
    return params


# 格式化回款及返点发票
def _format_back_money(back_moneys, type):
    data = []
    for k in back_moneys:
        if type == 'client':
            order_id = k.client_order_id
        else:
            order_id = k.douban_order_id
        data.append({'money': k.money,
                     'back_time': k.back_time.replace(day=1).date(),
                     'order_id': order_id})
    return data


# 在指定时间内回款金额
def _back_money(month, back_moneys):
    # 获取到指定时间之前的所有回款
    back_total = 0
    for k in back_moneys:
        if k['back_time'] <= month:
            back_total += k['money']
    return back_total


# 到账期后未回款合同总金额
def _need_back_money(orders, month):
    total_money = 0
    for k in orders:
        if k['reminde_date'] <= month:
            total_money += k['money']
    return total_money


@data_query_super_leader_back_money_bp.route('/client_order_json', methods=['POST'])
def client_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    orders = ClientOrder.query.filter(ClientOrder.back_money_status == 1,
                                      ClientOrder.status == 1,
                                      ClientOrder.reminde_date <= now_year_end)

    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'back_moneys': 0,
                                            'un_back_moneys': 0}
    # 回款
    back_moneys = list(ClientBackMoney.all()) + \
        list(ClientBackInvoiceRebate.all())
    back_moneys = _format_back_money(back_moneys, 'client')
    for k in back_moneys:
        if k['back_time'] in client_params:
            client_params[k['back_time']]['back_moneys'] += k['money']

    # 计算未回款金额累计
    orders = [_format_client_order(k) for k in orders if k.contract_status in [
        2, 4, 5, 19, 20]]
    for k in client_params:
        need_back_money = _need_back_money(orders, k)
        client_params[k][
            'un_back_moneys'] += need_back_money - _back_money(k, back_moneys)

    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])

    # 初始化highcharts数据
    data = []
    data.append({'name': u'已回款金额',
                 'data': []})
    data.append({'name': u'未回款金额',
                 'data': []})

    for k, v in client_params:
        day_time_stamp = int(datetime.datetime.strptime(
            str(k), '%Y-%m-%d').strftime('%s')) * 1000
        data[0]['data'].append([day_time_stamp, v['back_moneys']])
        data[1]['data'].append([day_time_stamp, v['un_back_moneys']])
    return jsonify({'data': data, 'title': u'新媒体订单回款分析（包含返点发票）'})


@data_query_super_leader_back_money_bp.route('/douban_order_json', methods=['POST'])
def douban_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    orders = DoubanOrder.query.filter(DoubanOrder.back_money_status == 1,
                                      DoubanOrder.status == 1,
                                      DoubanOrder.reminde_date <= now_year_end)
    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'back_moneys': 0,
                                            'un_back_moneys': 0}
    # 回款
    back_moneys = list(DoubanBackMoney.all()) + \
        list(DoubanBackInvoiceRebate.all())
    back_moneys = _format_back_money(back_moneys, 'douban')
    for k in back_moneys:
        if k['back_time'] in client_params:
            client_params[k['back_time']]['back_moneys'] += k['money']

    # 计算未回款金额累计
    orders = [_format_client_order(k) for k in orders if k.contract_status in [
        2, 4, 5, 19, 20]]
    for k in client_params:
        need_back_money = _need_back_money(orders, k)
        client_params[k][
            'un_back_moneys'] += need_back_money - _back_money(k, back_moneys)
    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])

    # 初始化highcharts数据
    data = []
    data.append({'name': u'已回款金额',
                 'data': []})
    data.append({'name': u'未回款金额',
                 'data': []})

    for k, v in client_params:
        day_time_stamp = int(datetime.datetime.strptime(
            str(k), '%Y-%m-%d').strftime('%s')) * 1000
        data[0]['data'].append([day_time_stamp, v['back_moneys']])
        data[1]['data'].append([day_time_stamp, v['un_back_moneys']])
    return jsonify({'data': data, 'title': u'直签豆瓣订单回款分析（包含返点发票）'})
