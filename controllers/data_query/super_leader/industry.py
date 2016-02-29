# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from models.consts import CLIENT_INDUSTRY_LIST

data_query_super_leader_industry_bp = Blueprint(
    'data_query_super_leader_industry', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_industry_bp.route('/client', methods=['GET'])
def client():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/industry.html',
               title=u'新媒体订单行业分析',
               type='client')


@data_query_super_leader_industry_bp.route('/douban', methods=['GET'])
def douban():

    return tpl('/data_query/super_leader/industry.html',
               title=u'豆瓣订单行业分析',
               type='douban')


@data_query_super_leader_industry_bp.route('/client_json', methods=['POST'])
def client_json():
    now_date = datetime.datetime.now()
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

    medium_orders = [{'month_day': k.month_day, 'client_id': k.client_order.client.id,
                      'client': k.client_order.client,
                      'medium_money2': k.medium_money2,
                      } for k in medium_orders if k.status == 1]
    medium_date = [{'industry_name': CLIENT_INDUSTRY_LIST[k['client'].industry],
                    'money':k['medium_money2']}
                   for k in medium_orders]

    industry_params = {}
    for k in CLIENT_INDUSTRY_LIST:
        industry_params[k] = 0

    for k in medium_date:
        if k['industry_name'] in industry_params:
            industry_params[k['industry_name']] += k['money']
    industry_params = sorted(industry_params.iteritems(), key=lambda x: x[1])
    industry_params.reverse()
    data = [{
        "name": u"行业分析",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in industry_params])
    for k, v in industry_params:
        if sum_saler_money == 0:
            percent = u'0.00%'
        else:
            percent = '%.2f%%' % (v / sum_saler_money * 100)
        data[0]['data'].append({'name': k,
                                'y': float('%.2f' % v),
                                'percent': percent})
    return jsonify({'data': data, 'title': u'新媒体订单行业分析'})


@data_query_super_leader_industry_bp.route('/douban_json', methods=['POST'])
def douban_json():
    now_date = datetime.datetime.now()
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

    medium_orders = [{'month_day': k.month_day, 'client_id': k.client_order.client.id,
                      'client': k.client_order.client,
                      'medium_id': int(k.order.medium_id),
                      'medium_money2': k.medium_money2,
                      } for k in medium_orders if k.status == 1]
    medium_date = [{'industry_name': CLIENT_INDUSTRY_LIST[k['client'].industry],
                    'medium_id': k['medium_id'],
                    'money':k['medium_money2']}
                   for k in medium_orders if k['medium_id'] in [3, 8]]
    douban_orders = [{'month_day': k.month_day,
                      'client': k.douban_order.client,
                      'money': k.money,
                      } for k in douban_orders if k.status == 1]
    douban_date = [{'industry_name': CLIENT_INDUSTRY_LIST[k['client'].industry],
                    'money':k['money']}
                   for k in douban_orders]

    industry_params = {}
    for k in CLIENT_INDUSTRY_LIST:
        industry_params[k] = 0

    for k in douban_date + medium_date:
        if k['industry_name'] in industry_params:
            industry_params[k['industry_name']] += k['money']
    industry_params = sorted(industry_params.iteritems(), key=lambda x: x[1])
    industry_params.reverse()
    data = [{
        "name": u"行业分析",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in industry_params])
    for k, v in industry_params:
        if sum_saler_money == 0:
            percent = u'0.00%'
        else:
            percent = '%.2f%%' % (v / sum_saler_money * 100)
        data[0]['data'].append({'name': k,
                                'y': float('%.2f' % v),
                                'percent': percent})
    return jsonify({'data': data, 'title': u'新媒体订单行业分析'})
