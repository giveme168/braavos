# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import render_template as tpl

from models.account.data import Notice

account_notice_bp = Blueprint(
    'account_notice', __name__, template_folder='../../templates/account/notice/')


@account_notice_bp.route('/index', methods=['GET'])
def index():
    notice = Notice.all()
    return tpl('/account/notice/index.html', notice=notice)
