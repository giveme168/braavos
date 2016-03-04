# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from models.medium import Medium

data_query_super_leader_medium_info_bp = Blueprint(
    'data_query_super_leader_medium_info', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_medium_info_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/medium_info.html',
               title=u'媒体执行额分析')


@data_query_super_leader_medium_info_bp.route('/index_json', methods=['POST'])
def index_json():
    if not g.user.is_super_leader():
        abort(403)
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

    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)

    medium_orders = [{'month_day': k.month_day,
                      'medium_name': k.order.medium.name,
                      'medium_money2': k.medium_money2,
                      } for k in medium_orders if k.status == 1]
    medium_date = [{'medium_name': k['medium_name'],
                    'money':k['medium_money2']}
                   for k in medium_orders]
    douban_date = [{'medium_name': u'豆瓣',
                    'money': k.money}
                   for k in douban_orders]

    medium_info_params = {}
    medium_info_params[u'豆瓣'] = 0
    for k in Medium.all():
        medium_info_params[k.name] = 0

    for k in medium_date+douban_date:
        if k['medium_name'] in medium_info_params:
            medium_info_params[k['medium_name']] += k['money']
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
    return jsonify({'data': data, 'title': u'媒体执行额分析',
                    'total': float(sum_saler_money)})
