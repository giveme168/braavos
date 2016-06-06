# -*- coding: utf-8 -*-
from flask import Blueprint, abort
from flask import render_template as tpl

from models.client_medium_order import ClientMediumOrder

saler_client_medium_order_back_money_bp = Blueprint(
    'saler_client_medium_order_back_money', __name__, template_folder='../../templates/saler')


@saler_client_medium_order_back_money_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    order = ClientMediumOrder.get(order_id)
    if not order:
        abort(404)
    return tpl('/saler/client_medium_order/back_money/index.html', order=order)
