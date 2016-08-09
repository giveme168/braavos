# -*- coding: UTF-8 -*-
import datetime
import operator

from flask import Blueprint, request, abort, g
from flask import render_template as tpl

from models.medium import Media
from libs.date_helpers import get_monthes_pre_days
from models.order import Order
from controllers.data_query.helpers.medium_helpers import write_client_excel


data_query_medium_bp = Blueprint(
    'data_query_medium', __name__, template_folder='../../templates/data_query')


def _parse_dict_order(order):
    d_order = {}
    d_order['month_day'] = order.month_day
    d_order['media_id'] = order.order.media.id
    d_order['money'] = order.client_order.money
    d_order['order_sale_money'] = order.order.sale_money
    d_order['contract_status'] = order.client_order.contract_status
    d_order['sale_money'] = order.sale_money
    d_order['medium_money2'] = order.medium_money2
    medium_rebate = order.order.medium_rebate_by_year(d_order['month_day'])
    agent_rebate = order.client_order.agent_rebate
    d_order['medium_rebate_value'] = d_order[
        'medium_money2'] * medium_rebate / 100
    # 单笔返点
    try:
        self_agent_rebate = order.client_order.self_agent_rebate
        d_order['self_agent_rebate'] = float(self_agent_rebate.split('-')[0])
        d_order['self_agent_rebate_value'] = float(
            self_agent_rebate.split('-')[1])
    except:
        d_order['self_agent_rebate'] = 0
        d_order['self_agent_rebate_value'] = 0
    if d_order['self_agent_rebate']:
        if d_order['money']:
            d_order['agent_rebate_value'] = d_order[
                'self_agent_rebate_value'] * d_order['sale_money'] / d_order['money']
        else:
            d_order['agent_rebate_value'] = 0
    else:
        d_order['agent_rebate_value'] = d_order[
            'sale_money'] * agent_rebate / 100
    d_order['status'] = order.client_order.status
    return d_order


def pre_month_money(money, start, end):
    start = datetime.datetime.strptime(start.strftime('%Y-%m-%d'), '%Y-%m-%d')
    end = datetime.datetime.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d')
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = []
    for k in pre_month_days:
        pre_month_money_data.append({'month_day': k['month'], 'money': pre_money * k['days']})
    return pre_month_money_data


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
    media_id = int(request.values.get('media_id', 0))

    ex_medium_orders = [o for o in Order.all(
    ) if o.medium_start.year == year or o.medium_end.year == year]
    obj_data = []
    for order in ex_medium_orders:
        pre_month_sale_money = pre_month_money(order.sale_money, order.medium_start, order.medium_end)
        pre_month_medium_money2 = pre_month_money(order.medium_money2, order.medium_start, order.medium_end)
        # 单笔返点
        agent_rebate = order.client_order.agent_rebate
        try:
            self_agent_rebate = order.client_order.self_agent_rebate
            self_agent_rebate = float(self_agent_rebate.split('-')[0])
            self_agent_rebate_value = float(self_agent_rebate.split('-')[1])
        except:
            self_agent_rebate = 0
            self_agent_rebate_value = 0
        for p in range(len(pre_month_sale_money)):
            d_order = {}
            d_order['media_id'] = order.media.id
            d_order['money'] = order.client_order.money
            d_order['contract_status'] = order.client_order.contract_status
            d_order['status'] = order.client_order.status
            d_order['sale_money'] = pre_month_sale_money[p]['money']
            d_order['medium_money2'] = pre_month_medium_money2[p]['money']
            d_order['month_day'] = pre_month_sale_money[p]['month_day']
            medium_rebate = order.medium_rebate_by_year(d_order['month_day'])
            # 媒体单笔返点
            try:
                self_medium_rebate_data = order.self_medium_rebate
                self_medium_rebate = self_medium_rebate_data.split('-')[0]
                self_medium_rebate_value = float(self_medium_rebate_data.split('-')[1])
            except:
                self_medium_rebate = 0
                self_medium_rebate_value = 0
            if int(self_medium_rebate):
                if d_order['sale_money']:
                    d_order['medium_rebate_value'] = d_order['sale_money'] / d_order['money'] * self_medium_rebate_value
                else:
                    d_order['medium_rebate_value'] == 0
            else:
                d_order['medium_rebate_value'] = d_order['medium_money2'] * medium_rebate / 100

            if self_agent_rebate:
                if d_order['money']:
                    d_order['agent_rebate_value'] = self_agent_rebate_value * d_order['sale_money'] / d_order['money']
                else:
                    d_order['agent_rebate_value'] = 0
            else:
                d_order['agent_rebate_value'] = d_order['sale_money'] * agent_rebate / 100
            obj_data.append(d_order)
    ex_medium_orders = [k for k in obj_data if k[
        'contract_status'] not in [0, 1, 3, 6, 7, 8, 81, 9] and k['status'] == 1]

    medium_data = []
    if media_id:
        medias = Media.query.filter_by(id=media_id)
    else:
        medias = Media.all()
    sum_sale_money = 0
    for k in medias:
        sale_money_data = []
        medium_money2_data = []
        medium_rebate_data = []
        agent_rebate_data = []
        for i in pre_monthes:
            sale_money_data.append(sum([ex['sale_money'] for ex in ex_medium_orders if ex[
                                   'media_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
            medium_money2_data.append(sum([ex['medium_money2'] for ex in ex_medium_orders if ex[
                                      'media_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
            medium_rebate_data.append(sum([ex['medium_rebate_value'] for ex in ex_medium_orders if ex[
                                      'media_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
            agent_rebate_data.append(sum([ex['agent_rebate_value'] for ex in ex_medium_orders if ex[
                                     'media_id'] == k.id and ex['month_day'].date() == i['month'].date()]))
        sum_sale_money += sum(sale_money_data)
        medium_data.append({'id': k.id, 'name': k.name,
                            'level': k.level or 100,
                            'sale_money_data': sale_money_data,
                            'medium_money2_data': medium_money2_data,
                            'medium_rebate_data': medium_rebate_data,
                            'agent_rebate_data': agent_rebate_data})
    medium_data = sorted(
        medium_data, key=operator.itemgetter('level'), reverse=False)
    if request.values.get('action', '') == 'download':
        return write_client_excel(medium_data, year)
    return tpl('/data_query/medium/index.html', medium_data=medium_data, media_id=media_id,
               year=year, params="?media_id=%s&year=%s" % (media_id, str(year)),
               s_medias=Media.all())
