# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from searchAd.models.order import searchAdMediumOrderExecutiveReport
from controllers.data_query.helpers.super_leader_helpers import write_pie_excel

RESOURCE_TYPE_AD = 0
RESOURCE_TYPE_CAMPAIGN = 1
RESOURCE_TYPE_FRAME = 2
RESOURCE_TYPE_OTHER = 4
RESOURCE_TYPE_CN = {
    RESOURCE_TYPE_AD: u"硬广",
    RESOURCE_TYPE_CAMPAIGN: u"互动",
    # RESOURCE_TYPE_FRAME: u"框架",
    RESOURCE_TYPE_OTHER: u"其他"
}

data_query_super_leader_sale_type_bp = Blueprint(
    'data_query_super_leader_sale_type', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_sale_type_bp.route('/client_order', methods=['GET'])
def client_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'新媒体订单售卖类型分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_pie_excel(client_order_excle_data())
    return tpl('/data_query/super_leader/sale_type.html',
               title=title,
               type='client')


@data_query_super_leader_sale_type_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'豆瓣订单售卖类型分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_pie_excel(douban_order_excle_data())
    return tpl('/data_query/super_leader/sale_type.html',
               title=title,
               type='douban')


@data_query_super_leader_sale_type_bp.route('/search', methods=['GET'])
def search():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    title = u'搜索业务售卖类型分析'
    action = request.values.get('action', '')
    if action == 'excel':
        return write_pie_excel(search_excle_data())
    return tpl('/data_query/super_leader/sale_type.html',
               title=title,
               type='search')


def _format_order(order, type='client'):
    params = {}
    params['month_day'] = order.month_day
    if type == 'client':
        params['order'] = order.client_order
        params['money'] = order.sale_money
        params['medium_id'] = order.order.medium_id
        params['direct_sales'] = order.client_order.direct_sales
        params['agent_sales'] = order.client_order.agent_sales
    else:
        params['order'] = order.douban_order
        params['money'] = order.money
        params['direct_sales'] = order.douban_order.direct_sales
        params['agent_sales'] = order.douban_order.agent_sales
    return params


def _get_money_by_location(order, location):
    if location != 0:
        if set(order['locations']) == set([location]):
            return order['money']
        else:
            # 用于查看渠道销售是否跨区
            direct_sales = order['direct_sales']
            direct_location = list(set([k['location'] for k in direct_sales]))
            # 用于查看直客销售是否跨区
            agent_sales = order['agent_sales']
            agent_location = list(set([k['location'] for k in agent_sales]))
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
    start_year = str(request.values.get('start_year', now_date.year))
    start_month = str(request.values.get('start_month', now_date.month))
    end_year = str(request.values.get('end_year', now_date.year - 1))
    end_month = str(request.values.get('end_month', now_date.month))

    start_date_month = datetime.datetime.strptime(
        start_year + '-' + start_month, '%Y-%m')
    end_date_month = datetime.datetime.strptime(
        end_year + '-' + end_month, '%Y-%m')
    medium_orders = searchAdMediumOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)

    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
    medium_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'money':_get_money_by_location(k, location)}
                   for k in medium_orders]
    sale_type_params = {
        u'硬广': 0,
        u'互动': 0,
        u'其他': 0,
    }

    for k in medium_date:
        if k['sale_type_name'] in sale_type_params:
            sale_type_params[k['sale_type_name']] += k['money']
    sale_type_params = sorted(sale_type_params.iteritems(), key=lambda x: x[1])
    sale_type_params.reverse()

    headings = ['#', u'售卖类型', u'执行额', u'占比']
    data = []
    data.append([k + 1 for k in range(len(sale_type_params))])
    data.append([k for k, v in sale_type_params])
    data.append([v for k, v in sale_type_params])
    sum_saler_money = sum([v for k, v in sale_type_params])
    if sum_saler_money:
        data.append(['%.2f%%' % (v / sum_saler_money * 100)
                     for k, v in sale_type_params])
    else:
        data.append(['0.00%' for k, v in sale_type_params])
    return {'data': data, 'title': u'搜索业务售卖类型分析',
            'total': float(sum_saler_money), 'headings': headings}


@data_query_super_leader_sale_type_bp.route('/search_json', methods=['POST'])
def search_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    location = 0
    start_year = str(request.values.get('start_year', now_date.year))
    start_month = str(request.values.get('start_month', now_date.month))
    end_year = str(request.values.get('end_year', now_date.year - 1))
    end_month = str(request.values.get('end_month', now_date.month))

    start_date_month = datetime.datetime.strptime(
        start_year + '-' + start_month, '%Y-%m')
    end_date_month = datetime.datetime.strptime(
        end_year + '-' + end_month, '%Y-%m')
    medium_orders = searchAdMediumOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)

    medium_orders = [_format_order(k) for k in medium_orders if k.status == 1]
    medium_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'money':_get_money_by_location(k, location)}
                   for k in medium_orders]
    sale_type_params = {
        u'硬广': 0,
        u'互动': 0,
        u'其他': 0,
    }

    for k in medium_date:
        if k['sale_type_name'] in sale_type_params:
            sale_type_params[k['sale_type_name']] += k['money']
    sale_type_params = sorted(sale_type_params.iteritems(), key=lambda x: x[1])
    sale_type_params.reverse()
    data = [{
        "name": u"占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in sale_type_params])
    for k, v in sale_type_params:
        if sum_saler_money == 0:
            percent = u'0.00%'
        else:
            percent = v / sum_saler_money * 100
        data[0]['data'].append({'name': k,
                                'y': v,
                                'percent': percent})
    return jsonify({'data': data, 'title': u'搜索业务售卖类型分析',
                    'total': float(sum_saler_money)})


def client_order_excle_data():
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
    medium_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'money':_get_money_by_location(k, location)}
                   for k in medium_orders]
    sale_type_params = {
        u'硬广': 0,
        u'互动': 0,
        u'其他': 0,
    }

    for k in medium_date:
        if k['sale_type_name'] in sale_type_params:
            sale_type_params[k['sale_type_name']] += k['money']
    sale_type_params = sorted(sale_type_params.iteritems(), key=lambda x: x[1])
    sale_type_params.reverse()

    headings = ['#', u'售卖类型', u'执行额', u'占比']
    data = []
    data.append([k + 1 for k in range(len(sale_type_params))])
    data.append([k for k, v in sale_type_params])
    data.append([v for k, v in sale_type_params])
    sum_saler_money = sum([v for k, v in sale_type_params])
    if sum_saler_money:
        data.append(['%.2f%%' % (v / sum_saler_money * 100)
                     for k, v in sale_type_params])
    else:
        data.append(['0.00%' for k, v in sale_type_params])
    return {'data': data, 'title': u'新媒体订单售卖类型分析',
            'total': float(sum_saler_money), 'headings': headings}


@data_query_super_leader_sale_type_bp.route('/client_order_json', methods=['POST'])
def client_order_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
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
    medium_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'money':_get_money_by_location(k, location)}
                   for k in medium_orders]
    sale_type_params = {
        u'硬广': 0,
        u'互动': 0,
        u'其他': 0,
    }

    for k in medium_date:
        if k['sale_type_name'] in sale_type_params:
            sale_type_params[k['sale_type_name']] += k['money']
    sale_type_params = sorted(sale_type_params.iteritems(), key=lambda x: x[1])
    sale_type_params.reverse()
    data = [{
        "name": u"占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in sale_type_params])
    for k, v in sale_type_params:
        if sum_saler_money == 0:
            percent = u'0.00%'
        else:
            percent = v / sum_saler_money * 100
        data[0]['data'].append({'name': k,
                                'y': v,
                                'percent': percent})
    return jsonify({'data': data, 'title': u'新媒体订单售卖类型分析',
                    'total': float(sum_saler_money)})


def douban_order_excle_data():
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
    medium_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'medium_id': k['medium_id'],
                    'money': _get_money_by_location(k, location)}
                   for k in medium_orders if k['medium_id'] in [3, 8]]
    douban_orders = [_format_order(k, 'douban')
                     for k in douban_orders if k.status == 1]
    douban_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'money':_get_money_by_location(k, location)}
                   for k in douban_orders]
    sale_type_params = {
        u'硬广': 0,
        u'互动': 0,
        u'其他': 0,
    }

    for k in douban_date + medium_date:
        if k['sale_type_name'] in sale_type_params:
            sale_type_params[k['sale_type_name']] += k['money']
    sale_type_params = sorted(sale_type_params.iteritems(), key=lambda x: x[1])
    sale_type_params.reverse()

    headings = ['#', u'售卖类型', u'执行额', u'占比']
    data = []
    data.append([k + 1 for k in range(len(sale_type_params))])
    data.append([k for k, v in sale_type_params])
    data.append([v for k, v in sale_type_params])
    sum_saler_money = sum([v for k, v in sale_type_params])
    if sum_saler_money:
        data.append(['%.2f%%' % (v / sum_saler_money * 100)
                     for k, v in sale_type_params])
    else:
        data.append(['0.00%' for k, v in sale_type_params])
    return {'data': data, 'title': u'直签豆瓣订单（含：优力、无线）售卖类型分析',
            'total': float(sum_saler_money), 'headings': headings}


@data_query_super_leader_sale_type_bp.route('/douban_order_json', methods=['POST'])
def douban_order_json():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
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
    medium_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'medium_id': k['medium_id'],
                    'money': _get_money_by_location(k, location)}
                   for k in medium_orders if k['medium_id'] in [3, 8]]
    douban_orders = [_format_order(k, 'douban')
                     for k in douban_orders if k.status == 1]
    douban_date = [{'sale_type_name': RESOURCE_TYPE_CN.get(k['order'].sale_type),
                    'money':_get_money_by_location(k, location)}
                   for k in douban_orders]

    sale_type_params = {
        u'硬广': 0,
        u'互动': 0,
        u'其他': 0,
    }

    for k in douban_date + medium_date:
        if k['sale_type_name'] in sale_type_params:
            sale_type_params[k['sale_type_name']] += k['money']
    sale_type_params = sorted(sale_type_params.iteritems(), key=lambda x: x[1])
    sale_type_params.reverse()
    data = [{
        "name": u"占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in sale_type_params])
    for k, v in sale_type_params:
        if sum_saler_money == 0:
            percent = u'0.00%'
        else:
            percent = v / sum_saler_money * 100
        data[0]['data'].append({'name': k,
                                'y': v,
                                'percent': percent})
    return jsonify({'data': data, 'title': u'直签豆瓣订单（含：优力、无线）售卖类型分析',
                    'total': float(sum_saler_money)})
