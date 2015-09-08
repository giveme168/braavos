# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, g
from flask import render_template as tpl

from models.client_order import ClientOrderExecutiveReport
from models.douban_order import DoubanOrderExecutiveReport
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q)


data_query_commission_bp = Blueprint(
    'data_query_commission', __name__, template_folder='../../templates/data_query')


# 整理单个销售报表数据
def _executive_report(order, user, now_year, monthes, sale_type):
    if sale_type == 'agent':
        count = len(order.agent_sales)
    else:
        count = len(order.direct_sales)
    if user.team.location == 3:
        count = len(order.agent_sales + order.direct_sales)
    if sale_type == 'normal':
        count = 1
    pre_reports = order.executive_report_data()
    moneys = []
    for j in monthes:
        for r in pre_reports:
            if r['month_day'].date() == datetime.datetime(int(now_year), int(j), 1).date():
                pre_money = r['money']
                break
            else:
                pre_money = 0
        try:
            moneys.append(round(pre_money / count, 2))
        except:
            moneys.append(0)
    return moneys


def _client_order_to_dict(client_order, now_year, Q_monthes, now_Q):
    dict_order = {}
    dict_order['client_name'] = client_order.client.name
    dict_order['money'] = client_order.money
    dict_order['agent_name'] = client_order.agent.name
    dict_order['contract'] = client_order.contract
    dict_order['campaign'] = client_order.campaign
    dict_order['industry_cn'] = client_order.client.industry_cn
    dict_order['locations'] = client_order.locations
    dict_order['last_back_moneys_time'] = client_order.last_back_moneys_time_by_Q(
        now_year, Q_monthes)
    dict_order['zhixing_money'] = [
        client_order.zhixing_money('agent'), client_order.zhixing_money('direct')]
    dict_order['direct_sales'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
    }for k in client_order.direct_sales]
    dict_order['agent_sales'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
    }for k in client_order.agent_sales]
    dict_order['direct_sales_data'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'location_cn': k.team.location_cn,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
        'zhixing_money': _executive_report(client_order, k, now_year, Q_monthes, 'direct'),
        'back_moneys_by_Q': client_order.back_moneys_by_Q(k, now_year, Q_monthes, 'direct'),
    }for k in client_order.direct_sales]
    dict_order['agent_sales_data'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'location_cn': k.team.location_cn,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
        'zhixing_money': _executive_report(client_order, k, now_year, Q_monthes, 'agent'),
        'back_moneys_by_Q': client_order.back_moneys_by_Q(k, now_year, Q_monthes, 'agent'),
    }for k in client_order.agent_sales]
    dict_order['salers_ids'] = [k['id']
                                for k in (dict_order['direct_sales'] + dict_order['agent_sales'])]
    dict_order['resource_type_cn'] = client_order.resource_type_cn
    dict_order['client_start'] = client_order.client_start
    dict_order['client_end'] = client_order.client_end
    return dict_order


def _douban_order_to_dict(douban_order, now_year, Q_monthes, now_Q):
    dict_order = {}
    dict_order['client_name'] = douban_order.client.name
    dict_order['money'] = douban_order.money
    dict_order['agent_name'] = douban_order.agent.name
    dict_order['contract'] = douban_order.contract
    dict_order['campaign'] = douban_order.campaign
    dict_order['industry_cn'] = douban_order.client.industry_cn
    dict_order['locations'] = douban_order.locations
    dict_order['last_back_moneys_time'] = douban_order.last_back_moneys_time_by_Q(
        now_year, Q_monthes)
    dict_order['zhixing_money'] = [
        douban_order.zhixing_money('agent'), douban_order.zhixing_money('direct')]
    dict_order['direct_sales'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
    }for k in douban_order.direct_sales]
    dict_order['agent_sales'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
    }for k in douban_order.agent_sales]
    dict_order['direct_sales_data'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'location_cn': k.team.location_cn,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
        'zhixing_money': _executive_report(douban_order, k, now_year, Q_monthes, 'direct'),
        'back_moneys_by_Q': douban_order.back_moneys_by_Q(k, now_year, Q_monthes, 'direct'),
    }for k in douban_order.direct_sales]
    dict_order['agent_sales_data'] = [{
        'id': k.id,
        'name': k.name,
        'location': k.team.location,
        'location_cn': k.team.location_cn,
        'commission': k.commission(now_year),
        'performance': k.performance(now_year, now_Q),
        'zhixing_money': _executive_report(douban_order, k, now_year, Q_monthes, 'agent'),
        'back_moneys_by_Q': douban_order.back_moneys_by_Q(k, now_year, Q_monthes, 'agent'),
    }for k in douban_order.agent_sales]
    dict_order['salers_ids'] = [k['id']
                                for k in (dict_order['direct_sales'] + dict_order['agent_sales'])]
    dict_order['resource_type_cn'] = douban_order.resource_type_cn
    dict_order['client_start'] = douban_order.client_start
    dict_order['client_end'] = douban_order.client_end
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
    start_Q_month = datetime.datetime(
        int(now_year), int(Q_monthes[0]), 1).date()
    end_Q_month = datetime.datetime(int(now_year), int(Q_monthes[-1]), 1).date()

    if g.user.is_super_leader():
        client_orders = list(set([report.client_order for report in ClientOrderExecutiveReport.query.filter(
            ClientOrderExecutiveReport.month_day >= start_Q_month, ClientOrderExecutiveReport.month_day <= end_Q_month)
            if report.client_order.status == 1]))
        douban_orders = list(set([report.douban_order for report in DoubanOrderExecutiveReport.query.filter(
            DoubanOrderExecutiveReport.month_day >= start_Q_month, DoubanOrderExecutiveReport.month_day <= end_Q_month)
            if report.douban_order.status == 1]))
    elif g.user.is_leader():
        client_orders = list(set([report.client_order for report in ClientOrderExecutiveReport.query.filter(
            ClientOrderExecutiveReport.month_day >= start_Q_month, ClientOrderExecutiveReport.month_day <= end_Q_month)
            if report.client_order.status == 1 and g.user.location in report.client_order.locations]))
        douban_orders = list(set([report.douban_order for report in DoubanOrderExecutiveReport.query.filter(
            DoubanOrderExecutiveReport.month_day >= start_Q_month, DoubanOrderExecutiveReport.month_day <= end_Q_month)
            if report.douban_order.status == 1 and g.user.location in report.douban_order.locations]))
    else:
        client_orders = list(set([report.client_order for report in ClientOrderExecutiveReport.query.filter(
            ClientOrderExecutiveReport.month_day >= start_Q_month, ClientOrderExecutiveReport.month_day <= end_Q_month)
            if report.client_order.status == 1 and g.user in report.client_order.direct_sales +
            report.client_order.agent_sales]))
        douban_orders = list(set([report.douban_order for report in DoubanOrderExecutiveReport.query.filter(
            DoubanOrderExecutiveReport.month_day >= start_Q_month, DoubanOrderExecutiveReport.month_day <= end_Q_month)
            if report.douban_order.status == 1 and g.user in report.douban_order.direct_sales +
            report.douban_order.agent_sales]))

    orders = []
    sales = []
    sales_data = []
    for k in client_orders + douban_orders:
        if k.contract_status not in [7, 8, 9]:
            # 格式化合同
            if k.__tablename__ == 'bra_client_order':
                dict_order = _client_order_to_dict(
                    k, now_year, Q_monthes, now_Q)
            else:
                dict_order = _douban_order_to_dict(
                    k, now_year, Q_monthes, now_Q)
            # 获取所有销售
            sales += dict_order['direct_sales'] + dict_order['agent_sales']
            # 获取所有销售数据（包含任务、提成比例）
            sales_data += dict_order['direct_sales_data'] + \
                dict_order['agent_sales_data']
            orders.append(dict_order)
    # 去重销售
    sales = [i for n, i in enumerate(sales) if i not in sales[n + 1:]]
    # 初始化销售完成金额为0
    sale_t_performance = {}
    for k in sales:
        sale_t_performance[str(k['id'])] = 0

    # 获取销售本季度完成情况
    for k in sales_data:
        sale_t_performance[str(k['id'])] += sum(k['zhixing_money'])

    # 设置每个合同中的销售完成率
    for k in orders:
        for s in k['direct_sales_data'] + k['agent_sales_data']:
            if s['performance']:
                final_rate = sale_t_performance[str(s['id'])] / s['performance']
            else:
                final_rate = 0
            if final_rate > 1:
                s['final_rate'] = 1
            else:
                s['final_rate'] = final_rate
            s['commission_money'] = "%.2f" % (
                s['final_rate'] * s['commission'] * s['back_moneys_by_Q'])
    return tpl('/data_query/commission/index.html',
               orders=orders,
               Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, location_id=location_id)
