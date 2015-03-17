# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask import render_template as tpl


operater_outsource_bp = Blueprint(
    'operater_outsource', __name__, template_folder='../../templates/operater')


@operater_outsource_bp.route('/', methods=['GET'])
def index():
    return tpl('/outsource/index.html', order=[])
