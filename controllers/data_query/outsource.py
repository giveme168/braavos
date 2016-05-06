# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.outsource import OutSourceExecutiveReport
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q)
from controllers.data_query.helpers.outsource_helpers import write_outsource_excel, write_outsource_info_excel


data_query_outsource_bp = Blueprint(
    'data_query_outsource', __name__, template_folder='../../templates/data_query')


def outsource_to_dict(outsource):
    dict_outsource = {}
    try:

        dict_outsource['otype'] = outsource.otype
        dict_outsource['order'] = outsource.order
        if dict_outsource['otype'] != 1 and outsource.order.id == 629:
            dict_outsource['order_status'] = 0
        else:
            dict_outsource['order_status'] = dict_outsource['order'].status
            dict_outsource['month_day'] = outsource.month_day
            dict_outsource['type'] = outsource.type
            dict_outsource['locations'] = list(set(dict_outsource['order'].locations))
            if outsource.target.id == 271:
                dict_outsource['pay_num'] = 0
                dict_outsource['l_pre_pay_num'] = 0
            else:
                dict_outsource['pay_num'] = outsource.pay_num
                dict_outsource['l_pre_pay_num'] = outsource.pay_num / len(dict_outsource['locations'])
    except:
        dict_outsource['order_status'] = 0
    return dict_outsource


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

    outsources = [outsource_to_dict(k) for k in OutSourceExecutiveReport.query.filter(
        OutSourceExecutiveReport.month_day >= start_month_day,
        OutSourceExecutiveReport.month_day <= end_month_day)]
    # 踢掉删除的合同
    outsources = [k for k in outsources if k['order_status'] == 1]

    # 所有外包分类
    types = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    monthes_data = {}
    for k in types:
        monthes_data[str(k)] = []
    monthes_data['t_locataion'] = []
    monthes_data['t_month'] = []
    for k in Q_monthes:
        month_day = datetime.datetime.strptime(now_year + '-' + str(k), '%Y-%m')
        t_huabei_num = 0
        t_huadong_num = 0
        t_huanan_num = 0
        for i in types:
            num_data = {}
            num_data['huabei'] = sum([j['l_pre_pay_num'] for j in outsources
                                      if j['month_day'] == month_day and j['type'] == i and 1 in j['locations']])
            num_data['huadong'] = sum([j['l_pre_pay_num'] for j in outsources
                                       if j['month_day'] == month_day and j['type'] == i and 2 in j['locations']])
            num_data['huanan'] = sum([j['l_pre_pay_num'] for j in outsources
                                      if j['month_day'] == month_day and j['type'] == i and 3 in j['locations']])
            t_huabei_num += num_data['huabei']
            t_huadong_num += num_data['huadong']
            t_huanan_num += num_data['huanan']
            monthes_data[str(i)].append(num_data)
        monthes_data['t_locataion'].append(
            {'huabei': t_huabei_num, 'huadong': t_huadong_num, 'huanan': t_huanan_num})
        monthes_data['t_month'].append(
            t_huabei_num + t_huadong_num + t_huanan_num)
    if request.values.get('action', '') == 'download':
        return write_outsource_excel(Q_monthes, monthes_data)
    return tpl('/data_query/outsource/index.html', Q=now_Q, now_year=now_year,
               Q_monthes=Q_monthes, monthes_data=monthes_data)


@data_query_outsource_bp.route('/info', methods=['GET'])
def info():
    now_year = request.values.get('year', datetime.datetime.now().year)
    now_year_date = datetime.datetime.strptime(str(now_year), '%Y')
    start_date = now_year_date
    end_date = now_year_date.replace(month=12, day=31)

    # outsources = [{'order': k.order, 'month': k.month_day, 'pay_num': k.pay_num,
    #                'type': k.type} for k in OutSourceExecutiveReport.query.filter(
    #     OutSourceExecutiveReport.month_day >= start_date,
    #     OutSourceExecutiveReport.month_day <= end_date) if k.order]

    outsources = [outsource_to_dict(k) for k in OutSourceExecutiveReport.query.filter(
        OutSourceExecutiveReport.month_day >= start_date,
        OutSourceExecutiveReport.month_day <= end_date)]
    outsources = [k for k in outsources if k['order_status'] == 1]
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
    orders = list(set([s['order'] for s in outsources]))
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
    '''
    # 获取每个月的合同信息
    pre_month_orders = {}
    for k in pre_monthes:
        pre_month_orders[str(k['month'].month)] = list(
            set([s['order'] for s in outsources if s['month_day'] == k['month']]))
    # 获取单个合同每个季度的单项外包数据
    for k in range(len(pre_month_orders.values())):
        orders = pre_month_orders[str(k+1)]
        for i in orders:
            o_money = []

            if k == 0:
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q1_monthes[0] and o[
                    'month_day'] <= Q1_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(21)]
            elif k == 1:
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q1_monthes[0] and o[
                    'month_day'] <= Q1_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(21)]
            elif k == 2:
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q1_monthes[0] and o[
                    'month_day'] <= Q1_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(21)]
            elif k == 3:
                o_money += [0.0 for d in range(7)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q2_monthes[0] and o[
                    'month_day'] <= Q2_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(14)]
            elif k == 4:
                o_money += [0.0 for d in range(7)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q2_monthes[0] and o[
                    'month_day'] <= Q2_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(14)]
            elif k == 5:
                o_money += [0.0 for d in range(7)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q2_monthes[0] and o[
                    'month_day'] <= Q2_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(14)]
            elif k == 6:
                o_money += [0.0 for d in range(14)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q3_monthes[0] and o[
                    'month_day'] <= Q3_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(7)]
            elif k == 7:
                o_money += [0.0 for d in range(14)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q3_monthes[0] and o[
                    'month_day'] <= Q3_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(7)]
            elif k == 8:
                o_money += [0.0 for d in range(14)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q3_monthes[0] and o[
                    'month_day'] <= Q3_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
                o_money += [0.0 for d in range(7)]
            elif k == 9:
                o_money += [0.0 for d in range(21)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q4_monthes[0] and o[
                    'month_day'] <= Q4_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
            elif k == 10:
                o_money += [0.0 for d in range(21)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q4_monthes[0] and o[
                    'month_day'] <= Q4_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
            elif k == 11:
                o_money += [0.0 for d in range(21)]
                o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q4_monthes[0] and o[
                    'month_day'] <= Q4_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
            # o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q1_monthes[0] and o[
            #     'month_day'] <= Q1_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
            # o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q2_monthes[0] and o[
            #     'month_day'] <= Q2_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
            # o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q3_monthes[0] and o[
            #     'month_day'] <= Q3_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
            # o_money += [float(sum([o['pay_num'] for o in outsources if o['month_day'] >= Q4_monthes[0] and o[
            #    'month_day'] <= Q4_monthes[2] and o['type'] == t and o['order'] == i])) for t in range(1, 8)]
            i.o_money = o_money
    total_Q_data = {}
    total_Q_data['first'] = numpy.array([float(0) for k in range(28)])
    total_Q_data['second'] = numpy.array([float(0) for k in range(28)])
    total_Q_data['third'] = numpy.array([float(0) for k in range(28)])
    total_Q_data['forth'] = numpy.array([float(0) for k in range(28)])
    for k in pre_month_orders['1'] + pre_month_orders['2'] + pre_month_orders['3']:
        total_Q_data['first'] += numpy.array(k.o_money)
    for k in pre_month_orders['4'] + pre_month_orders['5'] + pre_month_orders['6']:
        total_Q_data['second'] += numpy.array(k.o_money)
    for k in pre_month_orders['7'] + pre_month_orders['8'] + pre_month_orders['9']:
        total_Q_data['third'] += numpy.array(k.o_money)
    for k in pre_month_orders['10'] + pre_month_orders['11'] + pre_month_orders['12']:
        total_Q_data['forth'] += numpy.array(k.o_money)
    total = sum(total_Q_data['first']+total_Q_data['second']+total_Q_data['third']+total_Q_data['forth'])
    '''

    if request.values.get('action', '') == 'download':
        return write_outsource_info_excel(now_year, orders, total, r_outsource_pay)
    return tpl('/data_query/outsource/info.html', now_year=now_year, orders=orders,
               total=total, r_outsource_pay=r_outsource_pay)
