# -*- coding: UTF-8 -*-
import datetime
import operator
import numpy

from flask import request, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder, BackMoney, BackInvoiceRebate
from models.client_order import ClientOrder, BackMoney as ClientBackMoney
from models.client_order import BackInvoiceRebate as ClientBackInvoiceRebate
from searchAd.models.client_order import (searchAdClientOrder, searchAdBackMoney,
                                          searchAdConfirmMoney, searchAdBackInvoiceRebate)
from models.order import Order
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.accrued_helpers import write_order_excel, write_search_order_excel
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
    dict_order['money_data'] = [0 for k in pre_year_month]
    for m in client_order.medium_orders:
        dict_medium = {}
        dict_medium['sale_money'] = m.sale_money
        dict_medium['medium_money2'] = m.medium_money2
        start_datetime = datetime.datetime.strptime(
            m.medium_start.strftime(dt_format), dt_format)
        end_datetime = datetime.datetime.strptime(
            m.medium_end.strftime(dt_format), dt_format)
        sale_money_ex_data = pre_month_money(m.sale_money,
                                             start_datetime,
                                             end_datetime)
        # 媒体售卖执行金额
        dict_medium['sale_money_data'] = []
        for k in pre_year_month:
            if k['month'] in sale_money_ex_data:
                dict_medium['sale_money_data'].append(
                    sale_money_ex_data[k['month']])
            else:
                dict_medium['sale_money_data'].append(0)
        dict_order['money_data'] = numpy.array(dict_order['money_data']) + numpy.array(dict_medium['sale_money_data'])
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
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20]]
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
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20]]
    # 获取关联豆瓣合同
    medium_orders = [_medium_order_to_dict(k, client_back_money_data, pre_year_month, location)
                     for k in Order.all() if (k.medium_start.year == year or k.medium_end.year == year)
                     and k.associated_douban_order]
    if location:
        orders += [k for k in medium_orders if k['contract_status']
                   in [2, 4, 5, 10, 19, 20] and k['status'] == 1 and location in k['locations']]
    else:
        orders += [k for k in medium_orders if k['contract_status']
                   in [2, 4, 5, 10, 19, 20] and k['status'] == 1]
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


def _all_search_client_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.client_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in searchAdBackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.client_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in searchAdBackInvoiceRebate.all()]
    return dict_back_money_data


def _all_search_confirm_money():
    dict_back_money_data = [{'order_id': k.client_order_id, 'money': k.money,
                             'rebate': k.rebate} for k in searchAdConfirmMoney.all()]
    return dict_back_money_data


def _search_order_to_dict(search_order, all_back_moneys, confirm_money_data, pre_year_month):
    dict_order = {}
    dict_order['order_id'] = search_order.id
    dict_order['locations_cn'] = search_order.locations_cn
    dict_order['client_name'] = search_order.client.name
    dict_order['agent_name'] = search_order.agent.name
    dict_order['campaign'] = search_order.campaign
    dict_order['industry_cn'] = search_order.client.industry_cn
    dict_order['locations'] = search_order.locations
    dict_order['contract_status'] = search_order.contract_status
    dict_order['contract'] = search_order.contract
    dict_order['resource_type_cn'] = search_order.resource_type_cn
    dict_order['start_date_cn'] = search_order.start_date_cn
    dict_order['end_date_cn'] = search_order.end_date_cn
    dict_order['reminde_date_cn'] = search_order.reminde_date_cn
    dict_order['sale_type'] = search_order.sale_type_cn
    dict_order['money'] = search_order.money
    dict_order['medium_rebate_money'] = sum(
        [k['rebate'] for k in confirm_money_data if k['order_id'] == search_order.id])
    dict_order['client_firm_money'] = sum(
        [k['money'] for k in confirm_money_data if k['order_id'] == search_order.id])
    dict_order['back_moneys'] = sum(
        [k['money'] for k in all_back_moneys if k['order_id'] == search_order.id])
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        search_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        search_order.client_end.strftime(dt_format), dt_format)
    dict_order['medium_data'] = []
    dict_order['medium_sale_money'] = 0
    dict_order['medium_medium_money2'] = 0
    dict_order['medium_medium_money2_data'] = [0 for k in range(12)]
    for m in search_order.medium_orders:
        dict_medium = {}
        dict_medium['name'] = m.medium.abbreviation
        dict_medium['sale_money'] = m.sale_money
        dict_order['medium_sale_money'] += dict_medium['sale_money']
        dict_medium['medium_money2'] = m.medium_money2
        dict_order['medium_medium_money2'] += dict_medium['medium_money2']
        dict_medium['medium_contract'] = m.medium_contract
        medium_money2_ex_data = pre_month_money(m.medium_money2,
                                                start_datetime,
                                                end_datetime)
        # 媒体执行金额
        dict_medium['medium_money2_data'] = []
        for k in pre_year_month:
            if k['month'] in medium_money2_ex_data:
                dict_medium['medium_money2_data'].append(
                    medium_money2_ex_data[k['month']])
            else:
                dict_medium['medium_money2_data'].append(0)
        dict_order['medium_medium_money2_data'] = numpy.array(
            dict_order['medium_medium_money2_data']) + numpy.array(dict_medium['medium_money2_data'])
        dict_order['medium_data'].append(dict_medium)
    money_ex_data = pre_month_money(dict_order['medium_sale_money'],
                                    start_datetime,
                                    end_datetime)
    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']])
        else:
            dict_order['money_data'].append(0)
    return dict_order


@data_query_accrued_bp.route('/search_client_order', methods=['GET'])
def search_client_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance() or g.user.is_contract() or
            g.user.is_searchad_member()):
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    # 获取整年月份
    pre_year_month = get_monthes_pre_days(datetime.datetime.strptime(str(year) + '-01', '%Y-%m'),
                                          datetime.datetime.strptime(str(year) + '-12', '%Y-%m'))
    # 获取所有回款包含返点发票
    back_money_data = _all_search_client_order_back_moneys()
    # 获取所有媒体返点
    confirm_money_data = _all_search_confirm_money()
    # 获取当年合同
    orders = searchAdClientOrder.query.filter(searchAdClientOrder.status == 1)
    # 去重合同
    orders = [k for k in orders if k.client_start.year ==
              year or k.client_end.year == year]
    # 格式化合同
    orders = [_search_order_to_dict(k, back_money_data, confirm_money_data, pre_year_month
                                    ) for k in orders]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20]]
    orders = sorted(
        orders, key=operator.itemgetter('start_date_cn'), reverse=False)
    total_money_data = [0 for k in range(12)]
    medium_medium_money2_data = [0 for k in range(12)]
    for k in orders:
        total_money_data = numpy.array(
            total_money_data) + numpy.array(k['money_data'])
        medium_medium_money2_data = numpy.array(
            medium_medium_money2_data) + numpy.array(k['medium_medium_money2_data'])
    if request.values.get('action') == 'excel':
        return write_search_order_excel(orders=orders, year=year, total_money_data=total_money_data,
                                        medium_medium_money2_data=medium_medium_money2_data)
    return tpl('/data_query/accrued/search_client_order.html', orders=orders, year=year,
               total_money_data=total_money_data, medium_medium_money2_data=medium_medium_money2_data)
