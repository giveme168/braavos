# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder
from models.order import ClientOrder
from libs.date_helpers import get_monthes_pre_days

data_query_super_leader_client_info_bp = Blueprint(
    'data_query_super_leader_client_info', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_client_info_bp.route('/client_order', methods=['GET'])
def client_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/client_info.html',
               title=u'新媒体订单客户数量分析',
               type='client')


@data_query_super_leader_client_info_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/client_info.html',
               title=u'豆瓣订单客户数量分析',
               type='douban')


@data_query_super_leader_client_info_bp.route('/client_order_json', methods=['POST'])
def client_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
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
        sum_order_money = sum([i.money for i in v['orders']])
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


@data_query_super_leader_client_info_bp.route('/douban_order_json', methods=['POST'])
def douban_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
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
        sum_order_money = sum([i.money for i in v['orders']])
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
