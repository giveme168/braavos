# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, g, abort
from flask import render_template as tpl

from models.user import TEAM_LOCATION_CN
from models.client_order import ClientOrder, CONTRACT_STATUS_CN
from models.invoice import OutsourceInvoice
from libs.paginator import Paginator


finance_client_order_outsource_invoice_bp = Blueprint(
    'finance_client_order_outsource_invoice', __name__, template_folder='../../templates/finance/client_order')


ORDER_PAGE_NUM = 50


@finance_client_order_outsource_invoice_bp.route('/index', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = list(ClientOrder.all())
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.datetime.now().year))
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    orders = [k for k in orders if k.client_start.year == year or k.client_end.year == year]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower() in o.search_invoice_info.lower()]
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
    for k in orders.object_list:
        k.ex_money = sum(
            [i.ex_money for i in OutsourceInvoice.query.filter_by(client_order=k)])
        k.pay_num = sum([i.pay_num for i in k.get_outsources_by_status(4)])
        apply_outsources = []
        for i in [1, 2, 3, 5]:
            apply_outsources += k.get_outsources_by_status(i)
        k.apply_money = sum([j.pay_num for j in apply_outsources])
    return tpl('/finance/client_order/outsource/invoice.html', orders=orders, locations=select_locations,
               location_id=location_id, statuses=select_statuses, orderby=orderby,
               now_date=datetime.date.today(), search_info=search_info, page=page, year=year,
               params='&orderby=%s&searchinfo=%s&selected_location=%s&year=%s' %
                      (orderby, search_info, location_id, year))


@finance_client_order_outsource_invoice_bp.route('/<order_id>/info', methods=['GET', 'POST'])
def info(order_id):
    if not g.user.is_finance():
        abort(404)
    order = ClientOrder.get(order_id)
    outsources = order.get_outsources_by_status(4)
    apply_outsources = []
    for k in [1, 2, 3, 5]:
        apply_outsources += order.get_outsources_by_status(k)
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    invoices = OutsourceInvoice.query.filter_by(client_order=order)
    if request.method == 'POST':
        OutsourceInvoice.add(
            client_order=order,
            company=request.values.get('company', ''),
            money=float(request.values.get('money', 0)),
            ex_money=float(request.values.get('ex_money', 0)),
            invoice_num=request.values.get('invoice_num', ''),
            add_time=request.values.get('add_time', now_date),
            create_time=datetime.datetime.now(),
            creator=g.user
        )
        return redirect(url_for('finance_client_order_outsource_invoice.info', order_id=order.id))
    return tpl('/finance/client_order/outsource/invoice_info.html', order=order, outsources=outsources,
               now_date=now_date, invoices=invoices, apply_outsources=apply_outsources)


@finance_client_order_outsource_invoice_bp.route('<order_id>/invoice/<invoice_id>/delete', methods=['GET', 'POST'])
def delete(order_id, invoice_id):
    if not g.user.is_finance():
        abort(404)
    OutsourceInvoice.get(invoice_id).delete()
    return redirect(url_for('finance_client_order_outsource_invoice.info', order_id=order_id))
