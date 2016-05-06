# -*- coding: UTF-8 -*-
import datetime
import operator
import numpy

from flask import request, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder, BackMoney, BackInvoiceRebate
from models.client_order import ClientOrder, BackMoney as ClientBackMoney
from models.client_order import BackInvoiceRebate as ClientBackInvoiceRebate
from models.order import Order
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.accrued_helpers import write_order_excel
from flask import Blueprint

data_query_accrued_bp = Blueprint(
    'data_query_accrued', __name__,
    template_folder='../../templates/data_query')


def _all_client_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.client_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in ClientBackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.client_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in ClientBackInvoiceRebate.all()]
    return dict_back_money_data


def _all_douban_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.douban_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in BackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.douban_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in BackInvoiceRebate.all()]
    return dict_back_money_data


def pre_month_money(money, start, end):
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = {}
    for k in pre_month_days:
        pre_month_money_data[k['month']] = pre_money * k['days']
    return pre_month_money_data


def _client_order_to_dict(client_order, all_back_moneys, pre_year_month, location):
    dict_order = {}
    dict_order['locations_cn'] = client_order.locations_cn
    dict_order['client_name'] = client_order.client.name
    dict_order['agent_name'] = client_order.agent.name
    dict_order['campaign'] = client_order.campaign
    dict_order['industry_cn'] = client_order.client.industry_cn
    dict_order['locations'] = client_order.locations
    dict_order['contract_status'] = client_order.contract_status
    dict_order['contract'] = client_order.contract
    dict_order['resource_type_cn'] = client_order.resource_type_cn
    dict_order['start_date_cn'] = client_order.start_date_cn
    dict_order['end_date_cn'] = client_order.end_date_cn
    dict_order['reminde_date_cn'] = client_order.reminde_date_cn
    dict_order['sale_type'] = client_order.sale_type_cn
    dict_order['money'] = client_order.money
    dict_order['back_moneys'] = sum(
        [k['money'] for k in all_back_moneys if k['order_id'] == client_order.id])
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        client_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        client_order.client_end.strftime(dt_format), dt_format)
    money_ex_data = pre_month_money(client_order.money,
                                    start_datetime,
                                    end_datetime)
    # 计算跨区系数
    if location == 0:
        rate = 1
    else:
        if location in dict_order['locations']:
            if len(dict_order['locations']) > 1:
                agent_location = list(
                    set([k.location for k in client_order.agent_sales]))
                direct_location = list(
                    set([k.location for k in client_order.direct_sales]))
                if (location in agent_location) and (location not in direct_location):
                    if len(direct_location) > 0:
                        rate = 0.5
                    else:
                        rate = 1
                    rate = float(rate) / len(agent_location)
                elif (location in direct_location) and (location not in agent_location):
                    if len(agent_location) > 0:
                        rate = 0.5
                    else:
                        rate = 1
                    rate = float(rate) / len(direct_location)
                else:
                    rate = 0.5 / len(agent_location)
                    rate += 0.5 / len(direct_location)

            else:
                rate = 1
        else:
            rate = 0
    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']] * rate)
        else:
            dict_order['money_data'].append(0)
    dict_order['medium_data'] = []
    return dict_order


def _douban_order_to_dict(douban_order, all_back_moneys, pre_year_month, location):
    dict_order = {}
    dict_order['locations_cn'] = douban_order.locations_cn
    dict_order['client_name'] = douban_order.client.name
    dict_order['agent_name'] = douban_order.agent.name
    dict_order['campaign'] = douban_order.campaign
    dict_order['industry_cn'] = douban_order.client.industry_cn
    dict_order['locations'] = douban_order.locations
    dict_order['contract_status'] = douban_order.contract_status
    dict_order['contract'] = douban_order.contract
    dict_order['resource_type_cn'] = douban_order.resource_type_cn
    dict_order['start_date_cn'] = douban_order.start_date_cn
    dict_order['end_date_cn'] = douban_order.end_date_cn
    dict_order['reminde_date_cn'] = douban_order.reminde_date_cn
    dict_order['sale_type'] = douban_order.sale_type_cn
    dict_order['money'] = douban_order.money
    dict_order['back_moneys'] = sum(
        [k['money'] for k in all_back_moneys if k['order_id'] == douban_order.id])
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        douban_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        douban_order.client_end.strftime(dt_format), dt_format)
    money_ex_data = pre_month_money(douban_order.money,
                                    start_datetime,
                                    end_datetime)
    # 计算跨区系数
    if location == 0:
        rate = 1
    else:
        if location in dict_order['locations']:
            if len(dict_order['locations']) > 1:
                agent_location = list(
                    set([k.location for k in douban_order.agent_sales]))
                direct_location = list(
                    set([k.location for k in douban_order.direct_sales]))
                if (location in agent_location) and (location not in direct_location):
                    if len(direct_location) > 0:
                        rate = 0.5
                    else:
                        rate = 1
                    rate = float(rate) / len(agent_location)
                elif (location in direct_location) and (location not in agent_location):
                    if len(agent_location) > 0:
                        rate = 0.5
                    else:
                        rate = 1
                    rate = float(rate) / len(direct_location)
                else:
                    rate = 0.5 / len(agent_location)
                    rate += 0.5 / len(direct_location)

            else:
                rate = 1
        else:
            rate = 0

    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']] * rate)
        else:
            dict_order['money_data'].append(0)
    return dict_order


def _medium_order_to_dict(order, all_back_moneys, pre_year_month, location):
    dict_order = {}
    dict_order['client_order'] = order.client_order.id
    dict_order['locations_cn'] = order.client_order.locations_cn
    dict_order['client_name'] = order.client_order.client.name
    dict_order['agent_name'] = order.medium.name
    dict_order['campaign'] = order.client_order.campaign
    dict_order['industry_cn'] = order.client_order.client.industry_cn
    dict_order['locations'] = order.client_order.locations
    dict_order['contract_status'] = order.client_order.contract_status
    dict_order['status'] = order.client_order.status
    dict_order['contract'] = order.associated_douban_contract
    dict_order['resource_type_cn'] = order.client_order.resource_type_cn
    dict_order['start_date_cn'] = order.client_order.start_date_cn
    dict_order['end_date_cn'] = order.client_order.end_date_cn
    dict_order['reminde_date_cn'] = order.client_order.reminde_date_cn
    dict_order['sale_type'] = order.client_order.sale_type_cn
    dict_order['money'] = order.medium_money2
    dict_order['back_moneys'] = sum([order.sale_money / order.client_order.money * k['money'] for k in
                                     all_back_moneys if k['order_id'] == order.client_order.id])
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        order.client_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        order.client_order.client_end.strftime(dt_format), dt_format)
    if end_datetime < start_datetime:
        end_datetime = start_datetime
    money_ex_data = pre_month_money(order.medium_money2,
                                    start_datetime,
                                    end_datetime)
    # 计算跨区系数
    if location == 0:
        rate = 1
    else:
        if location in dict_order['locations']:
            if len(dict_order['locations']) > 1:
                agent_location = list(
                    set([k.location for k in order.client_order.agent_sales]))
                direct_location = list(
                    set([k.location for k in order.client_order.direct_sales]))
                if (location in agent_location) and (location not in direct_location):
                    if len(direct_location) > 0:
                        rate = 0.5
                    else:
                        rate = 1
                    rate = float(rate) / len(agent_location)
                elif (location in direct_location) and (location not in agent_location):
                    if len(agent_location) > 0:
                        rate = 0.5
                    else:
                        rate = 1
                    rate = float(rate) / len(direct_location)
                else:
                    rate = 0.5 / len(agent_location)
                    rate += 0.5 / len(direct_location)

            else:
                rate = 1
        else:
            rate = 0
    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']] * rate)
        else:
            dict_order['money_data'].append(0)
    return dict_order


@data_query_accrued_bp.route('/client_order', methods=['GET'])
def client_order():
    if not (g.user.is_super_leader() or g.user.is_finance() or g.user.is_contract()):
        abort(403)
    now_date = datetime.datetime.now()
    location = int(request.values.get('location', 0))
    year = int(request.values.get('year', now_date.year))
    # 获取整年月份
    pre_year_month = get_monthes_pre_days(datetime.datetime.strptime(str(year) + '-01', '%Y-%m'),
                                          datetime.datetime.strptime(str(year) + '-12', '%Y-%m'))
    # 获取所有回款包含返点发票
    back_money_data = _all_client_order_back_moneys()

    # 获取当年合同
    orders = ClientOrder.query.filter(ClientOrder.status == 1,
                                      ClientOrder.contract != '')
    # 获取当前执行年合同
    if location:
        orders = [k for k in orders if (
            k.client_start.year == year or k.client_end.year == year) and location in k.locations]
    else:
        orders = [k for k in orders if (
            k.client_start.year == year or k.client_end.year == year)]
    # 格式化合同
    orders = [_client_order_to_dict(k, back_money_data, pre_year_month, location
                                    ) for k in orders]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 19, 20]]
    orders = sorted(
        orders, key=operator.itemgetter('start_date_cn'), reverse=False)
    total_money_data = [0 for k in range(12)]
    for k in orders:
        total_money_data = numpy.array(
            total_money_data) + numpy.array(k['money_data'])
    if request.values.get('action') == 'excel':
        return write_order_excel(orders, year, total_money_data, location, 'client_order')
    return tpl('/data_query/accrued/client_order.html', orders=orders, year=year,
               total_money_data=total_money_data, location=location)


@data_query_accrued_bp.route('/douban_order', methods=['GET'])
def douban_order():
    if not (g.user.is_super_leader() or g.user.is_contract() or g.user.is_finance()):
        abort(403)
    location = int(request.values.get('location', 0))
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    # 获取整年月份
    pre_year_month = get_monthes_pre_days(datetime.datetime.strptime(str(year) + '-01', '%Y-%m'),
                                          datetime.datetime.strptime(str(year) + '-12', '%Y-%m'))
    # 获取所有回款包含返点发票
    back_money_data = _all_douban_order_back_moneys()
    client_back_money_data = _all_client_order_back_moneys()

    # 获取当年豆瓣合同
    orders = DoubanOrder.query.filter(DoubanOrder.status == 1,
                                      DoubanOrder.contract != '')
    # 获取当前执行年合同
    if location:
        orders = [k for k in orders if (k.client_start.year ==
                  year or k.client_end.year == year) and location in k.locations]
    else:
        orders = [k for k in orders if k.client_start.year == year or k.client_end.year == year]

    # 格式化合同
    orders = [_douban_order_to_dict(k, back_money_data, pre_year_month, location
                                    ) for k in orders]
    # 获取豆瓣合同结束
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 19, 20]]
    # 获取关联豆瓣合同
    medium_orders = [_medium_order_to_dict(k, client_back_money_data, pre_year_month, location)
                     for k in Order.all() if (k.medium_start.year == year or k.medium_end.year == year)
                     and k.associated_douban_order]
    if location:
        orders += [k for k in medium_orders if k['contract_status']
                   in [2, 4, 5, 19, 20] and k['status'] == 1 and location in k['locations']]
    else:
        orders += [k for k in medium_orders if k['contract_status']
                   in [2, 4, 5, 19, 20] and k['status'] == 1]
    # 获取关联豆瓣合同结束
    orders = sorted(
        orders, key=operator.itemgetter('start_date_cn'), reverse=False)
    total_money_data = [0 for k in range(12)]
    for k in orders:
        total_money_data = numpy.array(
            total_money_data) + numpy.array(k['money_data'])
    if request.values.get('action') == 'excel':
        return write_order_excel(orders, year, total_money_data, location, 'douban_order')
    return tpl('/data_query/accrued/douban_order.html', orders=orders, year=year,
               total_money_data=total_money_data, location=location)
