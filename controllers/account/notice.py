# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, jsonify, request
from flask import render_template as tpl

from models.account.data import Notice

account_notice_bp = Blueprint(
    'account_notice', __name__, template_folder='../../templates/account/notice/')


@account_notice_bp.route('/index', methods=['GET'])
def index():
    nid = int(request.values.get('nid', 0))
    if nid:
        notice = Notice.get(nid)
        s_date = datetime.datetime.strptime(
            notice.create_time.strftime('%Y-%m-%d'), '%Y-%m-%d')
        e_date = s_date + datetime.timedelta(days=1)
        notices = [{'id': k.id, 'title': k.title,
                    'create_time_cn': k.create_time_cn,
                    'content': k.content}
                   for k in Notice.all() if k.create_time >= s_date
                   and k.create_time <= e_date]
    else:
        notices = Notice.all()[:10]
        notice = None
    return tpl('/account/notice/index.html', notices=notices, nid=nid, notice=notice)


@account_notice_bp.route('/index_jsonp', methods=['GET', 'POST'])
def index_jsonp():
    date = request.values.get(
        'date', datetime.datetime.now().strftime('%Y-%m-%d'))
    s_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    e_date = s_date + datetime.timedelta(days=1)
    notices = [{'id': k.id, 'title': k.title,
                'create_time_cn': k.create_time_cn,
                'content': k.content}
               for k in Notice.all() if k.create_time >= s_date
               and k.create_time <= e_date]
    return jsonify({'data': notices})
