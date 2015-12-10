# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from models.invoice import (Invoice, AgentInvoice, AgentInvoicePay, MediumInvoice,
                            MediumInvoicePay, MediumRebateInvoice)
from models.client_order import BackMoney, BackInvoiceRebate
from models.outsource import (MergerOutSource, MergerPersonalOutSource,
                              MergerDoubanOutSource, MergerDoubanPersonalOutSource)
from controllers.finance.helpers.data_query_helpers import write_order_excel
finance_client_order_data_query_bp = Blueprint(
    'finance_client_order_data_query', __name__, template_folder='../../templates/finance/data_query')


@finance_client_order_data_query_bp.route('/agent_invoice', methods=['GET'])
def agent_invoice():
    if not g.user.is_finance():
        abort(404)
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
        orders = [k for k in Invoice.query.filter(Invoice.create_time >= search_date,
                                                  Invoice.create_time < end_search_date,
                                                  Invoice.invoice_status == 0) if k.client_order.status == 1]
    else:
        orders = [k for k in Invoice.all() if k.create_time.year == int(
            year) and k.invoice_status == 0 and k.client_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'agent_invoice')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已开客户发票", t_type='agent_invoice')


@finance_client_order_data_query_bp.route('/back_money', methods=['GET'])
def back_money():
    if not g.user.is_finance():
        abort(404)
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
                  if k.client_order.status == 1]
    else:
        orders = [k for k in BackMoney.all() if k.back_time.year == int(
            year) and k.client_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'back_money')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"客户回款金额", t_type='back_money')


@finance_client_order_data_query_bp.route('/back_invoice', methods=['GET'])
def back_invoice():
    if not g.user.is_finance():
        abort(404)
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
                  if k.client_order.status == 1]
    else:
        orders = [k for k in BackInvoiceRebate.all() if k.back_time.year == int(
            year) and k.client_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.back_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'back_invoice')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='back_invoice')


@finance_client_order_data_query_bp.route('/rebate_agent_invoice', methods=['GET'])
def rebate_agent_invoice():
    if not g.user.is_finance():
        abort(404)
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
        orders = [k for k in AgentInvoice.query.filter(AgentInvoice.add_time >= search_date,
                                                       AgentInvoice.add_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in AgentInvoice.all() if k.add_time.year == int(
            year) and k.client_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.add_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'rebate_agent_invoice')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='rebate_agent_invoice')


@finance_client_order_data_query_bp.route('/pay_rebate_agent_invoice', methods=['GET'])
def pay_rebate_agent_invoice():
    if not g.user.is_finance():
        abort(404)
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
        orders = [k for k in AgentInvoicePay.query.filter(AgentInvoicePay.pay_time >= search_date,
                                                          AgentInvoicePay.pay_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in AgentInvoicePay.all() if k.pay_time.year == int(
            year) and k.client_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.pay_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'pay_rebate_agent_invoice')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已收客户返点发票", t_type='pay_rebate_agent_invoice')


@finance_client_order_data_query_bp.route('/medium_invoice', methods=['GET'])
def medium_invoice():
    if not g.user.is_finance():
        abort(404)
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
        orders = [k for k in MediumInvoice.query.filter(MediumInvoice.add_time >= search_date,
                                                        MediumInvoice.add_time < end_search_date)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in MediumInvoice.all() if k.add_time.year == int(
            year) and k.client_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.add_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'medium_invoice')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已收媒体发票金额", t_type='medium_invoice')


@finance_client_order_data_query_bp.route('/pay_medium_invoice', methods=['GET'])
def pay_medium_invoice():
    if not g.user.is_finance():
        abort(404)
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
        orders = [k for k in MediumInvoicePay.query.filter(MediumInvoicePay.pay_time >= search_date,
                                                           MediumInvoicePay.pay_time < end_search_date)
                  if k.client_order.status == 1 and k.pay_status == 0]
    else:
        orders = [k for k in MediumInvoicePay.all() if k.pay_time.year == int(
            year) and k.client_order.status == 1 and k.pay_status == 0]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.pay_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'pay_medium_invoice')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"付款给媒体金额", t_type='pay_medium_invoice')


@finance_client_order_data_query_bp.route('/medium_rebate_invoice', methods=['GET'])
def medium_rebate_invoice():
    if not g.user.is_finance():
        abort(404)
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
        orders = [k for k in MediumRebateInvoice.query.filter(MediumRebateInvoice.create_time >= search_date,
                                                              MediumRebateInvoice.create_time < end_search_date,
                                                              MediumRebateInvoice.invoice_status == 0)
                  if k.client_order.status == 1]
    else:
        orders = [k for k in MediumRebateInvoice.all() if k.create_time.year == int(
            year) and k.invoice_status == 0 and k.client_order.status == 1]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'medium_rebate_invoice')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已开媒体返点发票", t_type='medium_rebate_invoice')


@finance_client_order_data_query_bp.route('/personal_outsource', methods=['GET'])
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

        orders = [k for k in MergerPersonalOutSource.query.filter(
            MergerPersonalOutSource.create_time >= search_date,
            MergerPersonalOutSource.create_time < end_search_date,
            MergerPersonalOutSource.status == 0)]
        '''orders += [k for k in MergerDoubanPersonalOutSource.query.filter(
            MergerDoubanPersonalOutSource.create_time >= search_date,
            MergerDoubanPersonalOutSource.create_time < end_search_date,
            MergerDoubanPersonalOutSource.status == 0)]'''
    else:
        orders = [k for k in MergerPersonalOutSource.all(
        ) if k.create_time.year == int(year) and k.status == 0]
        '''orders += [k for k in MergerDoubanPersonalOutSource.all()
                   if k.create_time.year == int(year) and k.status == 0]'''
    if location != 0:
        orders = [k for k in orders if location in k.locations]
    if info:
        orders = [k for k in orders if info in k.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'personal_outsource')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"个人外包打款", t_type='personal_outsource')


@finance_client_order_data_query_bp.route('/outsource', methods=['GET'])
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

        orders = [k for k in MergerOutSource.query.filter(MergerOutSource.create_time >= search_date,
                                                          MergerOutSource.create_time < end_search_date,
                                                          MergerOutSource.status == 0)]
        '''orders += [k for k in MergerDoubanOutSource.query.filter(MergerDoubanOutSource.create_time >= search_date,
                                                                 MergerDoubanOutSource.create_time < end_search_date,
                                                                 MergerDoubanOutSource.status == 0)]'''
    else:
        orders = [k for k in MergerOutSource.all(
        ) if k.create_time.year == int(year) and k.status == 0]
        '''orders += [k for k in MergerDoubanOutSource.all()
                   if k.create_time.year == int(year) and k.status == 0]'''
    if location != 0:
        orders = [k for k in orders if location in k.locations]
    if info:
        orders = [k for k in orders if info in k.search_invoice_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'outsource')
        return response
    return tpl('/finance/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"对公外包打款", t_type='outsource')
