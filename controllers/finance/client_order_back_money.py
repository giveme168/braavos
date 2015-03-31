# -*- coding: utf-8 -*-
from flask import request, Blueprint, abort
from flask import render_template as tpl

from models.user import TEAM_LOCATION_CN
from models.client_order import ClientOrder, CONTRACT_STATUS_CN

finance_client_order_back_money_bp = Blueprint(
    'finance_client_order_back_money', __name__, template_folder='../../templates/finance')


ORDER_PAGE_NUM = 50


@finance_client_order_back_money_bp.route('/orders', methods=['GET'])
def index():
    orders = list(ClientOrder.all())
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1
    sortby = request.args.get('sortby', '')
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    reverse = orderby != 'asc'
    page = int(request.args.get('p', 1))
    page = max(1, page)
    start = (page - 1) * ORDER_PAGE_NUM
    orders_len = len(orders)
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [o for o in orders if search_info in o.search_info]
    if sortby and orders_len and hasattr(orders[0], sortby):
        orders = sorted(
            orders, key=lambda x: getattr(x, sortby), reverse=reverse)
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    if 0 <= start < orders_len:
        orders = orders[start:min(start + ORDER_PAGE_NUM, orders_len)]
    else:
        orders = []

    return tpl('/finance/client_order_back_money/index.html', orders=orders,
               locations=select_locations, location_id=location_id,
               statuses=select_statuses, status_id=status_id,
               sortby=sortby, orderby=orderby,
               search_info=search_info, page=page)


@finance_client_order_back_money_bp.route('/order/<order_id>/back_money', methods=['GET', 'POST'])
def back_money(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    return tpl('/finance/client_order_back_money/info.html', order=order)
