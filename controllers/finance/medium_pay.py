# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.invoice import MediumInvoice, MEDIUM_INVOICE_STATUS_PASS, MEDIUM_INVOICE_STATUS_APPLY, INVOICE_TYPE_CN
from models.user import User
from libs.signals import medium_invoice_apply_signal
from controllers.finance.helpers.medium_pay_helpers import medium_write_excel
from controllers.tools import get_download_response


finance_medium_pay_bp = Blueprint(
    'finance_medium_pay', __name__, template_folder='../../templates/finance')


@finance_medium_pay_bp.route('/', methods=['GET'])
def index():
    orders = set([
        invoice.client_order for invoice in MediumInvoice.get_medium_invoices_status(MEDIUM_INVOICE_STATUS_APPLY)])
    return tpl('/finance/medium_pay/index.html', orders=orders)


@finance_medium_pay_bp.route('/pass', methods=['GET'])
def index_pass():
    orders = set([
        invoice.client_order for invoice in MediumInvoice.get_medium_invoices_status(MEDIUM_INVOICE_STATUS_PASS)])
    type = request.args.get('type', '')
    if type == 'excel':
        xls = medium_write_excel(list(orders))
        response = get_download_response(
            xls, ("%s-%s.xls" % (u"已打款的媒体信息", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8'))
        return response
    return tpl('/finance/medium_pay/index_pass.html', orders=orders)


@finance_medium_pay_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    invoices_data = {
        'pass': [x for x in order.get_medium_invoice_by_status(MEDIUM_INVOICE_STATUS_PASS)],
        'apply': [x for x in order.get_medium_invoice_by_status(MEDIUM_INVOICE_STATUS_APPLY)],
    }
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/medium_pay/info.html', order=order,
               invoices_data=invoices_data, reminder_emails=reminder_emails,
               INVOICE_TYPE_CN=INVOICE_TYPE_CN)


@finance_medium_pay_bp.route('/<invoice_id>/pay_num', methods=['POST'])
def invoice_pay_num(invoice_id):
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
    invoice = MediumInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoices_ids = request.values.getlist('invoices')
    invoices = MediumInvoice.gets(invoices_ids)
    if not invoices:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))

    to_users = invoice.client_order.direct_sales + invoice.client_order.agent_sales + \
        [invoice.client_order.creator, g.user] + User.operater_leaders()
    to_emails = list(set(emails + [x.email for x in to_users]))

    if action != 10:
        invoice_status = MEDIUM_INVOICE_STATUS_PASS
        action_msg = u'媒体订单款已打'
        for invoice in invoices:
            invoice.invoice_status = invoice_status
            invoice.create_time = datetime.date.today()
            invoice.pay_time = datetime.date.today()
            invoice.bool_pay = True
            invoice.save()
            flash(u'媒体订单款已打,名称:%s ' % (
                invoice.client_order.name + '-' + invoice.medium.name), 'success')
            invoice.client_order.add_comment(
                g.user, u'媒体订单款已打,名称%s ' % (invoice.client_order.name + '-' + invoice.medium.name), msg_channel=3)
    else:
        action_msg = u'消息提醒'

    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "send_type": "saler",
                     "order": invoice.client_order,
                     "invoices": invoices}
    medium_invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    return redirect(url_for("finance_medium_pay.info", order_id=invoice.client_order.id))
