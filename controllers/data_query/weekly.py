# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.user import TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG, TEAM_LOCATION_HUANAN
from models.client_order import ClientOrderExecutiveReport
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q,
                               get_last_year_month_by_Q, get_after_year_month_by_Q)


data_query_weekly_bp = Blueprint(
    'data_query_weekly', __name__, template_folder='../../templates/data_query')


@data_query_weekly_bp.route('/', methods=['GET'])
def index():
    now_year = request.values.get('year', '')
    now_Q = request.values.get('Q', '')
    if not now_year and not now_Q:
        now_date = datetime.date.today()
        now_year = now_date.strftime('%Y')
        now_month = now_date.strftime('%m')
        now_Q = check_month_get_Q(now_month)
    Q_monthes = check_Q_get_monthes(now_Q)
    last_year, last_month = get_last_year_month_by_Q(now_year, now_Q)
    after_year, after_month = get_after_year_month_by_Q(now_year, now_Q)
    start_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[0]), 1).date()
    end_Q_month = datetime.datetime(int(now_year), int(Q_monthes[-1]), 1).date()
    client_orders = list(set([report.client_order for report in ClientOrderExecutiveReport.query.filter(
        ClientOrderExecutiveReport.month_day >= start_Q_month, ClientOrderExecutiveReport.month_day <= end_Q_month)]))
    huabei_agent_salers_orders = []
    huabei_direct_salers_orders = []
    huanan_agent_salers_orders = []
    huanan_direct_salers_orders = []
    huadong_agent_salers_order = []
    huadong_direct_salers_order = []
    for k in client_orders:
        huabei_agent_salers_orders += [
            u for u in k.agent_sales if u.team.location == TEAM_LOCATION_HUABEI]
        huabei_direct_salers_orders += [
            u for u in k.direct_sales if u.team.location == TEAM_LOCATION_HUABEI and len(k.agent_sales) == 0]
        huanan_agent_salers_orders += [
            u for u in k.agent_sales if u.team.location == TEAM_LOCATION_HUANAN]
        huanan_direct_salers_orders += [
            u for u in k.direct_sales if u.team.location == TEAM_LOCATION_HUANAN and len(k.agent_sales) == 0]
        huadong_agent_salers_order += [
            u for u in k.agent_sales if u.team.location == TEAM_LOCATION_HUADONG]
        huadong_direct_salers_order += [
            u for u in k.direct_sales if u.team.location == TEAM_LOCATION_HUADONG and len(k.agent_sales) == 0]
    huabei_agent_salers_orders = list(set(huabei_agent_salers_orders))
    huabei_direct_salers_orders = list(set(huabei_direct_salers_orders))
    huanan_agent_salers_orders = list(set(huanan_agent_salers_orders))
    huanan_direct_salers_orders = list(set(huanan_direct_salers_orders))
    huadong_agent_salers_order = list(set(huadong_agent_salers_order))
    huadong_direct_salers_order = list(set(huadong_direct_salers_order))
    for k in huabei_agent_salers_orders + huanan_agent_salers_orders + huadong_agent_salers_order:
        k.orders = []
        for order in client_orders:
            if order.order_agent_owner(k):
                moneys = order.executive_report(now_year, Q_monthes)
                now_Q_money = sum(moneys)
                last_Q_money = sum(
                    order.executive_report(last_year, last_month))
                after_Q_money = sum(
                    order.executive_report(after_year, after_month))
                k.orders.append({'order': order, 'moneys': moneys, 'now_Q_money': now_Q_money,
                                 'after_Q_money': after_Q_money, 'last_Q_money': last_Q_money})

    for k in huabei_direct_salers_orders + huanan_direct_salers_orders + huadong_direct_salers_order:
        k.orders = []
        for order in client_orders:
            if order.order_agent_owner(k):
                moneys = order.executive_report(now_year, Q_monthes)
                now_Q_money = sum(moneys)
                last_Q_money = sum(
                    order.executive_report(last_year, last_month))
                after_Q_money = sum(
                    order.executive_report(after_year, after_month))
                k.orders.append({'order': order, 'moneys': moneys, 'now_Q_money': now_Q_money,
                                 'after_Q_money': after_Q_money, 'last_Q_money': last_Q_money})
    for k in (huabei_direct_salers_orders + huanan_direct_salers_orders + huadong_direct_salers_order +
              huabei_agent_salers_orders + huanan_agent_salers_orders + huadong_agent_salers_order):
        k.total_order_money = sum(
            [order['order'].money for order in k.orders])
        k.total_order_mediums_money2 = sum(
            [order['order'].mediums_money2 for order in k.orders])
        k.total_now_Q_money = sum(
            [order['now_Q_money'] for order in k.orders])
        k.total_last_Q_money = sum(
            [order['last_Q_money'] for order in k.orders])
        k.total_after_Q_money = sum(
            [order['after_Q_money'] for order in k.orders])
        k.total_frist_month_money = sum(
            [order['moneys'][0] for order in k.orders])
        k.total_second_month_money = sum(
            [order['moneys'][1] for order in k.orders])
        k.total_third_month_money = sum(
            [order['moneys'][2] for order in k.orders])
    return tpl('/data_query/weekly/index.html', huabei_agent_salers_orders=huabei_agent_salers_orders,
               huabei_direct_salers_orders=huabei_direct_salers_orders,
               Q=now_Q, now_year=now_year, Q_monthes=Q_monthes)
