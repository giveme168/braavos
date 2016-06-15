# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from searchAd.models.order import searchAdMediumOrderExecutiveReport
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.super_leader_helpers import write_line_excel

data_query_super_leader_money_bp = Blueprint(
    'data_query_super_leader_money', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_money_bp.route('/client_order', methods=['GET'])
def client_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'新媒体订单执行金额分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_line_excel(client_order_excle_data())
    return tpl('/data_query/super_leader/money.html',
               title=title,
               type='client')


@data_query_super_leader_money_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'豆瓣订单执行金额分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_line_excel(douban_order_excle_data())
    return tpl('/data_query/super_leader/money.html',
               title=title,
               type='douban')


@data_query_super_leader_money_bp.route('/search', methods=['GET'])
def search():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'搜索业务执行金额分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_line_excel(search_excle_data())
    return tpl('/data_query/super_leader/money.html',
               title=title,
               type='search')


def _format_order(order, type='client'):
    params = {}
    params['month_day'] = order.month_day
    if type == 'client':
        params['money'] = order.sale_money
        params['medium_id'] = order.order.medium_id
        params['direct_sales'] = order.client_order.direct_sales
        params['agent_sales'] = order.client_order.agent_sales
        params['locations'] = order.client_order.locations
    else:
        params['money'] = order.money
        params['direct_sales'] = order.douban_order.direct_sales
        params['agent_sales'] = order.douban_order.agent_sales
        params['locations'] = order.douban_order.locations
    return params


def _get_money_by_location(order, location):
    if location != 0:
        if set(order['locations']) == set([location]):
            return order['money']
        else:
            # 用于查看渠道销售是否跨区
            direct_sales = order['direct_sales']
            direct_location = list(set([k.team.location for k in direct_sales]))
            # 用于查看直客销售是否跨区
            agent_sales = order['agent_sales']
            agent_location = list(set([k.team.location for k in agent_sales]))
            money = 0
            if location in direct_location:
                money += float(order['money']) / len(direct_location)
            if location in agent_location:
                money += float(order['money']) / len(agent_location)
            return money
    return order['money']


def search_excle_data():
    now_date = datetime.datetime.now()
    location = 0
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
    medium_orders = searchAdMediumOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= before_last_year_start,
        searchAdMediumOrderExecutiveReport.month_day <= now_year_end)
    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
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
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
    # 格式化数据，把近三年数据放在一年用于画图
    now_monthes_data = sorted(now_monthes_data.iteritems(), key=lambda x: x[0])
    last_monthes_data = sorted(
        last_monthes_data.iteritems(), key=lambda x: x[0])
    before_monthes_data = sorted(
        before_monthes_data.iteritems(), key=lambda x: x[0])

    headings = ['月份', str(before_last_year_start.year) + u'年度',
                str(last_year_start.year) + u'年度',
                str(now_year_start.year) + u'年度']
    data = []
    data.append([str(k + 1) + u'月' for k in range(len(now_monthes_data))])
    data.append([v for k, v in before_monthes_data])
    data.append([v for k, v in last_monthes_data])
    data.append([v for k, v in now_monthes_data])
    return {'data': data, 'title': u'搜索业务执行额分析', 'headings': headings}


@data_query_super_leader_money_bp.route('/search_json', methods=['POST'])
def search_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    location = 0
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
    medium_orders = searchAdMediumOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= before_last_year_start,
        searchAdMediumOrderExecutiveReport.month_day <= now_year_end)
    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
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
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
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
    return jsonify({'data': data, 'title': u'搜索业务执行额分析'})


def client_order_excle_data():
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
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
    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
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
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
    # 格式化数据，把近三年数据放在一年用于画图
    now_monthes_data = sorted(now_monthes_data.iteritems(), key=lambda x: x[0])
    last_monthes_data = sorted(
        last_monthes_data.iteritems(), key=lambda x: x[0])
    before_monthes_data = sorted(
        before_monthes_data.iteritems(), key=lambda x: x[0])

    headings = ['月份', str(before_last_year_start.year) + u'年度',
                str(last_year_start.year) + u'年度',
                str(now_year_start.year) + u'年度']
    data = []
    data.append([str(k + 1) + u'月' for k in range(len(now_monthes_data))])
    data.append([v for k, v in before_monthes_data])
    data.append([v for k, v in last_monthes_data])
    data.append([v for k, v in now_monthes_data])
    return {'data': data, 'title': u'新媒体订单执行额分析', 'headings': headings}


@data_query_super_leader_money_bp.route('/client_order_json', methods=['POST'])
def client_order_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
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
    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
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
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
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


def douban_order_excle_data():
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
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
    douban_date = [_format_order(k, 'douban')
                   for k in douban_orders if k.status == 1]
    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
    douban_date += [{'month_day': k['month_day'], 'money':k['money'],
                     'locations':k['locations']}
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
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
    # 格式化数据，把近三年数据放在一年用于画图
    now_monthes_data = sorted(now_monthes_data.iteritems(), key=lambda x: x[0])
    last_monthes_data = sorted(
        last_monthes_data.iteritems(), key=lambda x: x[0])
    before_monthes_data = sorted(
        before_monthes_data.iteritems(), key=lambda x: x[0])

    headings = ['月份', str(before_last_year_start.year) + u'年度',
                str(last_year_start.year) + u'年度',
                str(now_year_start.year) + u'年度']
    data = []
    data.append([str(k + 1) + u'月' for k in range(len(now_monthes_data))])
    data.append([v for k, v in before_monthes_data])
    data.append([v for k, v in last_monthes_data])
    data.append([v for k, v in now_monthes_data])
    return {'data': data, 'title': u'直签豆瓣订单（含：优力、无线）执行额分析',
            'headings': headings}


@data_query_super_leader_money_bp.route('/douban_order_json', methods=['POST'])
def douban_order_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
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
    douban_date = [_format_order(k, 'douban')
                   for k in douban_orders if k.status == 1]
    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
    douban_date += [{'month_day': k['month_day'], 'money':k['money'],
                     'locations':k['locations']}
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
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in last_monthes_data:
            last_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
        if int(order['month_day'].strftime('%s')) * 1000 in before_monthes_data:
            before_monthes_data[
                int(order['month_day'].strftime('%s')) * 1000] += _get_money_by_location(order, location)
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
