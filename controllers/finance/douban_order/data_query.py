# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from models.douban_order import BackMoney, BackInvoiceRebate
from models.outsource import (MergerOutSource, MergerPersonalOutSource,
                              MergerDoubanOutSource, MergerDoubanPersonalOutSource)
from controllers.finance.helpers.data_query_helpers import write_order_excel
finance_douban_order_data_query_bp = Blueprint(
    'finance_douban_order_data_query', __name__, template_folder='../../templates/financd/data_query')


@finance_douban_order_data_query_bp.route('/back_money', methods=['GET'])
def back_money():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    location = int(request.values.get('location', 0))
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in BackMoney.query.filter(BackMoney.back_time >= search_date,
                                                    BackMoney.back_time < end_search_date)
                  if k.douban_order.status == 1]
    else:
        orders = [k for k in BackMoney.all() if k.back_time.year == int(
            year) and k.douban_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.douban_order.locations]
    if info:
        orders = [k for k in orders if info in k.douban_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'douban_back_money')
        return response
    return tpl('/finance/douban_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"客户回款金额", t_type='douban_back_money')


@finance_douban_order_data_query_bp.route('/back_invoice', methods=['GET'])
def back_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    location = int(request.values.get('location', 0))
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in BackInvoiceRebate.query.filter(BackInvoiceRebate.back_time >= search_date,
                                                            BackInvoiceRebate.back_time < end_search_date)
                  if k.douban_order.status == 1]
    else:
        orders = [k for k in BackInvoiceRebate.all() if k.back_time.year == int(
            year) and k.douban_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.douban_order.locations]
    if info:
        orders = [k for k in orders if info in k.douban_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'douban_back_invoice')
        return response
    return tpl('/finance/douban_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='douban_back_invoice')


@finance_douban_order_data_query_bp.route('/personal_outsource', methods=['GET'])
def personal_outsource():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    location = int(request.values.get('location', 0))
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)

        '''orders = [k for k in MergerPersonalOutSource.query.filter(
            MergerPersonalOutSource.create_time >= search_date,
            MergerPersonalOutSource.create_time < end_search_date,
            MergerPersonalOutSource.status == 0)]'''
        orders = [k for k in MergerDoubanPersonalOutSource.query.filter(
            MergerDoubanPersonalOutSource.create_time >= search_date,
            MergerDoubanPersonalOutSource.create_time < end_search_date,
            MergerDoubanPersonalOutSource.status == 0)]
    else:
        '''orders = [k for k in MergerPersonalOutSource.all(
        ) if k.create_time.year == int(year) and k.status == 0]'''
        orders = [k for k in MergerDoubanPersonalOutSource.all()
                   if k.create_time.year == int(year) and k.status == 0]
    if location != 0:
        orders = [k for k in orders if location in k.locations]
    if info:
        orders = [k for k in orders if info in k.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'personal_outsource')
        return response
    return tpl('/finance/douban_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"个人外包打款", t_type='personal_outsource')


@finance_douban_order_data_query_bp.route('/outsource', methods=['GET'])
def outsource():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    location = int(request.values.get('location', 0))
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))
    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)

        '''orders = [k for k in MergerOutSource.query.filter(MergerOutSource.create_time >= search_date,
                                                          MergerOutSource.create_time < end_search_date,
                                                          MergerOutSource.status == 0)]
        '''
        orders = [k for k in MergerDoubanOutSource.query.filter(MergerDoubanOutSource.create_time >= search_date,
                                                                 MergerDoubanOutSource.create_time < end_search_date,
                                                                 MergerDoubanOutSource.status == 0)]
    else:
        '''orders = [k for k in MergerOutSource.all(
        ) if k.create_time.year == int(year) and k.status == 0]'''
        orders = [k for k in MergerDoubanOutSource.all()
                   if k.create_time.year == int(year) and k.status == 0]
    if location != 0:
        orders = [k for k in orders if location in k.locations]
    if info:
        orders = [k for k in orders if info in k.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'outsource')
        return response
    return tpl('/finance/douban_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"对公外包打款", t_type='outsource')
