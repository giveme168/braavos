# -*- coding: UTF-8 -*-
import datetime
import operator
import numpy

from flask import request, g, abort
from flask import render_template as tpl

from models.client_order import ClientOrder, BackMoney, BackInvoiceRebate
from models.client import AgentRebate
from models.medium import MediumRebate
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.shenji_helpers import write_client_order_excel
from flask import Blueprint

cost_income_client_order_bp = Blueprint(
    'data_query_shenji_cost_income_client_order', __name__,
    template_folder='../../templates/data_query')


def _all_client_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.client_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in BackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.client_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in BackInvoiceRebate.all()]
    return dict_back_money_data


def _all_agent_rebate():
    agent_rebate_data = [{'agent_id': k.agent_id, 'inad_rebate': k.inad_rebate,
                          'douban_rebate': k.douban_rebate, 'year': k.year} for k in AgentRebate.all()]
    return agent_rebate_data


def _all_medium_rebate():
    medium_rebate_data = [{'medium_id': k.medium_id, 'rebate': k.rebate,
                           'year': k.year} for k in MediumRebate.all()]
    return medium_rebate_data


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


def _client_order_to_dict(client_order, all_back_moneys, all_agent_rebate, all_medium_rebate, pre_year_month):
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
    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']])
        else:
            dict_order['money_data'].append(0)
    # 单笔返点
    try:
        self_agent_rebate_data = client_order.self_agent_rebate
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
        agent_rebate_data = [k['inad_rebate'] for k in all_agent_rebate if client_order.agent.id == k[
            'agent_id'] and pre_year_month[0]['month'].year == k['year'].year]
        if agent_rebate_data:
            agent_rebate = agent_rebate_data[0]
        else:
            agent_rebate = 0
        dict_order['money_rebate_data'] = [
            k * agent_rebate / 100 for k in dict_order['money_data']]
    dict_order['medium_data'] = []
    # 初始化总计媒体执行金额
    total_medium_money2_data = [0 for k in range(12)]
    # 初始化总计媒体返点
    total_medium_money2_rebate_data = [0 for k in range(12)]
    dict_order['medium_sale_money'] = 0
    dict_order['medium_medium_money2'] = 0
    for m in client_order.medium_orders:
        dict_medium = {}
        dict_medium['name'] = m.medium.name
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
        # 媒体返点系数
        medium_rebate_data = [k['rebate'] for k in all_medium_rebate if m.medium.id == k[
            'medium_id'] and pre_year_month[0]['month'].year == k['year'].year]
        if medium_rebate_data:
            medium_rebate = medium_rebate_data[0]
        else:
            medium_rebate = 0
        dict_medium['medium_money2_rebate_data'] = [
            k * medium_rebate / 100 for k in dict_medium['medium_money2_data']]

        total_medium_money2_data = numpy.array(total_medium_money2_data) + \
            numpy.array(dict_medium['medium_money2_data'])
        total_medium_money2_rebate_data = numpy.array(total_medium_money2_rebate_data) + \
            numpy.array(dict_medium['medium_money2_rebate_data'])
        dict_order['medium_data'].append(dict_medium)
    # 合同利润
    dict_order['profit_data'] = numpy.array(dict_order['money_data']) - \
        numpy.array(dict_order['money_rebate_data']) - total_medium_money2_data + \
        total_medium_money2_rebate_data
    dict_order['total_medium_money2_data'] = total_medium_money2_data
    dict_order['total_medium_money2_rebate_data'] = total_medium_money2_rebate_data
    return dict_order


@cost_income_client_order_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance()):
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    # 获取整年月份
    pre_year_month = get_monthes_pre_days(datetime.datetime.strptime(str(year) + '-01', '%Y-%m'),
                                          datetime.datetime.strptime(str(year) + '-12', '%Y-%m'))
    # 获取所有回款包含返点发票
    back_money_data = _all_client_order_back_moneys()
    # 获取代理返点系数
    all_agent_rebate = _all_agent_rebate()
    # 获取媒体返点系数
    all_medium_rebate = _all_medium_rebate()
    # 获取当年合同
    orders = ClientOrder.query.filter(ClientOrder.status == 1,
                                      ClientOrder.contract != '')
    # 去重合同
    orders = [k for k in orders if k.client_start.year == year]
    # 格式化合同
    orders = [_client_order_to_dict(k, back_money_data, all_agent_rebate,
                                    all_medium_rebate, pre_year_month
                                    ) for k in orders]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 19, 20]]
    orders = sorted(
        orders, key=operator.itemgetter('start_date_cn'), reverse=False)
    total_money_data = [0 for k in range(12)]
    total_money_rebate_data = [0 for k in range(12)]
    total_profit_data = [0 for k in range(12)]
    total_medium_money2_data = [0 for k in range(12)]
    total_medium_money2_rebate_data = [0 for k in range(12)]
    for k in orders:
        total_money_data = numpy.array(
            total_money_data) + numpy.array(k['money_data'])
        total_money_rebate_data = numpy.array(
            total_money_rebate_data) + numpy.array(k['money_rebate_data'])
        total_profit_data = numpy.array(
            total_profit_data) + numpy.array(k['profit_data'])
        total_medium_money2_data = numpy.array(
            total_medium_money2_data) + numpy.array(k['total_medium_money2_data'])
        total_medium_money2_rebate_data = numpy.array(
            total_medium_money2_rebate_data) + numpy.array(k['total_medium_money2_rebate_data'])
    if request.values.get('action') == 'excel':
        return write_client_order_excel(orders=orders, year=year, total_money_data=total_money_data,
                                        total_money_rebate_data=total_money_rebate_data,
                                        total_profit_data=total_profit_data,
                                        total_medium_money2_data=total_medium_money2_data,
                                        total_medium_money2_rebate_data=total_medium_money2_rebate_data)
    return tpl('/shenji/cost_income_client_order.html', orders=orders, year=year, total_money_data=total_money_data,
               total_money_rebate_data=total_money_rebate_data, total_profit_data=total_profit_data,
               total_medium_money2_data=total_medium_money2_data,
               total_medium_money2_rebate_data=total_medium_money2_rebate_data)
