# -*- coding: utf-8 -*-
from flask import Blueprint, abort
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.invoice import OutsourceInvoice


saler_client_order_outsource_bp = Blueprint(
    'saler_client_order_outsource', __name__, template_folder='../../templates')


@saler_client_order_outsource_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    outsources = []
    for k in range(1, 6):
        outsources += order.get_outsources_by_status(k)
    invoices = OutsourceInvoice.query.filter_by(client_order=order)
    return tpl('/saler/client_order/outsource/index.html', order=order, outsources=outsources, invoices=invoices)
