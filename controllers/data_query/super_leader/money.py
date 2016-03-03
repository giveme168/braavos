# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from libs.date_helpers import get_monthes_pre_days

data_query_super_leader_money_bp = Blueprint(
    'data_query_super_leader_money', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_money_bp.route('/client_order', methods=['GET'])
def client_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/money.html',
               title=u'新媒体订单执行金额分析',
               type='client')


@data_query_super_leader_money_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/money.html',
               title=u'豆瓣订单执行金额分析',
               type='douban')


@data_query_super_leader_money_bp.route('/client_order_json', methods=['POST', 'GET'])
def client_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    last_year_start = datetime.datetime.strptime(
        str(year - 1) + '-01-01', '%Y-%m-%d')
    last_year_end = datetime.datetime.strptime(
        str(year - 1) + '-12-01', '%Y-%m-%d')
    before_last_year_start = datetime.datetime.strptime(
        str(year - 2) + '-01-01', '%Y-%m-%d')
    before_last_year_end = datetime.datetime.strptime(
        str(year - 2) + '-12-01', '%Y-%m-%d')
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= before_last_year_start,
        MediumOrderExecutiveReport.month_day <= now_year_end)
    medium_orders = [{'month_day': k.month_day,
                      'money': k.medium_money2,
                      } for k in medium_orders if k.status == 1]
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    last_monthes = get_monthes_pre_days(last_year_start, last_year_end)
    before_monthes = get_monthes_pre_days(
        before_last_year_start, before_last_year_end)

    # 格式化成字典
    now_monthes_data = {}
    for k in now_monthes:
        now_monthes_data[int(k['month'].strftime('%s')) * 1000] = 0.0
    last_monthes_data = {}
    for k in last_monthes:
        last_monthes_data[int(k['month'].strftime('%s')) * 1000] = 0.0
    before_monthes_data = {}
    for k in before_monthes:
        before_monthes_data[int(k['month'].strftime('%s')) * 1000] = 0.0

    for order in medium_orders:
        if int(order['month_day'].strftime('%s')) * 1000 in now_monthes_data:
            now_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += order['money']
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += order['money']
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += order['money']
    # 格式化数据，把近三年数据放在一年用于画图
    now_monthes_data = sorted(now_monthes_data.iteritems(), key=lambda x: x[0])
    # now_monthes_data.reverse()
    last_monthes_data = sorted(
        last_monthes_data.iteritems(), key=lambda x: x[0])
    # last_monthes_data.reverse()
    before_monthes_data = sorted(
        before_monthes_data.iteritems(), key=lambda x: x[0])
    # before_monthes_data.reverse()
    before_monthes_params = []
    last_monthes_params = []
    now_monthes_params = []
    # 整理近三年数据
    for k, v in now_monthes_data:
        month_day = datetime.datetime.fromtimestamp(k / 1000)
        month_day = month_day.replace(year=year)
        now_monthes_params.append({'time': int(month_day.strftime(
            '%s')) * 1000, 'money': v})
    for k, v in last_monthes_data:
        month_day = datetime.datetime.fromtimestamp(k / 1000)
        month_day = month_day.replace(year=year)
        last_monthes_params.append({'time': int(month_day.strftime(
            '%s')) * 1000, 'money': v})
    for k, v in before_monthes_data:
        month_day = datetime.datetime.fromtimestamp(k / 1000)
        month_day = month_day.replace(year=year)
        before_monthes_params.append({'time': int(month_day.strftime(
            '%s')) * 1000, 'money': v})
    data = []
    data.append({'name': str(before_last_year_start.year) + u'年度',
                 'data': [[k['time'], k['money']] for k in before_monthes_params]})
    data.append({'name': str(last_year_start.year) + u'年度',
                 'data': [[k['time'], k['money']] for k in last_monthes_params]})
    data.append({'name': str(now_year_start.year) + u'年度',
                 'data': [[k['time'], k['money']] for k in now_monthes_params]})
    return jsonify({'data': data, 'title': u'新媒体订单执行额分析'})


@data_query_super_leader_money_bp.route('/douban_order_json', methods=['POST', 'GET'])
def douban_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    last_year_start = datetime.datetime.strptime(
        str(year - 1) + '-01-01', '%Y-%m-%d')
    last_year_end = datetime.datetime.strptime(
        str(year - 1) + '-12-01', '%Y-%m-%d')
    before_last_year_start = datetime.datetime.strptime(
        str(year - 2) + '-01-01', '%Y-%m-%d')
    before_last_year_end = datetime.datetime.strptime(
        str(year - 2) + '-12-01', '%Y-%m-%d')
    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= before_last_year_start,
        DoubanOrderExecutiveReport.month_day <= now_year_end)
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= before_last_year_start,
        MediumOrderExecutiveReport.month_day <= now_year_end)
    douban_date = [{'month_day': k.month_day,
                    'money': k.money,
                    } for k in douban_orders if k.status == 1]
    medium_orders = [{'month_day': k.month_day,
                      'medium_id': int(k.order.medium_id),
                      'medium_money2': k.medium_money2
                      } for k in medium_orders if k.status == 1]
    douban_date += [{'month_day': k['month_day'], 'money':k['medium_money2']}
                    for k in medium_orders if k['medium_id'] in [3, 8]]

    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    last_monthes = get_monthes_pre_days(last_year_start, last_year_end)
    before_monthes = get_monthes_pre_days(
        before_last_year_start, before_last_year_end)

    now_monthes_data = {}
    for k in now_monthes:
        now_monthes_data[int(k['month'].strftime('%s')) * 1000] = 0.0
    last_monthes_data = {}
    for k in last_monthes:
        last_monthes_data[int(k['month'].strftime('%s')) * 1000] = 0.0
    before_monthes_data = {}
    for k in before_monthes:
        before_monthes_data[int(k['month'].strftime('%s')) * 1000] = 0.0

    for order in douban_date:
        if int(order['month_day'].strftime('%s')) * 1000 in now_monthes_data:
            now_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += order['money']
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += order['money']
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += order['money']
    # 格式化数据，把近三年数据放在一年用于画图
    now_monthes_data = sorted(now_monthes_data.iteritems(), key=lambda x: x[0])
    # now_monthes_data.reverse()
    last_monthes_data = sorted(
        last_monthes_data.iteritems(), key=lambda x: x[0])
    # last_monthes_data.reverse()
    before_monthes_data = sorted(
        before_monthes_data.iteritems(), key=lambda x: x[0])
    # before_monthes_data.reverse()
    before_monthes_params = []
    last_monthes_params = []
    now_monthes_params = []
    for k, v in now_monthes_data:
        month_day = datetime.datetime.fromtimestamp(k / 1000)
        month_day = month_day.replace(year=year)
        now_monthes_params.append({'time': int(month_day.strftime(
            '%s')) * 1000, 'money': v})
    for k, v in last_monthes_data:
        month_day = datetime.datetime.fromtimestamp(k / 1000)
        month_day = month_day.replace(year=year)
        last_monthes_params.append({'time': int(month_day.strftime(
            '%s')) * 1000, 'money': v})
    for k, v in before_monthes_data:
        month_day = datetime.datetime.fromtimestamp(k / 1000)
        month_day = month_day.replace(year=year)
        before_monthes_params.append({'time': int(month_day.strftime(
            '%s')) * 1000, 'money': v})
    data = []
    data.append({'name': str(before_last_year_start.year) + u'年度',
                 'data': [[k['time'], k['money']] for k in before_monthes_params]})
    data.append({'name': str(last_year_start.year) + u'年度',
                 'data': [[k['time'], k['money']] for k in last_monthes_params]})
    data.append({'name': str(now_year_start.year) + u'年度',
                 'data': [[k['time'], k['money']] for k in now_monthes_params]})
    return jsonify({'data': data, 'title': u'直签豆瓣订单（含：优力、无线）执行额分析'})
