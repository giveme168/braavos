# -*- coding: utf-8 -*-
from flask import Blueprint, abort
from flask import render_template as tpl

from models.client_order import ClientOrder

saler_client_order_back_money_bp = Blueprint(
    'saler_client_order_back_money', __name__, template_folder='../../templates/saler')


@saler_client_order_back_money_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    return tpl('/saler/client_order_back_money/index.html', order=order)
