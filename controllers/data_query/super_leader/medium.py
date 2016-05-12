# -*- coding: UTF-8 -*-
import datetime
import numpy

from flask import Blueprint, request, g
from flask import render_template as tpl

from libs.date_helpers import get_monthes_pre_days
from models.client import AgentRebate
from models.medium import MediumRebate
from models.medium import Medium
from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from searchAd.models.order import searchAdMediumOrderExecutiveReport
from searchAd.models.rebate_order import searchAdRebateOrderExecutiveReport
from controllers.data_query.helpers.super_leader_helpers import write_medium_money_excel

data_query_super_leader_medium_bp = Blueprint(
    'data_query_super_leader_medium', __name__, template_folder='../../templates/data_query')
except_medium_ids = [4, 5, 6, 7, 9, 14, 21, 51, 52, 57]


def _all_agent_rebate():
    agent_rebate_data = [{'agent_id': k.agent_id, 'inad_rebate': k.inad_rebate,
                          'douban_rebate': k.douban_rebate, 'year': k.year} for k in AgentRebate.all()]
    return agent_rebate_data


def _all_medium_rebate():
    medium_rebate_data = [{'medium_id': k.medium_id, 'rebate': k.rebate,
                           'year': k.year} for k in MediumRebate.all()]
    return medium_rebate_data


########
# 计算合同的收入成本值：
# 第一个参数：合同， 第二个参数：计算横跨时间段，第三个参数：媒体ids（用于识别计算媒体），
# 第四个参数：合同类型，第五个参数：代理信息（只有关联豆瓣订单时使用）
########
def _get_medium_moneys(orders, pre_monthes, medium_ids, o_type='zhiqian_order', year=2015):
    money_obj = {'sale_money': [], 'money2': [],
                 'm_ex_money': [], 'a_rebate': [], 'profit': []}
    for d in pre_monthes:
        if isinstance(medium_ids, list):
            pro_month_orders = [o for o in orders if o['month_day'] == d[
                'month'] and o['medium_id'] in medium_ids]
        elif medium_ids == 0:
            pro_month_orders = [
                o for o in orders if o['month_day'] == d['month']]
        else:
            pro_month_orders = [o for o in orders if o['month_day'] == d[
                'month'] and o['medium_id'] not in except_medium_ids]

        for k in range(1, 4):
            location_orders = [
                o for o in pro_month_orders if len(set(o['locations']) & set([k]))]
            if location_orders:
                if o_type == 'zhiqian_order':
                    sale_money = sum(
                        [o['sale_money'] / len(o['locations']) for o in location_orders])
                    money2 = sum([o['medium_money2'] / len(o['locations'])
                                  for o in location_orders])
                    if year == 2016:
                        money2 = money2 * 0.18
                    elif year == 2014:
                        money2 = money2 * 0.426
                    else:
                        money2 = money2 * 0.4
                    a_rebate = sum(
                        [o['money_rebate_data'] / len(o['locations']) for o in location_orders])
                    profit = money2 - a_rebate
                    m_ex_money = 0
                else:
                    sale_money = sum(
                        [o['sale_money'] / len(o['locations']) for o in location_orders])
                    money2 = sum([o['medium_money2'] / len(o['locations'])
                                  for o in location_orders])
                    m_ex_money = sum(
                        [o['m_ex_money'] / len(o['locations']) for o in location_orders])
                    a_rebate = sum(
                        [o['money_rebate_data'] / len(o['locations']) for o in location_orders])
                    profit = sum([o['profit_data'] / len(o['locations'])
                                  for o in location_orders])
                money_obj['sale_money'].append(round(sale_money, 2))
                money_obj['money2'].append(round(money2, 2))
                money_obj['m_ex_money'].append(round(m_ex_money, 2))
                money_obj['a_rebate'].append(round(a_rebate, 2))
                money_obj['profit'].append(round(profit, 2))
            else:
                money_obj['sale_money'].append(0.0)
                money_obj['money2'].append(0.0)
                money_obj['m_ex_money'].append(0.0)
                money_obj['a_rebate'].append(0.0)
                money_obj['profit'].append(0.0)
    return money_obj


def _parse_dict_order(order, all_agent_rebate=None):
    d_order = {}
    d_order['month_day'] = order.month_day
    if order.__tablename__ == 'bra_medium_order_executive_report':
        d_order['medium_id'] = order.order.medium.id
        d_order['order_id'] = order.client_order.id
        d_order['medium_order_id'] = order.order.id
    else:
        d_order['medium_id'] = 0
        d_order['medium_order_id'] = 0
    if order.__tablename__ == 'bra_douban_order_executive_report':
        d_order['order_id'] = order.douban_order.id
        d_order['locations'] = order.douban_order.locations
        d_order['contract_status'] = order.douban_order.contract_status
        d_order['sale_money'] = order.money
        d_order['medium_money2'] = order.money
        d_order['medium_rebate'] = 0
        # 单笔返点
        try:
            self_agent_rebate_data = order.douban_order.self_agent_rebate
            self_agent_rebate = self_agent_rebate_data.split('-')[0]
            self_agent_rebate_value = float(
                self_agent_rebate_data.split('-')[1])
        except:
            self_agent_rebate = 0
            self_agent_rebate_value = 0
        # 客户返点
        if int(self_agent_rebate):
            d_order['money_rebate_data'] = d_order['sale_money'] / \
                order.douban_order.money * self_agent_rebate_value
        else:
            # 代理返点系数
            agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate if order.douban_order.agent.id == k[
                'agent_id'] and order.month_day.year == k['year'].year]
            if agent_rebate_data:
                agent_rebate = agent_rebate_data[0]
            else:
                agent_rebate = 0
            d_order['money_rebate_data'] = d_order[
                'sale_money'] * agent_rebate / 100
        # 合同利润
        if int(order.month_day.year) > 2015:
            d_order['profit_data'] = d_order['sale_money'] * 0.18
        elif int(order.month_day.year) == 2015:
            d_order['profit_data'] = d_order['sale_money'] * 0.4
            d_order['profit_data'] = d_order[
                'profit_data'] - d_order['money_rebate_data']
        else:
            d_order['profit_data'] = d_order['sale_money'] * 0.426
            d_order['profit_data'] = d_order[
                'profit_data'] - d_order['money_rebate_data']
        d_order['m_ex_money'] = 0
        d_order['is_c_douban'] = False
    elif order.__tablename__ == 'bra_searchad_rebate_order_executive_report':
        d_order['locations'] = order.rebate_order.locations
        d_order['contract_status'] = order.rebate_order.contract_status
        d_order['sale_money'] = order.money
        d_order['medium_money2'] = order.money
        d_order['medium_rebate'] = 0
        d_order['money_rebate_data'] = 0
        # 单笔返点
        d_order['self_agent_rebate'] = 0
        d_order['self_agent_rebate_value'] = 0
        d_order['m_ex_money'] = 0
        d_order['profit_data'] = d_order['sale_money']
        # 是否关联豆瓣订单
        d_order['is_c_douban'] = False
    else:
        d_order['money'] = order.client_order.money
        d_order['locations'] = order.client_order.locations
        d_order['contract_status'] = order.client_order.contract_status
        d_order['sale_money'] = order.sale_money
        d_order['medium_money2'] = order.medium_money2
        medium_rebate = order.order.medium_rebate_by_year(d_order['month_day'])
        d_order['medium_rebate'] = d_order[
            'medium_money2'] * medium_rebate / 100
        # 是否关联豆瓣订单
        try:
            ass_order = order.order.associated_douban_order
            if ass_order:
                d_order['is_c_douban'] = True
            else:
                d_order['is_c_douban'] = False
        except:
            d_order['is_c_douban'] = False
        if all_agent_rebate:
            # 单笔返点
            try:
                self_agent_rebate_data = order.client_order.self_agent_rebate
                self_agent_rebate = self_agent_rebate_data.split('-')[0]
                self_agent_rebate_value = float(
                    self_agent_rebate_data.split('-')[1])
            except:
                self_agent_rebate = 0
                self_agent_rebate_value = 0
            # 客户返点
            if int(self_agent_rebate):
                d_order['money_rebate_data'] = d_order['sale_money'] / \
                    d_order['money'] * self_agent_rebate_value
            else:
                # 代理返点系数
                if d_order['is_c_douban']:
                    agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate
                                         if order.client_order.agent.id == k['agent_id'] and
                                         order.month_day.year == k['year'].year]
                else:
                    agent_rebate_data = [k['inad_rebate'] for k in all_agent_rebate
                                         if order.client_order.agent.id == k['agent_id'] and
                                         order.month_day.year == k['year'].year]
                if agent_rebate_data:
                    agent_rebate = agent_rebate_data[0]
                else:
                    agent_rebate = 0
                d_order['money_rebate_data'] = d_order[
                    'sale_money'] * agent_rebate / 100
        else:
            d_order['money_rebate_data'] = 0
        if d_order['is_c_douban']:
            # 合同利润
            if int(order.month_day.year) > 2015:
                d_order['profit_data'] = d_order['medium_money2'] * 0.18
            elif int(order.month_day.year) == 2015:
                d_order['profit_data'] = d_order['medium_money2'] * 0.4
                d_order['profit_data'] = d_order[
                    'profit_data'] - d_order['money_rebate_data'] - d_order['medium_rebate']
            else:
                d_order['profit_data'] = d_order['medium_money2'] * 0.426
                d_order['profit_data'] = d_order[
                    'profit_data'] - d_order['money_rebate_data'] - d_order['medium_rebate']
            d_order['sale_money'] = order.medium_money2
            d_order['medium_money2'] = order.medium_money2
        else:
            # 合同利润
            d_order['profit_data'] = d_order['medium_money2'] - \
                d_order['money_rebate_data'] - d_order['medium_rebate']
        d_order['m_ex_money'] = d_order[
            'medium_money2'] - d_order['medium_rebate']
    d_order['status'] = order.status
    return d_order


def _douban_order_to_dict(order, all_agent_rebate):
    douban_order = order.douban_order
    dict_order = {}
    dict_order['month_day'] = order.month_day
    dict_order['order_id'] = douban_order.id
    dict_order['type'] = 'douban_order'
    dict_order['locations'] = douban_order.locations
    dict_order['contract_status'] = douban_order.contract_status
    dict_order['contract'] = douban_order.contract
    dict_order['start_date_cn'] = douban_order.start_date_cn
    dict_order['end_date_cn'] = douban_order.end_date_cn
    dict_order['all_money'] = douban_order.money
    # 客户执行金额
    dict_order['sale_money'] = order.money
    dict_order['medium_money2'] = order.money
    dict_order['m_ex_money'] = 0
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
        dict_order['money_rebate_data'] = dict_order['sale_money'] / \
            dict_order['all_money'] * self_agent_rebate_value
    else:
        # 代理返点系数
        agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate if douban_order.agent.id == k[
            'agent_id'] and dict_order['month_day'].year == k['year'].year]
        if agent_rebate_data:
            agent_rebate = agent_rebate_data[0]
        else:
            agent_rebate = 0
        dict_order['money_rebate_data'] = dict_order[
            'sale_money'] * agent_rebate / 100
    return dict_order


def _ass_medium_order_to_dict(order, all_agent_rebate, all_medium_rebate):
    dict_order = {}
    dict_order['month_day'] = order.month_day
    dict_order['order_id'] = order.client_order.id
    dict_order['type'] = 'medium_order'
    dict_order['medium_order_id'] = order.id
    dict_order['locations'] = order.client_order.locations
    dict_order['contract_status'] = order.client_order.contract_status
    dict_order['status'] = order.client_order.status
    dict_order['contract'] = order.order.associated_douban_contract
    dict_order['start_date_cn'] = order.client_order.start_date_cn
    dict_order['end_date_cn'] = order.client_order.end_date_cn
    dict_order['all_money'] = order.client_order.money
    dict_order['sale_money'] = order.sale_money
    dict_order['medium_money2'] = order.medium_money2
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
        dict_order['money_rebate_data'] = dict_order['sale_money'] / \
            dict_order['all_money'] * self_agent_rebate_value
    else:
        # 代理返点系数
        if order.order.medium.id == 8:
            agent_id = 94
        elif order.order.medium.id == 3:
            agent_id = 105
        elif order.order.medium.id == 44:
            agent_id = 228
        elif order.order.medium.id == 27:
            agent_id = 93
        elif order.order.medium.id == 37:
            agent_id = 213
        else:
            agent_id = 0
        agent_rebate_data = [k['douban_rebate'] for k in all_agent_rebate if agent_id == k[
            'agent_id'] and dict_order['month_day'].year == k['year'].year]
        if agent_rebate_data:
            agent_rebate = agent_rebate_data[0]
        else:
            agent_rebate = 0
        dict_order['money_rebate_data'] = order.medium_money2 * \
            agent_rebate / 100
    # 合同利润
    dict_order['m_ex_money'] = 0
    dict_order['profit_data'] = dict_order[
        'medium_money2'] - dict_order['money_rebate_data']
    return dict_order


def _client_order_to_dict(order, all_agent_rebate, all_medium_rebate):
    dict_order = {}
    dict_order['medium_id'] = order.order.medium.id
    dict_order['month_day'] = order.month_day
    client_order = order.client_order
    dict_order['order_id'] = client_order.id
    dict_order['locations'] = client_order.locations
    dict_order['contract_status'] = client_order.contract_status
    dict_order['contract'] = client_order.contract
    dict_order['start_date_cn'] = client_order.start_date_cn
    dict_order['end_date_cn'] = client_order.end_date_cn
    dict_order['all_money'] = client_order.money
    dict_order['medium_money2'] = order.medium_money2
    dict_order['sale_money'] = order.sale_money
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
        if dict_order['sale_money']:
            dict_order['money_rebate_data'] = dict_order[
                'sale_money'] / dict_order['all_money'] * self_agent_rebate_value
        else:
            dict_order['money_rebate_data'] = 0
    else:
        # 代理返点系数
        agent_rebate_data = [k['inad_rebate'] for k in all_agent_rebate if client_order.agent.id == k[
            'agent_id'] and dict_order['month_day'].year == k['year'].year]
        if agent_rebate_data:
            agent_rebate = agent_rebate_data[0]
        else:
            agent_rebate = 0
        dict_order['money_rebate_data'] = dict_order[
            'sale_money'] * agent_rebate / 100

    medium_rebate_data = [k['rebate'] for k in all_medium_rebate if dict_order[
        'medium_id'] == k['medium_id'] and dict_order['month_day'].year == k['year'].year]
    if medium_rebate_data:
        medium_rebate = medium_rebate_data[0]
    else:
        medium_rebate = 0
    medium_money2_rebate_data = dict_order[
        'medium_money2'] * medium_rebate / 100
    # 合同利润
    dict_order['m_ex_money'] = dict_order[
        'medium_money2'] - medium_money2_rebate_data
    dict_order['profit_data'] = dict_order['sale_money'] - dict_order[
        'money_rebate_data'] - dict_order['medium_money2'] + medium_money2_rebate_data
    dict_order['status'] = client_order.status
    return dict_order


def _search_order_to_dict(order):
    dict_order = {}
    dict_order['month_day'] = order.month_day
    search_order = order.client_order
    dict_order['locations'] = search_order.locations
    dict_order['contract_status'] = search_order.contract_status
    dict_order['contract'] = search_order.contract
    dict_order['start_date_cn'] = search_order.start_date_cn
    dict_order['end_date_cn'] = search_order.end_date_cn
    dict_order['all_money'] = search_order.money
    # 客户执行金额
    dict_order['sale_money'] = order.sale_money
    dict_order['medium_money2'] = order.medium_money2
    dict_order['status'] = search_order.status
    dict_order['m_ex_money'] = dict_order['medium_money2']
    dict_order['money_rebate_data'] = 0
    dict_order['profit_data'] = dict_order['sale_money'] - \
        dict_order['money_rebate_data'] - dict_order['medium_money2']
    return dict_order


def _search_rebate_order_to_dict(order):
    dict_order = {}
    dict_order['month_day'] = order.month_day
    search_order = order.rebate_order
    dict_order['locations'] = search_order.locations
    dict_order['contract_status'] = search_order.contract_status
    dict_order['contract'] = search_order.contract
    dict_order['start_date_cn'] = search_order.start_date_cn
    dict_order['end_date_cn'] = search_order.end_date_cn
    dict_order['all_money'] = search_order.money
    # 客户执行金额
    dict_order['sale_money'] = order.money
    dict_order['medium_money2'] = order.money
    dict_order['m_ex_money'] = 0
    dict_order['money_rebate_data'] = 0
    dict_order['profit_data'] = dict_order['sale_money']
    dict_order['status'] = search_order.status
    return dict_order


##########
# 媒体清单计算方法
# 豆瓣执行收入：直签豆瓣订单合同金额 + 关联豆瓣订单合同金额
# 豆瓣服务费计提：直签豆瓣订单合同金额 * 0.4 + 关联豆瓣订单合同金额
# 豆瓣订单返点成本：直签豆瓣订单对代理的返点 + 关联豆瓣订单豆瓣对关联媒体的返点
#
# 媒体收入：媒体订单售卖金额
# 媒体合同金额：媒体订单媒体金额
# 媒体净成本：媒体合同金额 - 对媒体的返点
# 媒体代理成本：对客户/代理的返点
# 媒体毛利：媒体收入- 媒体净成本 - 媒体代理成本
#########
@data_query_super_leader_medium_bp.route('/money', methods=['GET'])
def money():
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    start_date_month = datetime.datetime.strptime(
        str(year) + '-01' + '-01', '%Y-%m-%d')
    end_date_month = datetime.datetime.strptime(
        str(year) + '-12' + '-31', '%Y-%m-%d')
    pre_monthes = get_monthes_pre_days(start_date_month, end_date_month)
    # 获取代理返点系数
    all_agent_rebate = _all_agent_rebate()
    # 获取媒体返点系数
    all_medium_rebate = _all_medium_rebate()

    # 直签豆瓣订单开始
    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)
    douban_orders = [_douban_order_to_dict(k, all_agent_rebate)
                     for k in douban_orders if k.status == 1]
    douban_orders = [k for k in douban_orders if k[
        'contract_status'] in [2, 4, 5, 19, 20]]
    douban_money = _get_medium_moneys(
        douban_orders, pre_monthes, 0, 'zhiqian_order', year)
    # 直签豆瓣订单结束

    # 媒体订单开始
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)
    # 关联豆瓣订单开始
    ass_douban_order = [_ass_medium_order_to_dict(
        k, all_agent_rebate, all_medium_rebate) for k in medium_orders if k.order.associated_douban_order]
    ass_douban_order = [k for k in ass_douban_order if k[
        'contract_status'] in [2, 4, 5, 19, 20]]
    ass_douban_money = _get_medium_moneys(
        ass_douban_order, pre_monthes, 0, 'medium_order', year)
    # 关联豆瓣订单结束

    # 普通媒体订单
    medium_orders = [_client_order_to_dict(k, all_agent_rebate, all_medium_rebate)
                     for k in medium_orders if k.status == 1]
    medium_orders = [k for k in medium_orders if k[
        'contract_status'] in [2, 4, 5, 19, 20] and k['status'] == 1]
    youli_money = _get_medium_moneys(
        medium_orders, pre_monthes, [3], 'medium_order', year)
    wuxian_money = _get_medium_moneys(
        medium_orders, pre_monthes, [8], 'medium_order', year)
    momo_money = _get_medium_moneys(
        medium_orders, pre_monthes, [7], 'medium_order', year)
    zhihu_money = _get_medium_moneys(
        medium_orders, pre_monthes, [5], 'medium_order', year)
    xiachufang_money = _get_medium_moneys(
        medium_orders, pre_monthes, [6], 'medium_order', year)
    xueqiu_money = _get_medium_moneys(
        medium_orders, pre_monthes, [9], 'medium_order', year)
    huxiu_money = _get_medium_moneys(
        medium_orders, pre_monthes, [14, 57], 'medium_order', year)
    kecheng_money = _get_medium_moneys(
        medium_orders, pre_monthes, [4], 'medium_order', year)
    midi_money = _get_medium_moneys(
        medium_orders, pre_monthes, [21], 'medium_order', year)
    weipiao_money = _get_medium_moneys(
        medium_orders, pre_monthes, [52], 'medium_order', year)
    one_money = _get_medium_moneys(
        medium_orders, pre_monthes, [51], 'medium_order', year)
    # ---计算大于100W的媒体
    up_money = {}
    other_money = {'sale_money': [0 for k in range(36)],
                   'money2': [0 for k in range(36)],
                   'm_ex_money': [0 for k in range(36)],
                   'a_rebate': [0 for k in range(36)],
                   'profit': [0 for k in range(36)]}
    # 用于计算合计的其他媒体售卖金额
    total_except_money = [0 for k in range(36)]
    total_a_rebate = [0 for k in range(36)]
    for k in Medium.all():
        if int(k.id) not in except_medium_ids:
            u_medium = _get_medium_moneys(
                medium_orders, pre_monthes, [int(k.id)], 'medium_order', year)
            if sum(u_medium['sale_money']) >= 1000000:
                up_money[k.name] = u_medium
            else:
                other_money['sale_money'] = numpy.array(
                    other_money['sale_money']) + numpy.array(u_medium['sale_money'])
                other_money['money2'] = numpy.array(
                    other_money['money2']) + numpy.array(u_medium['money2'])
                other_money['m_ex_money'] = numpy.array(
                    other_money['m_ex_money']) + numpy.array(u_medium['m_ex_money'])
                other_money['a_rebate'] = numpy.array(
                    other_money['a_rebate']) + numpy.array(u_medium['a_rebate'])
                other_money['profit'] = numpy.array(
                    other_money['profit']) + numpy.array(u_medium['profit'])
            total_except_money = numpy.array(
                total_except_money) + numpy.array(u_medium['sale_money'])
            total_a_rebate = numpy.array(
                total_a_rebate) + numpy.array(u_medium['a_rebate'])
    # 计算大于100W的媒体结束---

    # 媒体订单结束

    # 搜索直签订单开始
    searchAd_medium_orders = searchAdMediumOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)
    searchAd_medium_orders = [_search_order_to_dict(
        k) for k in searchAd_medium_orders if k.status == 1]
    searchAd_medium_orders = [k for k in searchAd_medium_orders if k[
        'contract_status'] in [2, 4, 5, 19, 20]]
    searchAD_money = _get_medium_moneys(
        searchAd_medium_orders, pre_monthes, 0, 's_medium_order', year)
    # 搜索直签订单结束

    # 搜索返点订单开始
    searchAd_rebate_orders = searchAdRebateOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)
    searchAd_rebate_orders = [_search_rebate_order_to_dict(k)
                              for k in searchAd_rebate_orders if k.status == 1]
    searchAd_rebate_orders = [k for k in searchAd_rebate_orders if k[
        'contract_status'] in [2, 4, 5, 19, 20]]
    rebate_order_money = _get_medium_moneys(
        searchAd_rebate_orders, pre_monthes, 0, '', year)
    # 搜索返点订单结束
    # 搜索业务毛利+返点收入
    searchAD_money['profit'] = numpy.array(
        searchAD_money['profit']) + numpy.array(rebate_order_money['sale_money'])
    # 豆瓣收入、服务费、返点、毛利为直签豆瓣+优力和无线总和
    douban_money['sale_money'] = numpy.array(
        douban_money['sale_money']) + numpy.array(ass_douban_money['money2'])
    if year == 2016:
        douban_money['money2'] = numpy.array(
            douban_money['money2']) + numpy.array([k * 0.18 for k in ass_douban_money['money2']])
        douban_money['a_rebate'] = [0 for k in range(36)]
        douban_money['profit'] = numpy.array(
            douban_money['money2']) - numpy.array(douban_money['a_rebate'])
    elif year == 2014:
        douban_money['money2'] = numpy.array(
            douban_money['money2']) + numpy.array([k * 0.426 for k in ass_douban_money['money2']])
        douban_money['a_rebate'] = numpy.array(
            douban_money['a_rebate']) + numpy.array(ass_douban_money['a_rebate'])
        douban_money['profit'] = numpy.array(
            douban_money['money2']) - numpy.array(douban_money['a_rebate'])
    else:
        douban_money['money2'] = numpy.array(
            douban_money['money2']) + numpy.array([k * 0.4 for k in ass_douban_money['money2']])
        douban_money['a_rebate'] = numpy.array(
            douban_money['a_rebate']) + numpy.array(ass_douban_money['a_rebate'])
        douban_money['profit'] = numpy.array(
            douban_money['money2']) - numpy.array(douban_money['a_rebate'])
    # 计算豆瓣收入、服务费、返点、毛利为直签豆瓣+优力和无线总和
    if g.user.is_aduit() and str(year) == '2014':
        total = numpy.array(momo_money['sale_money']) +\
            numpy.array(zhihu_money['sale_money']) +\
            numpy.array(xiachufang_money['sale_money']) +\
            numpy.array(xueqiu_money['sale_money']) +\
            numpy.array(huxiu_money['sale_money']) +\
            numpy.array(kecheng_money['sale_money']) +\
            numpy.array(midi_money['sale_money']) +\
            numpy.array(weipiao_money['sale_money']) +\
            numpy.array(one_money['sale_money']) +\
            numpy.array(total_except_money) +\
            numpy.array(searchAD_money['sale_money']) +\
            numpy.array(rebate_order_money['sale_money'])
    else:
        total = numpy.array(douban_money['profit']) +\
            numpy.array(momo_money['sale_money']) +\
            numpy.array(zhihu_money['sale_money']) +\
            numpy.array(xiachufang_money['sale_money']) +\
            numpy.array(xueqiu_money['sale_money']) +\
            numpy.array(huxiu_money['sale_money']) +\
            numpy.array(kecheng_money['sale_money']) +\
            numpy.array(midi_money['sale_money']) +\
            numpy.array(weipiao_money['sale_money']) +\
            numpy.array(one_money['sale_money']) +\
            numpy.array(total_except_money) +\
            numpy.array(searchAD_money['sale_money']) +\
            numpy.array(rebate_order_money['sale_money'])
    aa = sum([k['money_rebate_data'] for k in medium_orders])
    bb = numpy.array(momo_money['a_rebate']) + \
        numpy.array(zhihu_money['a_rebate']) + \
        numpy.array(xiachufang_money['a_rebate']) +\
        numpy.array(xueqiu_money['a_rebate']) + \
        numpy.array(huxiu_money['a_rebate']) +\
        numpy.array(kecheng_money['a_rebate']) +\
        numpy.array(midi_money['a_rebate']) +\
        numpy.array(weipiao_money['a_rebate']) +\
        numpy.array(one_money['a_rebate']) +\
        numpy.array(total_except_money)
    print aa
    print aa - sum(bb)
    if request.values.get('action', '') == 'download':
        response = write_medium_money_excel(pre_monthes=pre_monthes, douban_money=douban_money,
                                            youli_money=youli_money, wuxian_money=wuxian_money,
                                            momo_money=momo_money, zhihu_money=zhihu_money,
                                            xiachufang_money=xiachufang_money, xueqiu_money=xueqiu_money,
                                            huxiu_money=huxiu_money, kecheng_money=kecheng_money,
                                            weipiao_money=weipiao_money, one_money=one_money,
                                            midi_money=midi_money, other_money=other_money,
                                            searchAD_money=searchAD_money, rebate_order_money=rebate_order_money,
                                            total=total, up_money=up_money, year=str(
                                                year)
                                            )
        return response
    return tpl('/data_query/super_leader/medium_money.html',
               pre_monthes=pre_monthes, douban_money=douban_money,
               youli_money=youli_money, wuxian_money=wuxian_money,
               momo_money=momo_money, zhihu_money=zhihu_money,
               xiachufang_money=xiachufang_money, xueqiu_money=xueqiu_money,
               huxiu_money=huxiu_money, kecheng_money=kecheng_money,
               weipiao_money=weipiao_money, one_money=one_money,
               midi_money=midi_money, other_money=other_money, total=total,
               searchAD_money=searchAD_money, rebate_order_money=rebate_order_money,
               year=str(year), up_money=up_money)
