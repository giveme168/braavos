# -*- coding: UTF-8 -*-
import datetime
import operator

from flask import Blueprint, request
from flask import render_template as tpl

from models.client_order import ClientOrderExecutiveReport, BackMoney, BackInvoiceRebate
from models.douban_order import DoubanOrderExecutiveReport
from models.douban_order import BackMoney as DoubanBackMoney
from models.douban_order import BackInvoiceRebate as DoubanBackInvoiceRebate
from models.order import MediumOrderExecutiveReport
from controllers.data_query.helpers.profit_helpers import write_order_excel, write_douban_order_excel
from libs.date_helpers import get_monthes_pre_days
from models.client import AgentRebate
from models.invoice import AgentInvoicePay, MediumRebateInvoice
from models.medium import MediumRebate

data_query_profit_bp = Blueprint(
    'data_query_profit', __name__, template_folder='../../templates/data_query')


# 新版媒体周报开始
def pre_month_money(money, start, end):
    if money:
        pre_money = float(money) / ((end - start).days + 1)
    else:
        pre_money = 0
    pre_month_days = get_monthes_pre_days(start, end)
    pre_month_money_data = []
    for k in pre_month_days:
        pre_month_money_data.append(
            {'money': pre_money * k['days'], 'month': k['month'], 'days': k['days']})
    return pre_month_money_data


def _douban_order_to_dict(douban_order, all_back_moneys, all_agent_rebate, month_day):
    dict_order = {}
    dict_order['__tablename__'] = 'bra_douban_order'
    dict_order['locations_cn'] = douban_order.locations_cn
    dict_order['client_name'] = douban_order.client.name
    dict_order['agent_name'] = douban_order.agent.name
    dict_order['campaign'] = douban_order.campaign
    dict_order['industry_cn'] = douban_order.client.industry_cn
    dict_order['locations'] = douban_order.locations
    dict_order['contract_status'] = douban_order.contract_status
    dict_order['contract'] = douban_order.contract
    dict_order['direct_sales_names'] = douban_order.direct_sales_names
    dict_order['agent_sales_names'] = douban_order.agent_sales_names
    dict_order['resource_type_cn'] = douban_order.resource_type_cn
    dict_order['start_date_cn'] = douban_order.start_date_cn
    dict_order['end_date_cn'] = douban_order.end_date_cn
    dict_order['back_moneys'] = sum(
        [k['money'] for k in all_back_moneys if k['order_id'] == douban_order.id])
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        douban_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        douban_order.client_end.strftime(dt_format), dt_format)
    executive_report_data = pre_month_money(douban_order.money,
                                            start_datetime,
                                            end_datetime)
    dict_order['now_month_money_zhixing'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() == month_day.date()])

    # 代理返点系数
    agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate if douban_order.agent.id == k[
        'agent_id'] and month_day.year == k['year'].year]
    if agent_rebate_data:
        agent_rebate = agent_rebate_data[0]
    else:
        agent_rebate = 0
    dict_order['now_month_agent_rebate_money'] = dict_order[
        'now_month_money_zhixing'] * agent_rebate / 100
    dict_order['money'] = douban_order.money
    # 直签豆瓣订单客户金额与媒体进个相同
    dict_order['status'] = douban_order.status
    if month_day.year < 2016:
        dict_order['profit_money'] = dict_order[
            'now_month_money_zhixing'] * 0.4 - dict_order['now_month_agent_rebate_money']
    else:
        dict_order['profit_money'] = dict_order[
            'now_month_money_zhixing'] * 0.18
    return dict_order


def _order_to_dict(order, all_back_moneys, all_agent_rebate, month_day):
    dict_order = {}
    dict_order['__tablename__'] = 'bra_order'
    dict_order['medium_name'] = order.medium.name
    dict_order['locations_cn'] = order.client_order.locations_cn
    dict_order['client_name'] = order.client_order.client.name
    dict_order['agent_name'] = order.client_order.agent.name
    dict_order['campaign'] = order.client_order.campaign
    dict_order['industry_cn'] = order.client_order.client.industry_cn
    dict_order['locations'] = order.client_order.locations
    dict_order['contract_status'] = order.client_order.contract_status
    dict_order['contract'] = order.contract
    dict_order['associated_douban_contract'] = order.associated_douban_contract
    dict_order['direct_sales_names'] = order.client_order.direct_sales_names
    dict_order['agent_sales_names'] = order.client_order.agent_sales_names
    dict_order['resource_type_cn'] = order.client_order.resource_type_cn
    dict_order['start_date_cn'] = order.client_order.start_date_cn
    dict_order['end_date_cn'] = order.client_order.end_date_cn
    dict_order['back_moneys'] = sum([k['money'] for k in all_back_moneys if k[
                                    'order_id'] == order.client_order.id])
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        order.client_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        order.client_order.client_end.strftime(dt_format), dt_format)
    executive_report_data = pre_month_money(order.medium_money2,
                                            start_datetime,
                                            end_datetime)
    dict_order['now_month_money_zhixing'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() == month_day.date()])

    # 代理返点系数
    agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate if order.client_order.agent.id == k[
        'agent_id'] and month_day.year == k['year'].year]
    if agent_rebate_data:
        agent_rebate = agent_rebate_data[0]
    else:
        agent_rebate = 0
    dict_order['now_month_agent_rebate_money'] = dict_order[
        'now_month_money_zhixing'] * agent_rebate / 100
    if month_day.year < 2016:
        dict_order['profit_money'] = dict_order[
            'now_month_money_zhixing'] * 0.4 - dict_order['now_month_agent_rebate_money']
    else:
        dict_order['profit_money'] = dict_order[
            'now_month_money_zhixing'] * 0.18
    dict_order['medium_money2'] = order.medium_money2
    dict_order['sale_money'] = order.sale_money
    dict_order['status'] = order.client_order.status
    return dict_order


def _client_order_to_dict(client_order, all_back_moneys, all_agent_rebate, all_agent_rebate_pay,
                          all_medium_rebate, all_medium_rebate_invoice, month_day):
    dict_order = {}
    dict_order['locations_cn'] = client_order.locations_cn
    dict_order['client_name'] = client_order.client.name
    dict_order['agent_name'] = client_order.agent.name
    dict_order['campaign'] = client_order.campaign
    dict_order['industry_cn'] = client_order.client.industry_cn
    dict_order['locations'] = client_order.locations
    dict_order['contract_status'] = client_order.contract_status
    dict_order['contract'] = client_order.contract
    dict_order['direct_sales_names'] = client_order.direct_sales_names
    dict_order['agent_sales_names'] = client_order.agent_sales_names
    dict_order['resource_type_cn'] = client_order.resource_type_cn
    dict_order['start_date_cn'] = client_order.start_date_cn
    dict_order['end_date_cn'] = client_order.end_date_cn
    dict_order['money'] = client_order.money
    dict_order['back_moneys'] = sum(
        [k['money'] for k in all_back_moneys if k['order_id'] == client_order.id])
    dt_format = "%d%m%Y"
    start_datetime = datetime.datetime.strptime(
        client_order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(
        client_order.client_end.strftime(dt_format), dt_format)
    executive_report_data = pre_month_money(client_order.money,
                                            start_datetime,
                                            end_datetime)
    # 获取代理实际返点金额
    agent_rebate_money_data = sum([k['money'] for k in all_back_moneys if k[
                                  'order_id'] == client_order.id and k['type'] == 'invoice'])
    agent_rebate_money_data += sum([k['money']
                                    for k in all_agent_rebate_pay if ['order_id'] == client_order.id])
    rebate_executive_report_data = pre_month_money(agent_rebate_money_data,
                                                   start_datetime,
                                                   end_datetime)
    # 按月折算真实返点
    dict_order['now_month_agent_real_rebate_money'] = sum(
        [k['money'] for k in rebate_executive_report_data if k['month'].date() == month_day.date()])
    # 获取媒体实际返点金额
    medium_real_rebate_money = sum([k['money'] for k in all_medium_rebate_invoice if k[
                                   'order_id'] == client_order.id])
    medium_rebate_executive_report_data = pre_month_money(medium_real_rebate_money,
                                                          start_datetime,
                                                          end_datetime)
    dict_order['now_month_medium_real_rebate_money'] = sum(
        [k['money'] for k in medium_rebate_executive_report_data if k['month'].date() == month_day.date()])
    # 代理返点系数
    agent_rebate_data = [k['inad_rebate'] for k in all_agent_rebate if client_order.agent.id == k[
        'agent_id'] and month_day.year == k['year'].year]
    if agent_rebate_data:
        agent_rebate = agent_rebate_data[0]
    else:
        agent_rebate = 0
    dict_order['now_month_money_zhixing'] = sum(
        [k['money'] for k in executive_report_data if k['month'].date() == month_day.date()])
    dict_order['now_month_agent_rebate_money'] = dict_order[
        'now_month_money_zhixing'] * agent_rebate / 100
    dict_order['medium_data'] = []
    for m in client_order.medium_orders:
        dict_medium = {}
        dict_medium['name'] = m.medium.name
        dict_medium['contract'] = m.contract
        dict_medium['sale_money'] = m.sale_money
        dict_medium['medium_money2'] = m.medium_money2
        dict_medium['medium_contract'] = m.medium_contract
        sele_executive_report_data = pre_month_money(m.sale_money,
                                                     start_datetime,
                                                     end_datetime)
        executive_report_data = pre_month_money(m.medium_money2,
                                                start_datetime,
                                                end_datetime)
        dict_medium['now_month_money_zhixing'] = sum(
            [k['money'] for k in executive_report_data if k['month'].date() == month_day.date()])
        dict_medium['now_month_money_kehu'] = sum(
            [k['money'] for k in sele_executive_report_data if k['month'].date() == month_day.date()])
        # 媒体返点系数
        medium_rebate_data = [k['rebate'] for k in all_medium_rebate if m.medium.id == k[
            'medium_id'] and month_day.year == k['year'].year]
        if medium_rebate_data:
            medium_rebate = medium_rebate_data[0]
        else:
            medium_rebate = 0
        dict_medium['now_month_medium_rebate_money'] = dict_medium[
            'now_month_money_zhixing'] * medium_rebate / 100
        dict_order['medium_data'].append(dict_medium)
    dict_order['now_month_medium_rebate_money'] = sum(
        [k['now_month_medium_rebate_money'] for k in dict_order['medium_data']])
    dict_order['now_month_medium_money2_zhixing'] = sum(
        [k['now_month_money_zhixing'] for k in dict_order['medium_data']])
    dict_order['profit_money'] = dict_order['now_month_money_zhixing'] - dict_order['now_month_agent_rebate_money'] +\
        dict_order['now_month_medium_rebate_money'] - \
        dict_order['now_month_medium_money2_zhixing']
    dict_order['real_profit_money'] = dict_order['now_month_money_zhixing'] - dict_order['now_month_agent_real_rebate_money'] +\
        dict_order['now_month_medium_real_rebate_money'] - \
        dict_order['now_month_medium_money2_zhixing']
    dict_order['status'] = client_order.status
    return dict_order


def _all_client_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.client_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in BackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.client_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in BackInvoiceRebate.all()]
    return dict_back_money_data


def _all_douban_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.douban_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in DoubanBackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.douban_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in DoubanBackInvoiceRebate.all()]
    return dict_back_money_data


def _all_agent_rebate():
    agent_rebate_data = [{'agent_id': k.agent_id, 'inad_rebate': k.inad_rebate,
                          'douban_rebate': k.douban_rebate, 'year': k.year} for k in AgentRebate.all()]
    return agent_rebate_data


def _all_agent_rebate_pay():
    agent_rebate_pay_data = [{'order_id': k.agent_invoice.client_order_id,
                              'money': k.money, 'agent_id': k.agent_invoice.agent_id,
                              'pay_time': k.pay_time} for k in AgentInvoicePay.all() if k.pay_status == 0]
    return agent_rebate_pay_data


def _all_medium_rebate():
    medium_rebate_data = [{'medium_id': k.medium_id, 'rebate': k.rebate,
                           'year': k.year} for k in MediumRebate.all()]
    return medium_rebate_data


def _all_medium_rebate_invoice():
    medium_rebate_invoice = [{'order_id': k.client_order_id, 'money': k.money}
                             for k in MediumRebateInvoice.all() if k.invoice_status == 0]
    return medium_rebate_invoice


@data_query_profit_bp.route('/client_order', methods=['GET'])
def client_order():
    now_date = datetime.datetime.now()
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    client_orders = list(set([k.client_order for k in ClientOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.status == 1]))
    all_back_moneys = _all_client_order_back_moneys()
    all_agent_rebate = _all_agent_rebate()
    all_agent_rebate_pay = _all_agent_rebate_pay()
    all_medium_rebate = _all_medium_rebate()
    all_medium_rebate_invoice = _all_medium_rebate_invoice()
    client_order_data = [_client_order_to_dict(k, all_back_moneys, all_agent_rebate, all_agent_rebate_pay,
                                               all_medium_rebate, all_medium_rebate_invoice, now_month
                                               ) for k in client_orders]
    client_order_data = [k for k in client_order_data if k[
        'contract_status'] not in [0, 7, 8, 9]]
    if client_order_data:
        client_order_data = sorted(
            client_order_data, key=operator.itemgetter('start_date_cn'), reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(client_order_data, year, month)
        return response
    return tpl('/data_query/profit/client_order.html', year=int(year),
               month=int(month), client_orders=client_order_data)


@data_query_profit_bp.route('/douban_order', methods=['GET'])
def douban_order():
    now_date = datetime.datetime.now()
    year = str(request.values.get('year', now_date.year))
    month = str(request.values.get('month', now_date.month))
    now_month = datetime.datetime.strptime(year + '-' + month, '%Y-%m')
    all_back_moneys = _all_douban_order_back_moneys()
    all_client_back_moneys = _all_client_order_back_moneys()
    all_agent_rebate = _all_agent_rebate()
    douban_orders = list(set([k.douban_order for k in DoubanOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.douban_order.status == 1]))
    douban_order_data = [_douban_order_to_dict(
        k, all_back_moneys, all_agent_rebate, now_month) for k in douban_orders]
    medium_orders = list(set([k.order for k in MediumOrderExecutiveReport.query.filter_by(
        month_day=now_month) if k.status == 1 and k.order.associated_douban_order]))
    douban_order_data += [_order_to_dict(
        k, all_client_back_moneys, all_agent_rebate, now_month) for k in medium_orders]
    douban_order_data = [k for k in douban_order_data if k[
        'contract_status'] not in [0, 7, 8, 9]]
    if douban_order_data:
        douban_order_data = sorted(
            douban_order_data, key=operator.itemgetter('start_date_cn'), reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_douban_order_excel(douban_order_data, year, month)
        return response
    return tpl('/data_query/profit/douban_order.html', year=int(year),
               month=int(month), douban_orders=douban_order_data)
