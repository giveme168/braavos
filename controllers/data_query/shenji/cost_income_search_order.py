# -*- coding: UTF-8 -*-

from flask import Blueprint, g, abort
from flask import render_template as tpl

cost_income_search_order_bp = Blueprint(
    'data_query_shenji_cost_income_search_order', __name__,
    template_folder='../../templates/data_query')


@cost_income_search_order_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    return tpl('/shenji/cost_income_search_order.html')
