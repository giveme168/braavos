# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template as tpl
from models.douban_order import DoubanOrder
saler_douban_order_money_bp = Blueprint(
    'saler_douban_order_money', __name__, template_folder='../../templates')


@saler_douban_order_money_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    order = DoubanOrder.get(order_id)
    return tpl('/saler/douban_order/money/index.html', order=order)
