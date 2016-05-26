# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.super_leader_helpers import write_client_total_excel

from models.client import Client
from models.client_order import ClientOrder
from models.douban_order import DoubanOrder
from models.consts import CLIENT_INDUSTRY_CN

data_query_super_leader_client_total_bp = Blueprint(
    'data_query_super_leader_client_total', __name__, template_folder='../../templates/data_query')


def pre_month_money(money, start, end, locations):
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = []
    for k in pre_month_days:
        money = pre_money * k['days'] / len(set(locations))
        pre_month_money_data.append({'month': k['month'], 'money': money})
    return pre_month_money_data


def _format_order(order, year):
    dict_order = {}
    dict_order['table_name'] = order.__tablename__
    dict_order['id'] = order.id
    dict_order['client_start'] = order.client_start
    dict_order['client_end'] = order.client_start
    dict_order['agent_id'] = order.agent.id
    dict_order['agent_name'] = order.agent.name
    dict_order['client_id'] = order.client.id
    dict_order['industry'] = order.client.industry
    dict_order['contract'] = order.contract
    dict_order['contract_status'] = order.contract_status
    dict_order['status'] = order.status
    dict_order['campaign'] = order.campaign
    dict_order['locations'] = order.locations
    pre_month_money_data = pre_month_money(order.money,
                                           dict_order['client_start'],
                                           dict_order['client_end'],
                                           dict_order['locations'])
    # start_date = datetime.datetime.strptime(str(year) + "-01", "%Y-%m").date()
    # end_date = datetime.datetime.strptime(str(year) + "-12", "%Y-%m").date()
    Q1_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(1, 4)]
    Q2_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(4, 7)]
    Q3_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(7, 10)]
    Q4_monthes = [datetime.datetime.strptime(str(year) + "-" + str(k), "%Y-%m").date()
                  for k in range(10, 13)]
    dict_order['Q1_money'] = sum([k['money'] for k in pre_month_money_data
                                  if k['month'] >= Q1_monthes[0] and k['month'] <= Q1_monthes[-1]])
    dict_order['Q2_money'] = sum([k['money'] for k in pre_month_money_data
                                  if k['month'] >= Q2_monthes[0] and k['month'] <= Q2_monthes[-1]])
    dict_order['Q3_money'] = sum([k['money'] for k in pre_month_money_data
                                  if k['month'] >= Q3_monthes[0] and k['month'] <= Q3_monthes[-1]])
    dict_order['Q4_money'] = sum([k['money'] for k in pre_month_money_data
                                  if k['month'] >= Q4_monthes[0] and k['month'] <= Q4_monthes[-1]])
    return dict_order


def _format_location_data(industry_obj, orders, location):
    location_data = []
    total_Q1_money = 0
    total_Q2_money = 0
    total_Q3_money = 0
    total_Q4_money = 0
    for i in industry_obj:
        clients = i['clients']
        if clients:
            html_order_count = 1
        else:
            html_order_count = 0
        excel_order_count = 0
        client_data = []
        for c in clients:
            order_data = [k for k in orders if int(c['id']) == int(k['client_id']) and location in k['locations']]
            if order_data:
                total_Q1_money += sum([k['Q1_money'] for k in order_data])
                total_Q2_money += sum([k['Q2_money'] for k in order_data])
                total_Q3_money += sum([k['Q3_money'] for k in order_data])
                total_Q4_money += sum([k['Q4_money'] for k in order_data])
                html_order_count += len(order_data) + 1
                excel_order_count += len(order_data)
                client_data.append({'name': c['name'], 'orders': order_data, 'html_order_count': len(order_data)})
        if client_data:
            location_data.append({'name': i['name'], 'clients': client_data, 'html_order_count': html_order_count,
                                  'excel_order_count': excel_order_count})
    return {'location_data': location_data,
            'total_Q1_money': total_Q1_money,
            'total_Q2_money': total_Q2_money,
            'total_Q3_money': total_Q3_money,
            'total_Q4_money': total_Q4_money}


@data_query_super_leader_client_total_bp.route('/client_order', methods=['GET'])
def client_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    orders = [_format_order(k, year) for k in ClientOrder.all()]
    orders = [k for k in orders if k['client_start'].year == year]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 19, 20] and k['status'] == 1]
    # 获取行业
    industry_data = [{'id': k, 'name': CLIENT_INDUSTRY_CN[k]} for k in CLIENT_INDUSTRY_CN]
    # 获取所有客户
    client_data = [{'id': k.id, 'name': k.name, 'industry': k.industry} for k in Client.all()]
    # 行业合并客户
    industry_obj = []
    for i in industry_data:
        i['clients'] = [k for k in client_data if k['industry'] == i['id']]
        if i['clients']:
            industry_obj.append(i)
    HB_data = _format_location_data(industry_obj, orders, 1)
    HD_data = _format_location_data(industry_obj, orders, 2)
    HN_data = _format_location_data(industry_obj, orders, 3)

    action = request.values.get('action', '')
    if action == 'excel':
        return write_client_total_excel(year, HB_data=HB_data, HD_data=HD_data, HN_data=HN_data, type="client")
    return tpl('/data_query/super_leader/client_total.html', year=year, HB_data=HB_data,
               HD_data=HD_data, HN_data=HN_data)


@data_query_super_leader_client_total_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    orders = [_format_order(k, year) for k in DoubanOrder.all()]
    orders = [k for k in orders if k['client_start'].year == year]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 19, 20] and k['status'] == 1]
    # 获取行业
    industry_data = [{'id': k, 'name': CLIENT_INDUSTRY_CN[k]} for k in CLIENT_INDUSTRY_CN]
    # 获取所有客户
    client_data = [{'id': k.id, 'name': k.name, 'industry': k.industry} for k in Client.all()]
    # 行业合并客户
    industry_obj = []
    for i in industry_data:
        i['clients'] = [k for k in client_data if k['industry'] == i['id']]
        if i['clients']:
            industry_obj.append(i)
    HB_data = _format_location_data(industry_obj, orders, 1)
    HD_data = _format_location_data(industry_obj, orders, 2)
    HN_data = _format_location_data(industry_obj, orders, 3)

    action = request.values.get('action', '')
    if action == 'excel':
        return write_client_total_excel(year, HB_data=HB_data, HD_data=HD_data, HN_data=HN_data, type="douban")
    return tpl('/data_query/super_leader/client_total.html', year=year, HB_data=HB_data,
               HD_data=HD_data, HN_data=HN_data)
