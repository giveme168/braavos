# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort, json
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from models.medium import Medium

from searchAd.models.order import searchAdMediumOrderExecutiveReport
from searchAd.models.medium import searchAdMedium

data_query_super_leader_medium_info_bp = Blueprint(
    'data_query_super_leader_medium_info', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_medium_info_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/medium_info.html',
               title=u'媒体执行额分析',
               type="zhiqu")


@data_query_super_leader_medium_info_bp.route('/search', methods=['GET'])
def search():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/medium_info.html',
               title=u'搜索业务媒体执行额分析',
               type="search")


def _format_order(order, type='client'):
    params = {}
    params['month_day'] = order.month_day
    if type == 'client':
        params['money'] = order.medium_money2
        params['medium_id'] = order.order.medium_id
        params['medium_name'] = order.order.medium.name
    else:
        params['money'] = order.money
        params['medium_name'] = u'豆瓣'
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


@data_query_super_leader_medium_info_bp.route('/search_json', methods=['POST'])
def search_json():
    if not g.user.is_super_leader():
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

    medium_date = [_format_order(k) for k in medium_orders if k.status == 1]

    medium_info_params = {}
    for k in searchAdMedium.all():
        medium_info_params[k.name] = 0
    for k in medium_date:
        if k['medium_name'] in medium_info_params:
            medium_info_params[k['medium_name']] += _get_money_by_location(k, location)
    medium_info_params = sorted(
        medium_info_params.iteritems(), key=lambda x: x[1])
    medium_info_params.reverse()
    data = [{
        "name": u"媒体执行额占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in medium_info_params])
    for k, v in medium_info_params:
        if v > 0:
            if sum_saler_money == 0:
                percent = u'0.00%'
            else:
                percent = v / sum_saler_money * 100
            data[0]['data'].append({'name': k,
                                    'y': v,
                                    'percent': percent})
    return jsonify({'data': data, 'title': u'搜索业务媒体执行额分析',
                    'total': float(sum_saler_money)})


@data_query_super_leader_medium_info_bp.route('/index_json', methods=['POST'])
def index_json():
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

    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)

    medium_date = [_format_order(k) for k in medium_orders if k.status == 1]
    douban_date = [_format_order(k, 'douban') for k in douban_orders]

    medium_info_params = {}
    medium_info_params[u'豆瓣'] = 0
    for k in Medium.all():
        medium_info_params[k.name] = 0

    for k in medium_date + douban_date:
        if k['medium_name'] in medium_info_params:
            medium_info_params[k['medium_name']] += _get_money_by_location(k, location)
    medium_info_params = sorted(
        medium_info_params.iteritems(), key=lambda x: x[1])
    medium_info_params.reverse()
    data = [{
        "name": u"媒体执行额占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in medium_info_params])
    for k, v in medium_info_params:
        if v > 0:
            if sum_saler_money == 0:
                percent = u'0.00%'
            else:
                percent = v / sum_saler_money * 100
            data[0]['data'].append({'name': k,
                                    'y': v,
                                    'percent': percent})
    return jsonify({'data': data, 'title': u'致趣媒体执行额分析',
                    'total': float(sum_saler_money)})
