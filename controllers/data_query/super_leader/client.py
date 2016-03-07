# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort, json
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from models.client import Client

data_query_super_leader_client_bp = Blueprint(
    'data_query_super_leader_client', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_client_bp.route('/client_order', methods=['GET'])
def client_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/client.html',
               title=u'新媒体订单客户分析',
               type='client')


@data_query_super_leader_client_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/client.html',
               title=u'豆瓣订单客户分析',
               type='douban')


def _format_order(order, type='client'):
    params = {}
    params['month_day'] = order.month_day
    if type == 'client':
        params['client'] = order.client_order.client
        params['money'] = order.medium_money2
        params['medium_id'] = order.order.medium_id
    else:
        params['client'] = order.douban_order.client
        params['money'] = order.money
    params['order_json'] = json.loads(order.order_json)
    params['locations'] = params['order_json']['locations']
    return params


def _get_money_by_location(order, location):
    if location != 0:
        if set(order['locations']) == set([location]):
            return order['money']
        else:
            # 用于查看渠道销售是否跨区
            direct_sales = order['order_json']['direct_sales']
            direct_location = list(set([k['location'] for k in direct_sales]))
            # 用于查看直客销售是否跨区
            agent_sales = order['order_json']['agent_sales']
            agent_location = list(set([k['location'] for k in agent_sales]))
            money = 0
            if location in direct_location:
                money += float(order['money']) / len(direct_location)
            if location in agent_location:
                money += float(order['money']) / len(agent_location)
            return money
    return order['money']


@data_query_super_leader_client_bp.route('/client_order_json', methods=['POST'])
def client_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
    start_year = str(request.values.get('start_year', now_date.year))
    start_month = str(request.values.get('start_month', now_date.month))
    end_year = str(request.values.get('end_year', now_date.year - 1))
    end_month = str(request.values.get('end_month', now_date.month))

    start_date_month = datetime.datetime.strptime(
        start_year + '-' + start_month, '%Y-%m')
    end_date_month = datetime.datetime.strptime(
        end_year + '-' + end_month, '%Y-%m')
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)

    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
    medium_date = [{'client_name': k['client'].name,
                    'money': _get_money_by_location(k, location)}
                   for k in medium_orders]

    client_params = {}
    for k in Client.all():
        client_params[k.name] = 0

    for k in medium_date:
        if k['client_name'] in client_params:
            client_params[k['client_name']] += k['money']
    client_params = sorted(client_params.iteritems(), key=lambda x: x[1])
    client_params.reverse()
    data = [{
        "name": u"占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in client_params])
    for k, v in client_params:
        if v > 0:
            if sum_saler_money == 0:
                percent = u'0.00%'
            else:
                percent = v / sum_saler_money * 100
            data[0]['data'].append({'name': k,
                                    'y': v,
                                    'percent': percent})
    return jsonify({'data': data, 'title': u'新媒体订单客户分析',
                    'total': float(sum_saler_money)})


@data_query_super_leader_client_bp.route('/douban_order_json', methods=['POST'])
def douban_order_json():
    if not g.user.is_super_leader():
        abort(403)
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
    start_year = str(request.values.get('start_year', now_date.year))
    start_month = str(request.values.get('start_month', now_date.month))
    end_year = str(request.values.get('end_year', now_date.year - 1))
    end_month = str(request.values.get('end_month', now_date.month))

    start_date_month = datetime.datetime.strptime(
        start_year + '-' + start_month, '%Y-%m')
    end_date_month = datetime.datetime.strptime(
        end_year + '-' + end_month, '%Y-%m')
    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)

    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
    medium_date = [{'client_name': k['client'].name,
                    'medium_id': k['medium_id'],
                    'money':_get_money_by_location(k, location)}
                   for k in medium_orders if k['medium_id'] in [3, 8]]
    douban_orders = [_format_order(k, 'douban')
                     for k in douban_orders if k.status == 1]
    douban_date = [{'client_name': k['client'].name,
                    'money':_get_money_by_location(k, location)}
                   for k in douban_orders]

    client_params = {}
    for k in Client.all():
        client_params[k.name] = 0

    for k in douban_date + medium_date:
        if k['client_name'] in client_params:
            client_params[k['client_name']] += k['money']
    client_params = sorted(client_params.iteritems(), key=lambda x: x[1])
    client_params.reverse()
    data = [{
        "name": u"占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in client_params])
    for k, v in client_params:
        if v > 0:
            if sum_saler_money == 0:
                percent = u'0.00%'
            else:
                percent = v / sum_saler_money * 100
            data[0]['data'].append({'name': k,
                                    'y': v,
                                    'percent': percent})
    return jsonify({'data': data, 'title': u'直签豆瓣订单（含：优力、无线）客户分析',
                    'total': float(sum_saler_money)})
