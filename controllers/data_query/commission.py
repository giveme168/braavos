# -*- coding: UTF-8 -*-
import datetime
import calendar as cal
import operator

from flask import Blueprint, request, g
from flask import render_template as tpl

from models.client_order import ClientOrderExecutiveReport, BackMoney
from models.douban_order import DoubanOrderExecutiveReport, BackMoney as DoubanBackMoney
from libs.date_helpers import (
    check_Q_get_monthes, check_month_get_Q, get_monthes_pre_days)


data_query_commission_bp = Blueprint(
    'data_query_commission', __name__, template_folder='../../templates/data_query')


# 根据摸个合同获取最后一次回款时间，及当季度总回款金额
def _order_back_money_by_Q(order_id, start_Q_month, back_moneys, now_Q_back_moneys):
    now_Q_back_money_obj = [
        k for k in now_Q_back_moneys if k['order_id'] == order_id]
    now_Q_back_moneys = sum([k['money'] for k in now_Q_back_money_obj])
    now_Q_back_money_obj = sorted(
        now_Q_back_money_obj, key=operator.itemgetter('back_time'), reverse=True)
    if now_Q_back_money_obj:
        now_Q_back_money_last_time = now_Q_back_money_obj[
            0]['back_time'].strftime('%Y-%m-%d')
    else:
        now_Q_back_money_last_time = u'无'
    # 获取本季度之前的所有回款
    before_Q_back_money_obj = [k for k in now_Q_back_money_obj if k[
        'order_id'] == order_id and k['back_time'] < start_Q_month]
    before_Q_back_moneys = sum([k.money for k in before_Q_back_money_obj])

    return {'last_time': now_Q_back_money_last_time,
            'now_Q_back_moneys': now_Q_back_moneys,
            'before_Q_back_moneys': before_Q_back_moneys}


# 计算某个合同执行额
def _order_executive_reports(money, start, end):
    if money:
        pre_money = float(money) / ((start - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(datetime.datetime.strptime(start.strftime('%Y-%m-%d'), '%Y-%m-%d'),
                                          datetime.datetime.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d'))
    pre_month_money_data = []
    for k in pre_month_days:
        pre_month_money_data.append(
            {'money': pre_money * k['days'], 'month_day': k['month'], 'days': k['days']})
    return pre_month_money_data


# 计算某个合同中每个月的回款数，该合同所属回款季度
def _belong_time_by_back_money(money, start, end, back_money_obj):
    # 获取合同执行额
    report_money = _order_executive_reports(money, start, end)
    now_Q_back_moneys = back_money_obj['now_Q_back_moneys']
    t_report_money = 0
    report_times = []
    for k in range(len(report_money)):
        t_report_money += report_money[k]['money']
        if now_Q_back_moneys <= 0:
            break
        if report_money[k]['money'] < now_Q_back_moneys:
            report_times.append(
                (report_money[k]['month_day'], report_money[k]['money']))
        else:
            report_times.append(
                (report_money[k]['month_day'], now_Q_back_moneys))
        now_Q_back_moneys -= report_money[k]['money']
    if report_times:
        if len(report_times) > 1:
            start = report_times[0][0].strftime(
                '%Y') + '.' + check_month_get_Q(report_times[0][0].strftime('%m'))
            end = report_times[-1][0].strftime('%Y') + '.' + check_month_get_Q(
                report_times[-1][0].strftime('%m'))
            if start == end:
                return {'back_moneys': report_times, 'belong_time': end}
            return {'back_moneys': report_times, 'belong_time': start + u' 至 ' + end}
        start = report_times[0][0].strftime(
            '%Y') + '.' + check_month_get_Q(report_times[0][0].strftime('%m'))
        return {'back_moneys': report_times, 'belong_time': start}
    return {'back_moneys': [], 'belong_time': u'无'}


# 获取某个销售的季度执行额
def _get_performance_rate_by_user(order_type, performance, user, sale_type, t_report):
    performance_rate = {}
    for k, v in performance.items():
        q_monthes = check_Q_get_monthes(k[-2:])
        start_time = datetime.datetime.strptime(
            k[:-2] + '-' + q_monthes[0], '%Y-%m')
        end_time = datetime.datetime.strptime(
            k[:-2] + '-' + q_monthes[-1], '%Y-%m')
        order_report = [r for r in t_report if r.month_day >=
                        start_time and r.month_day <= end_time]
        if order_type == 'bra_client_order':
            if sale_type == 'direct':
                order_moneys = sum([o.get_money_by_user(
                    user, sale_type) for o in order_report if user in o.client_order.direct_sales])
            else:
                order_moneys = sum([o.get_money_by_user(
                    user, sale_type) for o in order_report if user in o.client_order.agent_sales])
        else:
            if sale_type == 'direct':
                order_moneys = sum([o.get_money_by_user(
                    user, sale_type) for o in order_report if user in o.douban_order.direct_sales])
            else:
                order_moneys = sum([o.get_money_by_user(
                    user, sale_type) for o in order_report if user in o.douban_order.agent_sales])
        order_moneys = order_moneys
        if v:
            rate = order_moneys / v
            if rate > 1:
                performance_rate[k + 'rate'] = (1, order_moneys, v)
            else:
                performance_rate[k + 'rate'] = (rate, order_moneys, v)
        else:
            performance_rate[k + 'rate'] = (0, order_moneys, v)
    return performance_rate


# 格式化合同
def _order_to_dict(order, start_Q_month, back_moneys, now_Q_back_moneys, t_report):
    dict_order = {}
    dict_order['client_name'] = order.client.name
    dict_order['money'] = order.money
    dict_order['agent_name'] = order.agent.name
    dict_order['contract'] = order.contract
    dict_order['campaign'] = order.campaign
    dict_order['locations'] = order.locations
    dict_order['contract_status'] = order.contract_status
    dict_order['status'] = order.status
    # 获取合同回款信息
    dict_order['back_money_obj'] = _order_back_money_by_Q(
        order.id, start_Q_month, back_moneys, now_Q_back_moneys)
    # 根据回款信息确定合同所属时间
    dict_order['belong_time'] = _belong_time_by_back_money(
        order.money, order.client_start, order.client_end, dict_order['back_money_obj'])
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
        d_saler['performance_rate'] = _get_performance_rate_by_user(
            order.__tablename__, d_saler['performance'], saler, 'direct', t_report)
        # 判断销售是否有平分金额
        if len(set(order.locations)) > 1:
            l_count = len(set(order.locations))
        else:
            l_count = 1
        count = len(order.direct_sales)
        if saler.team.location == 3 and len(order.locations) > 1:
            count = len(order.direct_sales)
        elif saler.team.location == 3 and len(order.locations) == 1:
            count = len(order.agent_sales + order.direct_sales)

        d_saler['str_formula'] = ""
        commission_money = 0
        for b_money_obj in dict_order['belong_time']['back_moneys']:
            b_money = float('%.2f' % (b_money_obj[1] / count / l_count))
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
                str('%.2f' % zhixing_money), str(performance_money),
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
        d_saler['performance_rate'] = _get_performance_rate_by_user(
            order.__tablename__, d_saler['performance'], saler, 'agent', t_report)
        # 判断销售是否有平分金额
        if len(set(order.locations)) > 1:
            l_count = len(set(order.locations))
        else:
            l_count = 1
        count = len(order.agent_sales)
        if saler.team.location == 3 and len(order.locations) > 1:
            count = len(order.agent_sales)
        elif saler.team.location == 3 and len(order.locations) == 1:
            count = len(order.agent_sales + order.direct_sales)

        d_saler['str_formula'] = ""
        commission_money = 0
        for b_money_obj in dict_order['belong_time']['back_moneys']:
            b_money = float('%.2f' % (b_money_obj[1] / count / l_count))
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
                str('%.2f' % zhixing_money), str(performance_money),
                str(commission), str(b_money), str(c_money),
                day.strftime('%Y-%m'))
        d_saler['commission_money'] = commission_money
        dict_order['agent_sales'].append(d_saler)
    dict_order['salers_ids'] = [k['id']
                                for k in (dict_order['direct_sales'] + dict_order['agent_sales'])]
    dict_order['client_start'] = order.client_start
    dict_order['client_end'] = order.client_end
    return dict_order


# 格式化回款
def _dict_back_money(back_money):
    dict_back_money = {}
    dict_back_money['money'] = back_money.money
    dict_back_money['back_time'] = back_money.back_time
    order = back_money.order
    dict_back_money['order'] = order
    dict_back_money['order_id'] = back_money.order.id
    dict_back_money['order_start'] = order.client_start
    dict_back_money['order_end'] = order.client_end
    return dict_back_money


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

    # 获取下季度的第一天为本季度的结束时间
    d = cal.monthrange(int(now_year), int(Q_monthes[-1]))
    end_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[-1]), d[1]) + datetime.timedelta(days=1)
    # 获取该季度及之前所有回款
    client_back_moneys = [_dict_back_money(
        k) for k in BackMoney.query.filter(BackMoney.back_time < end_Q_month)]
    douban_back_moneys = [_dict_back_money(
        k) for k in DoubanBackMoney.query.filter(BackMoney.back_time < end_Q_month)]
    # ####################获取相关订单执行额，用于计算销售季度完成率##################
    client_continue_time = []
    for k in client_back_moneys:
        client_continue_time += [k['order_start'], k['order_end']]
    douban_countinue_time = []
    for k in douban_back_moneys:
        douban_countinue_time += [k['order_start'], k['order_end']]

    client_continue_time.sort()
    douban_countinue_time.sort()

    if client_continue_time:
        client_continue_start = client_continue_time[0].replace(day=1)
        client_continue_end = client_continue_time[-1].replace(day=1)
        client_report = list(ClientOrderExecutiveReport.query.filter(
            ClientOrderExecutiveReport.month_day >= client_continue_start,
            ClientOrderExecutiveReport.month_day <= client_continue_end))
    else:
        client_report = []

    if douban_countinue_time:
        douban_countinue_start = douban_countinue_time[0].replace(day=1)
        douban_countinue_end = douban_countinue_time[-1].replace(day=1)
        douban_report = list(DoubanOrderExecutiveReport.query.filter(
            DoubanOrderExecutiveReport.month_day >= douban_countinue_start,
            DoubanOrderExecutiveReport.month_day <= douban_countinue_end))
    else:
        douban_report = []
    # ####################获取相关订单执行额，用于计算销售季度完成率##################

    # 获取当前季度所有回款
    now_Q_client_back_moneys = [
        k for k in client_back_moneys if k['back_time'] >= start_Q_month]
    now_Q_douban_back_moneys = [
        k for k in douban_back_moneys if k['back_time'] >= start_Q_month]

    # 回去当季度回款的所有合同
    client_orders = list(set([k['order'] for k in now_Q_client_back_moneys]))
    douban_orders = list(set([k['order'] for k in now_Q_douban_back_moneys]))

    orders = [_order_to_dict(k, start_Q_month, client_back_moneys, now_Q_client_back_moneys, client_report)
              for k in client_orders if k.contract_status not in [7, 8, 9] and k.status == 1 and k.contract]

    orders += [_order_to_dict(k, start_Q_month, douban_back_moneys, now_Q_douban_back_moneys, douban_report)
               for k in douban_orders if k.contract_status not in [7, 8, 9] and k.status == 1 and k.contract]

    if g.user.is_super_leader() or g.user.is_finance():
        orders = orders
    elif g.user.is_leader():
        orders = [k for k in orders if g.user.location in k['locations']]
    else:
        orders = [k for k in orders if g.user.id in k['salers_ids']]

    if location_id:
        orders = [k for k in orders if location_id in k['locations']]
    return tpl('/data_query/commission/index.html',
               orders=orders,
               Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, location_id=location_id)
