# -*- coding: UTF-8 -*-
import datetime
import operator

from flask import Blueprint, request, abort, g
from flask import render_template as tpl

from models.medium import Medium
from libs.date_helpers import get_monthes_pre_days
from models.order import MediumOrderExecutiveReport
from controllers.data_query.helpers.medium_helpers import write_client_excel


data_query_medium_bp = Blueprint(
    'data_query_medium', __name__, template_folder='../../templates/data_query')


def _parse_dict_order(order):
    d_order = {}
    d_order['month_day'] = order.month_day
    d_order['medium_id'] = order.order.medium.id
    d_order['money'] = order.client_order.money
    d_order['contract_status'] = order.client_order.contract_status
    d_order['sale_money'] = order.sale_money
    d_order['medium_money2'] = order.medium_money2
    medium_rebate = order.order.medium_rebate_by_year(d_order['month_day'])
    agent_rebate = order.client_order.agent_rebate
    d_order['medium_rebate_value'] = d_order['medium_money2'] * medium_rebate / 100
    d_order['agent_rebate_value'] = d_order['sale_money'] * agent_rebate / 100
    # 单笔返点
    try:
        self_agent_rebate = order.client_order.self_agent_rebate
        d_order['self_agent_rebate'] = int(self_agent_rebate.split('-')[0])
        d_order['agent_rebate_value'] = int(self_agent_rebate.split('-')[1])
    except:
        d_order['self_agent_rebate'] = 0
        d_order['agent_rebate_value'] = 0
    d_order['status'] = order.status
    return d_order


@data_query_medium_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_media_leader()):
        return abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    start_date_month = datetime.datetime.strptime(
        str(year) + '-01' + '-01', '%Y-%m-%d')
    end_date_month = datetime.datetime.strptime(
        str(year) + '-12' + '-31', '%Y-%m-%d')
    pre_monthes = get_monthes_pre_days(start_date_month, end_date_month)
    medium_id = int(request.values.get('medium_id', 0))

    ex_medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)
    ex_medium_orders = [_parse_dict_order(k) for k in ex_medium_orders]
    ex_medium_orders = [k for k in ex_medium_orders if k[
        'contract_status'] not in [0, 7, 8, 9] and k['status'] == 1]

    medium_data = []
    if medium_id:
        mediums = Medium.query.filter_by(id=medium_id)
    else:
        mediums = Medium.all()
    for k in mediums:
        sale_money_data = []
        medium_money2_data = []
        medium_rebate_data = []
        agent_rebate_data = []
        for i in pre_monthes:
            sale_money_data.append(sum([ex['sale_money'] for ex in ex_medium_orders if ex[
                                   'medium_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
            medium_money2_data.append(sum([ex['medium_money2'] for ex in ex_medium_orders if ex[
                                      'medium_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
            medium_rebate_data.append(sum([ex['medium_rebate_value'] for ex in ex_medium_orders if ex[
                                      'medium_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
            agent_rebate_data.append(sum([ex['agent_rebate_value'] for ex in ex_medium_orders if ex[
                                     'medium_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
        medium_data.append({'id': k.id, 'name': k.name,
                            'level': k.level or 100,
                            'sale_money_data': sale_money_data,
                            'medium_money2_data': medium_money2_data,
                            'medium_rebate_data': medium_rebate_data,
                            'agent_rebate_data': agent_rebate_data})
    medium_data = sorted(medium_data, key=operator.itemgetter('level'), reverse=False)
    if request.values.get('action', '') == 'download':
        return write_client_excel(medium_data, year)
    return tpl('/data_query/medium/index.html', medium_data=medium_data, medium_id=medium_id,
               year=year, params="?medium_id=%s&year=%s" % (medium_id, str(year)),
               s_mediums=Medium.all())
