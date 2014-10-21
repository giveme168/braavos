# -*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, url_for
from flask import render_template as tpl, jsonify
from datetime import datetime, timedelta
from collections import defaultdict

from models.consts import DATE_FORMAT
from models.medium import Medium, AdPosition

storage_bp = Blueprint('storage', __name__, template_folder='../templates/storage')


@storage_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('storage.storage'))


@storage_bp.route('/storage', methods=['GET'])
def storage():
    dates_info = {}
    start_str = request.args.get('start_date', datetime.now().strftime(DATE_FORMAT))
    start = datetime.strptime(start_str, DATE_FORMAT).date()
    m_dict = defaultdict(list)
    dates_list = []
    for x in range(0, 30):
        current = start + timedelta(days=x)
        m_dict[current.month].append(current)
        dates_list.append(current)
    dates_info['dates'] = dates_list
    dates_info['months'] = [(m, len(d_list)) for m, d_list in m_dict.items()]
    medium_id = int(request.args.get('selected_medium', 0))
    select_medium = [(m.id, m.name) for m in Medium.all()]
    select_medium.insert(0, (0, u'全部媒体'))
    positions_info = AdPosition.all_positions_info_by_date()
    if medium_id:
        medium = Medium.get(medium_id)
        positions_info = medium.positions_info_by_date()
    return tpl('storage.html', dates_info=dates_info, medium=select_medium,
               medium_id=medium_id, positions_info=positions_info, start_date=start_str,
               per_start_date=(start - timedelta(days=30)).strftime(DATE_FORMAT),
               next_start_date=(start + timedelta(days=30)).strftime(DATE_FORMAT))


@storage_bp.route('/storage_info/', methods=['GET'])
def storage_info():
    """ajax 获取库存数据"""
    date = datetime.strptime(request.values.get('date'), DATE_FORMAT).date()
    position = AdPosition.get(request.values.get('position_id'))
    return jsonify(position.get_storage_info(date))
