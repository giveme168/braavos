# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.invoice import (Invoice, INVOICE_STATUS_CN, INVOICE_TYPE_CN,
                            INVOICE_STATUS_NORMAL, INVOICE_STATUS_PASS,
                            INVOICE_STATUS_APPLY, INVOICE_STATUS_APPLYPASS,
                            INVOICE_STATUS_FAIL)
from models.user import User
from forms.invoice import InvoiceForm
from libs.signals import invoice_apply_signal


saler_invoice_bp = Blueprint(
    'saler_invoice', __name__, template_folder='../../templates/saler')


@saler_invoice_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    invoices = Invoice.query.filter_by(client_order=order)
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
    new_invoice_form = InvoiceForm()
    new_invoice_form.client_order.choices = [(order.id, order.client.name)]
    new_invoice_form.company.data = order.agent.name
    new_invoice_form.bank.data = order.agent.bank
    new_invoice_form.bank_id.data = order.agent.bank_num
    new_invoice_form.address.data = order.agent.address
    new_invoice_form.phone.data = order.agent.phone_num
    new_invoice_form.tax_id.data = order.agent.tax_num
    new_invoice_form.back_time.data = datetime.date.today()
    return tpl('/saler/invoice/index.html', order=order,
               invoices_data=invoices_data, new_invoice_form=new_invoice_form,
               INVOICE_STATUS_CN=INVOICE_STATUS_CN, reminder_emails=reminder_emails,
               INVOICE_TYPE_CN=INVOICE_TYPE_CN)


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
    invoice_form.invoice_type.data = invoice.invoice_type
    if invoice.back_time:
        invoice_form.back_time.data = invoice.back_time.strftime('%Y-%m-%d')
    else:
        invoice_form.back_time.data = ''
    return invoice_form


@saler_invoice_bp.route('/<order_id>/order/new', methods=['POST'])
def new_invoice(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    form = InvoiceForm(request.form)
    form.client_order.choices = [(order.id, order.client.name)]
    if request.method == 'POST' and form.validate():
        if int(form.money.data) > (int(order.money) - int(order.invoice_apply_sum) - int(order.invoice_pass_sum)):
            flash(u"新建发票失败，您申请的发票超过了合同总额", 'danger')
            return redirect(url_for("saler_invoice.index", order_id=order_id))
        back_time = request.values.get('back_time', datetime.date.today())
        invoice = Invoice.add(client_order=order,
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
                              back_time=back_time)
        invoice.save()
        flash(u'新建发票(%s)成功!' % form.company.data, 'success')
        order.add_comment(g.user, u"添加发票申请信息：%s" % (
            u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=1)
    else:
        for k in form.errors:
            flash(u"新建发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("saler_invoice.index", order_id=order_id))


@saler_invoice_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
    if not invoice:
        abort(404)
    form = InvoiceForm(request.form)
    form.client_order.choices = [
        (invoice.client_order.id, invoice.client_order.client.name)]
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
            invoice.client_order.add_comment(g.user, u"修改发票信息,%s" % (
                u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=1)
    else:
        for k in form.errors:
            flash(u"修改发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("saler_invoice.index", order_id=invoice.client_order.id))


@saler_invoice_bp.route('/<invoice_id>/apply', methods=['POST'])
def apply_invoice(invoice_id):
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

    send_type = "saler"
    if action == 2:
        invoice_status = INVOICE_STATUS_APPLY
        action_msg = u'发票开具申请'
    elif action == 3:
        to_emails = list(set(to_emails + [k.email for k in User.finances()]))
        invoice_status = INVOICE_STATUS_APPLYPASS
        action_msg = u'批准开发票'
        send_type = "finance"
    elif action == 4:
        invoice_status = INVOICE_STATUS_FAIL
        action_msg = u'发票审批未通过'
    if action != 10:
        for invoice in invoices:
            invoice.invoice_status = invoice_status
            invoice.create_time = datetime.date.today()
            invoice.save()
            flash(u'[%s 发票开具申请，发票金额%s]  %s ' %
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
                     "send_type": send_type,
                     "invoices": invoices}
    invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s 发票开具申请] 已发送邮件给 %s ' %
          (invoice.client_order, ', '.join(to_emails)), 'info')
    return redirect(url_for("saler_invoice.index", order_id=invoice.client_order.id))
