# -*- coding: UTF-8 -*-
import datetime
import operator
import numpy

from flask import Blueprint, g, abort, request
from flask import render_template as tpl

from models.douban_order import DoubanOrder, BackMoney, BackInvoiceRebate
from models.client_order import BackMoney as ClientBackMoney
from models.client_order import BackInvoiceRebate as ClientBackInvoiceRebate
from models.outsource import DoubanOutSource, OutSource
from models.order import Order
from models.client import AgentRebate
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.shenji_helpers import write_douban_order_excel

cost_income_douban_order_bp = Blueprint(
    'data_query_shenji_cost_income_douban_order', __name__,
    template_folder='../../templates/data_query')


def _all_douban_order_outsource():
    outsource = [{'order_id': o.douban_order.id, 'money': o.num, 'type': 'douban'}
                 for o in DoubanOutSource.all() if o.status in [2, 3, 4]]
    outsource += [{'order_id': o.medium_order.id, 'money': o.num, 'type': 'client'}
                  for o in OutSource.all() if o.status in [2, 3, 4]]
    return outsource


def _all_douban_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.douban_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in BackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.douban_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in BackInvoiceRebate.all()]
    return dict_back_money_data


def _all_client_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.client_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in ClientBackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.client_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in ClientBackInvoiceRebate.all()]
    return dict_back_money_data


def _all_agent_rebate():
    agent_rebate_data = [{'agent_id': k.agent_id, 'inad_rebate': k.inad_rebate,
                          'douban_rebate': k.douban_rebate, 'year': k.year} for k in AgentRebate.all()]
    return agent_rebate_data


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


def _douban_order_to_dict(douban_order, all_back_moneys, all_agent_rebate, pre_year_month, all_outsource, shenji):
    dict_order = {}
    dict_order['order_id'] = douban_order.id
    dict_order['type'] = 'douban_order'
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
    # 获取所有外包信息
    t_outsource_money = sum([o['money'] for o in all_outsource if o['order_id']
                             == dict_order['order_id'] and o['type'] == 'douban'])
    outsource_ex_data = pre_month_money(t_outsource_money,
                                        start_datetime,
                                        end_datetime)
    dict_order['outsource_data'] = []
    for k in pre_year_month:
        if k['month'] in outsource_ex_data:
            dict_order['outsource_data'].append(
                outsource_ex_data[k['month']])
        else:
            dict_order['outsource_data'].append(0)
    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']])
        else:
            dict_order['money_data'].append(0)
    # 单笔返点
    try:
        self_agent_rebate_data = douban_order.self_agent_rebate
        self_agent_rebate = self_agent_rebate_data.split('-')[0]
        self_agent_rebate_value = float(self_agent_rebate_data.split('-')[1])
    except:
        self_agent_rebate = 0
        self_agent_rebate_value = 0
    # 客户返点
    if int(self_agent_rebate):
        dict_order['money_rebate_data'] = [k / dict_order['money'] * self_agent_rebate_value
                                           for k in dict_order['money_data']]
    else:
        # 代理返点系数
        agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate if douban_order.agent.id == k[
            'agent_id'] and pre_year_month[0]['month'].year == k['year'].year]
        if agent_rebate_data:
            agent_rebate = agent_rebate_data[0]
        else:
            agent_rebate = 0
        dict_order['money_rebate_data'] = [
            k * agent_rebate / 100 for k in dict_order['money_data']]
    if int(pre_year_month[0]['month'].year) > 2015:
        dict_order['money_rebate_data'] = [0 for k in range(12)]
    # 合同利润
    if int(pre_year_month[0]['month'].year) > 2015:
        dict_order['profit_data'] = [
            k * 0.18 for k in dict_order['money_data']]
    elif int(pre_year_month[0]['month'].year) == 2015:
        dict_order['profit_data'] = [k * 0.4 for k in dict_order['money_data']]
        dict_order['profit_data'] = numpy.array(
            dict_order['profit_data']) - numpy.array(dict_order['money_rebate_data'])
    else:
        dict_order['profit_data'] = [
            k * 0.426 for k in dict_order['money_data']]
        dict_order['profit_data'] = numpy.array(
            dict_order['profit_data']) - numpy.array(dict_order['money_rebate_data'])
    if shenji:
        dict_order['profit_data'] = numpy.array(dict_order['profit_data']) - numpy.array(dict_order['outsource_data'])
    return dict_order


def _medium_order_to_dict(order, all_back_moneys, all_agent_rebate, pre_year_month, all_outsource, shenji):
    dict_order = {}
    dict_order['order_id'] = order.client_order.id
    dict_order['type'] = 'medium_order'
    dict_order['medium_order_id'] = order.id
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
    dict_order['all_money'] = order.client_order.money
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
    # 获取所有外包信息
    t_outsource_money = sum([o['money'] for o in all_outsource if o['order_id'] ==
                             dict_order['medium_order_id'] and o['type'] == 'client'])
    outsource_ex_data = pre_month_money(t_outsource_money,
                                        start_datetime,
                                        end_datetime)
    dict_order['outsource_data'] = []
    for k in pre_year_month:
        if k['month'] in outsource_ex_data:
            dict_order['outsource_data'].append(
                outsource_ex_data[k['month']])
        else:
            dict_order['outsource_data'].append(0)
    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']])
        else:
            dict_order['money_data'].append(0)

    sale_money_ex_data = pre_month_money(order.sale_money,
                                         start_datetime,
                                         end_datetime)
    # 客户执行金额
    dict_order['sale_money_data'] = []
    for k in pre_year_month:
        if k['month'] in sale_money_ex_data:
            dict_order['sale_money_data'].append(
                sale_money_ex_data[k['month']])
        else:
            dict_order['sale_money_data'].append(0)

    # 单笔返点
    try:
        self_agent_rebate_data = order.client_order.self_agent_rebate
        self_agent_rebate = self_agent_rebate_data.split('-')[0]
        self_agent_rebate_value = float(self_agent_rebate_data.split('-')[1])
    except:
        self_agent_rebate = 0
        self_agent_rebate_value = 0
    # 客户返点
    if int(self_agent_rebate):
        dict_order['money_rebate_data'] = [k / dict_order['all_money'] * self_agent_rebate_value
                                           for k in dict_order['sale_money_data']]
    else:
        # 代理返点系数
        if order.medium.id == 8:
            agent_id = 94
        elif order.medium.id == 3:
            agent_id = 105
        elif order.medium.id == 44:
            agent_id = 228
        elif order.medium.id == 27:
            agent_id = 93
        elif order.medium.id == 37:
            agent_id = 213
        else:
            agent_id = 0
        agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate if agent_id == k[
            'agent_id'] and pre_year_month[0]['month'].year == k['year'].year]
        if agent_rebate_data:
            agent_rebate = agent_rebate_data[0]
        else:
            agent_rebate = 0
        dict_order['money_rebate_data'] = [
            k * agent_rebate / 100 for k in dict_order['money_data']]
    if int(pre_year_month[0]['month'].year) > 2015:
        dict_order['money_rebate_data'] = [0 for k in range(12)]
    # 合同利润
    if int(pre_year_month[0]['month'].year) > 2015:
        dict_order['profit_data'] = [
            k * 0.18 for k in dict_order['money_data']]
    elif int(pre_year_month[0]['month'].year) == 2015:
        dict_order['profit_data'] = [k * 0.4 for k in dict_order['money_data']]
        dict_order['profit_data'] = numpy.array(
            dict_order['profit_data']) - numpy.array(dict_order['money_rebate_data'])
    else:
        dict_order['profit_data'] = [
            k * 0.426 for k in dict_order['money_data']]
        dict_order['profit_data'] = numpy.array(
            dict_order['profit_data']) - numpy.array(dict_order['money_rebate_data'])
    if shenji:
        dict_order['profit_data'] = numpy.array(dict_order['profit_data']) - numpy.array(dict_order['outsource_data'])
    return dict_order


@cost_income_douban_order_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance() or g.user.is_contract()):
        abort(403)
    shenji = int(request.values.get('shenji', 0))
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    # 获取整年月份
    pre_year_month = get_monthes_pre_days(datetime.datetime.strptime(str(year) + '-01', '%Y-%m'),
                                          datetime.datetime.strptime(str(year) + '-12', '%Y-%m'))
    # 获取所有回款包含返点发票
    back_money_data = _all_douban_order_back_moneys()
    client_back_money_data = _all_client_order_back_moneys()
    # 获取代理返点系数
    all_agent_rebate = _all_agent_rebate()
    # 获取所有外包
    all_outsource_data = _all_douban_order_outsource()

    # 获取当年豆瓣合同
    orders = DoubanOrder.query.filter(DoubanOrder.status == 1,
                                      DoubanOrder.contract != '')
    # 去重合同
    orders = [k for k in orders if k.client_start.year ==
              year or k.client_end.year == year]
    # 格式化合同
    orders = [_douban_order_to_dict(k, back_money_data, all_agent_rebate, pre_year_month,
                                    all_outsource_data, shenji) for k in orders]
    # 获取豆瓣合同结束
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20]]
    # 获取关联豆瓣合同
    medium_orders = [_medium_order_to_dict(k, client_back_money_data, all_agent_rebate,
                                           pre_year_month, all_outsource_data, shenji)
                     for k in Order.all() if (k.medium_start.year == year or k.medium_end.year == year)
                     and k.associated_douban_order]
    orders += [k for k in medium_orders if k['contract_status']
               in [2, 4, 5, 10, 19, 20] and k['status'] == 1]
    # 获取关联豆瓣合同结束
    orders = sorted(
        orders, key=operator.itemgetter('start_date_cn'), reverse=False)
    total_outsource_data = [0 for k in range(12)]
    total_money_data = [0 for k in range(12)]
    total_money_rebate_data = [0 for k in range(12)]
    total_profit_data = [0 for k in range(12)]
    for k in orders:
        total_money_data = numpy.array(
            total_money_data) + numpy.array(k['money_data'])
        total_outsource_data = numpy.array(
            total_outsource_data) + numpy.array(k['outsource_data'])
        total_money_rebate_data = numpy.array(
            total_money_rebate_data) + numpy.array(k['money_rebate_data'])
        total_profit_data = numpy.array(
            total_profit_data) + numpy.array(k['profit_data'])
    if request.values.get('action') == 'excel':
        return write_douban_order_excel(orders=orders, year=year, total_money_data=total_money_data,
                                        total_money_rebate_data=total_money_rebate_data,
                                        total_profit_data=total_profit_data, total_outsource_data=total_outsource_data,
                                        shenji=shenji)
    if shenji:
        tpl_html = '/shenji/cost_income_douban_order_s.html'
    else:
        tpl_html = '/shenji/cost_income_douban_order.html'
    return tpl(tpl_html, orders=orders, year=year,
               total_money_data=total_money_data,
               total_money_rebate_data=total_money_rebate_data,
               total_outsource_data=total_outsource_data,
               total_profit_data=total_profit_data)
