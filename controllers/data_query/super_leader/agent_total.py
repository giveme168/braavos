# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.super_leader_helpers import write_agent_total_excel

from models.client_order import ClientOrder
from models.client import Group, Agent
data_query_super_leader_agent_total_bp = Blueprint(
    'data_query_super_leader_agent_total', __name__, template_folder='../../templates/data_query')


def pre_month_money(money, start, end):
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = []
    for k in pre_month_days:
        money = pre_money * k['days']
        pre_month_money_data.append({'month': k['month'], 'money': money})
    return pre_month_money_data


def _format_order(order, year):
    dict_order = {}
    dict_order['id'] = order.id
    dict_order['client_start'] = order.client_start
    dict_order['client_end'] = order.client_start
    dict_order['agent_id'] = order.agent.id
    dict_order['contract'] = order.contract
    dict_order['contract_status'] = order.contract_status
    dict_order['status'] = order.status
    dict_order['campaign'] = order.campaign
    direct_sales = order.direct_sales
    agent_sales = order.agent_sales
    sales = direct_sales + agent_sales
    pre_month_money_data = pre_month_money(order.money,
                                           dict_order['client_start'],
                                           dict_order['client_end'])
    start_date = datetime.datetime.strptime(str(year) + "-01", "%Y-%m").date()
    end_date = datetime.datetime.strptime(str(year) + "-12", "%Y-%m").date()
    r_money = sum([k['money'] for k in pre_month_money_data
                   if k['month'] >= start_date and k['month'] <= end_date])
    # 是否是媒介订单
    if 148 in [int(k.id) for k in sales]:
        dict_order['is_medium_money'] = r_money
        dict_order['is_sale_money'] = 0
    else:
        dict_order['is_medium_money'] = 0
        dict_order['is_sale_money'] = r_money
    return dict_order


@data_query_super_leader_agent_total_bp.route('/index', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    orders = [_format_order(k, year) for k in ClientOrder.all()]
    orders = [k for k in orders if k['client_start'].year == year]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 19, 20] and k['status'] == 1]
    # 获取所有代理
    agents = [{'name': a.name, 'id': a.id, 'group_id': a.group.id} for a in Agent.all()]
    # 获取代理集团
    groups = [{'name': gp.name, 'agents': [p for p in agents if p['group_id'] == gp.id]} for gp in Group.all()]
    # xxx_count 用于html合并表单
    agent_obj = []
    total_is_sale_money = 0
    total_is_medium_money = 0
    for k in groups:
        if not k['agents']:
            html_order_count = 0
        else:
            html_order_count = 1
        excel_order_count = 0
        agent_data = []
        for a in k['agents']:
            order_data = [o for o in orders if o['agent_id'] == a['id']]
            if order_data:
                html_order_count += len(order_data) + 1
                excel_order_count += len(order_data)
                total_is_sale_money += sum([o['is_sale_money'] for o in order_data])
                total_is_medium_money += sum([o['is_medium_money'] for o in order_data])
                agent_data.append({'name': a['name'], 'orders': order_data, 'html_order_count': len(order_data)})
        if agent_data:
            agent_obj.append({'name': k['name'], 'agents': agent_data, 'html_order_count': html_order_count,
                              'excel_order_count': excel_order_count})
    action = request.values.get('action', '')
    if action == 'excel':
        return write_agent_total_excel(year=year, agent_obj=agent_obj, total_is_sale_money=total_is_sale_money,
                                       total_is_medium_money=total_is_medium_money)
    return tpl('/data_query/super_leader/agent_total.html', year=year, agent_obj=agent_obj,
               total_is_sale_money=total_is_sale_money, total_is_medium_money=total_is_medium_money)
