# -*- coding: utf-8 -*-
from flask import Blueprint, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder
from models.invoice import DoubanOutsourceInvoice


saler_douban_order_outsource_bp = Blueprint(
    'saler_douban_order_outsource', __name__, template_folder='../../templates')


@saler_douban_order_outsource_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    outsources = []
    for k in range(1, 6):
        outsources += order.get_outsources_by_status(k)
    invoices = DoubanOutsourceInvoice.query.filter_by(douban_order=order)
    return tpl('/saler/douban_order/outsource/index.html', order=order, outsources=outsources, invoices=invoices)
