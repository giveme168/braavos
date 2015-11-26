# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.client_order import ClientOrderExecutiveReport
from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from controllers.data_query.helpers.profit_helpers import write_order_excel, write_douban_order_excel

data_query_profit_bp = Blueprint(
    'data_query_profit', __name__, template_folder='../../templates/data_query')


@data_query_profit_bp.route('/client_order', methods=['GET'])
def client_order():
    now_date = datetime.datetime.now()
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    client_orders = list(set([k.client_order for k in ClientOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.client_order.status == 1]))
    if client_orders:
        client_orders = sorted(
            client_orders, key=lambda x: getattr(x, 'id'), reverse=True)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(client_orders, year, month)
        return response
    return tpl('/data_query/profit/client_order.html', year=int(year),
               month=int(month), client_orders=client_orders)


@data_query_profit_bp.route('/douban_order', methods=['GET'])
def douban_order():
    now_date = datetime.datetime.now()
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    douban_orders = list(set([k.douban_order for k in DoubanOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.douban_order.status == 1]))
    douban_orders += list(set([k.order for k in MediumOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.client_order.status == 1]))
    if douban_orders:
        douban_orders = sorted(
            douban_orders, key=lambda x: getattr(x, 'id'), reverse=True)
    if request.values.get('action', '') == 'download':
        response = write_douban_order_excel(douban_orders, year, month)
        return response
    return tpl('/data_query/profit/douban_order.html', year=int(year),
               month=int(month), douban_orders=douban_orders)
