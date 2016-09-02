# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.outsource import OutSource, DoubanOutSource
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q, get_monthes_pre_days)
from controllers.data_query.helpers.outsource_helpers import (write_outsource_excel,
                                                              write_outsource_info_excel,
                                                              write_outsource_order_info_excel)


data_query_outsource_bp = Blueprint(
    'data_query_outsource', __name__, template_folder='../../templates/data_query')


def outsource_to_dict(outsource):
    dict_outsource = {}
    try:
        dict_outsource['otype'] = outsource.otype
        dict_outsource['order'] = outsource.order
        dict_outsource['order_status'] = 1
        dict_outsource['month_day'] = outsource.month_day
        dict_outsource['type'] = outsource.type
        dict_outsource['locations'] = list(
            set(dict_outsource['order'].locations))
        if outsource.target.id == 271:
            dict_outsource['pay_num'] = 0
            dict_outsource['l_pre_pay_num'] = 0
        else:
            dict_outsource['pay_num'] = outsource.pay_num
            dict_outsource['l_pre_pay_num'] = outsource.pay_num / \
                len(dict_outsource['locations'])
    except:
        dict_outsource['order_status'] = 0
    return dict_outsource


def _all_outsource():
    dt_format = "%d%m%Y"
    outsources = []
    client_order_outsources = list(OutSource.all())
    douban_order_outsources = list(DoubanOutSource.all())
    for o in client_order_outsources + douban_order_outsources:
        if o.__tablename__ == 'out_source':
            order = o.client_order
            order_type = 'client_order'
        else:
            order = o.douban_order
            order_type = 'douban_order'
        start_datetime = datetime.datetime.strptime(order.client_start.strftime(dt_format), dt_format)
        end_datetime = datetime.datetime.strptime(order.client_end.strftime(dt_format), dt_format)
        money_ex_data = pre_month_money(o.pay_num,
                                        start_datetime,
                                        end_datetime)
        for k, v in money_ex_data.items():
            dict_outsource = {}
            dict_outsource['order_type'] = order_type
            dict_outsource['order'] = order
            dict_outsource['order_id'] = order.id
            dict_outsource['type'] = o.type
            dict_outsource['money'] = v
            dict_outsource['pay_num'] = v
            dict_outsource['month_day'] = k
            dict_outsource['status'] = int(o.status)
            dict_outsource['target_id'] = o.target.id
            dict_outsource['target_name'] = o.target.name
            dict_outsource['target_bank'] = o.target.bank
            dict_outsource['target_card'] = o.target.card
            dict_outsource['target_alipay'] = o.target.alipay
            dict_outsource['target_otype'] = o.target.otype
            dict_outsource['target_otype_cn'] = o.target.otype_cn
            dict_outsource['locations'] = list(set(order.locations))
            dict_outsource['l_pre_pay_num'] = dict_outsource['money'] / len(dict_outsource['locations'])
            dict_outsource['type_cn'] = o.type_cn
            if o.status == 4:
                dict_outsource['pay_status_cn'] = u'已付款'
                dict_outsource['pay_time_cn'] = o.create_time.strftime('%Y-%m-%d')
            else:
                dict_outsource['pay_status_cn'] = u'未付款'
                dict_outsource['pay_time_cn'] = u'无'
            if dict_outsource['target_id'] == 271 or dict_outsource['status'] not in [2, 3, 4]:
                dict_outsource = {}
            if dict_outsource:
                outsources.append(dict_outsource)
    return outsources


@data_query_outsource_bp.route('/', methods=['GET'])
def index():
    now_year = request.values.get('year', '')
    now_Q = request.values.get('Q', '')
    if not now_year and not now_Q:
        now_date = datetime.date.today()
        now_year = now_date.strftime('%Y')
        now_month = now_date.strftime('%m')
        now_Q = check_month_get_Q(now_month)
    Q_monthes = check_Q_get_monthes(now_Q)
    start_month_day = datetime.datetime.strptime(
        now_year + '-' + str(Q_monthes[0]), '%Y-%m')
    end_month_day = datetime.datetime.strptime(
        now_year + '-' + str(Q_monthes[-1]), '%Y-%m')
    outsources = _all_outsource()
    if now_Q == '00':
        outsources = [k for k in outsources if int(k['month_day'].year) == int(now_year)]
    else:
        outsources = [k for k in outsources if k['month_day'] >= start_month_day and k['month_day'] <= end_month_day]
    # 所有外包分类
    types = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    monthes_data = {}
    for k in types:
        monthes_data[str(k)] = []
    monthes_data['t_locataion'] = []
    monthes_data['t_month'] = []
    for k in Q_monthes:
        month_day = datetime.datetime.strptime(
            now_year + '-' + str(k), '%Y-%m')
        t_huabei_num = 0
        t_huadong_num = 0
        t_huanan_num = 0
        t_meijie_num = 0
        for i in types:
            num_data = {}
            num_data['huabei'] = sum([j['l_pre_pay_num'] for j in outsources
                                      if j['month_day'] == month_day and j['type'] == i and 1 in j['locations']])
            num_data['huadong'] = sum([j['l_pre_pay_num'] for j in outsources
                                       if j['month_day'] == month_day and j['type'] == i and 2 in j['locations']])
            num_data['huanan'] = sum([j['l_pre_pay_num'] for j in outsources
                                      if j['month_day'] == month_day and j['type'] == i and 3 in j['locations']])
            num_data['meijie'] = sum([j['l_pre_pay_num'] for j in outsources
                                      if j['month_day'] == month_day and j['type'] == i and 4 in j['locations']])
            t_huabei_num += num_data['huabei']
            t_huadong_num += num_data['huadong']
            t_huanan_num += num_data['huanan']
            t_meijie_num += num_data['meijie']
            monthes_data[str(i)].append(num_data)
        monthes_data['t_locataion'].append(
            {'huabei': t_huabei_num, 'huadong': t_huadong_num, 'huanan': t_huanan_num, 'meijie': t_meijie_num})
        monthes_data['t_month'].append(
            t_huabei_num + t_huadong_num + t_huanan_num + t_meijie_num)
    if request.values.get('action', '') == 'download':
        return write_outsource_excel(Q_monthes, monthes_data)
    return tpl('/data_query/outsource/index.html', Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, monthes_data=monthes_data)


@data_query_outsource_bp.route('/info', methods=['GET'])
def info():
    now_year = int(request.values.get('year', datetime.datetime.now().year))
    outsources = _all_outsource()
    r_outsource_pay = sum([k['pay_num'] for k in outsources])
    # pre_monthes = get_monthes_pre_days(start_date, end_date)

    # 季度月份数
    Q1_monthes = [datetime.datetime.strptime(
        str(now_year) + '-' + k, '%Y-%m') for k in check_Q_get_monthes('Q1')]
    Q2_monthes = [datetime.datetime.strptime(
        str(now_year) + '-' + k, '%Y-%m') for k in check_Q_get_monthes('Q2')]
    Q3_monthes = [datetime.datetime.strptime(
        str(now_year) + '-' + k, '%Y-%m') for k in check_Q_get_monthes('Q3')]
    Q4_monthes = [datetime.datetime.strptime(
        str(now_year) + '-' + k, '%Y-%m') for k in check_Q_get_monthes('Q4')]

    total = 0
    orders = list(set([s['order'] for s in outsources if s['month_day'].year == now_year]))
    for i in orders:
        o_money = []
        o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q1_monthes[0] and o[
            'month_day'] <= Q1_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 10)]
        o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q2_monthes[0] and o[
            'month_day'] <= Q2_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 10)]
        o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q3_monthes[0] and o[
            'month_day'] <= Q3_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 10)]
        o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q4_monthes[0] and o[
            'month_day'] <= Q4_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 10)]
        i.o_money = o_money
        total += sum(o_money)
    if request.values.get('action', '') == 'download':
        return write_outsource_info_excel(now_year, orders, total, r_outsource_pay)
    return tpl('/data_query/outsource/info.html', now_year=now_year, orders=orders,
               total=total, r_outsource_pay=r_outsource_pay)


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


def _target_outsource_to_dict(outsource, type, now_year):
    dict_outsource = {}
    dt_format = "%d%m%Y"
    if type == 'douban_order':
        order = outsource.douban_order
        dict_outsource['order_type'] = 'douban_order'
        dict_outsource['order_id'] = outsource.douban_order.id
    else:
        order = outsource.client_order
        dict_outsource['order_type'] = 'client_order'
        dict_outsource['order_id'] = outsource.medium_order.client_order.id
    dict_outsource['order'] = order
    dict_outsource['type'] = outsource.type
    start_datetime = datetime.datetime.strptime(order.client_start.strftime(dt_format), dt_format)
    end_datetime = datetime.datetime.strptime(order.client_end.strftime(dt_format), dt_format)
    money_ex_data = pre_month_money(outsource.pay_num,
                                    start_datetime,
                                    end_datetime)
    dict_outsource['money'] = sum([v for k, v in money_ex_data.items() if k.year == now_year])
    dict_outsource['status'] = int(outsource.status)
    dict_outsource['target_id'] = outsource.target.id
    dict_outsource['target_name'] = outsource.target.name
    dict_outsource['target_bank'] = outsource.target.bank
    dict_outsource['target_card'] = outsource.target.card
    dict_outsource['target_alipay'] = outsource.target.alipay
    dict_outsource['target_otype'] = outsource.target.otype
    dict_outsource['target_otype_cn'] = outsource.target.otype_cn
    dict_outsource['type_cn'] = outsource.type_cn
    if outsource.status == 4:
        dict_outsource['pay_status_cn'] = u'已付款'
        dict_outsource['pay_time_cn'] = outsource.create_time.strftime('%Y-%m-%d')
    else:
        dict_outsource['pay_status_cn'] = u'未付款'
        dict_outsource['pay_time_cn'] = u'无'
    dict_outsource['order_year'] = list(set([order.client_start.year, order.client_end.year]))
    if dict_outsource['target_id'] == 271 or dict_outsource['status'] not in [2, 3, 4]:
        dict_outsource = {}
    return dict_outsource


@data_query_outsource_bp.route('/order_info', methods=['GET'])
def order_info():
    now_year = int(request.values.get('year', datetime.datetime.now().year))
    outsources = [_target_outsource_to_dict(k, 'client_order', now_year) for k in OutSource.all()]
    outsources += [_target_outsource_to_dict(k, 'douban_order', now_year) for k in DoubanOutSource.all()]
    outsources = [o for o in outsources if o]
    orders = list(set([s['order'] for s in outsources if now_year in s['order_year']]))
    order_obj = []
    for k in orders:
        order_dict = {}
        if k.__tablename__ == 'bra_client_order':
            order_dict['outsource_obj'] = [o for o in outsources if o[
                'order_type'] == 'client_order' and o['order_id'] == k.id]
        else:
            order_dict['outsource_obj'] = [o for o in outsources if o[
                'order_type'] == 'douban_order' and o['order_id'] == k.id]
        order_dict['contract'] = k.contract
        order_dict['campaign'] = k.campaign
        order_dict['money'] = k.money
        order_dict['locations_cn'] = k.locations_cn
        order_dict['outsources_sum'] = k.outsources_sum
        order_dict['outsources_percent'] = k.outsources_percent
        order_dict['outsources_paied_sum'] = k.outsources_paied_sum_by_shenji('all')
        if order_dict['outsource_obj']:
            order_obj.append(order_dict)
    if request.values.get('action', '') == 'download':
        return write_outsource_order_info_excel(order_obj)
    return tpl('/data_query/outsource/order_info.html', orders=order_obj, now_year=now_year)
