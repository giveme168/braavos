# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.client_order import ClientOrderExecutiveReport

data_query_finance_bp = Blueprint(
    'data_query_finance', __name__, template_folder='../../templates/data_query')


@data_query_finance_bp.route('/order', methods=['GET'])
def order():
    now_date = datetime.datetime.now()
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    client_orders = list(set([k.client_order for k in ClientOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.client_order.status == 1]))
    return tpl('/data_query/finance/order.html', year=int(year),
               month=int(month), client_orders=client_orders)
