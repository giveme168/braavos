# -*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request
from flask import render_template as tpl

from models.outsource import OutSourceExecutiveReport
from libs.date_helpers import (check_Q_get_monthes, check_month_get_Q)
from libs.date_helpers import get_monthes_pre_days
from controllers.data_query.helpers.outsource_helpers import write_outsource_excel


data_query_outsource_bp = Blueprint(
    'data_query_outsource', __name__, template_folder='../../templates/data_query')


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
    outsources = [k for k in OutSourceExecutiveReport.query.filter(
        OutSourceExecutiveReport.month_day >= start_month_day,
        OutSourceExecutiveReport.month_day <= end_month_day)
        if k.contract_status not in [7, 8, 9] and k.order_status == 1]
    # 所有外包分类
    types = [1, 2, 3, 4, 5, 6, 7]

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
            num_data['huabei'] = sum(
                [j.pay_num for j in outsources if j.month_day == month_day and j.type == i and j.is_location(1)])
            num_data['huadong'] = sum(
                [j.pay_num for j in outsources if j.month_day == month_day and j.type == i and j.is_location(2)])
            num_data['huanan'] = sum(
                [j.pay_num for j in outsources if j.month_day == month_day and j.type == i and j.is_location(3)])
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

    outsources = [k for k in OutSourceExecutiveReport.query.filter(
        OutSourceExecutiveReport.month_day >= start_date,
        OutSourceExecutiveReport.month_day <= end_date)
        if k.contract_status not in [7, 8, 9] and k.order_status == 1]

    pre_monthes = get_monthes_pre_days(start_date, end_date)
    pre_month_orders = {}
    for k in pre_monthes:
        pre_month_orders[str(k['month'].month)] = list(set([s.order for s in outsources if s.month_day == k['month']]))
    return tpl('/data_query/outsource/info.html', now_year=now_year, pre_month_orders=pre_month_orders)
