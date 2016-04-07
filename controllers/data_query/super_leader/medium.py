# -*- coding: UTF-8 -*-
import datetime
import numpy

from flask import Blueprint, request
from flask import render_template as tpl

from libs.date_helpers import get_monthes_pre_days
from models.client import AgentRebate
from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from searchAd.models.order import searchAdMediumOrderExecutiveReport
from searchAd.models.rebate_order import searchAdRebateOrderExecutiveReport
from controllers.data_query.helpers.super_leader_helpers import write_medium_money_excel

data_query_super_leader_medium_bp = Blueprint(
    'data_query_super_leader_medium', __name__, template_folder='../../templates/data_query')


########
# 计算合同的收入成本值：
# 第一个参数：合同， 第二个参数：计算横跨时间段，第三个参数：媒体ids（用于识别计算媒体），
# 第四个参数：合同类型，第五个参数：代理信息（只有关联豆瓣订单时使用）
########
def _get_medium_moneys(orders, pre_monthes, medium_ids, o_type='zhiqian_order', agent_rebate_obj=None):
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
                'month'] and o['medium_id'] not in [3, 4, 5, 6, 7, 8, 9, 14, 21, 51, 52, 57]]

        for k in range(1, 4):
            location_orders = [
                o for o in pro_month_orders if len(set(o['locations']) & set([k]))]
            if location_orders:
                if o_type == 'zhiqian_order':
                    # 按区分售卖金额
                    sale_money = sum([o['sale_money'] / len(o['locations'])
                                      for o in location_orders])
                    # 按区分媒体金额
                    money2 = sum([o['medium_money2'] / len(o['locations'])
                                  for o in location_orders]) * 0.4
                    # 媒体返点
                    medium_rebate = 0
                    # 媒体净成本
                    m_ex_money = 0
                    # 代理返点
                    a_rebate = 0
                    for l_order in location_orders:
                        if int(l_order['self_agent_rebate']):
                            a_rebate += float(l_order['self_agent_rebate_value']) / len(l_order['locations'])
                        else:
                            a_rebate += float(l_order['sale_money']) / len(l_order['locations']) * float(l_order[
                                'agent_rebate']) / 100
                    # 净利润
                    profit = money2 - a_rebate
                else:
                    # 按区分售卖金额
                    sale_money = sum([o['sale_money'] / len(o['locations'])
                                      for o in location_orders])
                    # 按区分媒体金额
                    money2 = sum([o['medium_money2'] / len(o['locations'])
                                  for o in location_orders])
                    # 媒体返点
                    medium_rebate = sum(
                        [o['medium_money2'] / len(o['locations']) * o['medium_rebate'] / 100 for o in location_orders])
                    # 媒体净成本
                    m_ex_money = money2 - medium_rebate
                    # 代理返点
                    a_rebate = 0
                    for l_order in location_orders:

                        if int(l_order['self_agent_rebate']):
                            a_rebate += float(l_order['self_agent_rebate_value']) * \
                                float(
                                    l_order['sale_money']) / float(l_order['money']) / len(l_order['locations'])
                        else:
                            if l_order['is_c_douban'] and agent_rebate_obj:
                                if int(l_order['medium_id']) in agent_rebate_obj:
                                    agent_rebate = agent_rebate_obj[
                                        int(l_order['medium_id'])]
                                else:
                                    agent_rebate = 0
                            else:
                                agent_rebate = l_order['agent_rebate']
                            a_rebate += float(l_order['sale_money']) / len(
                                l_order['locations']) * float(agent_rebate) / 100
                    # 净利润
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
    '''
    client_order = json.loads(order.order_json)
    d_order.update(client_order)
    medium_order = json.loads(order.medium_order_json)
    d_order.update(medium_order)
    '''
    d_order['month_day'] = order.month_day
    if order.__tablename__ == 'bra_medium_order_executive_report':
        d_order['medium_id'] = order.order.medium.id
        d_order['medium_order_id'] = order.order.id
    else:
        d_order['medium_id'] = 0
        d_order['medium_order_id'] = 0
    if order.__tablename__ == 'bra_douban_order_executive_report':
        d_order['locations'] = order.douban_order.locations
        d_order['contract_status'] = order.douban_order.contract_status
        d_order['sale_money'] = order.money
        d_order['medium_money2'] = order.money
        d_order['medium_rebate'] = 0
        d_order['agent_rebate'] = order.douban_order.agent_rebate
        # 单笔返点
        try:
            self_agent_rebate = order.douban_order.self_agent_rebate
            d_order['self_agent_rebate'] = self_agent_rebate.split('-')[0]
            d_order['self_agent_rebate_value'] = self_agent_rebate.split('-')[1]
        except:
            d_order['self_agent_rebate'] = 0
            d_order['self_agent_rebate_value'] = 0
        # 是否关联豆瓣订单
        d_order['is_c_douban'] = False
    elif order.__tablename__ == 'bra_searchad_rebate_order_executive_report':
        d_order['locations'] = order.rebate_order.locations
        d_order['contract_status'] = order.rebate_order.contract_status
        d_order['sale_money'] = order.money
        d_order['medium_money2'] = order.money
        d_order['medium_rebate'] = 0
        d_order['agent_rebate'] = order.rebate_order.agent_rebate
        # 单笔返点
        d_order['self_agent_rebate'] = 0
        d_order['self_agent_rebate_value'] = 0
        # 是否关联豆瓣订单
        d_order['is_c_douban'] = False
    else:
        d_order['money'] = order.client_order.money
        d_order['locations'] = order.client_order.locations
        d_order['contract_status'] = order.client_order.contract_status
        d_order['sale_money'] = order.sale_money
        d_order['medium_money2'] = order.medium_money2
        d_order['medium_rebate'] = order.order.medium_rebate_by_year(d_order[
                                                                     'month_day'])
        d_order['agent_rebate'] = order.client_order.agent_rebate
        # 单笔返点
        try:
            self_agent_rebate = order.client_order.self_agent_rebate
            d_order['self_agent_rebate'] = self_agent_rebate.split('-')[0]
            d_order['self_agent_rebate_value'] = self_agent_rebate.split('-')[1]
        except:
            d_order['self_agent_rebate'] = 0
            d_order['self_agent_rebate_value'] = 0
        # 是否关联豆瓣订单
        try:
            ass_order = order.order.associated_douban_order
            if ass_order:
                d_order['is_c_douban'] = True
            else:
                d_order['is_c_douban'] = False
        except:
            d_order['is_c_douban'] = False

    d_order['status'] = order.status
    return d_order


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

    # 获取关联豆瓣订单代理返点，用于快速计算关联豆瓣订单代理
    try:
        agent_youli_rebate = AgentRebate.query.filter_by(
            year=start_date_month, agent_id=105).first().douban_rebate
    except:
        agent_youli_rebate = 0
    try:
        agent_wuxian_rebate = AgentRebate.query.filter_by(
            year=start_date_month, agent_id=94).first().douban_rebate
    except:
        agent_wuxian_rebate = 0
    try:
        agent_haohai_rebate = AgentRebate.query.filter_by(
            year=start_date_month, agent_id=228).first().douban_rebate
    except:
        agent_haohai_rebate = 0
    try:
        agent_pinzhong_rebate = AgentRebate.query.filter_by(
            year=start_date_month, agent_id=213).first().douban_rebate
    except:
        agent_pinzhong_rebate = 0
    try:
        agent_yingrui_rabate = AgentRebate.query.filter_by(
            year=start_date_month, agent_id=93).first().douban_rebate
    except:
        agent_yingrui_rabate = 0

    agent_rebate_obj = {8: agent_wuxian_rebate,
                        3: agent_youli_rebate,
                        44: agent_haohai_rebate,
                        27: agent_yingrui_rabate,
                        37: agent_pinzhong_rebate}

    # 直签豆瓣订单开始
    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)
    douban_orders = [_parse_dict_order(k)
                     for k in douban_orders if k.status == 1]
    douban_orders = [k for k in douban_orders if k[
        'contract_status'] not in [0, 7, 8, 9]]
    douban_money = _get_medium_moneys(
        douban_orders, pre_monthes, 0, 'zhiqian_order')
    # 直签豆瓣订单结束

    # 媒体订单开始
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)
    medium_orders = [_parse_dict_order(k)
                     for k in medium_orders if k.status == 1]
    medium_orders = [k for k in medium_orders if k[
        'contract_status'] not in [0, 7, 8, 9]]

    # 关联豆瓣订单开始
    ass_douban_order = [k for k in medium_orders if k['is_c_douban']]
    ass_douban_money = _get_medium_moneys(
        ass_douban_order, pre_monthes, 0, 'medium_order', agent_rebate_obj)
    # 关联豆瓣订单结束

    # 排除媒体订单中的关联豆瓣订单
    # ass_douban_order_ids = [k['medium_order_id'] for k in ass_douban_order]
    # medium_orders = [k for k in medium_orders if k['medium_order_id'] not in ass_douban_order_ids]

    youli_money = _get_medium_moneys(
        medium_orders, pre_monthes, [3], 'medium_order')
    wuxian_money = _get_medium_moneys(
        medium_orders, pre_monthes, [8], 'medium_order')
    momo_money = _get_medium_moneys(
        medium_orders, pre_monthes, [7], 'medium_order')
    zhihu_money = _get_medium_moneys(
        medium_orders, pre_monthes, [5], 'medium_order')
    xiachufang_money = _get_medium_moneys(
        medium_orders, pre_monthes, [6], 'medium_order')
    xueqiu_money = _get_medium_moneys(
        medium_orders, pre_monthes, [9], 'medium_order')
    huxiu_money = _get_medium_moneys(
        medium_orders, pre_monthes, [14, 57], 'medium_order')
    kecheng_money = _get_medium_moneys(
        medium_orders, pre_monthes, [4], 'medium_order')
    midi_money = _get_medium_moneys(
        medium_orders, pre_monthes, [21], 'medium_order')
    weipiao_money = _get_medium_moneys(
        medium_orders, pre_monthes, [52], 'medium_order')
    one_money = _get_medium_moneys(
        medium_orders, pre_monthes, [51], 'medium_order')
    other_money = _get_medium_moneys(
        medium_orders, pre_monthes, None, 'medium_order')
    # 媒体订单结束

    # 搜索直签订单开始
    searchAd_medium_orders = searchAdMediumOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)
    searchAd_medium_orders = [_parse_dict_order(
        k) for k in searchAd_medium_orders if k.status == 1]
    searchAd_medium_orders = [k for k in searchAd_medium_orders if k[
        'contract_status'] not in [0, 7, 8, 9]]
    searchAD_money = _get_medium_moneys(
        searchAd_medium_orders, pre_monthes, 0, 's_medium_order')
    # 搜索直签订单结束

    # 搜索返点订单开始
    searchAd_rebate_orders = searchAdRebateOrderExecutiveReport.query.filter(
        searchAdMediumOrderExecutiveReport.month_day >= start_date_month,
        searchAdMediumOrderExecutiveReport.month_day <= end_date_month)
    searchAd_rebate_orders = [_parse_dict_order(k)
                              for k in searchAd_rebate_orders if k.status == 1]
    searchAd_rebate_orders = [k for k in searchAd_rebate_orders if k[
        'contract_status'] not in [0, 7, 8, 9]]
    rebate_order_money = _get_medium_moneys(
        searchAd_rebate_orders, pre_monthes, 0, 'zhiqian_order')
    # 搜索返点订单结束

    # 豆瓣收入、服务费、返点、毛利为直签豆瓣+优力和无线总和
    douban_money['sale_money'] = numpy.array(
        douban_money['sale_money']) + numpy.array(ass_douban_money['money2'])
    douban_money['money2'] = numpy.array(
        douban_money['money2']) + numpy.array([k * 0.4 for k in ass_douban_money['money2']])
    douban_money['a_rebate'] = numpy.array(
        douban_money['a_rebate']) + numpy.array(ass_douban_money['a_rebate'])
    douban_money['profit'] = numpy.array(
        douban_money['money2']) - numpy.array(douban_money['a_rebate'])
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
        numpy.array(rebate_order_money['sale_money'])
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
