# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder
from models.order import ClientOrder
from searchAd.models.client_order import searchAdClientOrder
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.super_leader_helpers import write_line_excel

data_query_super_leader_client_info_bp = Blueprint(
    'data_query_super_leader_client_info', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_client_info_bp.route('/client_order', methods=['GET'])
def client_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'新媒体订单客户数量分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_line_excel(client_order_excle_data())
    return tpl('/data_query/super_leader/client_info.html',
               title=title,
               type='client')


@data_query_super_leader_client_info_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'豆瓣订单客户数量分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_line_excel(douban_order_excle_data())
    return tpl('/data_query/super_leader/client_info.html',
               title=title,
               type='douban')


@data_query_super_leader_client_info_bp.route('/search', methods=['GET'])
def search():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'搜索业务客户数量分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_line_excel(search_excle_data())
    return tpl('/data_query/super_leader/client_info.html',
               title=title,
               type='search')


def _get_money_by_location(order, location):
    if location != 0:
        if set(order.locations) == set([location]):
            return order.money
        else:
            # 用于查看渠道销售是否跨区
            direct_sales = order.direct_sales
            direct_location = list(set([k.team.location for k in direct_sales]))
            # 用于查看直客销售是否跨区
            agent_sales = order.agent_sales
            agent_location = list(set([k.team.location for k in agent_sales]))
            money = 0
            if location in direct_location:
                money += float(order.money) / len(direct_location)
            if location in agent_location:
                money += float(order.money) / len(agent_location)
            return money
    return order.money


def search_excle_data():
    now_date = datetime.datetime.now()
    location = 0
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'orders': [],
                                            'order_count': 0,
                                            'order_pre_money': 0}
    # 获取所有合同
    orders = searchAdClientOrder.all()
    for k in orders:
        if k.contract_status in [2, 4, 5, 19, 20]:
            create_month = k.client_start.replace(day=1)
            if create_month in client_params:
                if location == 0:
                    client_params[create_month]['orders'].append(k)
                elif location in k.locations:
                    client_params[create_month]['orders'].append(k)
    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])

    headings = [u'月份', u'成单客户数', u'平均客户金额']
    data = []
    data.append([str(k + 1) + u'月' for k in range(len(client_params))])

    # 成单客户数
    count_client = []
    # 平均客户金额
    pre_money_client = []
    for k, v in client_params:
        order_count = len(v['orders'])
        sum_order_money = sum([_get_money_by_location(i, location) for i in v['orders']])
        if order_count:
            order_pre_money = sum_order_money / order_count
        else:
            order_pre_money = 0
        count_client.append(order_count)
        pre_money_client.append(order_pre_money)
    data.append(count_client)
    data.append(pre_money_client)
    return {'data': data, 'title': u'搜索业务客户数量分析', 'headings': headings}


@data_query_super_leader_client_info_bp.route('/search_json', methods=['POST'])
def search_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    location = 0
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'orders': [],
                                            'order_count': 0,
                                            'order_pre_money': 0}
    # 获取所有合同
    orders = searchAdClientOrder.all()
    for k in orders:
        if k.contract_status in [2, 4, 5, 19, 20]:
            create_month = k.client_start.replace(day=1)
            if create_month in client_params:
                if location == 0:
                    client_params[create_month]['orders'].append(k)
                elif location in k.locations:
                    client_params[create_month]['orders'].append(k)
    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])
    # 初始化highcharts数据
    data = []
    data.append({'name': u'客户成交数量',
                 'data': []})
    data.append({'name': u'客户平均成交额',
                 'data': []})
    # 根据时间组装合同
    for k, v in client_params:
        order_count = len(v['orders'])
        sum_order_money = sum([_get_money_by_location(i, location) for i in v['orders']])
        if order_count:
            order_pre_money = sum_order_money / order_count
        else:
            order_pre_money = 0
        # 主装highcharts数据
        day_time_stamp = int(datetime.datetime.strptime(
            str(k), '%Y-%m-%d').strftime('%s')) * 1000
        data[0]['data'].append([day_time_stamp, order_count])
        data[1]['data'].append([day_time_stamp, order_pre_money])
    return jsonify({'data': data, 'title': u'搜索业务客户数量分析'})


def client_order_excle_data():
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'orders': [],
                                            'order_count': 0,
                                            'order_pre_money': 0}
    # 获取所有合同
    orders = ClientOrder.all()
    for k in orders:
        if k.contract_status in [2, 4, 5, 19, 20]:
            create_month = k.client_start.replace(day=1)
            if create_month in client_params:
                if location == 0:
                    client_params[create_month]['orders'].append(k)
                elif location in k.locations:
                    client_params[create_month]['orders'].append(k)
    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])

    headings = [u'月份', u'成单客户数', u'平均客户金额']
    data = []
    data.append([str(k + 1) + u'月' for k in range(len(client_params))])

    # 成单客户数
    count_client = []
    # 平均客户金额
    pre_money_client = []
    for k, v in client_params:
        order_count = len(v['orders'])
        sum_order_money = sum([_get_money_by_location(i, location) for i in v['orders']])
        if order_count:
            order_pre_money = sum_order_money / order_count
        else:
            order_pre_money = 0
        count_client.append(order_count)
        pre_money_client.append(order_pre_money)
    data.append(count_client)
    data.append(pre_money_client)
    return {'data': data, 'title': u'新媒体订单客户数量分析', 'headings': headings}


@data_query_super_leader_client_info_bp.route('/client_order_json', methods=['POST'])
def client_order_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'orders': [],
                                            'order_count': 0,
                                            'order_pre_money': 0}
    # 获取所有合同
    orders = ClientOrder.all()
    for k in orders:
        if k.contract_status in [2, 4, 5, 19, 20]:
            create_month = k.client_start.replace(day=1)
            if create_month in client_params:
                if location == 0:
                    client_params[create_month]['orders'].append(k)
                elif location in k.locations:
                    client_params[create_month]['orders'].append(k)
    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])
    # 初始化highcharts数据
    data = []
    data.append({'name': u'客户成交数量',
                 'data': []})
    data.append({'name': u'客户平均成交额',
                 'data': []})
    # 根据时间组装合同
    for k, v in client_params:
        order_count = len(v['orders'])
        sum_order_money = sum([_get_money_by_location(i, location) for i in v['orders']])
        if order_count:
            order_pre_money = sum_order_money / order_count
        else:
            order_pre_money = 0
        # 主装highcharts数据
        day_time_stamp = int(datetime.datetime.strptime(
            str(k), '%Y-%m-%d').strftime('%s')) * 1000
        data[0]['data'].append([day_time_stamp, order_count])
        data[1]['data'].append([day_time_stamp, order_pre_money])
    return jsonify({'data': data, 'title': u'新媒体订单客户数量分析'})


def douban_order_excle_data():
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'orders': [],
                                            'order_count': 0,
                                            'order_pre_money': 0}
    # 获取所有合同
    orders = DoubanOrder.all()
    for k in orders:
        if k.contract_status in [2, 4, 5, 19, 20]:
            create_month = k.client_start.replace(day=1)
            if create_month in client_params:
                if location == 0:
                    client_params[create_month]['orders'].append(k)
                elif location in k.locations:
                    client_params[create_month]['orders'].append(k)
    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])

    headings = [u'月份', u'成单客户数', u'平均客户金额']
    data = []
    data.append([str(k + 1) + u'月' for k in range(len(client_params))])

    # 成单客户数
    count_client = []
    # 平均客户金额
    pre_money_client = []
    for k, v in client_params:
        order_count = len(v['orders'])
        sum_order_money = sum([_get_money_by_location(i, location) for i in v['orders']])
        if order_count:
            order_pre_money = sum_order_money / order_count
        else:
            order_pre_money = 0
        count_client.append(order_count)
        pre_money_client.append(order_pre_money)
    data.append(count_client)
    data.append(pre_money_client)
    return {'data': data, 'title': u'直签豆瓣订单客户数量分析', 'headings': headings}


@data_query_super_leader_client_info_bp.route('/douban_order_json', methods=['POST'])
def douban_order_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
    year = int(request.values.get('year', now_date.year))
    now_year_start = datetime.datetime.strptime(
        str(year) + '-01-01', '%Y-%m-%d')
    now_year_end = datetime.datetime.strptime(str(year) + '-12-01', '%Y-%m-%d')
    client_params = {}
    now_monthes = get_monthes_pre_days(now_year_start, now_year_end)
    for k in now_monthes:
        client_params[k['month'].date()] = {'orders': [],
                                            'order_count': 0,
                                            'order_pre_money': 0}
    # 获取所有合同
    orders = DoubanOrder.all()
    for k in orders:
        if k.contract_status in [2, 4, 5, 19, 20]:
            create_month = k.client_start.replace(day=1)
            if create_month in client_params:
                if location == 0:
                    client_params[create_month]['orders'].append(k)
                elif location in k.locations:
                    client_params[create_month]['orders'].append(k)
    client_params = sorted(
        client_params.iteritems(), key=lambda x: x[0])
    # 初始化highcharts数据
    data = []
    data.append({'name': u'客户成交数量',
                 'data': []})
    data.append({'name': u'客户平均成交额',
                 'data': []})
    # 根据时间组装合同
    for k, v in client_params:
        order_count = len(v['orders'])
        sum_order_money = sum([_get_money_by_location(i, location) for i in v['orders']])
        if order_count:
            order_pre_money = sum_order_money / order_count
        else:
            order_pre_money = 0
        # 主装highcharts数据
        day_time_stamp = int(datetime.datetime.strptime(
            str(k), '%Y-%m-%d').strftime('%s')) * 1000
        data[0]['data'].append([day_time_stamp, order_count])
        data[1]['data'].append([day_time_stamp, order_pre_money])
    return jsonify({'data': data, 'title': u'直签豆瓣订单客户数量分析'})
