# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from searchAd.models.rebate_order_invoice import (searchAdInvoice, searchAdRebateAgentInvoice, searchAdAgentInvoicePay)
from searchAd.models.rebate_order import searchAdBackMoney, searchAdBackInvoiceRebate

from controllers.finance.helpers.data_query_helpers import write_order_excel

searchAd_saler_rebate_order_data_query_bp = Blueprint(
    'searchAd_saler_rebate_order_data_query', __name__, template_folder='../../templates/saler/searchAd_rebate_order/data_query')


@searchAd_saler_rebate_order_data_query_bp.route('/agent_invoice', methods=['GET'])
def agent_invoice():
    if not g.user.is_finance():
        abort(404)
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
                                                  searchAdInvoice.invoice_status == 0) if k.rebate_order.status == 1]
    else:
        orders = [k for k in searchAdInvoice.all() if k.create_time.year == int(
            year) and k.invoice_status == 0 and k.rebate_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.rebate_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'agent_invoice')
        return response
    return tpl('/saler/searchAd_rebate_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已开客户发票", t_type='agent_invoice')


@searchAd_saler_rebate_order_data_query_bp.route('/back_money', methods=['GET'])
def back_money():
    if not g.user.is_finance():
        abort(404)
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
                  if k.rebate_order.status == 1]
    else:
        orders = [k for k in searchAdBackMoney.all() if k.back_time.year == int(
            year) and k.rebate_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.rebate_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'back_money')
        return response
    return tpl('/saler/searchAd_rebate_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"客户回款金额", t_type='back_money')


@searchAd_saler_rebate_order_data_query_bp.route('/back_invoice', methods=['GET'])
def back_invoice():
    if not g.user.is_finance():
        abort(404)
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
                  if k.rebate_order.status == 1]
    else:
        orders = [k for k in searchAdBackInvoiceRebate.all() if k.back_time.year == int(
            year) and k.rebate_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.rebate_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'back_invoice')
        return response
    return tpl('/saler/searchAd_rebate_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='back_invoice')


@searchAd_saler_rebate_order_data_query_bp.route('/rebate_agent_invoice', methods=['GET'])
def rebate_agent_invoice():
    if not g.user.is_finance():
        abort(404)
    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        end_search_date = (
            search_date + datetime.timedelta(days=(search_date.max.day - search_date.day) + 1)).replace(day=1)
        orders = [k for k in searchAdRebateAgentInvoice.query.filter(searchAdRebateAgentInvoice.add_time >= search_date,
                                                       searchAdRebateAgentInvoice.add_time < end_search_date)
                  if k.rebate_order.status == 1]
    else:
        orders = [k for k in searchAdRebateAgentInvoice.all() if k.add_time.year == int(
            year) and k.rebate_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.rebate_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.add_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'rebate_agent_invoice')
        return response
    return tpl('/saler/searchAd_rebate_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='rebate_agent_invoice')


@searchAd_saler_rebate_order_data_query_bp.route('/pay_rebate_agent_invoice', methods=['GET'])
def pay_rebate_agent_invoice():
    if not g.user.is_finance():
        abort(404)
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
                  if k.rebate_order.status == 1]
    else:
        orders = [k for k in searchAdAgentInvoicePay.all() if k.pay_time.year == int(
            year) and k.rebate_order.status == 1]
    if info:
        orders = [k for k in orders if info in k.rebate_order.search_invoice_info]

    orders = sorted(list(orders), key=lambda x: x.pay_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'pay_rebate_agent_invoice')
        return response
    return tpl('/saler/searchAd_rebate_order/data_query/index.html',
               orders=orders,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='pay_rebate_agent_invoice')
