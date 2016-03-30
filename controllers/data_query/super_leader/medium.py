# -*- coding: UTF-8 -*-
import datetime
import numpy

from flask import Blueprint, request, json
from flask import render_template as tpl

from libs.date_helpers import get_monthes_pre_days
from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from searchAd.models.order import searchAdMediumOrderExecutiveReport
from searchAd.models.rebate_order import searchAdRebateOrderExecutiveReport
from models.client import Agent
from controllers.data_query.helpers.super_leader_helpers import write_medium_money_excel

data_query_super_leader_medium_bp = Blueprint(
    'data_query_super_leader_medium', __name__, template_folder='../../templates/data_query')


def _get_medium_moneys(orders, pre_monthes, medium_ids):
    money_obj = {'sale_money': [], 'money2': [],
                 'm_ex_money': [], 'a_rebate': [], 'profit': []}
    for d in pre_monthes:
        if isinstance(medium_ids, list):
            pro_month_orders = [o for o in orders if o['month_day'] == d[
                'month'] and o['status'] == 1 and o['medium_id'] in medium_ids]
        elif medium_ids == 0:
            pro_month_orders = [
                o for o in orders if o['month_day'] == d['month'] and o['status'] == 1]
        else:
            pro_month_orders = [o for o in orders if o['month_day'] == d[
                'month'] and o['status'] == 1 and o['medium_id'] not in [3, 4, 5, 6, 7, 8, 9, 14, 21, 51, 52, 57]]

        for k in range(1, 4):
            location_orders = [
                o for o in pro_month_orders if len(set(o['locations']) & set([k]))]
            if location_orders:
                sale_money = sum([o['sale_money'] / len(o['locations'])
                                  for o in location_orders])
                money2 = sum([o['medium_money2'] / len(o['locations'])
                              for o in location_orders])
                medium_rebate = sum(
                    [o['medium_money2'] / len(o['locations']) * o['medium_rebate'] / 100 for o in location_orders])
                m_ex_money = money2 - medium_rebate
                a_rebate = sum([o['sale_money'] / len(o['locations']) *
                                o['agent_rebate'] / 100 for o in location_orders])
                profit = sale_money - m_ex_money - a_rebate
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


def _parse_dict_order(order):
    d_order = {}
    client_order = json.loads(order.order_json)
    d_order.update(client_order)
    medium_order = json.loads(order.medium_order_json)
    d_order.update(medium_order)
    d_order['contract_status'] = order.client_order.contract_status
    d_order['month_day'] = order.month_day
    d_order['status'] = order.status
    d_order['sale_money'] = order.sale_money
    d_order['medium_money2'] = order.medium_money2
    d_order['medium_rebate'] = order.order.medium_rebate_by_year(d_order['month_day'])
    d_order['agent_rebate'] = order.client_order.agent_rebate
    return d_order


@data_query_super_leader_medium_bp.route('/money', methods=['GET'])
def money():
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    start_date_month = datetime.datetime.strptime(str(year) + '-01' + '-01', '%Y-%m-%d')
    end_date_month = datetime.datetime.strptime(str(year) + '-12' + '-31', '%Y-%m-%d')
    pre_monthes = get_monthes_pre_days(start_date_month, end_date_month)

    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)

    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)
    medium_orders = [_parse_dict_order(k) for k in medium_orders if k.status == 1]
    medium_orders = [k for k in medium_orders if k['contract_status'] not in [0, 7, 8, 9]]
    # 搜索部门合同
    # 普通订单
    searchAd_medium_orders = searchAdMediumOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)
    searchAd_medium_orders = [_parse_dict_order(k) for k in searchAd_medium_orders if k.status == 1]
    searchAd_medium_orders = [k for k in searchAd_medium_orders if k['contract_status'] not in [0, 7, 8, 9]]
    searchAD_money = _get_medium_moneys(searchAd_medium_orders, pre_monthes, 0)
    # 返点订单
    searchAd_rebate_orders = searchAdRebateOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)
    rebate_order_money = {'ex_money': []}
    for d in pre_monthes:
        pro_month_orders = [
            o for o in searchAd_rebate_orders.filter_by(month_day=d['month']) if o.status == 1]
        for k in range(1, 4):
            location_orders = [
                o for o in pro_month_orders if len(set(o.locations) & set([k]))]
            if location_orders:
                ex_money = sum([k.money for k in pro_month_orders])
                rebate_order_money['ex_money'].append(round(ex_money, 2))
            else:
                rebate_order_money['ex_money'].append(0.0)
    # 搜索部门毛利：普通订单收入+返点订单收入-执行金额
    searchAD_money['profit'] = numpy.array(
        searchAD_money['profit']) + numpy.array(rebate_order_money['ex_money'])
    # 搜索部门合同结束
    youli_money = _get_medium_moneys(medium_orders, pre_monthes, [3])
    wuxian_money = _get_medium_moneys(medium_orders, pre_monthes, [8])
    momo_money = _get_medium_moneys(medium_orders, pre_monthes, [7])
    zhihu_money = _get_medium_moneys(medium_orders, pre_monthes, [5])
    xiachufang_money = _get_medium_moneys(medium_orders, pre_monthes, [6])
    xueqiu_money = _get_medium_moneys(medium_orders, pre_monthes, [9])
    huxiu_money = _get_medium_moneys(medium_orders, pre_monthes, [14, 57])
    kecheng_money = _get_medium_moneys(medium_orders, pre_monthes, [4])
    midi_money = _get_medium_moneys(medium_orders, pre_monthes, [21])
    weipiao_money = _get_medium_moneys(medium_orders, pre_monthes, [52])
    one_money = _get_medium_moneys(medium_orders, pre_monthes, [51])
    other_money = _get_medium_moneys(medium_orders, pre_monthes, None)

    # 获取直签豆瓣数据
    douban_money = {'ex_money': [], 'in_money': [], 'rebate': [], 'profit': []}
    for d in pre_monthes:
        pro_month_orders = [
            o for o in douban_orders.filter_by(month_day=d['month']) if o.status == 1]
        for k in range(1, 4):
            location_orders = [
                o for o in pro_month_orders if len(set(o.locations) & set([k]))]
            if location_orders:
                ex_money = sum([k.money / len(k.locations)
                                for k in location_orders])
                in_money = ex_money * 0.4
                rebate = sum(
                    [k.money / len(k.locations) * k.douban_order.agent_rebate / 100 for k in location_orders])
                profit = in_money - rebate
                douban_money['ex_money'].append(round(ex_money, 2))
                douban_money['in_money'].append(round(in_money, 2))
                douban_money['rebate'].append(round(rebate, 2))
                douban_money['profit'].append(round(profit, 2))
            else:
                douban_money['ex_money'].append(0.0)
                douban_money['in_money'].append(0.0)
                douban_money['rebate'].append(0.0)
                douban_money['profit'].append(0.0)
    # 直签豆瓣数据结束

    # 豆瓣收入、服务费、返点、毛利为直签豆瓣+优力和无线总和
    douban_money['ex_money'] = numpy.array(douban_money['ex_money']) + numpy.array(youli_money['money2']) +\
        numpy.array(wuxian_money['money2'])
    douban_money['in_money'] = numpy.array(douban_money['in_money']) + numpy.array(
        [k * 0.4 for k in youli_money['money2']]) + numpy.array([k * 0.4 for k in wuxian_money['money2']])
    # 获取代理优力的豆瓣返点
    try:
        agent_youli_rebate = Agent.get(
            94).douban_rebate_by_year(year) / 100
    except:
        agent_youli_rebate = 0
    # 获取代理无线的豆瓣返点
    try:
        agent_wuxian_rebate = Agent.get(
            105).douban_rebate_by_year(year) / 100
    except:
        agent_wuxian_rebate = 0
    douban_money['rebate'] = numpy.array(douban_money['rebate']) +\
        numpy.array([k * agent_youli_rebate for k in youli_money['money2']]) +\
        numpy.array([k * agent_wuxian_rebate for k in wuxian_money['money2']])
    douban_money['profit'] = numpy.array(
        douban_money['in_money']) - numpy.array(douban_money['rebate'])
    # 计算豆瓣收入、服务费、返点、毛利为直签豆瓣+优力和无线总和
    total = numpy.array(douban_money['profit']) +\
        numpy.array(youli_money['sale_money']) +\
        numpy.array(wuxian_money['sale_money']) +\
        numpy.array(momo_money['sale_money']) +\
        numpy.array(zhihu_money['sale_money']) +\
        numpy.array(xiachufang_money['sale_money']) +\
        numpy.array(xueqiu_money['sale_money']) +\
        numpy.array(huxiu_money['sale_money']) +\
        numpy.array(kecheng_money['sale_money']) +\
        numpy.array(midi_money['sale_money']) +\
        numpy.array(weipiao_money['sale_money']) +\
        numpy.array(one_money['sale_money']) +\
        numpy.array(other_money['sale_money']) +\
        numpy.array(searchAD_money['sale_money']) +\
        numpy.array(rebate_order_money['ex_money'])
    if request.values.get('action', '') == 'download':
        response = write_medium_money_excel(pre_monthes=pre_monthes, douban_money=douban_money,
                                            youli_money=youli_money, wuxian_money=wuxian_money,
                                            momo_money=momo_money, zhihu_money=zhihu_money,
                                            xiachufang_money=xiachufang_money, xueqiu_money=xueqiu_money,
                                            huxiu_money=huxiu_money, kecheng_money=kecheng_money,
                                            weipiao_money=weipiao_money, one_money=one_money,
                                            midi_money=midi_money, other_money=other_money,
                                            searchAD_money=searchAD_money, rebate_order_money=rebate_order_money,
                                            total=total,
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
               year=str(year))
