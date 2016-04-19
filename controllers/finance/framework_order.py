# -*- coding: utf-8 -*-
import datetime

from flask import request, Blueprint, abort, g, render_template as tpl

from models.user import TEAM_LOCATION_CN
from libs.paginator import Paginator
from models.framework_order import FrameworkOrder, CONTRACT_STATUS_CN

finance_framework_order_bp = Blueprint(
    'finance_framework_order', __name__, template_folder='../../templates/finance/framework_order')


ORDER_PAGE_NUM = 50


@finance_framework_order_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = list(FrameworkOrder.all())
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1

    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.datetime.now().year))
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower() in o.search_info.lower()]
    orders = [k for k in orders if k.client_start.year == year or k.client_end.year == year]
    if orderby and len(orders):
        orders = sorted(
            orders, key=lambda x: getattr(x, orderby), reverse=True)
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    paginator = Paginator(orders, ORDER_PAGE_NUM)
    try:
        orders = paginator.page(page)
    except:
        orders = paginator.page(paginator.num_pages)
    return tpl('/finance/framework_order/index.html', orders=orders,
               locations=select_locations, location_id=location_id,
               statuses=select_statuses, status_id=status_id,
               orderby=orderby, now_date=datetime.date.today(),
               search_info=search_info, page=page, year=year,
               params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s&year=%s' %
                      (orderby, search_info, location_id, status_id, str(year)))


@finance_framework_order_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    if not g.user.is_finance():
        abort(404)
    order = FrameworkOrder.get(order_id)
    if not order or order.status == 0:
        abort(404)
    return tpl('/finance/framework_order/info.html', order=order)
