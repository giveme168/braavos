# -*- coding: UTF-8 -*-
import os
import datetime
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
#sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app
import numpy

from libs.date_helpers import get_monthes_pre_days
from models.client import AgentRebate
from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport
from searchAd.models.order import searchAdMediumOrderExecutiveReport
from searchAd.models.rebate_order import searchAdRebateOrderExecutiveReport
from controllers.data_query.helpers.super_leader_helpers import write_medium_money_excel


########
# 计算合同的收入成本值：
# 第一个参数：合同， 第二个参数：计算横跨时间段，第三个参数：媒体ids（用于识别计算媒体），
# 第四个参数：合同类型，第五个参数：代理信息（只有关联豆瓣订单时使用）
########
def _get_medium_moneys(orders, pre_monthes, medium_ids, o_type='zhiqian_order', agent_rebate_obj=None):
    for order in orders:
        if o_type == 'zhiqian_order':
            if int(order['self_agent_rebate']):
                order['a_rebate'] = float(order['self_agent_rebate_value'])
            else:
                order['a_rebate'] = float(order['sale_money']) * float(order['agent_rebate']) / 100
        else:
            if int(order['self_agent_rebate']):
                order['a_rebate'] = float(order['self_agent_rebate_value']) * \
                    float(order['sale_money']) / float(order['money'])
            else:
                if order['is_c_douban']:
                    if int(order['medium_id']) in agent_rebate_obj:
                        agent_rebate = agent_rebate_obj[int(order['medium_id'])]
                    else:
                        agent_rebate = 0
                else:
                    agent_rebate = order['agent_rebate']
                order['a_rebate'] = float(order['sale_money']) * float(agent_rebate) / 100
    return orders


def _parse_dict_order(order):
    d_order = {}
    d_order['month_day'] = order.month_day
    if order.__tablename__ == 'bra_medium_order_executive_report':
        d_order['medium_id'] = order.order.medium.id
        d_order['medium_order_id'] = order.order.id
    else:
        d_order['medium_id'] = 0
        d_order['medium_order_id'] = 0

    if order.__tablename__ == 'bra_douban_order_executive_report':
        d_order['money'] = order.douban_order.money
        d_order['locations'] = order.douban_order.locations
        d_order['agent'] = order.douban_order.agent.name
        d_order['campaign'] = order.douban_order.campaign
        d_order['order_id'] = order.douban_order.id
        d_order['contract'] = order.douban_order.contract
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
    else:
        d_order['money'] = order.client_order.money
        d_order['locations'] = order.client_order.locations
        d_order['campaign'] = order.client_order.campaign
        d_order['agent'] = order.client_order.agent.name
        d_order['order_id'] = order.client_order.id
        d_order['contract'] = order.client_order.contract
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


if __name__ == '__main__':
    year = 2015
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
    douban_money = _get_medium_moneys(douban_orders, pre_monthes, 0, 'zhiqian_order')
    # 直签豆瓣订单结束
    # 媒体订单开始
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)
    medium_orders = [_parse_dict_order(k)
                     for k in medium_orders if k.status == 1]
    medium_orders = [k for k in medium_orders if k[
        'contract_status'] not in [0, 7, 8, 9]]
    medium_money = _get_medium_moneys(medium_orders, pre_monthes, 0, 'medium_order', agent_rebate_obj)
    agent_obj = {}
    for k in medium_money:
        if k['contract'] in agent_obj:
            agent_obj[k['contract']] += k['a_rebate']
        else:
            agent_obj[k['contract']] = 0
    print agent_obj
    # 关联豆瓣订单开始
    ass_douban_order = [k for k in medium_orders if k['is_c_douban']]
    ass_douban_order_ids = [k['medium_order_id'] for k in ass_douban_order]
    ass_douban_money = _get_medium_moneys(
        ass_douban_order, pre_monthes, 0, 'medium_order', agent_rebate_obj)
    # 关联豆瓣订单结束

    # 排除媒体订单中的关联豆瓣订单
    medium_orders = [k for k in medium_orders if k['medium_order_id'] not in ass_douban_order_ids]





