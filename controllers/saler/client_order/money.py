# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template as tpl
from models.client_order import ClientOrder
saler_client_order_money_bp = Blueprint(
    'saler_client_order_money', __name__, template_folder='../../templates')


@saler_client_order_money_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    order = ClientOrder.get(order_id)
    return tpl('/saler/client_order/money/index.html', order=order)
