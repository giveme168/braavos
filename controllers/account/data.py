# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import render_template as tpl

account_data_bp = Blueprint(
    'account_data', __name__, template_folder='../../templates/account/data/')


@account_data_bp.route('/handbook', methods=['GET'])
def handbook():
    return tpl('/account/data/handbook.html')
