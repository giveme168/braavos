# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from searchAd.models.client_order import searchAdClientOrderExecutiveReport
from searchAd.models.rebate_order import searchAdRebateOrderExecutiveReport
from searchAd.controllers.data_query.helpers.profit_helpers import write_order_excel, write_rebate_order_excel

searchAd_data_query_profit_bp = Blueprint(
    'searchAd_data_query_profit', __name__, template_folder='../../templates/searchAd/data_query')


@searchAd_data_query_profit_bp.route('/client_order', methods=['GET'])
def client_order():
    now_date = datetime.datetime.now()
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    client_orders = list(set([k.client_order for k in searchAdClientOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.client_order.status == 1]))
    if client_orders:
        client_orders = sorted(
            client_orders, key=lambda x: getattr(x, 'id'), reverse=True)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(client_orders, year, month)
        return response
    return tpl('/searchAd/data_query/profit/client_order.html', year=int(year),
               month=int(month), client_orders=client_orders)


@searchAd_data_query_profit_bp.route('/rebate_order', methods=['GET'])
def rebate_order():
    now_date = datetime.datetime.now()
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    rebate_orders = list(set([k.rebate_order for k in searchAdRebateOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.rebate_order.status == 1]))
    print rebate_orders
    if rebate_orders:
        rebate_orders = sorted(
            rebate_orders, key=lambda x: getattr(x, 'id'), reverse=True)
    if request.values.get('action', '') == 'download':
        response = write_rebate_order_excel(rebate_orders, year, month)
        return response
    return tpl('/searchAd/data_query/profit/rebate_order.html', year=int(year),
               month=int(month), rebate_orders=rebate_orders)