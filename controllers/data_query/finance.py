# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.medium import Medium


data_query_finance_bp = Blueprint(
    'data_query_finance', __name__, template_folder='../../templates/data_query')


@data_query_finance_bp.route('/order', methods=['GET'])
def order():
    now_date = datetime.datetime.now()
    medium_id = int(request.values.get('medium_id', 0))
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    # now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    return tpl('/data_query/finance/order.html', mediums=Medium.all(),
               year=int(year), month=int(month), medium_id=medium_id)
