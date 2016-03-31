# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template as tpl

saler_client_order_money_bp = Blueprint(
    'saler_client_order_money', __name__, template_folder='../../templates')


@saler_client_order_money_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    return tpl('/saler/client_order/money/index.html')
