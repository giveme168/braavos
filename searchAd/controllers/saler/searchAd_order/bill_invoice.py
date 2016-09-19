# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app, jsonify
from flask import render_template as tpl

from libs.email_signals import bill_invoice_apply_signal
from searchAd.forms.invoice import BillInvoiceForm
from searchAd.models.client_order import searchAdClientOrderBill
from searchAd.models.invoice import (INVOICE_TYPE_CN, searchAdBillInvoice,
                                     INVOICE_STATUS_PASS, INVOICE_STATUS_NORMAL, INVOICE_STATUS_APPLY,
                                     INVOICE_STATUS_APPLYPASS, INVOICE_STATUS_FAIL, INVOICE_STATUS_CN)
from models.user import User


searchAd_saler_client_order_bill_invoice_bp = Blueprint(
    'searchAd_saler_client_order_bill_invoice', __name__, template_folder='../../../../templates/')


@searchAd_saler_client_order_bill_invoice_bp.route('/<bill_id>/bill', methods=['GET'])
def index(bill_id):
    bill = searchAdClientOrderBill.get(bill_id)
    if not bill:
        abort(404)
    invoices = searchAdBillInvoice.query.filter_by(client_order_bill=bill)
    invoices_data = {
        'PASS': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                 invoices if x.invoice_status == INVOICE_STATUS_PASS],
        'NORMAL': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                   invoices if x.invoice_status == INVOICE_STATUS_NORMAL],
        'APPLY': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                  invoices if x.invoice_status == INVOICE_STATUS_APPLY],
        'APPLYPASS': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                      invoices if x.invoice_status == INVOICE_STATUS_APPLYPASS],
        'FAIL': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                 invoices if x.invoice_status == INVOICE_STATUS_FAIL],
    }

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    new_invoice_form = BillInvoiceForm()
    new_invoice_form.client_medium_order.data = bill.medium.name
    new_invoice_form.back_time.data = datetime.date.today()
    return tpl('/saler/searchAd_bill/rebate_invoice/index.html', bill=bill,
               invoices_data=invoices_data, new_invoice_form=new_invoice_form,
               INVOICE_STATUS_CN=INVOICE_STATUS_CN, reminder_emails=reminder_emails,
               INVOICE_TYPE_CN=INVOICE_TYPE_CN)


def get_invoice_from(invoice):
    invoice_form = BillInvoiceForm()
    invoice_form.client_medium_order.data = invoice.client_order_bill.medium.name
    invoice_form.company.data = invoice.company
    invoice_form.bank.data = invoice.bank
    invoice_form.bank_id.data = invoice.bank_id
    invoice_form.address.data = invoice.address
    invoice_form.phone.data = invoice.phone
    invoice_form.tax_id.data = invoice.tax_id
    invoice_form.money.data = invoice.money
    invoice_form.detail.data = invoice.detail
    invoice_form.invoice_type.data = invoice.invoice_type
    if invoice.back_time:
        invoice_form.back_time.data = invoice.back_time.strftime('%Y-%m-%d')
    else:
        invoice_form.back_time.data = ''
    return invoice_form


@searchAd_saler_client_order_bill_invoice_bp.route('/<bill_id>/bill/new', methods=['POST'])
def new_invoice(bill_id):
    bill = searchAdClientOrderBill.get(bill_id)
    if not bill:
        abort(404)
    form = BillInvoiceForm(request.form)
    if request.method == 'POST' and form.validate():
        if int(form.money.data) > (int(bill.rebate_money) - int(bill.invoice_apply_sum) - int(bill.invoice_pass_sum)):
            flash(u"新建发票失败，您申请的发票超过了返点总额", 'danger')
            return redirect(url_for("searchAd_saler_client_order_bill_invoice.index",bill_id=bill.id))
        invoice = searchAdBillInvoice.add(client_order_bill=bill,
                                          company=form.company.data,
                                          tax_id=form.tax_id.data,
                                          address=form.address.data,
                                          phone=form.phone.data,
                                          bank_id=form.bank_id.data,
                                          bank=form.bank.data,
                                          detail=form.detail.data,
                                          money=form.money.data,
                                          invoice_type=form.invoice_type.data,
                                          invoice_status=INVOICE_STATUS_NORMAL,
                                          creator=g.user,
                                          invoice_num=" ",
                                          back_time=form.back_time.data)
        invoice.save()
        flash(u'新建发票(%s)成功!' % form.company.data, 'success')
        bill.add_comment(g.user, u"添加发票申请信息：%s" % (
             u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=1)
    else:
        for k in form.errors:
            flash(u"新建发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("searchAd_saler_client_order_bill_invoice.index", bill_id=bill.id))


@searchAd_saler_client_order_bill_invoice_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id):
    invoice = searchAdBillInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    form = BillInvoiceForm(request.form)
    form.client_medium_order = invoice.client_order_bill
    if request.method == 'POST' and form.validate():
        back_time = request.values.get('back_time', datetime.date.today())
        if not form.tax_id.data:
            flash(u"修改发票失败，公司名称不能为空", 'danger')
        elif not form.detail.data:
            flash(u"修改发票失败，发票内容不能为空", 'danger')
        elif not form.money.data:
            flash(u"修改发票失败，发票金额不能为空", 'danger')
        else:
            invoice.company = form.company.data,
            invoice.tax_id = form.tax_id.data,
            invoice.address = form.address.data,
            invoice.phone = form.phone.data,
            invoice.bank_id = form.bank_id.data,
            invoice.bank = form.bank.data,
            invoice.detail = form.detail.data,
            invoice.money = form.money.data,
            invoice.invoice_type = form.invoice_type.data,
            invoice.creator = g.user
            invoice.create_time = datetime.date.today()
            invoice.back_time = back_time
            invoice.save()
            flash(u'修改发票(%s)成功!' % form.company.data, 'success')
            invoice.client_order_bill.add_comment(g.user, u"修改发票信息,%s" % (
                u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=1)
    else:
        for k in form.errors:
            flash(u"修改发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("searchAd_saler_client_order_bill_invoice.index", bill_id=invoice.client_order_bill.id))


@searchAd_saler_client_order_bill_invoice_bp.route('/<invoice_id>/apply', methods=['POST'])
def apply_invoice(invoice_id):
    invoice = searchAdBillInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoices_ids = request.values.getlist('invoices')
    invoices = searchAdBillInvoice.gets(invoices_ids)
    if not invoices:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))
    send_type = "saler"
    if action == 2:
        to_users = User.searchAd_leaders() + list(set([i.creator for i in invoices]))
        invoice_status = INVOICE_STATUS_APPLY
        action_msg = u'对账单返点发票开具申请'
    elif action == 3:
        to_users = User.finances()
        invoice_status = INVOICE_STATUS_APPLYPASS
        action_msg = u'同意对账单返点发票开具申请'
        send_type = "finance"
    elif action == 4:
        to_users = User.searchAd_leaders() + list(set([i.creator for i in invoices]))
        invoice_status = INVOICE_STATUS_FAIL
        action_msg = u'客户发票开具申请未通过'
    if action != 10:
        to_users = User.searchAd_leaders() + list(set([i.creator for i in invoices]))
        for invoice in invoices:
            invoice.invoice_status = invoice_status
            invoice.create_time = datetime.date.today()
            invoice.save()
            flash(u'[%s 发票开具申请，发票金额%s]  %s ' %
                  (invoice.company, invoice.money, action_msg), 'success')
            invoice.client_order_bill.add_comment(g.user, u"%s,%s" % (
                action_msg, u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=1)
    else:
        action_msg = u'消息提醒'

    context = {"to_users": to_users,
               "action_msg": action_msg,
               "info": msg,
               "order": invoice.client_order_bill,
               "send_type": send_type,
               "action": action,
               "invoices": invoices,
               "to_other": emails
               }
    bill_invoice_apply_signal.send(
        current_app._get_current_object(), context=context)
    return redirect(url_for("searchAd_saler_client_order_bill_invoice.index", bill_id=invoice.client_order_bill.id))

