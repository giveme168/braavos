# -*- coding: utf-8 -*-
from flask import Blueprint, abort
from flask import render_template as tpl

from searchAd.models.client_order import searchAdClientOrder

searchAd_saler_client_order_back_money_bp = Blueprint(
    'searchAd_saler_client_order_back_money', __name__, template_folder='../../../../templates/saler')


@searchAd_saler_client_order_back_money_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    order = searchAdClientOrder.get(order_id)
    if not order:
        abort(404)
    return tpl('/saler/searchAd_order/back_money/index.html', order=order)
