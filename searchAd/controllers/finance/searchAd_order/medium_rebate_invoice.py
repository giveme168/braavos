# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.user import User, TEAM_LOCATION_CN
from searchAd.models.client_order import searchAdClientOrder, CONTRACT_STATUS_CN
from searchAd.models.invoice import (searchAdMediumRebateInvoice, INVOICE_STATUS_CN,
                            INVOICE_TYPE_CN, INVOICE_STATUS_PASS,
                            INVOICE_STATUS_APPLYPASS)
from libs.email_signals import medium_rebate_invoice_apply_signal
from libs.paginator import Paginator
from controllers.finance.helpers.invoice_helpers import write_medium_rebate_invoice_excel
from controllers.tools import get_download_response
from searchAd.controllers.saler.searchAd_order.medium_rebate_invoice import get_invoice_from, new_invoice as _new_invoice

searchAd_finance_client_order_medium_rebate_invoice_bp = Blueprint(
    'searchAd_finance_client_order_medium_rebate_invoice', __name__, template_folder='../../../../templates/finance/client_order')

ORDER_PAGE_NUM = 50


@searchAd_finance_client_order_medium_rebate_invoice_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = set([
        invoice.client_order for invoice in searchAdMediumRebateInvoice.get_invoices_status(INVOICE_STATUS_APPLYPASS)])
    return tpl('/finance/searchAd_order/medium_rebate_invoice/index.html', orders=orders)


@searchAd_finance_client_order_medium_rebate_invoice_bp.route('/pass', methods=['GET'])
def index_pass():
    if not g.user.is_finance():
        abort(404)
    orders = list(searchAdClientOrder.all())
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower() in o.search_info.lower()]
    if orderby and len(orders):
        orders = sorted(
            orders, key=lambda x: getattr(x, orderby), reverse=True)
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    paginator = Paginator(orders, ORDER_PAGE_NUM)
    try:
        orders = paginator.page(page)
    except:
        orders = paginator.page(paginator.num_pages)
    type = request.args.get('type', '')
    if type == 'excel':
        orders = set([invoice.client_order for invoice in searchAdMediumRebateInvoice.get_invoices_status(
            INVOICE_STATUS_PASS)])
        xls = write_medium_rebate_invoice_excel(list(orders))
        response = get_download_response(
            xls, ("%s-%s.xls" % (u"申请过的媒体返点发票信息", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8'))
        return response
    return tpl('/finance/searchAd_order/medium_rebate_invoice/index_pass.html', orders=orders, locations=select_locations,
               location_id=location_id, statuses=select_statuses, orderby=orderby,
               now_date=datetime.date.today(), search_info=search_info, page=page,
               params='&orderby=%s&searchinfo=%s&selected_location=%s' %
                      (orderby, search_info, location_id))


@searchAd_finance_client_order_medium_rebate_invoice_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    if not g.user.is_finance():
        abort(404)
    order = searchAdClientOrder.get(order_id)
    if not order:
        abort(404)
    invoices_data = {
        'PASS': [{'invoice': x, 'form': get_invoice_from(order, x)} for x in
                 searchAdMediumRebateInvoice.query.filter_by(client_order=order) if x.invoice_status == INVOICE_STATUS_PASS],
        'APPLYPASS': [{'invoice': x, 'form': get_invoice_from(order, x)} for x in
                      searchAdMediumRebateInvoice.query.filter_by(client_order=order)
                      if x.invoice_status == INVOICE_STATUS_APPLYPASS],
    }
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    new_invoice_form = get_invoice_from(order, invoice=None)
    return tpl('/finance/searchAd_order/medium_rebate_invoice/info.html', order=order,
               invoices_data=invoices_data, INVOICE_STATUS_CN=INVOICE_STATUS_CN,
               reminder_emails=reminder_emails, INVOICE_TYPE_CN=INVOICE_TYPE_CN,
               new_invoice_form=new_invoice_form)


@searchAd_finance_client_order_medium_rebate_invoice_bp.route('/<order_id>/order/new', methods=['POST'])
def new_invoice(order_id, redirect_epoint='searchAd_finance_medium_rebate_invoice.info'):
    return _new_invoice(order_id, redirect_epoint)


@searchAd_finance_client_order_medium_rebate_invoice_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id):
    invoice = searchAdMediumRebateInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    if request.method == 'POST':
        company = request.values.get('edit_company', '')
        tax_id = request.values.get('edit_tax_id', '')
        detail = request.values.get('edit_detail', '')
        money = request.values.get('edit_money', 0)
        invoice_num = request.values.get('edit_invoice_num', '')
        invoice_type = request.values.get('invoice_type', 0)
        if not tax_id:
            flash(u"修改发票失败，税号不能为空", 'danger')
        elif not company:
            flash(u"修改发票失败, 公司名称不能为空", 'danger')
        elif not detail:
            flash(u"修改发票失败，发票内容不能为空", 'danger')
        elif not money:
            flash(u"修改发票失败，发票金额不能为空", 'danger')
        elif not invoice_num:
            flash(u"修改发票失败，发票号不能为空", 'danger')
        else:
            invoice.company = company
            invoice.tax_id = tax_id
            invoice.detail = detail
            invoice.invoice_num = invoice_num
            invoice.money = money
            invoice.invoice_type = invoice_type
            invoice.save()
            flash(u'修改发票(%s)成功!' % company, 'success')
            invoice.client_order.add_comment(g.user, u"修改发票信息,%s" % (
                u'发票内容: %s; 发票号: %s; 发票金额: %s元' % (invoice.detail, invoice_num, str(invoice.money))), msg_channel=6)
    return redirect(url_for("searchAd_finance_client_order_medium_rebate_invoice.info", order_id=invoice.client_order.id))


@searchAd_finance_client_order_medium_rebate_invoice_bp.route('/<invoice_id>/invoice_num', methods=['POST'])
def invoice_num(invoice_id):
    if not g.user.is_finance():
        abort(404)
    invoice = searchAdMediumRebateInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoice_num = request.values.get('invoice_num', '')
    invoice.invoice_num = invoice_num
    invoice.save()
    flash(u'保存成功!', 'success')
    invoice.client_order.add_comment(
        g.user, u"%s" % (u'更新了发票号: %s;' % (invoice.invoice_num)), msg_channel=6)
    return redirect(url_for("searchAd_finance_client_order_medium_rebate_invoice.info", order_id=invoice.client_order.id))


@searchAd_finance_client_order_medium_rebate_invoice_bp.route('/<invoice_id>/pass', methods=['POST'])
def pass_invoice(invoice_id):
    if not g.user.is_finance():
        abort(404)
    invoice = searchAdMediumRebateInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoices_ids = request.values.getlist('invoices')
    invoices = searchAdMediumRebateInvoice.gets(invoices_ids)
    if not invoices:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))
    to_users = invoice.client_order.direct_sales + invoice.client_order.agent_sales + \
        [invoice.client_order.creator, g.user] + \
        invoice.client_order.leaders
    if action != 10:
        invoice_status = INVOICE_STATUS_PASS
        action_msg = u'发票已开'
        for invoice in invoices:
            invoice.invoice_status = invoice_status
            invoice.create_time = datetime.date.today()
            invoice.save()
            flash(u'[%s 发票已开，发票金额%s]  %s ' %
                  (invoice.company, invoice.money, action_msg), 'success')
            invoice.client_order.add_comment(g.user, u"%s,%s" % (
                action_msg, u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=6)
    else:
        action_msg = u'消息提醒'

    context = {"to_users": to_users,
               "to_other": emails,
               "action_msg": action_msg,
               "action": 0,
               "info": msg,
               "order": invoice.client_order,
               "send_type": 'end',
               "invoices": invoices
               }
    medium_rebate_invoice_apply_signal.send(
        current_app._get_current_object(), context=context)
    return redirect(url_for("searchAd_finance_client_order_medium_rebate_invoice.info", order_id=invoice.client_order.id))
