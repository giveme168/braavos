# -*- coding: UTF-8 -*-
import datetime
import operator

from flask import Blueprint, request, abort, g
from flask import render_template as tpl

from models.medium import Media
from models.client import AgentMediaRebate, AgentRebate
from models.medium import MediumGroupRebate, MediumGroupMediaRebate
from libs.date_helpers import get_monthes_pre_days
from models.order import Order
from controllers.data_query.helpers.medium_helpers import write_client_excel


data_query_medium_bp = Blueprint(
    'data_query_medium', __name__, template_folder='../../templates/data_query')


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
    all_agent_rebate_data = [{'agent_id': k.agent_id, 'inad_rebate': k.inad_rebate,
                              'douban_rebate': k.douban_rebate, 'year': k.year} for k in AgentRebate.all()]
    all_medium_rebate_data = [{'media_id': k.media_id, 'rebate': k.rebate, 'medium_group_id': k.medium_group.id,
                               'year': k.year} for k in MediumGroupMediaRebate.all()]
    all_medium_group_rebate_data = [{'rebate': k.rebate, 'medium_group_id': k.medium_group.id,
                                     'year': k.year} for k in MediumGroupRebate.all()]
    all_agent_media_rebate_data = [{'agent_id': k.agent.id, 'media_id': k.media.id, 'year': k.year,
                                    'rebate': k.rebate} for k in AgentMediaRebate.all()]
    pre_monthes = get_monthes_pre_days(start_date_month, end_date_month)
    media_id = int(request.values.get('media_id', 0))
    ex_medium_orders = [o for o in Order.all(
    ) if o.medium_start.year == year or o.medium_end.year == year]
    obj_data = []
    for order in ex_medium_orders:
        pre_month_sale_money = pre_month_money(order.sale_money, order.medium_start, order.medium_end)
        pre_month_medium_money2 = pre_month_money(order.medium_money2, order.medium_start, order.medium_end)
        # 单笔返点
        try:
            self_agent_rebate_data = order.client_order.self_agent_rebate
            self_agent_rebate = float(self_agent_rebate_data.split('-')[0])
            self_agent_rebate_value = float(self_agent_rebate_data.split('-')[1])
        except:
            self_agent_rebate = 0
            self_agent_rebate_value = 0
        for p in range(len(pre_month_sale_money)):
            try:
                d_order = {}
                d_order['media_id'] = order.media.id
                d_order['money'] = order.client_order.money
                d_order['contract_status'] = order.client_order.contract_status
                d_order['contract'] = order.client_order.contract
                d_order['status'] = order.client_order.status
                d_order['order_id'] = order.client_order.id
                d_order['sale_money'] = pre_month_sale_money[p]['money']
                d_order['all_sale_money'] = order.client_order.money
                d_order['medium_money2'] = pre_month_medium_money2[p]['money']
                d_order['all_medium_money2'] = order.medium_money2
                d_order['month_day'] = pre_month_sale_money[p]['month_day']
                # 客户返点系数
                if int(self_agent_rebate):
                    if d_order['all_sale_money']:
                        d_order['agent_rebate_value'] = d_order['sale_money'] / \
                            d_order['all_sale_money'] * self_agent_rebate_value
                    else:
                        d_order['agent_rebate_value'] = 0
                else:
                    # 是否有代理针对媒体的特殊返点
                    agent_media_rebate = [k['rebate'] for k in all_agent_media_rebate_data
                                          if order.client_order.agent.id == k['agent_id'] and
                                          d_order['month_day'].year == k['year'].year and
                                          order.media.id == k['media_id']]
                    if agent_media_rebate:
                        agent_rebate = agent_media_rebate[0]
                    else:
                        agent_rebate_data = [k['inad_rebate'] for k in all_agent_rebate_data
                                             if order.client_order.agent.id == k['agent_id'] and
                                             d_order['month_day'].year == k['year'].year]
                        if agent_rebate_data:
                            agent_rebate = agent_rebate_data[0]
                        else:
                            agent_rebate = 0
                    d_order['agent_rebate_value'] = agent_rebate / 100 * d_order['sale_money']
                # 媒体返点系数
                # 是否有媒体单笔返点
                try:
                    self_medium_rebate_data = order.self_medium_rebate
                    self_medium_rebate = self_medium_rebate_data.split('-')[0]
                    self_medium_rebate_value = float(self_medium_rebate_data.split('-')[1])
                except:
                    self_medium_rebate = 0
                    self_medium_rebate_value = 0
                if int(self_medium_rebate):
                    if d_order['all_medium_money2']:
                        d_order['medium_rebate_value'] = d_order['medium_money2'] / \
                            d_order['all_medium_money2'] * self_medium_rebate_value
                    else:
                        d_order['medium_rebate_value'] = 0
                else:
                    # 是否有媒体供应商针对媒体的特殊返点
                    medium_rebate_data = [k['rebate'] for k in all_medium_rebate_data
                                          if order.media.id == k['media_id'] and
                                          d_order['month_day'].year == k['year'].year and
                                          order.medium_group.id == k['medium_group_id']]
                    if medium_rebate_data:
                        medium_rebate = medium_rebate_data[0]
                    else:
                        # 是否有媒体供应商返点
                        medium_group_rebate = [k['rebate'] for k in all_medium_group_rebate_data
                                               if d_order['month_day'].year == k['year'].year and
                                               order.medium_group.id == k['medium_group_id']]
                        if medium_group_rebate:
                            medium_rebate = medium_group_rebate[0]
                        else:
                            medium_rebate = 0
                    d_order['medium_rebate_value'] = medium_rebate / 100 * d_order['medium_money2']
                obj_data.append(d_order)
            except:
                pass
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
