# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, g
from flask import render_template as tpl

from models.user import TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN
from models.client_order import ClientOrderExecutiveReport, IntentionOrder
from models.douban_order import DoubanOrder, DoubanOrderExecutiveReport
from models.order import Order
from models.medium import Medium
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q, get_monthes_pre_days,
                               get_last_year_month_by_Q, get_after_year_month_by_Q)
from controllers.data_query.helpers.weekly_helpers import write_client_excel, write_medium_index_excel


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
            salers += [u for u in k['agent_sales']
                       if u['location'] == location]
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
    end_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[-1]), 1).date()

    douban_orders = list(set([report.douban_order for report in DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_Q_month, DoubanOrderExecutiveReport.month_day <= end_Q_month)
        if report.status == 1]))
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
    dict_order['contract_status'] = douban_order.contract_status
    dict_order['contract'] = douban_order.contract
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
    # 用于新的媒体周报数据
    dict_order['money'] = douban_order.money
    # 直签豆瓣订单客户金额与媒体进个相同
    dict_order['medium_money2'] = douban_order.money
    return dict_order


def _client_order_to_dict(client_order, now_year, Q_monthes):
    dict_order = {}
    dict_order['client_name'] = client_order.client.name
    dict_order['agent_name'] = client_order.agent.name
    dict_order['contract'] = client_order.contract
    dict_order['campaign'] = client_order.campaign
    dict_order['industry_cn'] = client_order.client.industry_cn
    dict_order['locations'] = client_order.locations
    dict_order['contract_status'] = client_order.contract_status
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
    end_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[-1]), 1).date()

    client_orders = list(set([report.client_order for report in ClientOrderExecutiveReport.query.filter(
        ClientOrderExecutiveReport.month_day >= start_Q_month, ClientOrderExecutiveReport.month_day <= end_Q_month)
        if report.status == 1]))

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


# 新版媒体周报开始
def pre_month_money(money, start, end):
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = []
    for k in pre_month_days:
        pre_month_money_data.append(
            {'money': pre_money * k['days'], 'month': k['month'], 'days': k['days']})
    return pre_month_money_data


def _new_douban_order_to_dict(douban_order, last_Q_monthes, now_Q_monthes, after_Q_monthes):
    dict_order = {}
    dict_order['client_name'] = douban_order.client.name
    dict_order['agent_name'] = douban_order.agent.name
    dict_order['campaign'] = douban_order.campaign
    dict_order['industry_cn'] = douban_order.client.industry_cn
    dict_order['locations'] = douban_order.locations
    dict_order['contract_status'] = douban_order.contract_status
    dict_order['contract'] = douban_order.contract
    dict_order['direct_sales_names'] = douban_order.direct_sales_names
    dict_order['agent_sales_names'] = douban_order.agent_sales_names
    dict_order['salers_ids'] = [k.id
                                for k in (douban_order.direct_sales + douban_order.agent_sales)]
    dict_order['get_saler_leaders'] = [
        k.id for k in douban_order.get_saler_leaders()]
    dict_order['resource_type_cn'] = douban_order.resource_type_cn
    dict_order['operater_names'] = ",".join(
        [u.name for u in douban_order.operater_users])
    dict_order['client_start'] = douban_order.client_start
    dict_order['client_end'] = douban_order.client_end
    dict_order['finish_time'] = douban_order.finish_time.date().replace(day=1)
    dict_order['L_50'] = ''
    dict_order['U_50'] = ''
    dict_order['S_80'] = ''
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        douban_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        douban_order.client_end.strftime(dt_format), dt_format)
    executive_report_data = pre_month_money(douban_order.money,
                                            start_datetime,
                                            end_datetime)
    if dict_order['contract_status'] == 20:
        if dict_order['finish_time'] in now_Q_monthes:
            dict_order['now_Q_money_check'] = sum(
                [k['money'] for k in executive_report_data if k['month'].date() < now_Q_monthes[2]])
        elif dict_order['finish_time'] < now_Q_monthes[0]:
            # 本季度确认金额与本季度执行金额一致
            dict_order['now_Q_money_check'] = sum(
                [k['money'] for k in executive_report_data if k['month'].date() in now_Q_monthes])
        else:
            # 本季度确认金额与本季度执行金额一致
            dict_order['now_Q_money_check'] = 0
    else:
        dict_order['now_Q_money_check'] = 0

    dict_order['now_Q_money_zhixing'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() in now_Q_monthes])
    # 下季度执行金额
    dict_order['after_Q_money'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() in after_Q_monthes])
    # 上季度执行金额
    dict_order['last_Q_money'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() in last_Q_monthes])
    # 本季度按月执行额
    now_Q_date_param = {}
    for k in now_Q_monthes:
        now_Q_date_param[k] = 0
    for k in executive_report_data:
        if k['month'].date() in now_Q_date_param:
            now_Q_date_param[k['month'].date()] += k['money']
    now_Q_date_param = sorted(now_Q_date_param.iteritems(), key=lambda x: x[0])
    dict_order['first_month_money'] = now_Q_date_param[0][1]
    dict_order['second_month_money'] = now_Q_date_param[1][1]
    dict_order['third_month_money'] = now_Q_date_param[2][1]

    dict_order['money'] = douban_order.money
    # 直签豆瓣订单客户金额与媒体进个相同
    dict_order['medium_money2'] = douban_order.money

    pre_month_days = get_monthes_pre_days(start_datetime, end_datetime)
    dict_order['pre_month_days'] = set([k['month'] for k in pre_month_days])
    dict_order['status'] = douban_order.status
    return dict_order


def _new_medium_order_to_dict(order, last_Q_monthes, now_Q_monthes, after_Q_monthes):
    dict_order = {}
    dict_order['medium_id'] = order.medium.id
    dict_order['client_name'] = order.client_order.client.name
    dict_order['agent_name'] = order.client_order.agent.name
    dict_order['campaign'] = order.client_order.campaign
    dict_order['industry_cn'] = order.client_order.client.industry_cn
    dict_order['locations'] = order.client_order.locations
    dict_order['contract_status'] = order.client_order.contract_status
    dict_order['contract'] = order.client_order.contract
    dict_order['direct_sales_names'] = order.client_order.direct_sales_names
    dict_order['agent_sales_names'] = order.client_order.agent_sales_names
    dict_order['salers_ids'] = [k.id for k in (
        order.client_order.direct_sales + order.client_order.agent_sales)]
    dict_order['get_saler_leaders'] = [
        k.id for k in order.client_order.get_saler_leaders()]
    dict_order['resource_type_cn'] = order.client_order.resource_type_cn
    dict_order['operater_names'] = ",".join(
        [u.name for u in order.client_order.operater_users])
    dict_order['client_start'] = order.client_order.client_start
    dict_order['client_end'] = order.client_order.client_end
    dict_order['money'] = order.sale_money
    dict_order['medium_money2'] = order.medium_money2
    dict_order['L_50'] = ''
    dict_order['U_50'] = ''
    dict_order['S_80'] = ''
    dict_order[
        'finish_time'] = order.client_order.finish_time.date().replace(day=1)
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        order.medium_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        order.medium_end.strftime(dt_format), dt_format)
    sale_executive_report_data = pre_month_money(dict_order['money'],
                                                 start_datetime,
                                                 end_datetime)
    executive_report_data = pre_month_money(dict_order['medium_money2'],
                                            start_datetime,
                                            end_datetime)
    # 本季度确认金额
    if dict_order['contract_status'] == 20:
        if dict_order['finish_time'] in now_Q_monthes:
            dict_order['now_Q_money_check'] = sum(
                [k['money'] for k in sale_executive_report_data if k['month'].date() < now_Q_monthes[2]])
        elif dict_order['finish_time'] < now_Q_monthes[0]:
            dict_order['now_Q_money_check'] = sum(
                [k['money'] for k in sale_executive_report_data if k['month'].date() in now_Q_monthes])
        else:
            dict_order['now_Q_money_check'] = 0
    else:
        dict_order['now_Q_money_check'] = 0
    dict_order['now_Q_money_zhixing'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() in now_Q_monthes])
    # 下季度执行金额
    dict_order['after_Q_money'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() in after_Q_monthes])
    # 上季度执行金额
    dict_order['last_Q_money'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() in last_Q_monthes])
    # 本季度按月执行额
    now_Q_date_param = {}
    for k in now_Q_monthes:
        now_Q_date_param[k] = 0
    for k in executive_report_data:
        if k['month'].date() in now_Q_date_param:
            now_Q_date_param[k['month'].date()] += k['money']
    now_Q_date_param = sorted(now_Q_date_param.iteritems(), key=lambda x: x[0])
    dict_order['first_month_money'] = now_Q_date_param[0][1]
    dict_order['second_month_money'] = now_Q_date_param[1][1]
    dict_order['third_month_money'] = now_Q_date_param[2][1]
    pre_month_days = get_monthes_pre_days(start_datetime, end_datetime)
    dict_order['pre_month_days'] = set([k['month'] for k in pre_month_days])
    dict_order['status'] = order.client_order.status
    return dict_order


def _new_intention_order_to_dict(order):
    dict_order = {}
    dict_order['medium_id'] = order.medium_id
    dict_order['client_name'] = order.client
    dict_order['agent_name'] = order.agent
    dict_order['campaign'] = order.campaign
    dict_order['industry_cn'] = ''
    dict_order['locations'] = order.locations
    dict_order['contract'] = ''
    dict_order['direct_sales_names'] = order.direct_sales_names
    dict_order['agent_sales_names'] = order.agent_sales_names
    dict_order['salers_ids'] = [k.id for k in (
        order.direct_sales + order.agent_sales)]
    dict_order['get_saler_leaders'] = [
        k.id for k in order.get_saler_leaders()]
    dict_order['resource_type_cn'] = ''
    dict_order['operater_names'] = ''
    dict_order['client_start'] = order.client_start
    dict_order['client_end'] = order.client_end
    dict_order['L_50'] = 0
    dict_order['U_50'] = 0
    dict_order['S_80'] = 0
    if order.complete_percent == 1:
        dict_order['L_50'] = order.money
    elif order.complete_percent == 2:
        dict_order['U_50'] = order.money
    elif order.complete_percent == 3:
        dict_order['S_80'] = order.money
    dict_order['money'] = ''
    dict_order['medium_money2'] = ''
    dict_order['now_Q_money_check'] = ''

    dict_order['now_Q_money_zhixing'] = ''
    # 下季度执行金额
    dict_order['after_Q_money'] = ''
    # 上季度执行金额
    dict_order['last_Q_money'] = ''
    # 本季度按月执行额

    dict_order['first_month_money'] = ''
    dict_order['second_month_money'] = ''
    dict_order['third_month_money'] = ''

    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        order.client_end.strftime(dt_format), dt_format)
    pre_month_days = get_monthes_pre_days(start_datetime, end_datetime)
    dict_order['pre_month_days'] = set([k['month'] for k in pre_month_days])
    return dict_order


@data_query_weekly_bp.route('/medium', methods=['GET'])
def medium_index():
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
    end_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[-1]), 1).date()

    # 本季度月份数
    now_Q_monthes = [datetime.datetime(
        int(now_year), int(k), 1).date()for k in Q_monthes]
    # 上季度月份数
    last_year, last_month = get_last_year_month_by_Q(now_year, now_Q)
    last_Q_monthes = [datetime.datetime(
        int(last_year), int(k), 1).date()for k in last_month]
    # 下季度月份数
    after_year, after_month = get_after_year_month_by_Q(now_year, now_Q)
    after_Q_monthes = [datetime.datetime(
        int(after_year), int(k), 1).date()for k in after_month]

    # 获取搜索月份数，用于比对合同是否在整个区间
    dt_format = "%d%m%Y"
    pre_month_days = get_monthes_pre_days(datetime.datetime.strptime(start_Q_month.strftime(dt_format), dt_format),
                                          datetime.datetime.strptime(end_Q_month.strftime(dt_format), dt_format))

    pre_month_days = set([k['month'] for k in pre_month_days])

    # 获取洽谈中的订单
    intention_orders = [k for k in IntentionOrder.query.filter(int(now_year) >= DoubanOrder.client_start_year,
                                                               int(now_year) <= DoubanOrder.client_end_year)]
    intention_orders = [_new_intention_order_to_dict(
        k) for k in intention_orders]
    intention_orders = [k for k in intention_orders if len(
        pre_month_days & k['pre_month_days']) > 0]
    if location_id:
        intention_orders = [
            k for k in intention_orders if location_id in k['locations']]
    if g.user.is_contract() or g.user.is_media() or g.user.is_super_leader() or \
            g.user.is_finance() or g.user.is_media_leader():
        intention_orders = intention_orders
    elif g.user.is_leader():
        intention_orders = [
            o for o in intention_orders if g.user.location in o['locations']]
    else:
        intention_orders = [o for o in intention_orders if (
            g.user.id in o['salers_ids']) or (g.user.id in o['get_saler_leaders'])]
    # 获取洽谈中的订单结束

    # 获取直签豆瓣订单
    douban_orders = [k for k in DoubanOrder.query.filter(int(now_year) >= DoubanOrder.client_start_year,
                                                         int(now_year) <= DoubanOrder.client_end_year,
                                                         DoubanOrder.status == 1)]
    douban_orders = [_new_douban_order_to_dict(k, last_Q_monthes,
                                               now_Q_monthes,
                                               after_Q_monthes) for k in set(douban_orders)]
    # 去除撤单、新建合同
    douban_orders = [k for k in douban_orders if k[
        'contract_status'] not in [0, 7, 8, 9]]
    # 获取查询区间的豆瓣合同
    douban_orders = [k for k in douban_orders if len(
        pre_month_days & k['pre_month_days']) > 0]

    # 根据区域查询合同
    if location_id:
        douban_orders = [
            k for k in douban_orders if location_id in k['locations']]
    # 根据权限查看合同
    if g.user.is_contract() or g.user.is_media() or g.user.is_super_leader() or \
            g.user.is_finance() or g.user.is_media_leader():
        douban_orders = douban_orders
    elif g.user.is_leader():
        douban_orders = [
            o for o in douban_orders if g.user.location in o['locations']]
    else:
        douban_orders = [
            o for o in douban_orders if (g.user.id in o['salers_ids']) or (g.user.id in o['get_saler_leaders'])]
    douban_data = {'Delivered': [],
                   'Confirmed': [],
                   'Intention': [o for o in intention_orders if o['medium_id'] == 0]}
    for k in douban_orders:
        if k['contract'] and k['contract_status'] == 20:
            douban_data['Delivered'].append(k)
        elif k['contract'] and k['contract_status'] != 20:
            douban_data['Confirmed'].append(k)
    # 获取直签豆瓣订单结束

    # 获取媒体订单开始
    # 获取所有媒体订单
    medium_orders = [k for k in Order.all() if int(
        now_year) == k.medium_start.year or int(now_year) == k.medium_end.year]

    medium_orders = [_new_medium_order_to_dict(k, last_Q_monthes,
                                               now_Q_monthes,
                                               after_Q_monthes) for k in set(medium_orders)]
    medium_orders = [k for k in medium_orders if k[
        'contract_status'] not in [0, 7, 8, 9] and k['status'] == 1]
    # 获取查询区间的媒体合同
    medium_orders = [k for k in medium_orders if len(
        pre_month_days & k['pre_month_days']) > 0]
    # 根据区域查询合同
    if location_id:
        medium_orders = [
            k for k in medium_orders if location_id in k['locations']]
    # 根据权限查看合同
    if g.user.is_contract() or g.user.is_media() or g.user.is_super_leader() or \
            g.user.is_finance() or g.user.is_media_leader():
        medium_orders = medium_orders
    elif g.user.is_leader():
        medium_orders = [
            o for o in medium_orders if g.user.location in o['locations']]
    else:
        medium_orders = [
            o for o in medium_orders if (g.user.id in o['salers_ids']) or (g.user.id in o['get_saler_leaders'])]
    youli_data = {'Delivered': [],
                  'Confirmed': [],
                  'Intention': [o for o in intention_orders if o['medium_id'] == 3]}
    youli_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [3] and k['contract'] and k['contract_status'] == 20]
    youli_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [3]
        and k['contract'] and k['contract_status'] != 20]

    wuxian_data = {'Delivered': [],
                   'Confirmed': [],
                   'Intention': [o for o in intention_orders if o['medium_id'] == 8]}
    wuxian_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [8] and k['contract'] and k['contract_status'] == 20]
    wuxian_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [8]
        and k['contract'] and k['contract_status'] != 20]

    zhihu_data = {'Delivered': [],
                  'Confirmed': [],
                  'Intention': [o for o in intention_orders if o['medium_id'] == 5]}
    zhihu_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [5] and k['contract'] and k['contract_status'] == 20]
    zhihu_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [5]
        and k['contract'] and k['contract_status'] != 20]
    weipiao_data = {'Delivered': [],
                    'Confirmed': [],
                    'Intention': [o for o in intention_orders if o['medium_id'] == 52]}
    weipiao_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [52] and k['contract'] and k['contract_status'] == 20]
    weipiao_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [52]
        and k['contract'] and k['contract_status'] != 20]

    one_data = {'Delivered': [],
                'Confirmed': [],
                'Intention': [o for o in intention_orders if o['medium_id'] in [51, 67]]}
    one_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [51, 67] and k['contract'] and k['contract_status'] == 20]
    one_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [51, 67]
        and k['contract'] and k['contract_status'] != 20]

    xueqiu_data = {'Delivered': [],
                   'Confirmed': [],
                   'Intention': [o for o in intention_orders if o['medium_id'] == 9]}
    xueqiu_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [9] and k['contract'] and k['contract_status'] == 20]
    xueqiu_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [9]
        and k['contract'] and k['contract_status'] != 20]

    huxiu_data = {'Delivered': [],
                  'Confirmed': [],
                  'Intention': [o for o in intention_orders if o['medium_id'] in [14, 57]]}
    huxiu_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [14, 57] and k['contract'] and k['contract_status'] == 20]
    huxiu_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [14, 57]
        and k['contract'] and k['contract_status'] != 20]

    ledongli_data = {'Delivered': [],
                     'Confirmed': [],
                     'Intention': [o for o in intention_orders if o['medium_id'] == 66]}
    ledongli_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [66] and k['contract'] and k['contract_status'] == 20]
    ledongli_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [66]
        and k['contract'] and k['contract_status'] != 20]

    kecheng_data = {'Delivered': [],
                    'Confirmed': [],
                    'Intention': [o for o in intention_orders if o['medium_id'] == 4]}
    kecheng_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [4] and k['contract'] and k['contract_status'] == 20]
    kecheng_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [4]
        and k['contract'] and k['contract_status'] != 20]

    xiecheng_data = {'Delivered': [],
                     'Confirmed': [],
                     'Intention': [o for o in intention_orders if o['medium_id'] == 59]}
    xiecheng_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [59] and k['contract'] and k['contract_status'] == 20]
    xiecheng_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [59]
        and k['contract'] and k['contract_status'] != 20]

    momo_data = {'Delivered': [],
                 'Confirmed': [],
                 'Intention': [o for o in intention_orders if o['medium_id'] == 7]}
    momo_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [7] and k['contract'] and k['contract_status'] == 20]
    momo_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [7]
        and k['contract'] and k['contract_status'] != 20]

    lama_data = {'Delivered': [],
                 'Confirmed': [],
                 'Intention': [o for o in intention_orders if o['medium_id'] == 39]}
    lama_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [39] and k['contract'] and k['contract_status'] == 20]
    lama_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [39]
        and k['contract'] and k['contract_status'] != 20]

    nice_data = {'Delivered': [],
                 'Confirmed': [],
                 'Intention': [o for o in intention_orders if o['medium_id'] == 12]}
    nice_data['Delivered'] = [
        k for k in medium_orders if k['medium_id'] in [12] and k['contract'] and k['contract_status'] == 20]
    nice_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] in [12]
        and k['contract'] and k['contract_status'] != 20]

    except_medium_ids = [3, 8, 5, 52, 51, 67, 9, 14, 57, 66, 4, 59, 7, 39, 12]
    other_data = {'Delivered': [],
                  'Confirmed': [],
                  'Intention': [o for o in intention_orders if o['medium_id'] not in except_medium_ids]}
    other_data['Delivered'] = [k for k in medium_orders if k[
        'medium_id'] not in except_medium_ids and k['contract'] and k['contract_status'] == 20]
    other_data['Confirmed'] = [
        k for k in medium_orders if k['medium_id'] not in except_medium_ids
        and k['contract'] and k['contract_status'] != 20]
    meijie_data = {'Delivered': [],
                   'Confirmed': [],
                   'Intention': []}
    meijie_data['Delivered'] = [k for k in medium_orders if k[
        'contract'] and 148 in k['salers_ids'] and k['contract_status'] == 20]
    meijie_data['Confirmed'] = [
        k for k in medium_orders if 148 in k['salers_ids']
        and k['contract'] and k['contract_status'] != 20]

    total_money = sum([k['money'] for k in douban_data['Delivered']]) + \
        sum([k['money'] for k in douban_data['Confirmed']]) + \
        sum([k['money'] for k in youli_data['Delivered']]) +\
        sum([k['money'] for k in youli_data['Confirmed']]) + \
        sum([k['money'] for k in wuxian_data['Delivered']]) +\
        sum([k['money'] for k in wuxian_data['Confirmed']]) + \
        sum([k['money'] for k in zhihu_data['Delivered']]) + \
        sum([k['money'] for k in zhihu_data['Confirmed']]) + \
        sum([k['money'] for k in weipiao_data['Delivered']]) + \
        sum([k['money'] for k in weipiao_data['Confirmed']]) + \
        sum([k['money'] for k in one_data['Delivered']]) +\
        sum([k['money'] for k in one_data['Confirmed']]) + \
        sum([k['money'] for k in xueqiu_data['Delivered']]) +\
        sum([k['money'] for k in xueqiu_data['Confirmed']]) + \
        sum([k['money'] for k in huxiu_data['Delivered']]) + \
        sum([k['money'] for k in huxiu_data['Confirmed']]) + \
        sum([k['money'] for k in ledongli_data['Delivered']]) + \
        sum([k['money'] for k in ledongli_data['Confirmed']]) + \
        sum([k['money'] for k in kecheng_data['Delivered']]) +\
        sum([k['money'] for k in kecheng_data['Confirmed']]) + \
        sum([k['money'] for k in xiecheng_data['Delivered']]) +\
        sum([k['money'] for k in xiecheng_data['Confirmed']]) + \
        sum([k['money'] for k in momo_data['Delivered']]) + \
        sum([k['money'] for k in momo_data['Confirmed']]) + \
        sum([k['money'] for k in lama_data['Delivered']]) + \
        sum([k['money'] for k in lama_data['Confirmed']]) + \
        sum([k['money'] for k in nice_data['Delivered']]) + \
        sum([k['money'] for k in nice_data['Confirmed']]) + \
        sum([k['money'] for k in other_data['Confirmed']]) + \
        sum([k['money'] for k in other_data['Delivered']])

    total_medium_money2 = sum([k['medium_money2'] for k in douban_data['Delivered']]) + \
        sum([k['medium_money2'] for k in douban_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in youli_data['Delivered']]) +\
        sum([k['medium_money2'] for k in youli_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in wuxian_data['Delivered']]) +\
        sum([k['medium_money2'] for k in wuxian_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in zhihu_data['Delivered']]) + \
        sum([k['medium_money2'] for k in zhihu_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in weipiao_data['Delivered']]) + \
        sum([k['medium_money2'] for k in weipiao_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in one_data['Delivered']]) +\
        sum([k['medium_money2'] for k in one_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in xueqiu_data['Delivered']]) +\
        sum([k['medium_money2'] for k in xueqiu_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in huxiu_data['Delivered']]) + \
        sum([k['medium_money2'] for k in huxiu_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in ledongli_data['Delivered']]) + \
        sum([k['medium_money2'] for k in ledongli_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in kecheng_data['Delivered']]) +\
        sum([k['medium_money2'] for k in kecheng_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in xiecheng_data['Delivered']]) +\
        sum([k['medium_money2'] for k in xiecheng_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in momo_data['Delivered']]) + \
        sum([k['medium_money2'] for k in momo_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in lama_data['Delivered']]) + \
        sum([k['medium_money2'] for k in lama_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in nice_data['Delivered']]) + \
        sum([k['medium_money2'] for k in nice_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in other_data['Confirmed']]) + \
        sum([k['medium_money2'] for k in other_data['Delivered']])

    total_now_Q_money_check = sum([k['now_Q_money_check'] for k in douban_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in youli_data['Delivered']]) +\
        sum([k['now_Q_money_check'] for k in wuxian_data['Delivered']]) +\
        sum([k['now_Q_money_check'] for k in zhihu_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in weipiao_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in one_data['Delivered']]) +\
        sum([k['now_Q_money_check'] for k in xueqiu_data['Delivered']]) +\
        sum([k['now_Q_money_check'] for k in huxiu_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in ledongli_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in kecheng_data['Delivered']]) +\
        sum([k['now_Q_money_check'] for k in xiecheng_data['Delivered']]) +\
        sum([k['now_Q_money_check'] for k in momo_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in lama_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in nice_data['Delivered']]) + \
        sum([k['now_Q_money_check'] for k in other_data['Delivered']])

    total_now_Q_money_zhixing = sum([k['now_Q_money_zhixing'] for k in douban_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in douban_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in youli_data['Delivered']]) +\
        sum([k['now_Q_money_zhixing'] for k in youli_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in wuxian_data['Delivered']]) +\
        sum([k['now_Q_money_zhixing'] for k in wuxian_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in zhihu_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in zhihu_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in weipiao_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in weipiao_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in one_data['Delivered']]) +\
        sum([k['now_Q_money_zhixing'] for k in one_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in xueqiu_data['Delivered']]) +\
        sum([k['now_Q_money_zhixing'] for k in xueqiu_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in huxiu_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in huxiu_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in ledongli_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in ledongli_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in kecheng_data['Delivered']]) +\
        sum([k['now_Q_money_zhixing'] for k in kecheng_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in xiecheng_data['Delivered']]) +\
        sum([k['now_Q_money_zhixing'] for k in xiecheng_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in momo_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in momo_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in lama_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in lama_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in nice_data['Delivered']]) + \
        sum([k['now_Q_money_zhixing'] for k in nice_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in other_data['Confirmed']]) + \
        sum([k['now_Q_money_zhixing'] for k in other_data['Delivered']])

    total_first_month_money = sum([k['first_month_money'] for k in douban_data['Delivered']]) + \
        sum([k['first_month_money'] for k in douban_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in youli_data['Delivered']]) +\
        sum([k['first_month_money'] for k in youli_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in wuxian_data['Delivered']]) +\
        sum([k['first_month_money'] for k in wuxian_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in zhihu_data['Delivered']]) + \
        sum([k['first_month_money'] for k in zhihu_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in weipiao_data['Delivered']]) + \
        sum([k['first_month_money'] for k in weipiao_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in one_data['Delivered']]) +\
        sum([k['first_month_money'] for k in one_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in xueqiu_data['Delivered']]) +\
        sum([k['first_month_money'] for k in xueqiu_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in huxiu_data['Delivered']]) + \
        sum([k['first_month_money'] for k in huxiu_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in ledongli_data['Delivered']]) + \
        sum([k['first_month_money'] for k in ledongli_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in kecheng_data['Delivered']]) +\
        sum([k['first_month_money'] for k in kecheng_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in xiecheng_data['Delivered']]) +\
        sum([k['first_month_money'] for k in xiecheng_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in momo_data['Delivered']]) + \
        sum([k['first_month_money'] for k in momo_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in lama_data['Delivered']]) + \
        sum([k['first_month_money'] for k in lama_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in nice_data['Delivered']]) + \
        sum([k['first_month_money'] for k in nice_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in other_data['Confirmed']]) + \
        sum([k['first_month_money'] for k in other_data['Delivered']])

    total_second_month_money = sum([k['second_month_money'] for k in douban_data['Delivered']]) + \
        sum([k['second_month_money'] for k in douban_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in youli_data['Delivered']]) +\
        sum([k['second_month_money'] for k in youli_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in wuxian_data['Delivered']]) +\
        sum([k['second_month_money'] for k in wuxian_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in zhihu_data['Delivered']]) + \
        sum([k['second_month_money'] for k in zhihu_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in weipiao_data['Delivered']]) + \
        sum([k['second_month_money'] for k in weipiao_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in one_data['Delivered']]) +\
        sum([k['second_month_money'] for k in one_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in xueqiu_data['Delivered']]) +\
        sum([k['second_month_money'] for k in xueqiu_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in huxiu_data['Delivered']]) + \
        sum([k['second_month_money'] for k in huxiu_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in ledongli_data['Delivered']]) + \
        sum([k['second_month_money'] for k in ledongli_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in kecheng_data['Delivered']]) +\
        sum([k['second_month_money'] for k in kecheng_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in xiecheng_data['Delivered']]) +\
        sum([k['second_month_money'] for k in xiecheng_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in momo_data['Delivered']]) + \
        sum([k['second_month_money'] for k in momo_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in lama_data['Delivered']]) + \
        sum([k['second_month_money'] for k in lama_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in nice_data['Delivered']]) + \
        sum([k['second_month_money'] for k in nice_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in other_data['Confirmed']]) + \
        sum([k['second_month_money'] for k in other_data['Delivered']])

    total_third_month_money = sum([k['third_month_money'] for k in douban_data['Delivered']]) + \
        sum([k['third_month_money'] for k in douban_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in youli_data['Delivered']]) +\
        sum([k['third_month_money'] for k in youli_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in wuxian_data['Delivered']]) +\
        sum([k['third_month_money'] for k in wuxian_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in zhihu_data['Delivered']]) + \
        sum([k['third_month_money'] for k in zhihu_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in weipiao_data['Delivered']]) + \
        sum([k['third_month_money'] for k in weipiao_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in one_data['Delivered']]) +\
        sum([k['third_month_money'] for k in one_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in xueqiu_data['Delivered']]) +\
        sum([k['third_month_money'] for k in xueqiu_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in huxiu_data['Delivered']]) + \
        sum([k['third_month_money'] for k in huxiu_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in ledongli_data['Delivered']]) + \
        sum([k['third_month_money'] for k in ledongli_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in kecheng_data['Delivered']]) +\
        sum([k['third_month_money'] for k in kecheng_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in xiecheng_data['Delivered']]) +\
        sum([k['third_month_money'] for k in xiecheng_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in momo_data['Delivered']]) + \
        sum([k['third_month_money'] for k in momo_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in lama_data['Delivered']]) + \
        sum([k['third_month_money'] for k in lama_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in nice_data['Delivered']]) + \
        sum([k['third_month_money'] for k in nice_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in other_data['Confirmed']]) + \
        sum([k['third_month_money'] for k in other_data['Delivered']])
    if request.values.get('action') == 'download':
        response = write_medium_index_excel(Q=now_Q, now_year=now_year,
                                            Q_monthes=Q_monthes, location_id=location_id,
                                            douban_data=douban_data, youli_data=youli_data,
                                            wuxian_data=wuxian_data, zhihu_data=zhihu_data,
                                            weipiao_data=weipiao_data, one_data=one_data,
                                            xueqiu_data=xueqiu_data, huxiu_data=huxiu_data,
                                            ledongli_data=ledongli_data, kecheng_data=kecheng_data,
                                            xiecheng_data=xiecheng_data, momo_data=momo_data,
                                            lama_data=lama_data, nice_data=nice_data, meijie_data=meijie_data,
                                            other_data=other_data, total_money=total_money,
                                            total_medium_money2=total_medium_money2,
                                            total_now_Q_money_check=total_now_Q_money_check,
                                            total_first_month_money=total_first_month_money,
                                            total_second_month_money=total_second_month_money,
                                            total_third_month_money=total_third_month_money,
                                            total_now_Q_money_zhixing=total_now_Q_money_zhixing)
        return response
    # 获取没定订单结束
    return tpl('/data_query/weekly/medium_index.html', Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, location_id=location_id,
               douban_data=douban_data, youli_data=youli_data, wuxian_data=wuxian_data,
               zhihu_data=zhihu_data, weipiao_data=weipiao_data, one_data=one_data,
               xueqiu_data=xueqiu_data, huxiu_data=huxiu_data, ledongli_data=ledongli_data,
               kecheng_data=kecheng_data, xiecheng_data=xiecheng_data, momo_data=momo_data,
               lama_data=lama_data, nice_data=nice_data, meijie_data=meijie_data,
               other_data=other_data, total_money=total_money, total_medium_money2=total_medium_money2,
               total_now_Q_money_check=total_now_Q_money_check, total_first_month_money=total_first_month_money,
               total_second_month_money=total_second_month_money, total_third_month_money=total_third_month_money,
               total_now_Q_money_zhixing=total_now_Q_money_zhixing)
# 新版媒体周报结束
