# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, g
from flask import render_template as tpl

from models.user import TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN
from models.client_order import ClientOrderExecutiveReport
from models.douban_order import DoubanOrderExecutiveReport
from models.medium import Medium
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q,
                               get_last_year_month_by_Q, get_after_year_month_by_Q)
from controllers.data_query.helpers.weekly_helpers import write_client_excel


data_query_weekly_bp = Blueprint(
    'data_query_weekly', __name__, template_folder='../../templates/data_query')


# 整理单个销售报表数据
def _executive_report(order, user, now_year, monthes, sale_type):
    if len(set(order['locations'])) > 1:
        l_count = len(set(order['locations']))
    else:
        l_count = 1
    if sale_type == 'agent':
        count = len(order['agent_sales'])
    else:
        count = len(order['direct_sales'])
    if user['location'] == 3 and len(order['locations']) > 1:
        if sale_type == 'agent':
            count = len(order['agent_sales'])
        else:
            count = len(order['direct_sales'])
    elif user['location'] == 3 and len(order['locations']) == 1:
        count = len(order['agent_sales'] + order['direct_sales'])
    if sale_type == 'normal':
        count = 1
    pre_reports = order['executive_report_data']
    moneys = []
    for j in monthes:
        for r in pre_reports:
            if r['month_day'].date() == datetime.datetime(int(now_year), int(j), 1).date():
                pre_money = r['money']
                break
            else:
                pre_money = 0
        try:
            moneys.append(round(pre_money / count / l_count, 2))
        except:
            moneys.append(0)
    return moneys


def _get_report_by_user(user, client_orders, now_year, now_Q, Q_monthes, type='agent'):
    last_year, last_month = get_last_year_month_by_Q(now_year, now_Q)
    after_year, after_month = get_after_year_month_by_Q(now_year, now_Q)
    orders = []
    for order in client_orders:
        if type == 'agent':
            if user['id'] not in [k['id'] for k in order['agent_sales']]:
                order = None
        else:
            if len(order['locations']) > 1:
                if user['id'] not in [k['id'] for k in order['direct_sales']]:
                    order = None
            else:
                if user['location'] == 3:
                    if user['id'] not in [k['id'] for k in order['direct_sales']]:
                        order = None
                else:
                    if not (user['id'] in [k['id'] for k in order['direct_sales']] and len(order['agent_sales']) == 0):
                        order = None
        if order:
            moneys = _executive_report(order, user, now_year, Q_monthes, type)
            now_Q_money = sum(moneys)
            last_Q_money = sum(
                _executive_report(order, user, last_year, last_month, type))
            after_Q_money = sum(
                _executive_report(order, user, after_year, after_month, type))
            orders.append({'order': order, 'moneys': moneys, 'now_Q_money': now_Q_money,
                           'after_Q_money': after_Q_money, 'last_Q_money': last_Q_money})
    return orders


def _get_salers_user_by_location(client_orders, location, type='agent'):
    salers = []
    for k in client_orders:
        if type == 'agent':
            salers += [u for u in k['agent_sales'] if u['location'] == location]
        else:
            if len(k['locations']) > 1:
                salers += [u for u in k['direct_sales']
                           if u['location'] == location]
            else:
                if int(location) == 3:
                    salers += [u for u in k['direct_sales'] if u['location'] ==
                               location]
                else:
                    salers += [u for u in k['direct_sales'] if u['location'] ==
                               location and len(k['agent_sales']) == 0]
    f = lambda x, y: x if y in x else x + [y]
    set_orders = reduce(f, [[], ] + salers)
    return set_orders


def _get_report_total(saler_orders, now_year, Q_monthes, type='client_order', saler_type='agent'):
    for k in saler_orders:
        if saler_type == 'agent':
            k['total_order_money'] = sum(
                [order['order']['zhixing_money'][0] for order in k['orders']])
        else:
            k['total_order_money'] = sum(
                [order['order']['zhixing_money'][1] for order in k['orders']])
        k['total_now_Q_money'] = sum(
            [order['now_Q_money'] for order in k['orders']])
        k['total_last_Q_money'] = sum(
            [order['last_Q_money'] for order in k['orders']])
        k['total_after_Q_money'] = sum(
            [order['after_Q_money'] for order in k['orders']])
        k['total_frist_month_money'] = sum(
            [order['moneys'][0] for order in k['orders']])
        k['total_second_month_money'] = sum(
            [order['moneys'][1] for order in k['orders']])
        k['total_third_month_money'] = sum(
            [order['moneys'][2] for order in k['orders']])
        if type == 'client_order':
            k['total_order_invoice'] = sum(
                [order['order']['invoice_pass_sum'] for order in k['orders']])
            if saler_type == 'agent':
                k['total_order_mediums_money2'] = sum(
                    [order['order']['zhixing_medium_money2'][0] for order in k['orders']])
            else:
                k['total_order_mediums_money2'] = sum(
                    [order['order']['zhixing_medium_money2'][1] for order in k['orders']])
            k['total_frist_medium_money2_by_month'] = 0
            k['total_second_medium_money2_by_month'] = 0
            k['total_third_medium_money2_by_month'] = 0
            k['total_frist_saler_money_by_month'] = 0
            k['total_second_saler_money_by_month'] = 0
            k['total_third_saler_money_by_month'] = 0
            k['total_frist_douban_money_by_month'] = 0
            k['total_second_douban_money_by_month'] = 0
            k['total_third_douban_money_by_month'] = 0
            for i in range(len(Q_monthes)):
                if saler_type == 'agent':
                    total_medium_money2 = sum([order['order']['medium_money_by_month'][i][
                                              0]['medium_money2'] for order in k['orders']])
                    sale_money = sum([order['order']['medium_money_by_month'][i][
                                     0]['sale_money'] for order in k['orders']])
                    douban_money = sum(
                        [order['order']['associated_douban_pro_month_money'][i][0] for order in k['orders']])
                else:
                    total_medium_money2 = sum([order['order']['medium_money_by_month'][i][
                                              1]['medium_money2'] for order in k['orders']])
                    sale_money = sum([order['order']['medium_money_by_month'][i][
                                     1]['sale_money'] for order in k['orders']])
                    douban_money = sum(
                        [order['order']['associated_douban_pro_month_money'][i][1] for order in k['orders']])
                if i == 0:
                    k['total_frist_medium_money2_by_month'] += total_medium_money2
                    k['total_frist_saler_money_by_month'] += sale_money
                    k['total_frist_douban_money_by_month'] += douban_money
                elif i == 1:
                    k['total_second_medium_money2_by_month'] += total_medium_money2
                    k['total_second_saler_money_by_month'] += sale_money
                    k['total_second_douban_money_by_month'] += douban_money
                elif i == 2:
                    k['total_third_medium_money2_by_month'] += total_medium_money2
                    k['total_third_saler_money_by_month'] += sale_money
                    k['total_third_douban_money_by_month'] += douban_money
    return saler_orders


@data_query_weekly_bp.route('/douban', methods=['GET'])
def douban_index():
    now_year = request.values.get('year', '')
    now_Q = request.values.get('Q', '')
    location_id = int(request.values.get('location_id', 0))
    if not now_year and not now_Q:
        now_date = datetime.date.today()
        now_year = now_date.strftime('%Y')
        now_month = now_date.strftime('%m')
        now_Q = check_month_get_Q(now_month)
    Q_monthes = check_Q_get_monthes(now_Q)

    start_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[0]), 1).date()
    end_Q_month = datetime.datetime(int(now_year), int(Q_monthes[-1]), 1).date()

    douban_orders = list(set([report.douban_order for report in DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_Q_month, DoubanOrderExecutiveReport.month_day <= end_Q_month)
        if report.douban_order.status == 1]))
    douban_orders = [
        _douban_order_to_dict(k, now_year, Q_monthes) for k in douban_orders if k.contract_status not in [7, 8, 9]]
    if g.user.is_contract() or g.user.is_media() or g.user.is_super_leader() or \
            g.user.is_finance() or g.user.is_media_leader():
        douban_orders = douban_orders
    elif g.user.is_leader():
        douban_orders = [
            o for o in douban_orders if g.user.location in o['locations']]
    else:
        douban_orders = [
            o for o in douban_orders if (g.user.id in o['salers_ids']) or (g.user.id in o['get_saler_leaders'])]
    huabei_agent_salers = []
    huabei_direct_salers = []
    huanan_agent_salers = []
    huanan_direct_salers = []
    huadong_agent_salers = []
    huadong_direct_salers = []
    if location_id == 0:
        huabei_agent_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUABEI)
        huabei_direct_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUABEI, 'direct')
        huanan_agent_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUANAN)
        huanan_direct_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUANAN, 'direct')
        huadong_agent_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUADONG)
        huadong_direct_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUADONG, 'direct')
    elif location_id == 1:
        huabei_agent_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUABEI)
        huabei_direct_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUABEI, 'direct')
    elif location_id == 2:
        huadong_agent_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUADONG)
        huadong_direct_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUADONG, 'direct')
    elif location_id == 3:
        huanan_agent_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUANAN)
        huanan_direct_salers = _get_salers_user_by_location(
            douban_orders, TEAM_LOCATION_HUANAN, 'direct')

    huabei_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huabei_agent_salers]
    huabei_agent_salers_orders = _get_report_total(
        huabei_agent_saler_orders, now_year, Q_monthes, 'douban_order', 'agent')
    huabei_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huabei_direct_salers]
    huabei_direct_salers_orders = _get_report_total(
        huabei_agent_saler_orders, now_year, Q_monthes, 'douban_order', 'direct')
    huanan_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huanan_agent_salers]
    huanan_agent_salers_orders = _get_report_total(
        huanan_agent_saler_orders, now_year, Q_monthes, 'douban_order', 'agent')
    huanan_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huanan_direct_salers]
    huanan_direct_salers_orders = _get_report_total(
        huanan_direct_saler_orders, now_year, Q_monthes, 'douban_order', 'direct')
    huadong_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huadong_agent_salers]
    huadong_agent_salers_orders = _get_report_total(
        huadong_agent_saler_orders, now_year, Q_monthes, 'douban_order', 'agent')
    huadong_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huadong_direct_salers]
    huadong_direct_salers_orders = _get_report_total(
        huadong_direct_saler_orders, now_year, Q_monthes, 'douban_order', 'direct')
    if request.values.get('action', '') == 'download':
        response = write_client_excel(huabei_agent_salers_orders=huabei_agent_salers_orders,
                                      huabei_direct_salers_orders=huabei_direct_salers_orders,
                                      huanan_agent_salers_orders=huanan_agent_salers_orders,
                                      huanan_direct_salers_orders=huanan_direct_salers_orders,
                                      huadong_agent_salers_orders=huadong_agent_salers_orders,
                                      huadong_direct_salers_orders=huadong_direct_salers_orders,
                                      now_year=now_year, Q=now_Q, Q_monthes=Q_monthes, otype='douban')
        return response
    return tpl('/data_query/weekly/douban_index.html',
               huabei_agent_salers_orders=huabei_agent_salers_orders,
               huabei_direct_salers_orders=huabei_direct_salers_orders,
               huanan_agent_salers_orders=huanan_agent_salers_orders,
               huanan_direct_salers_orders=huanan_direct_salers_orders,
               huadong_agent_salers_orders=huadong_agent_salers_orders,
               huadong_direct_salers_orders=huadong_direct_salers_orders,
               Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, mediums=Medium.all(), location_id=location_id)


def _douban_order_to_dict(douban_order, now_year, Q_monthes):
    dict_order = {}
    dict_order['client_name'] = douban_order.client.name
    dict_order['agent_name'] = douban_order.agent.name
    dict_order['contract'] = douban_order.contract
    dict_order['campaign'] = douban_order.campaign
    dict_order['industry_cn'] = douban_order.client.industry_cn
    dict_order['locations'] = douban_order.locations
    dict_order['direct_sales'] = [
        {'id': k.id, 'name': k.name, 'location': k.team.location}for k in douban_order.direct_sales]
    dict_order['agent_sales'] = [
        {'id': k.id, 'name': k.name, 'location': k.team.location}for k in douban_order.agent_sales]
    dict_order['salers_ids'] = [k['id']
                                for k in (dict_order['direct_sales'] + dict_order['agent_sales'])]
    dict_order['get_saler_leaders'] = [
        k.id for k in douban_order.get_saler_leaders()]
    dict_order['zhixing_money'] = [
        douban_order.zhixing_money('agent'), douban_order.zhixing_money('direct')]
    dict_order['resource_type_cn'] = douban_order.resource_type_cn
    dict_order['operater_users'] = [
        {'id': k.id, 'name': k.name}for k in douban_order.operater_users]
    dict_order['client_start'] = douban_order.client_start
    dict_order['client_end'] = douban_order.client_end
    dict_order['executive_report_data'] = douban_order.executive_report_data()
    return dict_order


def _client_order_to_dict(client_order, now_year, Q_monthes):
    dict_order = {}
    dict_order['client_name'] = client_order.client.name
    dict_order['agent_name'] = client_order.agent.name
    dict_order['contract'] = client_order.contract
    dict_order['campaign'] = client_order.campaign
    dict_order['industry_cn'] = client_order.client.industry_cn
    dict_order['locations'] = client_order.locations
    dict_order['direct_sales'] = [
        {'id': k.id, 'name': k.name, 'location': k.team.location}for k in client_order.direct_sales]
    dict_order['agent_sales'] = [
        {'id': k.id, 'name': k.name, 'location': k.team.location}for k in client_order.agent_sales]
    dict_order['salers_ids'] = [k['id']
                                for k in (dict_order['direct_sales'] + dict_order['agent_sales'])]
    dict_order['get_saler_leaders'] = [
        k.id for k in client_order.get_saler_leaders()]
    dict_order['zhixing_money'] = [
        client_order.zhixing_money('agent'), client_order.zhixing_money('direct')]
    dict_order['invoice_pass_sum'] = client_order.invoice_pass_sum
    dict_order['zhixing_medium_money2'] = [client_order.zhixing_medium_money2(
        'agent'), client_order.zhixing_medium_money2('direct')]
    dict_order['medium_orders'] = [{'name': k.medium.name,
                                    'contract': k.associated_douban_contract,
                                    'medium_id': k.medium.id,
                                    'zhixing_medium_money2': [k.zhixing_medium_money2('agent'),
                                                              k.zhixing_medium_money2('direct')],
                                    'medium_money_by_month': [
                                        [k.get_executive_report_medium_money_by_month(now_year, m, 'agent'),
                                         k.get_executive_report_medium_money_by_month(now_year, m, 'direct')]
                                        for m in Q_monthes],
                                    'associated_douban_pro_month_money': [
                                        [k.associated_douban_orders_pro_month_money(now_year, m, 'agent'),
                                         k.associated_douban_orders_pro_month_money(now_year, m, 'direct')]
                                        for m in Q_monthes]
                                    } for k in client_order.medium_orders]
    dict_order['medium_money_by_month'] = [
        [client_order.get_executive_report_medium_money_by_month(now_year, m, 'agent'),
         client_order.get_executive_report_medium_money_by_month(now_year, m, 'direct')] for m in Q_monthes]
    dict_order['associated_douban_pro_month_money'] = [
        [client_order.associated_douban_orders_pro_month_money(now_year, m, 'agent'),
         client_order.associated_douban_orders_pro_month_money(now_year, m, 'direct')] for m in Q_monthes]

    dict_order['resource_type_cn'] = client_order.resource_type_cn
    dict_order['operater_users'] = [
        {'id': k.id, 'name': k.name}for k in client_order.operater_users]
    dict_order['client_start'] = client_order.client_start
    dict_order['client_end'] = client_order.client_end
    dict_order['executive_report_data'] = client_order.executive_report_data()
    return dict_order


@data_query_weekly_bp.route('/', methods=['GET'])
def index():
    now_year = request.values.get('year', '')
    now_Q = request.values.get('Q', '')
    medium_id = int(request.values.get('medium_id', 0))
    location_id = int(request.values.get('location_id', 0))
    if not now_year and not now_Q:
        now_date = datetime.date.today()
        now_year = now_date.strftime('%Y')
        now_month = now_date.strftime('%m')
        now_Q = check_month_get_Q(now_month)
    Q_monthes = check_Q_get_monthes(now_Q)

    start_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[0]), 1).date()
    end_Q_month = datetime.datetime(int(now_year), int(Q_monthes[-1]), 1).date()

    client_orders = list(set([report.client_order for report in ClientOrderExecutiveReport.query.filter(
        ClientOrderExecutiveReport.month_day >= start_Q_month, ClientOrderExecutiveReport.month_day <= end_Q_month)
        if report.client_order.status == 1]))

    # 获取未撤单的合同
    client_orders = [
        _client_order_to_dict(k, now_year, Q_monthes) for k in client_orders if k.contract_status not in [7, 8, 9]]

    # 根据媒体查询合同
    if medium_id:
        client_orders = [
            order for order in client_orders if medium_id in [o['medium_id'] for o in order['medium_orders']]]

    # 个级别管理查看不同的合同
    if g.user.is_contract() or g.user.is_media() or g.user.is_super_leader() or \
            g.user.is_finance() or g.user.is_media_leader():
        client_orders = client_orders
    elif g.user.is_leader():
        client_orders = [
            o for o in client_orders if g.user.location in o['locations']]
    else:
        client_orders = [
            o for o in client_orders if (g.user.id in o['salers_ids']) or (g.user.id in o['get_saler_leaders'])]

    huabei_agent_salers = []
    huabei_direct_salers = []
    huanan_agent_salers = []
    huanan_direct_salers = []
    huadong_agent_salers = []
    huadong_direct_salers = []
    if location_id == 0:
        huabei_agent_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUABEI)
        huabei_direct_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUABEI, 'direct')
        huanan_agent_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUANAN)
        huanan_direct_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUANAN, 'direct')
        huadong_agent_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUADONG)
        huadong_direct_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUADONG, 'direct')
    elif location_id == 1:
        huabei_agent_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUABEI)
        huabei_direct_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUABEI, 'direct')
    elif location_id == 2:
        huadong_agent_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUADONG)
        huadong_direct_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUADONG, 'direct')
    elif location_id == 3:
        huanan_agent_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUANAN)
        huanan_direct_salers = _get_salers_user_by_location(
            client_orders, TEAM_LOCATION_HUANAN, 'direct')

    # 获取华北销售合同
    huabei_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huabei_agent_salers]
    huabei_agent_salers_orders = _get_report_total(
        huabei_agent_saler_orders, now_year, Q_monthes, 'client_order', 'agent')
    huabei_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huabei_direct_salers]
    huabei_direct_salers_orders = _get_report_total(
        huabei_agent_saler_orders, now_year, Q_monthes, 'client_order', 'direct')
    # 获取华南销售合同
    huanan_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huanan_agent_salers]
    huanan_agent_salers_orders = _get_report_total(
        huanan_agent_saler_orders, now_year, Q_monthes, 'client_order', 'agent')
    huanan_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huanan_direct_salers]
    huanan_direct_salers_orders = _get_report_total(
        huanan_direct_saler_orders, now_year, Q_monthes, 'client_order', 'direct')
    # 获取华东销售合同
    huadong_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huadong_agent_salers]
    huadong_agent_salers_orders = _get_report_total(
        huadong_agent_saler_orders, now_year, Q_monthes, 'client_order', 'agent')
    huadong_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huadong_direct_salers]
    huadong_direct_salers_orders = _get_report_total(
        huadong_direct_saler_orders, now_year, Q_monthes, 'client_order', 'direct')
    if request.values.get('action', '') == 'download':
        response = write_client_excel(huabei_agent_salers_orders=huabei_agent_salers_orders,
                                      huabei_direct_salers_orders=huabei_direct_salers_orders,
                                      huanan_agent_salers_orders=huanan_agent_salers_orders,
                                      huanan_direct_salers_orders=huanan_direct_salers_orders,
                                      huadong_agent_salers_orders=huadong_agent_salers_orders,
                                      huadong_direct_salers_orders=huadong_direct_salers_orders,
                                      now_year=now_year, Q=now_Q, Q_monthes=Q_monthes)
        return response
    return tpl('/data_query/weekly/index.html',
               huabei_agent_salers_orders=huabei_agent_salers_orders,
               huabei_direct_salers_orders=huabei_direct_salers_orders,
               huanan_agent_salers_orders=huanan_agent_salers_orders,
               huanan_direct_salers_orders=huanan_direct_salers_orders,
               huadong_agent_salers_orders=huadong_agent_salers_orders,
               huadong_direct_salers_orders=huadong_direct_salers_orders,
               medium_id=medium_id, Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, mediums=Medium.all(), location_id=location_id)
