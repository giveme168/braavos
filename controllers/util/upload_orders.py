# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import render_template as tpl


util_upload_orders_bp = Blueprint(
    'util_upload_orders', __name__, template_folder='../../templates/util')


@util_upload_orders_bp.route('/', methods=['GET', 'POST'])
def index():
    # xls_orders = request.files.get('upload_file')
    return tpl('upload_orders.html')
