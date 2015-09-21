# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import render_template as tpl


finance_client_order_data_query_bp = Blueprint(
    'finance_client_order_data_query', __name__, template_folder='../../templates/finance/data_query')


@finance_client_order_data_query_bp.route('/agent_invoice', methods=['GET'])
def agent_invoice():
    return tpl('/finance/client_order/data_query/agent_invoice.html')
