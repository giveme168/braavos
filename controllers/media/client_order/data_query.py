# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, g, abort
from flask import render_template as tpl

from models.invoice import MediumInvoice, MediumInvoicePay, MediumRebateInvoice
from controllers.finance.helpers.data_query_helpers import write_order_excel
media_client_order_data_query_bp = Blueprint(
    'media_client_order_data_query', __name__, template_folder='../../templates/media/client_order/data_query')


@media_client_order_data_query_bp.route('/medium_invoice', methods=['GET'])
def medium_invoice():
    if not (g.user.is_media() or g.user.is_media_leader() or g.user.is_contract()):
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
        orders = [k for k in orders if info in k.client_order.search_info]
    orders = sorted(list(orders), key=lambda x: x.add_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'medium_invoice')
        return response
    return tpl('/media/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已收媒体发票金额", t_type='medium_invoice')


@media_client_order_data_query_bp.route('/apply_pay_medium_invoice', methods=['GET'])
def apply_pay_medium_invoice():
    if not (g.user.is_media() or g.user.is_media_leader() or g.user.is_contract()):
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
                  if k.client_order.status == 1 and k.pay_status == 3]
    else:
        orders = [k for k in MediumInvoicePay.all() if k.pay_time.year == int(
            year) and k.client_order.status == 1 and k.pay_status == 3]
    if location != 0:
        orders = [k for k in orders if location in k.client_order.locations]
    if info:
        orders = [k for k in orders if info in k.client_order.search_info]
    orders = sorted(list(orders), key=lambda x: x.pay_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'pay_medium_invoice')
        return response
    return tpl('/media/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"申请中的媒体付款", t_type='pay_medium_invoice')


@media_client_order_data_query_bp.route('/pay_medium_invoice', methods=['GET'])
def pay_medium_invoice():
    if not (g.user.is_media() or g.user.is_media_leader() or g.user.is_contract()):
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
        orders = [k for k in orders if info in k.client_order.search_info]
    orders = sorted(list(orders), key=lambda x: x.pay_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'pay_medium_invoice')
        return response
    return tpl('/media/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"付款给媒体金额", t_type='pay_medium_invoice')


@media_client_order_data_query_bp.route('/medium_rebate_invoice', methods=['GET'])
def medium_rebate_invoice():
    if not (g.user.is_media() or g.user.is_media_leader() or g.user.is_contract()):
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
        orders = [k for k in orders if info in k.client_order.search_info]
    orders = sorted(list(orders), key=lambda x: x.create_time, reverse=False)
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders), 'medium_rebate_invoice')
        return response
    return tpl('/media/client_order/data_query/index.html',
               orders=orders, location=location,
               year=year, month=month, info=info,
               title=u"已开媒体返点发票", t_type='medium_rebate_invoice')
