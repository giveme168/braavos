# -*- coding: utf-8 -*-
from flask import Blueprint, g, abort
from flask import render_template as tpl


account_performance_bp = Blueprint(
    'account_performance', __name__, template_folder='../../templates/account/performance/')


@account_performance_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_leader() or g.user.is_super_leader()):
        return abort(404)
    return tpl('/account/performance/index.html')
