# -*- coding: UTF-8 -*-
import datetime

from flask import request, g, abort, Blueprint
from flask import render_template as tpl

from searchAd.models.client_order import searchAdClientOrderBill
from searchAd.models.order import searchAdOrder
from libs.date_helpers import get_monthes_pre_days, check_year_Q_get_monthes, get_last_year_month_by_Q
from controllers.data_query.helpers.shenji_helpers import write_search_order_excel

cost_income_search_order_bp = Blueprint(
    'data_query_shenji_cost_income_search_order', __name__,
    template_folder='../../templates/data_query')


def pre_month_money(money, start, end):
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = []
    for k in pre_month_days:
        pre_month_money_data.append({'month': k['month'], 'money': pre_money * k['days']})
    return pre_month_money_data


'''
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
    return tpl('/shenji/cost_income_search_order.html', orders=orders, year=year, total_money_data=total_money_data,
               medium_medium_money2_data=medium_medium_money2_data)
'''


def _search_order_to_dict(search_order):
    search_client_order = search_order.client_order
    dict_order = {}
    dict_order['client_name'] = search_client_order.client.name
    dict_order['client_id'] = search_client_order.client.id
    dict_order['medium_name'] = search_order.medium.name
    dict_order['medium_id'] = search_order.medium.id
    dict_order['contract_status'] = search_client_order.contract_status
    dict_order['contract'] = search_client_order.contract
    dict_order['status'] = search_client_order.status
    dict_order['channel_type'] = search_order.channel_type or 0
    start_datetime = datetime.datetime.strptime(search_client_order.client_start.strftime('%d%m%Y'), '%d%m%Y')
    end_datetime = datetime.datetime.strptime(search_client_order.client_end.strftime('%d%m%Y'), '%d%m%Y')
    dict_order['sale_money_pre_month'] = pre_month_money(search_order.sale_money,
                                                         start_datetime,
                                                         end_datetime)
    dict_order['medium_money2_pre_month'] = pre_month_money(search_order.medium_money2,
                                                            start_datetime,
                                                            end_datetime)
    # 单笔返点
    try:
        self_agent_rebate_data = search_client_order.self_agent_rebate
        self_agent_rebate = self_agent_rebate_data.split('-')[0]
        self_agent_rebate_value = float(self_agent_rebate_data.split('-')[1])
    except:
        self_agent_rebate = 0
        self_agent_rebate_value = 0
    # 客户返点
    if int(self_agent_rebate):
        if search_client_order.money:
            money_rebate_data = search_order.sale_money / search_client_order.money * self_agent_rebate_value
        else:
            money_rebate_data = 0
    else:
        money_rebate_data = 0
    dict_order['agent_rebate_pre_month'] = pre_month_money(money_rebate_data, start_datetime, end_datetime)
    return dict_order


def _bill_to_dict(bill):
    dict_bill = {}
    dict_bill['client_name'] = bill.client.name
    dict_bill['client_id'] = bill.client.id
    dict_bill['medium_name'] = bill.medium.name
    dict_bill['medium_id'] = bill.medium.id
    start_datetime = datetime.datetime.strptime(bill.start.strftime('%d%m%Y'), '%d%m%Y')
    end_datetime = datetime.datetime.strptime(bill.end.strftime('%d%m%Y'), '%d%m%Y')
    dict_bill['money_pre_month'] = pre_month_money(bill.money,
                                                   start_datetime,
                                                   end_datetime)
    dict_bill['rebate_money_pre_month'] = pre_month_money(bill.rebate_money,
                                                          start_datetime,
                                                          end_datetime)
    return dict_bill


@cost_income_search_order_bp.route('/', methods=['GET'])
def index():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance() or g.user.is_contract() or
            g.user.is_searchad_member()):
        abort(403)
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    Q = request.values.get('Q', 'Q1')
    now_Q_monthes = check_year_Q_get_monthes(year, Q)
    last_Q_year, last_Q_month = get_last_year_month_by_Q(year, Q)
    last_Q_monthes = [datetime.datetime.strptime(str(last_Q_year) + k, '%Y%m') for k in last_Q_month]
    channel = int(request.values.get('channel', -1))
    orders = [_search_order_to_dict(k) for k in searchAdOrder.all()]
    if channel != -1:
        orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20] and
                  k['status'] == 1 and k['channel_type'] == channel]
    else:
        orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20] and
                  k['status'] == 1]
    bills = [_bill_to_dict(k) for k in searchAdClientOrderBill.all()]
    # 根据合同获取所有媒体
    medium_ids = []
    medium_info = []
    for o in orders:
        if o['medium_id'] not in medium_ids:
            medium_info.append({'medium_name': o['medium_name'], 'medium_id': o['medium_id'], 'client_obj': []})
            medium_ids.append(o['medium_id'])
    # 根据媒体，获取投放该媒体的所有客户
    for m in medium_info:
        order_client_ids = []
        order_client_info = []
        for o in orders:
            if o['client_id'] not in order_client_ids and o['medium_id'] == m['medium_id']:
                order_client_info.append({'client_name': o['client_name'], 'client_id': o['client_id'], 'sale_money': 0,
                                          'medium_money2': 0, 'pre_session_last_money': 0,
                                          'real_money': 0, 'rebate_money': 0, 'agent_rebate': 0, 'profit': 0,
                                          'last_money': 0})
                order_client_ids.append(o['client_id'])
        m['client_info'] = order_client_info
    # 根据执行时间按月打散合同
    pro_month_orders = []
    for o in orders:
        for p in range(len(o['sale_money_pre_month'])):
            dict_order = {}
            dict_order['client_id'] = o['client_id']
            dict_order['medium_id'] = o['medium_id']
            dict_order['channel_type'] = o['channel_type']
            dict_order['sale_money'] = o['sale_money_pre_month'][p]['money']
            dict_order['medium_money2'] = o['medium_money2_pre_month'][p]['money']
            dict_order['month'] = o['medium_money2_pre_month'][p]['month']
            dict_order['agent_rebate'] = o['agent_rebate_pre_month'][p]['money']
            pro_month_orders.append(dict_order)
    # 根据时间打散所有对账单
    pro_month_bills = []
    for b in bills:
        for p in range(len(b['money_pre_month'])):
            dict_bill = {}
            dict_bill['client_id'] = b['client_id']
            dict_bill['medium_id'] = b['medium_id']
            dict_bill['money'] = b['money_pre_month'][p]['money']
            dict_bill['rebate_money'] = b['rebate_money_pre_month'][p]['money']
            dict_bill['month'] = b['rebate_money_pre_month'][p]['month']
        pro_month_bills.append(dict_bill)
    # 根据媒体、客户、对账单计算数据报表
    for m in medium_info:
        for c in m['client_info']:
            # 获取上个季度媒体执行额
            c['last_session_medium_money2'] = sum([k['medium_money2'] for k in pro_month_orders if
                                                   k['client_id'] == c['client_id'] and
                                                   k['medium_id'] == m['medium_id'] and
                                                   k['channel_type'] == channel and
                                                   k['month'] <= last_Q_monthes[-1] and
                                                   k['month'] >= last_Q_monthes[0]])
            # 获取上个季度消耗金额
            c['last_session_real_money'] = sum([k['money'] for k in pro_month_bills if
                                                k['client_id'] == c['client_id'] and
                                                k['medium_id'] == m['medium_id'] and
                                                k['month'] <= last_Q_monthes[-1] and
                                                k['month'] >= last_Q_monthes[0]])
            # 计算上个季度剩余量
            c['pre_session_last_money'] = c['last_session_medium_money2'] - c['last_session_real_money']
            # 本季度客户金额
            c['sale_money'] = sum([k['sale_money'] for k in pro_month_orders if k['client_id'] == c['client_id'] and
                                   k['medium_id'] == m['medium_id'] and
                                   k['month'] <= now_Q_monthes[-1] and
                                   k['month'] >= now_Q_monthes[0]])
            # 本季度媒体金额
            c['medium_money2'] = sum([k['medium_money2'] for k in pro_month_orders if
                                      k['client_id'] == c['client_id'] and
                                      k['medium_id'] == m['medium_id'] and
                                      k['month'] <= now_Q_monthes[-1] and
                                      k['month'] >= now_Q_monthes[0]])
            # 本季度代理返点
            c['agent_rebate'] = sum([k['agent_rebate'] for k in pro_month_orders if
                                     k['client_id'] == c['client_id'] and
                                     k['medium_id'] == m['medium_id'] and
                                     k['month'] <= now_Q_monthes[-1] and
                                     k['month'] >= now_Q_monthes[0]])
            # 本季度消耗金额
            c['real_money'] = sum([k['money'] for k in pro_month_bills if k['client_id'] == c['client_id'] and
                                   k['medium_id'] == m['medium_id'] and
                                   k['month'] <= now_Q_monthes[-1] and
                                   k['month'] >= now_Q_monthes[0]])
            # 本季度媒体返点
            c['rebate_money'] = sum([k['rebate_money'] for k in pro_month_bills if k['client_id'] == c['client_id'] and
                                     k['medium_id'] == m['medium_id'] and
                                     k['month'] <= now_Q_monthes[-1] and
                                     k['month'] >= now_Q_monthes[0]])
            # 本季度利润
            c['profit'] = c['sale_money'] - c['real_money'] - c['agent_rebate'] + c['rebate_money']
            # 本季度未消耗金额
            c['last_money'] = c['medium_money2'] - c['real_money']
    if request.values.get('action') == 'excel':
        return write_search_order_excel(year=year, Q=Q, channel=channel, medium_info=medium_info)
    return tpl('/shenji/cost_income_search_order.html', year=year, Q=Q, channel=channel, medium_info=medium_info)
