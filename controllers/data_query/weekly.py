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


def _get_report_by_user(user, client_orders, now_year, now_Q, Q_monthes, type='agent'):
    last_year, last_month = get_last_year_month_by_Q(now_year, now_Q)
    after_year, after_month = get_after_year_month_by_Q(now_year, now_Q)
    orders = []
    for order in client_orders:
        if type == 'agent':
            if not order.order_agent_owner(user):
                order = None
        else:
            if not (order.order_direct_owner(user) and len(order.agent_sales) == 0):
                order = None
        if order:
            moneys = order.executive_report(user, now_year, Q_monthes, type)
            now_Q_money = sum(moneys)
            last_Q_money = sum(
                order.executive_report(user, last_year, last_month, type))
            after_Q_money = sum(
                order.executive_report(user, after_year, after_month, type))
            orders.append({'order': order, 'moneys': moneys, 'now_Q_money': now_Q_money,
                           'after_Q_money': after_Q_money, 'last_Q_money': last_Q_money})
    return orders


def _get_salers_user_by_location(client_orders, location, type='agent'):
    salers = []
    for k in client_orders:
        if type == 'agent':
            salers += [u for u in k.agent_sales if u.team.location == location]
        else:
            salers += [u for u in k.direct_sales if u.team.location ==
                       location and len(k.agent_sales) == 0]
    return list(set(salers))


def _get_report_total(saler_orders, now_year, Q_monthes, type='client_order'):
    for k in saler_orders:
        k['total_order_money'] = sum(
            [order['order'].money for order in k['orders']])
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
            k['total_order_mediums_money2'] = sum(
                [order['order'].mediums_money2 for order in k['orders']])
            k['total_frist_medium_money2_by_month'] = 0
            k['total_second_medium_money2_by_month'] = 0
            k['total_third_medium_money2_by_month'] = 0
            k['total_frist_saler_money_by_month'] = 0
            k['total_second_saler_money_by_month'] = 0
            k['total_third_saler_money_by_month'] = 0
            for i in range(len(Q_monthes)):
                total_medium_money2 = sum([order['order'].get_executive_report_medium_money_by_month(
                    now_year, Q_monthes[i])['medium_money2'] for order in k['orders']])
                sale_money = sum([order['order'].get_executive_report_medium_money_by_month(
                    now_year, Q_monthes[i])['sale_money'] for order in k['orders']])
                if i == 0:
                    k['total_frist_medium_money2_by_month'] += total_medium_money2
                    k['total_frist_saler_money_by_month'] += sale_money
                elif i == 1:
                    k['total_second_medium_money2_by_month'] += total_medium_money2
                    k['total_second_saler_money_by_month'] += sale_money
                elif i == 2:
                    k['total_third_medium_money2_by_month'] += total_medium_money2
                    k['total_third_saler_money_by_month'] += sale_money
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
        DoubanOrderExecutiveReport.month_day >= start_Q_month, DoubanOrderExecutiveReport.month_day <= end_Q_month)]))

    if g.user.is_contract() or g.user.is_media() or g.user.is_super_leader() or g.user.is_finance():
        douban_orders = douban_orders
    elif g.user.is_leader():
        douban_orders = [
            o for o in douban_orders if g.user.location in o.locations]
    else:
        douban_orders = [
            o for o in douban_orders if g.user in o.direct_sales + o.agent_sales]

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
        huabei_agent_saler_orders, now_year, Q_monthes, 'douban_order')
    huabei_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huabei_direct_salers]
    huabei_direct_salers_orders = _get_report_total(
        huabei_agent_saler_orders, now_year, Q_monthes, 'douban_order')
    huanan_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huanan_agent_salers]
    huanan_agent_salers_orders = _get_report_total(
        huanan_agent_saler_orders, now_year, Q_monthes, 'douban_order')
    huanan_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huanan_direct_salers]
    huanan_direct_salers_orders = _get_report_total(
        huanan_direct_saler_orders, now_year, Q_monthes, 'douban_order')
    huadong_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huadong_agent_salers]
    huadong_agent_salers_orders = _get_report_total(
        huadong_agent_saler_orders, now_year, Q_monthes, 'douban_order')
    huanan_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, douban_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huadong_direct_salers]
    huadong_direct_salers_orders = _get_report_total(
        huanan_direct_saler_orders, now_year, Q_monthes, 'douban_order')
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
        ClientOrderExecutiveReport.month_day >= start_Q_month, ClientOrderExecutiveReport.month_day <= end_Q_month)]))
    if medium_id:
        client_orders = [
            order for order in client_orders if medium_id in [k.id for k in order.mediums]]

    if g.user.is_contract() or g.user.is_media() or g.user.is_super_leader() or g.user.is_finance():
        client_orders = client_orders
    elif g.user.is_leader():
        client_orders = [
            o for o in client_orders if g.user.location in o.locations]
    else:
        client_orders = [
            o for o in client_orders if g.user in o.direct_sales + o.agent_sales]
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

    huabei_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huabei_agent_salers]
    huabei_agent_salers_orders = _get_report_total(
        huabei_agent_saler_orders, now_year, Q_monthes)
    huabei_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huabei_direct_salers]
    huabei_direct_salers_orders = _get_report_total(
        huabei_agent_saler_orders, now_year, Q_monthes)
    huanan_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huanan_agent_salers]
    huanan_agent_salers_orders = _get_report_total(
        huanan_agent_saler_orders, now_year, Q_monthes)
    huanan_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huanan_direct_salers]
    huanan_direct_salers_orders = _get_report_total(
        huanan_direct_saler_orders, now_year, Q_monthes)
    huadong_agent_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'agent')} for user in huadong_agent_salers]
    huadong_agent_salers_orders = _get_report_total(
        huadong_agent_saler_orders, now_year, Q_monthes)
    huanan_direct_saler_orders = [{'user': user, 'orders': _get_report_by_user(
        user, client_orders, now_year, now_Q, Q_monthes, 'direct')} for user in huadong_direct_salers]
    huadong_direct_salers_orders = _get_report_total(
        huanan_direct_saler_orders, now_year, Q_monthes)

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
