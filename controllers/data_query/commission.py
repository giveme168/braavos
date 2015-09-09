# -*- coding: UTF-8 -*-
import datetime
import calendar as cal

from flask import Blueprint, request, g
from flask import render_template as tpl

from models.client_order import BackMoney
from models.douban_order import BackMoney as DoubanBackMoney
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q)


data_query_commission_bp = Blueprint(
    'data_query_commission', __name__, template_folder='../../templates/data_query')


def _order_to_dict(order, now_year, Q_monthes, now_Q):
    dict_order = {}
    dict_order['client_name'] = order.client.name
    dict_order['money'] = order.money
    dict_order['agent_name'] = order.agent.name
    dict_order['contract'] = order.contract
    dict_order['campaign'] = order.campaign
    dict_order['locations'] = order.locations
    # 获取合同回款信息
    dict_order['back_money_obj'] = order.back_moneys_by_Q(now_year, Q_monthes)
    # 根据回款信息确定合同所属时间
    dict_order['belong_time'] = order.belong_time_by_back_money(
        dict_order['back_money_obj'])
    dict_order['last_rebate_agent_time'] = order.last_rebate_agent_time()
    dict_order['last_rebate_agent_money'] = order.last_rebate_agent_money()

    dict_order['direct_sales'] = []
    for saler in order.direct_sales:
        d_saler = {}
        d_saler['id'] = saler.id
        d_saler['name'] = saler.name
        d_saler['location_cn'] = saler.location_cn
        d_saler['performance'] = saler.get_performance(
            dict_order['belong_time'])
        d_saler['commission'] = saler.get_commission(dict_order['belong_time'])
        d_saler['performance_rate'] = order.get_performance_rate(
            d_saler['performance'], saler, 'direct')
        # 判断销售是否有平分金额
        count = len(order.direct_sales)
        if saler.team.location == 3:
            count = len(order.agent_sales + order.direct_sales)

        d_saler['str_formula'] = ""
        commission_money = 0
        for b_money_obj in dict_order['belong_time']['back_moneys']:
            b_money = b_money_obj[1] / count
            day = b_money_obj[0]
            Q = check_month_get_Q(day.strftime('%m'))

            if str(day.year) + Q + 'rate' in d_saler['performance_rate']:
                # 完成率
                performance_rate = d_saler['performance_rate'][
                    str(day.year) + Q + 'rate'][0]
                # 执行金额
                zhixing_money = d_saler['performance_rate'][
                    str(day.year) + Q + 'rate'][1]
                # 销售业绩
                performance_money = d_saler['performance_rate'][
                    str(day.year) + Q + 'rate'][2]
            else:
                performance_rate = 0
                zhixing_money = 0
                performance_money = 0
            if day.strftime('%Y') in d_saler['commission']:
                commission = d_saler['commission'][day.strftime('%Y')]
            else:
                commission = 0
            c_money = float('%.2f' % (performance_rate * commission * b_money))
            commission_money += c_money
            # 计算公式
            d_saler['str_formula'] += u"(%s / %s) * %s * %s = %s &nbsp;&nbsp;(%s月 提成信息)<br/>" % (
                str(zhixing_money), str(performance_money),
                str(commission), str(b_money), str(c_money),
                day.strftime('%Y-%m'))
        d_saler['commission_money'] = commission_money
        dict_order['direct_sales'].append(d_saler)

    dict_order['agent_sales'] = []
    for saler in order.agent_sales:
        d_saler = {}
        d_saler['id'] = saler.id
        d_saler['name'] = saler.name
        d_saler['location_cn'] = saler.location_cn
        d_saler['performance'] = saler.get_performance(
            dict_order['belong_time'])
        d_saler['commission'] = saler.get_commission(dict_order['belong_time'])
        d_saler['performance_obj'] = order.get_performance_rate(
            d_saler['performance'], saler, 'agent')
        d_saler['performance_rate'] = order.get_performance_rate(
            d_saler['performance'], saler, 'agent')
        # 判断销售是否有平分金额
        count = len(order.agent_sales)
        if saler.team.location == 3:
            count = len(order.agent_sales + order.direct_sales)

        d_saler['str_formula'] = ""
        commission_money = 0
        for b_money_obj in dict_order['belong_time']['back_moneys']:
            b_money = b_money_obj[1] / count
            day = b_money_obj[0]
            Q = check_month_get_Q(day.strftime('%m'))

            if str(day.year) + Q + 'rate' in d_saler['performance_rate']:
                # 完成率
                performance_rate = d_saler['performance_rate'][
                    str(day.year) + Q + 'rate'][0]
                # 执行金额
                zhixing_money = d_saler['performance_rate'][
                    str(day.year) + Q + 'rate'][1]
                # 销售业绩
                performance_money = d_saler['performance_rate'][
                    str(day.year) + Q + 'rate'][2]
            else:
                performance_rate = 0
                zhixing_money = 0
                performance_money = 0
            if day.strftime('%Y') in d_saler['commission']:
                commission = d_saler['commission'][day.strftime('%Y')]
            else:
                commission = 0
            c_money = float('%.2f' % (performance_rate * commission * b_money))
            commission_money += c_money
            # 计算公式
            d_saler['str_formula'] += u"(%s / %s) * %s * %s = %s &nbsp;&nbsp;(%s月 提成计算方法)<br/>" % (
                str(zhixing_money), str(performance_money),
                str(commission), str(b_money), str(c_money),
                day.strftime('%Y-%m'))
        d_saler['commission_money'] = commission_money
        dict_order['agent_sales'].append(d_saler)
    dict_order['salers_ids'] = [k['id']
                                for k in (dict_order['direct_sales'] + dict_order['agent_sales'])]
    dict_order['client_start'] = order.client_start
    dict_order['client_end'] = order.client_end
    return dict_order


@data_query_commission_bp.route('/', methods=['GET'])
def index():
    now_year = request.values.get('year', '')
    now_Q = request.values.get('Q', '')
    location_id = int(request.values.get('location_id', 0))
    if not now_year and not now_Q:
        now_date = datetime.date.today()
        now_year = now_date.strftime('%Y')
        now_month = now_date.strftime('%m')
        now_Q = check_month_get_Q(now_month)
    Q_monthes = check_Q_get_monthes(now_Q)
    start_Q_month = datetime.datetime(int(now_year), int(Q_monthes[0]), 1)

    # 获取下季度的第一天为结束时间
    d = cal.monthrange(int(now_year), int(Q_monthes[-1]))
    end_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[-1]), d[1]) + datetime.timedelta(days=1)

    # 获取当前季度回款的所有合同
    client_orders = list(set([k.client_order for k in BackMoney.query.filter(
        BackMoney.back_time >= start_Q_month,
        BackMoney.back_time < end_Q_month
    ) if k.client_order.status == 1 and k.client_order.contract]))
    douban_orders = list(set([k.douban_order for k in DoubanBackMoney.query.filter(
        DoubanBackMoney.back_time >= start_Q_month,
        DoubanBackMoney.back_time < end_Q_month
    ) if k.douban_order.status == 1 and k.douban_order.contract]))

    # 根据权限查看不同的合同
    if g.user.is_super_leader():
        client_orders = [
            k for k in client_orders if k.contract_status not in [7, 8, 9]]
        douban_orders = [
            k for k in douban_orders if k.contract_status not in [7, 8, 9]]
    elif g.user.is_leader():
        client_orders = [k for k in client_orders if k.contract_status not in [
            7, 8, 9] and g.user.location in k.locations]
        douban_orders = [k for k in douban_orders if k.contract_status not in [
            7, 8, 9] and g.user.location in k.locations]
    else:
        client_orders = [k for k in client_orders if k.contract_status not in [
            7, 8, 9] and g.user in k.direct_sales + k.agent_sales]
        douban_orders = [k for k in douban_orders if k.contract_status not in [
            7, 8, 9] and g.user in k.direct_sales + k.agent_sales]

    if location_id:
        client_orders = [k for k in client_orders if location_id in k.locations]
        douban_orders = [k for k in douban_orders if location_id in k.locations]
    orders = [_order_to_dict(k, now_year, Q_monthes, now_Q)
              for k in client_orders]
    orders += [_order_to_dict(k, now_year, Q_monthes, now_Q)
               for k in douban_orders]
    return tpl('/data_query/commission/index.html',
               orders=orders,
               Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, location_id=location_id)
