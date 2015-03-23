# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.invoice import (Invoice, INVOICE_STATUS_CN,
                            INVOICE_TYPE_CN, INVOICE_STATUS_PASS,
                            INVOICE_STATUS_APPLYPASS)
from models.user import User
from libs.signals import invoice_apply_signal
from forms.invoice import InvoiceForm


finance_invoice_bp = Blueprint(
    'finance_invoice', __name__, template_folder='../../templates/finance')


@finance_invoice_bp.route('/', methods=['GET'])
def index():
    orders = [
        invoice.client_order for invoice in Invoice.get_applypass_invoices()]
    for order in orders:
        order.apply_invoice_count = len(
            order.get_invoice_by_status(INVOICE_STATUS_APPLYPASS))
    return tpl('/finance/invoice/index.html', orders=orders)


@finance_invoice_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    invoices_data = {
        'PASS': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                 Invoice.query.filter_by(client_order=order) if x.invoice_status == INVOICE_STATUS_PASS],
        'APPLYPASS': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                      Invoice.query.filter_by(client_order=order) if x.invoice_status == INVOICE_STATUS_APPLYPASS],
    }
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/invoice/info.html', order=order,
               invoices_data=invoices_data, INVOICE_STATUS_CN=INVOICE_STATUS_CN,
               reminder_emails=reminder_emails, INVOICE_TYPE_CN=INVOICE_TYPE_CN)


@finance_invoice_bp.route('/<invoice_id>/pass', methods=['POST'])
def pass_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoices_ids = request.values.getlist('invoices')
    invoices = Invoice.gets(invoices_ids)
    if not invoices:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))
    to_users = invoice.client_order.direct_sales + invoice.client_order.agent_sales + \
        [invoice.client_order.creator, g.user] + \
        invoice.client_order.leaders
    to_emails = list(set(emails + [x.email for x in to_users]))

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
                action_msg, u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=1)
    else:
        action_msg = u'消息提醒'

    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": invoice.client_order,
                     "send_type": "saler",
                     "invoices": invoices}
    invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s 发票已开] 已发送邮件给 %s ' %
          (invoice.client_order, ', '.join(to_emails)), 'info')
    return redirect(url_for("finance_invoice.info", order_id=invoice.client_order.id))


def get_invoice_from(invoice):
    invoice_form = InvoiceForm()
    invoice_form.client_order.choices = [
        (invoice.client_order.id, invoice.client_order.client.name)]
    invoice_form.company.data = invoice.company
    invoice_form.bank.data = invoice.bank
    invoice_form.bank_id.data = invoice.bank_id
    invoice_form.address.data = invoice.address
    invoice_form.phone.data = invoice.phone
    invoice_form.tax_id.data = invoice.tax_id
    invoice_form.money.data = invoice.money
    invoice_form.detail.data = invoice.detail
    return invoice_form
