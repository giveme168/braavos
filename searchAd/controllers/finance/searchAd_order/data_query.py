# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from searchAd.models.invoice import (searchAdInvoice, searchAdAgentInvoice, searchAdAgentInvoicePay,
                                     searchAdMediumInvoice, searchAdMediumInvoicePay, searchAdMediumRebateInvoice)
from searchAd.models.client_order import searchAdBackMoney, searchAdBackInvoiceRebate

from controllers.finance.helpers.data_query_helpers import write_order_excel

searchAd_finance_client_order_data_query_bp = Blueprint(
    'searchAd_finance_client_order_data_query', __name__, template_folder='../../templates/finance/searchAd_order/data_query')


@searchAd_finance_client_order_data_query_bp.route('/agent_invoice', methods=['GET'])
def agent_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))
    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdInvoice.query.filter(searchAdInvoice.create_time >= search_date,
                                                  searchAdInvoice.create_time < end_search_date,
                                                  searchAdInvoice.invoice_status == 0) if k.client_order.status == 1]
    else:
        orders = [k for k in searchAdInvoice.all() if k.create_time.year == int(
            year) and k.invoice_status == 0 and k.client_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'agent_invoice')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已开客户发票", t_type='agent_invoice')


@searchAd_finance_client_order_data_query_bp.route('/back_money', methods=['GET'])
def back_money():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdBackMoney.query.filter(searchAdBackMoney.back_time >= search_date,
                                                    searchAdBackMoney.back_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in searchAdBackMoney.all() if k.back_time.year == int(
            year) and k.client_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'back_money')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"客户回款金额", t_type='back_money')


@searchAd_finance_client_order_data_query_bp.route('/back_invoice', methods=['GET'])
def back_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdBackInvoiceRebate.query.filter(searchAdBackInvoiceRebate.back_time >= search_date,
                                                            searchAdBackInvoiceRebate.back_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in searchAdBackInvoiceRebate.all() if k.back_time.year == int(
            year) and k.client_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'back_invoice')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='back_invoice')


@searchAd_finance_client_order_data_query_bp.route('/rebate_agent_invoice', methods=['GET'])
def rebate_agent_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdAgentInvoice.query.filter(searchAdAgentInvoice.add_time >= search_date,
                                                       searchAdAgentInvoice.add_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in searchAdAgentInvoice.all() if k.add_time.year == int(
            year) and k.client_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.add_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'rebate_agent_invoice')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='rebate_agent_invoice')


@searchAd_finance_client_order_data_query_bp.route('/pay_rebate_agent_invoice', methods=['GET'])
def pay_rebate_agent_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdAgentInvoicePay.query.filter(searchAdAgentInvoicePay.pay_time >= search_date,
                                                          searchAdAgentInvoicePay.pay_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in searchAdAgentInvoicePay.all() if k.pay_time.year == int(
            year) and k.client_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]

    orders = sorted(list(orders), key=lambda x: x.pay_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'pay_rebate_agent_invoice')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='pay_rebate_agent_invoice')


@searchAd_finance_client_order_data_query_bp.route('/medium_invoice', methods=['GET'])
def medium_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdMediumInvoice.query.filter(searchAdMediumInvoice.add_time >= search_date,
                                                        searchAdMediumInvoice.add_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in searchAdMediumInvoice.all() if k.add_time.year == int(
            year) and k.client_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.add_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'medium_invoice')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已收媒体发票金额", t_type='medium_invoice')


@searchAd_finance_client_order_data_query_bp.route('/pay_medium_invoice', methods=['GET'])
def pay_medium_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdMediumInvoicePay.query.filter(searchAdMediumInvoicePay.pay_time >= search_date,
                                                           searchAdMediumInvoicePay.pay_time < end_search_date)
                  if k.client_order.status == 1 and k.pay_status == 0]
    else:
        orders = [k for k in searchAdMediumInvoicePay.all() if k.pay_time.year == int(
            year) and k.client_order.status == 1 and k.pay_status == 0]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.pay_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'pay_medium_invoice')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"付款给媒体金额", t_type='pay_medium_invoice')


@searchAd_finance_client_order_data_query_bp.route('/medium_rebate_invoice', methods=['GET'])
def medium_rebate_invoice():
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdMediumRebateInvoice.query.filter(searchAdMediumRebateInvoice.create_time >= search_date,
                                                              searchAdMediumRebateInvoice.create_time < end_search_date,
                                                              searchAdMediumRebateInvoice.invoice_status == 0)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in searchAdMediumRebateInvoice.all() if k.create_time.year == int(
            year) and k.invoice_status == 0 and k.client_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'medium_rebate_invoice')
        return response
    return tpl('/finance/searchAd_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已开媒体返点发票", t_type='medium_rebate_invoice')
