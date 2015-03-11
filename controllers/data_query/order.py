# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask import render_template as tpl

data_query_order_bp = Blueprint('data_query_order', __name__, template_folder='../../templates/data_query/order')


@data_query_order_bp.route('/', methods=['GET'])
def index():
    return tpl('index.html')
