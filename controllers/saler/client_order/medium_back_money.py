# -*- coding: utf-8 -*-
from flask import Blueprint, abort
from flask import render_template as tpl

from models.client_order import ClientOrder, MediumBackMoney

saler_client_order_medium_back_money_bp = Blueprint(
    'saler_client_order_medium_back_money', __name__, template_folder='../../templates/saler')


@saler_client_order_medium_back_money_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    order = ClientOrder.get(order_id)
    back_moneys = MediumBackMoney.query.filter_by(client_order_id=order_id)
    if not order:
        abort(404)
    return tpl('/saler/client_order/medium_back_money/index.html', order=order, back_moneys=back_moneys)
