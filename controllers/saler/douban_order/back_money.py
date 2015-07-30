# -*- coding: utf-8 -*-
from flask import Blueprint, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder

saler_douban_order_back_money_bp = Blueprint(
    'saler_douban_order_back_money', __name__, template_folder='../../templates/saler/douban_order')


@saler_douban_order_back_money_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    return tpl('/saler/douban_order/back_money/index.html', order=order)
