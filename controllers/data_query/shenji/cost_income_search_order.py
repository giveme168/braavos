# -*- coding: UTF-8 -*-
import datetime
import operator
import numpy

from flask import request, g, abort
from flask import render_template as tpl

from searchAd.models.client_order import (searchAdClientOrder, searchAdBackMoney,
                                          searchAdBackInvoiceRebate, searchAdConfirmMoney)
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.shenji_helpers import write_search_order_excel
from flask import Blueprint

cost_income_search_order_bp = Blueprint(
    'data_query_shenji_cost_income_search_order', __name__,
    template_folder='../../templates/data_query')


def _all_client_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.client_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in searchAdBackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.client_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in searchAdBackInvoiceRebate.all()]
    return dict_back_money_data


def _all_confirm_money():
    dict_back_money_data = [{'order_id': k.client_order_id, 'money': k.money,
                             'rebate': k.rebate} for k in searchAdConfirmMoney.all()]
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
    money_ex_data = pre_month_money(search_order.money,
                                    start_datetime,
                                    end_datetime)
    # 客户执行金额
    dict_order['money_data'] = []
    for k in pre_year_month:
        if k['month'] in money_ex_data:
            dict_order['money_data'].append(money_ex_data[k['month']])
        else:
            dict_order['money_data'].append(0)
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
    return dict_order


@cost_income_search_order_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance() or g.user.is_contract() or
            g.user.is_searchad_member()):
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    # 获取整年月份
    pre_year_month = get_monthes_pre_days(datetime.datetime.strptime(str(year) + '-01', '%Y-%m'),
                                          datetime.datetime.strptime(str(year) + '-12', '%Y-%m'))
    # 获取所有回款包含返点发票
    back_money_data = _all_client_order_back_moneys()
    # 获取所有媒体返点
    confirm_money_data = _all_confirm_money()
    # 获取当年合同
    orders = searchAdClientOrder.query.filter(searchAdClientOrder.status == 1)
    # 去重合同
    orders = [k for k in orders if k.client_start.year ==
              year or k.client_end.year == year]
    # 格式化合同
    orders = [_search_order_to_dict(k, back_money_data, confirm_money_data, pre_year_month
                                    ) for k in orders]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 19, 20]]
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
    return tpl('/shenji/cost_income_search_order.html', orders=orders, year=year, total_money_data=total_money_data,
               medium_medium_money2_data=medium_medium_money2_data)
