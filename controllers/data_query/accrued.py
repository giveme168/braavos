# -*- coding: UTF-8 -*-
import datetime
import operator
import numpy

from flask import request, g, abort
from flask import render_template as tpl

from models.douban_order import DoubanOrder, BackMoney as DoubanBackMoney, BackInvoiceRebate as DoubanBackInvoiceRebate
from models.client_order import ClientOrder, BackMoney, BackInvoiceRebate
from models.client import AgentRebate, AgentMediaRebate
from models.medium import MediumGroupRebate, MediumGroupMediaRebate
from models.outsource import DoubanOutSource, OutSource
from searchAd.models.client_order import (searchAdClientOrder, searchAdBackMoney,
                                          searchAdConfirmMoney, searchAdBackInvoiceRebate)
from models.order import Order
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.accrued_helpers import write_search_order_excel
from controllers.data_query.helpers.shenji_helpers import write_client_order_excel, write_douban_order_excel
from flask import Blueprint

data_query_accrued_bp = Blueprint(
    'data_query_accrued', __name__,
    template_folder='../../templates/data_query')


def _all_client_order_outsource():
    return [{'order_id': o.medium_order.client_order.id,
             'money': o.num} for o in OutSource.all() if o.status in [2, 3, 4]]


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
    medium_rebate_data = [{'media_id': k.media_id, 'rebate': k.rebate, 'medium_group_id': k.medium_group.id,
                           'year': k.year} for k in MediumGroupMediaRebate.all()]
    return medium_rebate_data


def _all_medium_group_rebate():
    medium_group_rebate_data = [{'rebate': k.rebate, 'medium_group_id': k.medium_group.id,
                                 'year': k.year} for k in MediumGroupRebate.all()]
    return medium_group_rebate_data


def _all_agent_media_rebate():
    agent_media_rebate_data = [{'agent_id': k.agent.id, 'media_id': k.media.id, 'year': k.year,
                                'rebate': k.rebate} for k in AgentMediaRebate.all()]
    return agent_media_rebate_data


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


def _client_order_to_dict(client_order, all_back_moneys, all_agent_rebate,
                          all_medium_rebate, all_medium_group_rebate, all_agent_media_rebate,
                          pre_year_month, all_outsource, shenji=1):
    dict_order = {}
    dict_order['order_id'] = client_order.id
    dict_order['subject_cn'] = client_order.subject_cn
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
    # 获取所有外包信息
    t_outsource_money = sum([o['money'] for o in all_outsource if o['order_id'] == dict_order['order_id']])
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
    dict_order['money_data'] = [0 for k in pre_year_month]
    # 初始化媒体数据容器
    dict_order['medium_data'] = []
    # 初始化总计媒体执行金额
    total_medium_money2_data = [0 for k in range(12)]
    # 初始化总计媒体返点
    total_medium_money2_rebate_data = [0 for k in range(12)]
    dict_order['medium_sale_money'] = 0
    dict_order['medium_medium_money2'] = 0
    # 单笔返点
    try:
        self_agent_rebate_data = client_order.self_agent_rebate
        self_agent_rebate = self_agent_rebate_data.split('-')[0]
        self_agent_rebate_value = float(self_agent_rebate_data.split('-')[1])
    except:
        self_agent_rebate = 0
        self_agent_rebate_value = 0
    # 初始化代理返点
    dict_order['money_rebate_data'] = [0 for k in range(12)]
    '''
    # 客户返点
    if int(self_agent_rebate):
        if dict_order['money']:
            dict_order['money_rebate_data'] = [k / dict_order['money'] * self_agent_rebate_value
                                               for k in dict_order['money_data']]
        else:
            dict_order['money_rebate_data'] = [0 for k in dict_order['money_data']]
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
    '''
    for m in client_order.medium_orders:
        dict_medium = {}
        dict_medium['medium_group_name'] = m.medium_group.name
        dict_medium['name'] = m.media.name
        dict_medium['sale_money'] = m.sale_money
        dict_order['medium_sale_money'] += dict_medium['sale_money']
        dict_medium['medium_money2'] = m.medium_money2
        dict_order['medium_medium_money2'] += dict_medium['medium_money2']
        dict_medium['medium_contract'] = m.medium_contract
        start_datetime = datetime.datetime.strptime(
            m.medium_start.strftime(dt_format), dt_format)
        end_datetime = datetime.datetime.strptime(
            m.medium_end.strftime(dt_format), dt_format)
        sale_money_ex_data = pre_month_money(m.sale_money,
                                             start_datetime,
                                             end_datetime)
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
        # 媒体售卖执行金额
        dict_medium['sale_money_data'] = []
        for k in pre_year_month:
            if k['month'] in sale_money_ex_data:
                dict_medium['sale_money_data'].append(
                    sale_money_ex_data[k['month']])
            else:
                dict_medium['sale_money_data'].append(0)
        dict_order['money_data'] = numpy.array(dict_order['money_data']) + numpy.array(dict_medium['sale_money_data'])
        # 客户返点系数
        if int(self_agent_rebate):
            if dict_medium['sale_money']:
                dict_medium['sale_money_rebate_data'] = [k / dict_order['money'] * self_agent_rebate_value
                                                         for k in dict_medium['sale_money_data']]
            else:
                dict_medium['sale_money_rebate_data'] = [0 for k in dict_medium['sale_money_data']]
        else:
            # 是否有代理针对媒体的特殊返点
            agent_media_rebate = [k['rebate'] for k in all_agent_media_rebate
                                  if client_order.agent.id == k['agent_id'] and
                                  pre_year_month[0]['month'].year == k['year'].year and
                                  m.media.id == k['media_id']]
            if agent_media_rebate:
                agent_rebate = agent_media_rebate[0]
            else:
                agent_rebate_data = [k['inad_rebate'] for k in all_agent_rebate if client_order.agent.id == k[
                    'agent_id'] and pre_year_month[0]['month'].year == k['year'].year]
                if agent_rebate_data:
                    agent_rebate = agent_rebate_data[0]
                else:
                    agent_rebate = 0
            if agent_rebate:
                dict_medium['sale_money_rebate_data'] = [k * agent_rebate / 100 for k in dict_medium['sale_money_data']]
            else:
                dict_medium['sale_money_rebate_data'] = [0 for k in dict_medium['sale_money_data']]
        dict_order['money_rebate_data'] = numpy.array(dict_order['money_rebate_data']) +\
            numpy.array(dict_medium['sale_money_rebate_data'])
        # 媒体返点系数
        # 是否有媒体单笔返点
        try:
            self_medium_rebate_data = m.self_medium_rebate
            self_medium_rebate = self_medium_rebate_data.split('-')[0]
            self_medium_rebate_value = float(self_medium_rebate_data.split('-')[1])
        except:
            self_medium_rebate = 0
            self_medium_rebate_value = 0
        if int(self_medium_rebate):
            if dict_medium['medium_money2']:
                dict_medium['medium_money2_rebate_data'] = [k / dict_medium['medium_money2'] * self_medium_rebate_value
                                                            for k in dict_medium['medium_money2_data']]
            else:
                dict_medium['medium_money2_rebate_data'] = [0 for k in dict_medium['medium_money2_data']]
        else:
            # 是否有媒体供应商针对媒体的特殊返点
            medium_rebate_data = [k['rebate'] for k in all_medium_rebate
                                  if m.media.id == k['media_id'] and
                                  pre_year_month[0]['month'].year == k['year'].year and
                                  m.medium_group.id == k['medium_group_id']]
            if medium_rebate_data:
                medium_rebate = medium_rebate_data[0]
            else:
                # 是否有媒体供应商返点
                medium_group_rebate = [k['rebate'] for k in all_medium_group_rebate
                                       if pre_year_month[0]['month'].year == k['year'].year and
                                       m.medium_group.id == k['medium_group_id']]
                if medium_group_rebate:
                    medium_rebate = medium_group_rebate[0]
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
    if shenji:
        dict_order['profit_data'] = numpy.array(dict_order['profit_data']) - numpy.array(dict_order['outsource_data'])
    dict_order['total_medium_money2_data'] = total_medium_money2_data
    dict_order['total_medium_money2_rebate_data'] = total_medium_money2_rebate_data
    return dict_order


@data_query_accrued_bp.route('/client_order', methods=['GET'])
def client_order():
    if not (g.user.is_super_leader() or g.user.is_aduit() or g.user.is_finance() or g.user.is_contract()):
        abort(403)
    shenji = int(request.values.get('shenji', 0))
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    # 获取整年月份
    pre_year_month = get_monthes_pre_days(datetime.datetime.strptime(str(year) + '-01', '%Y-%m'),
                                          datetime.datetime.strptime(str(year) + '-12', '%Y-%m'))
    # 获取所有回款包含返点发票
    back_money_data = _all_client_order_back_moneys()
    # 获取代理返点系数
    all_agent_rebate = _all_agent_rebate()
    # 获取媒体供应商针对媒体返点系数
    all_medium_rebate = _all_medium_rebate()
    # 获取媒体供应商返点
    all_medium_group_rebate = _all_medium_group_rebate()
    # 获取代理针对特殊媒体的返点
    all_agent_media_rebate = _all_agent_media_rebate()
    # 获取所有外包信息
    all_outsource = _all_client_order_outsource()
    # 获取当年合同
    orders = ClientOrder.query.filter(ClientOrder.status == 1,
                                      ClientOrder.contract != '')
    # 去重合同
    orders = [k for k in orders if k.client_start.year ==
              year or k.client_end.year == year]
    # 格式化合同
    orders = [_client_order_to_dict(k, back_money_data, all_agent_rebate,
                                    all_medium_rebate, all_medium_group_rebate,
                                    all_agent_media_rebate, pre_year_month,
                                    all_outsource, shenji) for k in orders]
    # 去掉撤单、申请中的合同
    orders = [k for k in orders if k['contract_status'] in [2, 4, 5, 10, 19, 20]]
    orders = sorted(
        orders, key=operator.itemgetter('start_date_cn'), reverse=False)
    total_outsource_data = [0 for k in range(12)]
    total_money_data = [0 for k in range(12)]
    total_money_rebate_data = [0 for k in range(12)]
    total_profit_data = [0 for k in range(12)]
    total_medium_money2_data = [0 for k in range(12)]
    total_medium_money2_rebate_data = [0 for k in range(12)]
    for k in orders:
        total_outsource_data = numpy.array(
            total_outsource_data) + numpy.array(k['outsource_data'])
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
                                        total_medium_money2_rebate_data=total_medium_money2_rebate_data,
                                        total_outsource_data=total_outsource_data,
                                        shenji=shenji)
    if shenji:
        tpl_html = '/data_query/accrued/client_order_s.html'
    else:
        tpl_html = '/data_query/accrued/client_order.html'
    return tpl(tpl_html, orders=orders, year=year, total_money_data=total_money_data,
               total_money_rebate_data=total_money_rebate_data, total_profit_data=total_profit_data,
               total_medium_money2_data=total_medium_money2_data,
               total_medium_money2_rebate_data=total_medium_money2_rebate_data,
               total_outsource_data=total_outsource_data)


def _all_douban_order_outsource():
    outsource = [{'order_id': o.douban_order.id, 'money': o.num, 'type': 'douban'}
                 for o in DoubanOutSource.all() if o.status in [2, 3, 4]]
    outsource += [{'order_id': o.medium_order.id, 'money': o.num, 'type': 'client'}
                  for o in OutSource.all() if o.status in [2, 3, 4]]
    return outsource


def _all_douban_order_back_moneys():
    dict_back_money_data = [{'money': k.money, 'order_id': k.douban_order_id,
                             'back_time': k.back_time, 'type': 'money'} for k in DoubanBackMoney.all()]
    dict_back_money_data += [{'money': k.money, 'order_id': k.douban_order_id,
                              'back_time': k.back_time, 'type': 'invoice'} for k in DoubanBackInvoiceRebate.all()]
    return dict_back_money_data


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
    t_outsource_money = sum([o['money'] for o in all_outsource
                             if o['order_id'] == dict_order['order_id'] and o['type'] == 'douban'])
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
    dict_order['agent_name'] = order.medium_group.name
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
        if order.medium_group.id == 19:
            agent_id = 94
        elif order.medium_group.id == 8:
            agent_id = 105
        elif order.medium_group.id == 68:
            agent_id = 228
        elif order.medium_group.id == 9:
            agent_id = 93
        elif order.medium_group.id == 39:
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


@data_query_accrued_bp.route('/douban_order', methods=['GET'])
def douban_order():
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
                                           pre_year_month, all_outsource_data, shenji) for k in Order.all()
                     if (k.medium_start.year == year or k.medium_end.year == year) and k.associated_douban_order]
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
        tpl_html = '/data_query/accrued/douban_order_s.html'
    else:
        tpl_html = '/data_query/accrued/douban_order.html'
    return tpl(tpl_html, orders=orders, year=year,
               total_money_data=total_money_data,
               total_money_rebate_data=total_money_rebate_data,
               total_outsource_data=total_outsource_data,
               total_profit_data=total_profit_data)


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
