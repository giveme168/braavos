# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint
from flask import render_template as tpl

from libs.date_helpers import get_monthes_pre_days
from models.douban_order import DoubanOrderExecutiveReport
from models.order import MediumOrderExecutiveReport

data_query_super_leader_medium_bp = Blueprint(
    'data_query_super_leader_medium', __name__, template_folder='../../templates/data_query')


def _get_medium_moneys(orders, pre_monthes, medium_id):
    money_obj = {'sale_money': [], 'money2': [],
                 'm_ex_money': [], 'a_rebate': [], 'profit': []}
    for d in pre_monthes:
        if medium_id:
            pro_month_orders = [o for o in orders if o['month_day'] == d[
                'month'] and o['status'] == 1 and o['medium_id'] == medium_id]
        else:
            pro_month_orders = [o for o in orders if o['month_day'] == d[
                'month'] and o['status'] == 1 and o['medium_id'] not in [3, 4, 5, 6, 7, 8, 9, 14, 21]]
        for k in range(1, 4):
            location_orders = [
                o for o in pro_month_orders if len(set(o['locations']) & set([k]))]
            if location_orders:
                sale_money = sum([k['sale_money'] / len(k['locations'])
                                  for k in location_orders])
                money2 = sum([k['medium_money2'] / len(k['locations'])
                              for k in location_orders])
                medium_rebate = sum(
                    [k['medium_money2'] / len(k['locations']) * k['medium_rebate'] / 100 for k in location_orders])
                m_ex_money = money2 - medium_rebate
                a_rebate = sum([k['medium_money2'] / len(k['locations']) *
                                k['agent_rebate'] / 100 for k in location_orders])
                profit = sale_money - m_ex_money - a_rebate
                money_obj['sale_money'].append(sale_money)
                money_obj['money2'].append(money2)
                money_obj['m_ex_money'].append(m_ex_money)
                money_obj['a_rebate'].append(a_rebate)
                money_obj['profit'].append(profit)
            else:
                money_obj['sale_money'].append(0)
                money_obj['money2'].append(0)
                money_obj['m_ex_money'].append(0)
                money_obj['a_rebate'].append(0)
                money_obj['profit'].append(0)
    return money_obj


@data_query_super_leader_medium_bp.route('/money', methods=['GET'])
def money():
    now_date = datetime.datetime.now()
    end_date_month = now_date.replace(
        month=now_date.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date_month = now_date.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    pre_monthes = get_monthes_pre_days(start_date_month, end_date_month)

    douban_orders = DoubanOrderExecutiveReport.query.filter(
        DoubanOrderExecutiveReport.month_day >= start_date_month,
        DoubanOrderExecutiveReport.month_day <= end_date_month)
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
                douban_money['ex_money'].append(ex_money)
                douban_money['in_money'].append(in_money)
                douban_money['rebate'].append(rebate)
                douban_money['profit'].append(profit)
            else:
                douban_money['ex_money'].append(0)
                douban_money['in_money'].append(0)
                douban_money['rebate'].append(0)
                douban_money['profit'].append(0)
    medium_orders = MediumOrderExecutiveReport.query.filter(
        MediumOrderExecutiveReport.month_day >= start_date_month,
        MediumOrderExecutiveReport.month_day <= end_date_month)
    medium_orders = [{'month_day': k.month_day,
                      'status': k.status, 'medium_id': k.order.medium_id,
                      'locations': k.locations, 'sale_money': k.sale_money,
                      'medium_money2': k.medium_money2, 'medium_rebate': k.order.medium_rebate,
                      'agent_rebate': k.client_order.agent_rebate} for k in medium_orders]
    youli_money = _get_medium_moneys(medium_orders, pre_monthes, 3)
    wuxian_money = _get_medium_moneys(medium_orders, pre_monthes, 8)
    momo_money = _get_medium_moneys(medium_orders, pre_monthes, 7)
    zhihu_money = _get_medium_moneys(medium_orders, pre_monthes, 5)
    xiachufang_money = _get_medium_moneys(medium_orders, pre_monthes, 6)
    xueqiu_money = _get_medium_moneys(medium_orders, pre_monthes, 9)
    huxiu_money = _get_medium_moneys(medium_orders, pre_monthes, 14)
    kecheng_money = _get_medium_moneys(medium_orders, pre_monthes, 4)
    midi_money = _get_medium_moneys(medium_orders, pre_monthes, 21)
    other_money = _get_medium_moneys(medium_orders, pre_monthes, None)
    return tpl('/data_query/super_leader/medium_money.html',
               pre_monthes=pre_monthes, douban_money=douban_money,
               youli_money=youli_money, wuxian_money=wuxian_money,
               momo_money=momo_money, zhihu_money=zhihu_money,
               xiachufang_money=xiachufang_money, xueqiu_money=xueqiu_money,
               huxiu_money=huxiu_money, kecheng_money=kecheng_money,
               midi_money=midi_money, other_money=other_money)
