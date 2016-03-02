# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, jsonify, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from models.client import Agent

data_query_super_leader_agent_bp = Blueprint(
    'data_query_super_leader_agent', __name__, template_folder='../../templates/data_query')


@data_query_super_leader_agent_bp.route('/client_order', methods=['GET'])
def client_order():
    if not g.user.is_super_leader():
        abort(403)
    return tpl('/data_query/super_leader/agent.html',
               title=u'新媒体订单代理分析',
               type='client')


@data_query_super_leader_agent_bp.route('/douban_order', methods=['GET'])
def douban_order():

    return tpl('/data_query/super_leader/agent.html',
               title=u'豆瓣订单代理分析',
               type='douban')


@data_query_super_leader_agent_bp.route('/client_order_json', methods=['POST'])
def client_order_json():
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

    medium_orders = [{'month_day': k.month_day,
                      'agent_id': k.client_order.agent.id,
                      'agent': k.client_order.agent,
                      'medium_money2': k.medium_money2,
                      } for k in medium_orders if k.status == 1]
    medium_date = [{'agent_name': k['agent'].name,
                    'money':k['medium_money2']}
                   for k in medium_orders]

    agent_params = {}
    for k in Agent.all():
        agent_params[k.name] = 0

    for k in medium_date:
        if k['agent_name'] in agent_params:
            agent_params[k['agent_name']] += k['money']
    agent_params = sorted(agent_params.iteritems(), key=lambda x: x[1])
    agent_params.reverse()
    data = [{
        "name": u"占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in agent_params])
    for k, v in agent_params:
        if v > 0:
            if sum_saler_money == 0:
                percent = u'0.00%'
            else:
                percent = '%.2f%%' % (v / sum_saler_money * 100)
            data[0]['data'].append({'name': k,
                                    'y': float('%.2f' % v),
                                    'percent': percent})
    return jsonify({'data': data, 'title': u'新媒体订单代理分析',
                    'total': float('%.2f' % sum_saler_money)})


@data_query_super_leader_agent_bp.route('/douban_order_json', methods=['POST'])
def douban_order_json():
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

    medium_orders = [{'month_day': k.month_day,
                      'agent_id': k.client_order.agent.id,
                      'agent': k.client_order.agent,
                      'medium_id': int(k.order.medium_id),
                      'medium_money2': k.medium_money2,
                      } for k in medium_orders if k.status == 1]
    medium_date = [{'agent_name': k['agent'].name,
                    'medium_id': k['medium_id'],
                    'money':k['medium_money2']}
                   for k in medium_orders if k['medium_id'] in [3, 8]]
    douban_orders = [{'month_day': k.month_day,
                      'agent': k.douban_order.agent,
                      'money': k.money,
                      } for k in douban_orders if k.status == 1]
    douban_date = [{'agent_name': k['agent'].name,
                    'money':k['money']}
                   for k in douban_orders]

    agent_params = {}
    for k in Agent.all():
        agent_params[k.name] = 0

    for k in douban_date + medium_date:
        if k['agent_name'] in agent_params:
            agent_params[k['agent_name']] += k['money']
    agent_params = sorted(agent_params.iteritems(), key=lambda x: x[1])
    agent_params.reverse()
    data = [{
        "name": u"占比",
        "data": []
    }]
    sum_saler_money = sum([v for k, v in agent_params])
    for k, v in agent_params:
        if v > 0:
            if sum_saler_money == 0:
                percent = u'0.00%'
            else:
                percent = '%.2f%%' % (v / sum_saler_money * 100)
            data[0]['data'].append({'name': k,
                                    'y': float('%.2f' % v),
                                    'percent': percent})
    return jsonify({'data': data, 'title': u'直签豆瓣订单（含：优力、无线）代理分析',
                    'total': float('%.2f' % sum_saler_money)})
