# -*- coding: utf-8 -*-

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.invoice import (MediumInvoice, MediumInvoicePay, MEDIUM_INVOICE_STATUS_PASS,
                            INVOICE_TYPE_CN, MEDIUM_INVOICE_STATUS_AGREE)
from models.user import User
from libs.signals import medium_invoice_apply_signal


finance_medium_pay_bp = Blueprint(
    'finance_medium_pay', __name__, template_folder='../../templates/finance')


@finance_medium_pay_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = set([
        invoicepay.medium_invoice.client_order for invoicepay in
        MediumInvoicePay.get_medium_invoices_status(MEDIUM_INVOICE_STATUS_AGREE)])
    return tpl('/finance/medium_pay/index.html', orders=orders)


@finance_medium_pay_bp.route('/pass', methods=['GET'])
def index_pass():
    if not g.user.is_finance():
        abort(404)
    orders = set([
        invoicepay.medium_invoice.client_order for invoicepay in
        MediumInvoicePay.get_medium_invoices_status(MEDIUM_INVOICE_STATUS_PASS)])
    return tpl('/finance/medium_pay/index.html', orders=orders)


@finance_medium_pay_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    if not g.user.is_finance():
        abort(404)
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    invoices = MediumInvoice.query.filter_by(client_order=order)
    return tpl('/finance/medium_pay/info.html', order=order, invoices=invoices)


@finance_medium_pay_bp.route('/<invoice_id>/pay_info', methods=['GET'])
def pay_info(invoice_id):
    if not g.user.is_finance():
        abort(404)
    invoice = MediumInvoice.get(invoice_id)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/medium_pay/pay_info.html', invoice=invoice, reminder_emails=reminder_emails,
               INVOICE_TYPE_CN=INVOICE_TYPE_CN)


@finance_medium_pay_bp.route('/<invoice_id>/pay_num', methods=['POST'])
def invoice_pay_num(invoice_id):
    if not g.user.is_finance():
        abort(404)
    invoice = MediumInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    pay_money = request.form.get('pay_money', 0)
    invoice.pay_money = pay_money
    invoice.save()
    flash(u'保存成功!', 'success')
    invoice.client_order.add_comment(g.user,
                                     u"更新了打款金额:\n\r%s" % invoice.pay_money,
                                     msg_channel=3)
    return redirect(url_for("finance_medium_pay.info", order_id=invoice.client_order.id))


@finance_medium_pay_bp.route('/<invoice_id>/pass', methods=['POST'])
def invoice_pass(invoice_id):
    if not g.user.is_finance():
        abort(404)
    invoice = MediumInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoices_ids = request.values.getlist('invoices')
    invoices_pay = MediumInvoicePay.gets(invoices_ids)
    if not invoices_pay:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))

    to_users = invoice.client_order.direct_sales + invoice.client_order.agent_sales + \
        [invoice.client_order.creator, g.user] + \
        User.operater_leaders() + User.medias()
    to_emails = list(set(emails + [x.email for x in to_users]))

    if action != 10:
        invoice_status = MEDIUM_INVOICE_STATUS_PASS
        action_msg = u'媒体订单款已打'
        for invoice_pay in invoices_pay:
            invoice_pay.pay_status = invoice_status
            invoice_pay.save()
            flash(u'媒体订单款已打,名称:%s, 打款金额%s' % (
                invoice_pay.medium_invoice.client_order.name +
                '-' + invoice_pay.medium_invoice.medium.name,
                str(invoice_pay.money)), 'success')
            invoice_pay.medium_invoice.client_order.add_comment(
                g.user, u'媒体订单款已打款,名称%s, 打款金额%s ' % (
                    invoice_pay.medium_invoice.client_order.name +
                        '-' + invoice_pay.medium_invoice.medium.name,
                    str(invoice_pay.money)),
                msg_channel=3)
    else:
        action_msg = u'消息提醒'
    apply_context = {"title": "媒体订单款已打款",
                     "sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "send_type": "saler",
                     "invoice": invoice,
                     "invoice_pays": invoices_pay}
    medium_invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'已发送邮件给 %s ' % (', '.join(to_emails)), 'info')
    return redirect(url_for("finance_medium_pay.pay_info", invoice_id=invoice_id))
