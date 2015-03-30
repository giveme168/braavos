# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.invoice import (MediumInvoice, INVOICE_TYPE_CN, MEDIUM_INVOICE_BOOL_INVOICE_CN,
                            MEDIUM_INVOICE_STATUS_NORMAL, MEDIUM_INVOICE_STATUS_APPLY,
                            MEDIUM_INVOICE_STATUS_PASS, MEDIUM_INVOICE_STATUS_CN)
from models.user import User
from models.medium import Medium
from forms.invoice import MediumInvoiceForm
from libs.signals import medium_invoice_apply_signal


saler_medium_invoice_bp = Blueprint(
    'saler_medium_invoice', __name__, template_folder='../../templates')


@saler_medium_invoice_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    invoices = MediumInvoice.query.filter_by(client_order=order)
    invoices_data = {
        'pass': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                 invoices if x.invoice_status == MEDIUM_INVOICE_STATUS_PASS],
        'normal': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                   invoices if x.invoice_status == MEDIUM_INVOICE_STATUS_NORMAL],
        'apply': [{'invoice': x, 'form': get_invoice_from(x)} for x in
                  invoices if x.invoice_status == MEDIUM_INVOICE_STATUS_APPLY],
    }
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    new_invoice_form = MediumInvoiceForm()
    new_invoice_form.client_order.choices = [(order.id, order.client.name)]
    new_invoice_form.medium.choices = [(k.id, k.name)for k in order.mediums]
    new_invoice_form.add_time.data = datetime.date.today()
    return tpl('/saler/medium/index.html', order=order, reminder_emails=reminder_emails,
               new_invoice_form=new_invoice_form, invoices_data=invoices_data,
               MEDIUM_INVOICE_STATUS_CN=MEDIUM_INVOICE_STATUS_CN, INVOICE_TYPE_CN=INVOICE_TYPE_CN)


@saler_medium_invoice_bp.route('/<order_id>/order/new', methods=['POST'])
def new_invoice(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    form = MediumInvoiceForm(request.form)
    form.client_order.choices = [(order.id, order.client.name)]
    form.medium.choices = [(order.id, order.client.name) for k in order.mediums]
    form.bool_invoice.choices = MEDIUM_INVOICE_BOOL_INVOICE_CN.items()
    if request.method == 'POST':
        invoice = MediumInvoice.add(client_order=order,
                                    medium=Medium.get(form.medium.data),
                                    company=form.company.data,
                                    tax_id=form.tax_id.data,
                                    address=form.address.data,
                                    phone=form.phone.data,
                                    bank_id=form.bank_id.data,
                                    bank=form.bank.data,
                                    detail=form.detail.data,
                                    money=form.money.data,
                                    invoice_type=form.invoice_type.data,
                                    invoice_status=MEDIUM_INVOICE_STATUS_NORMAL,
                                    creator=g.user,
                                    invoice_num=form.invoice_num.data,
                                    add_time=form.add_time.data,
                                    bool_invoice=form.bool_invoice.data)
        invoice.save()
        flash(u'新建打款发票(%s)成功!' % form.company.data, 'success')
        order.add_comment(g.user, u"添加打款发票申请信息：%s" % (
            u'发票内容: %s; 发票金额: %s元; 发票号: %s' % (invoice.detail, str(invoice.money), invoice.invoice_num)), msg_channel=3)
    else:
        for k in form.errors:
            print k
            flash(u"新建打款发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("saler_medium_invoice.index", order_id=order_id))


def get_invoice_from(invoice):
    invoice_form = MediumInvoiceForm()
    invoice_form.client_order.choices = [
        (invoice.client_order.id, invoice.client_order.client.name)]

    invoice_form.medium.choices = [(invoice.medium.id, invoice.medium.name)]
    invoice_form.company.data = invoice.company
    invoice_form.bank.data = invoice.bank
    invoice_form.bank_id.data = invoice.bank_id
    invoice_form.address.data = invoice.address
    invoice_form.phone.data = invoice.phone
    invoice_form.tax_id.data = invoice.tax_id
    invoice_form.money.data = invoice.money
    invoice_form.detail.data = invoice.detail
    invoice_form.invoice_type.data = invoice.invoice_type
    invoice_form.invoice_num.data = invoice.invoice_num
    if invoice.add_time:
        invoice_form.add_time.data = invoice.add_time.strftime('%Y-%m-%d')
    else:
        invoice_form.add_time.data = ''
    invoice_form.bool_invoice.data = str(invoice.bool_invoice)
    return invoice_form


@saler_medium_invoice_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id):
    invoice = MediumInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    form = MediumInvoiceForm(request.form)
    form.client_order.choices = [
        (invoice.client_order.id, invoice.client_order.name)]
    form.medium.choices = [(invoice.medium.id, invoice.medium.name)]
    form.bool_invoice.bool_invoice = MEDIUM_INVOICE_BOOL_INVOICE_CN.items()
    if request.method == 'POST':
        if not form.invoice_num.data:
            flash(u"修改打款发票失败，发票号不能为空", 'danger')
        elif not form.money.data:
            flash(u"修改打款发票失败，发票金额不能为空", 'danger')
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
            invoice.add_time = form.add_time.data
            invoice.pay_time = datetime.date.today()
            invoice.bool_invoice = form.bool_invoice.data
            invoice.save()
            flash(u'修改打款发票(%s)成功!' % form.company.data, 'success')
            invoice.client_order.add_comment(g.user, u"修改打款发票信息,%s" % (
                u'打款发票内容: %s; 发票金额: %s元; 发票号: %s' %
                (invoice.detail, str(invoice.money), invoice.invoice_num)), msg_channel=3)
    else:
        for k in form.errors:
            flash(u"修改打款发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("saler_medium_invoice.index", order_id=invoice.client_order.id))


@saler_medium_invoice_bp.route('/<invoice_id>/apply', methods=['POST'])
def apply_invoice(invoice_id):
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
        [invoice.client_order.creator, g.user] + \
        invoice.client_order.leaders
    to_emails = list(set(emails + [x.email for x in to_users]))

    send_type = "saler"
    if action == 2:
        invoice_status = MEDIUM_INVOICE_STATUS_APPLY
        action_msg = u'发票开具申请'
    if action != 10:
        for invoice in invoices:
            invoice.invoice_status = invoice_status
            invoice.save()
            flash(u'[%s 打款发票申请，发票金额: %s, 发票号: %s]  %s ' %
                  (invoice.company, invoice.money, invoice.invoice_num, action_msg), 'success')
            invoice.client_order.add_comment(g.user, u"%s,%s" % (
                action_msg, u'打款发票内容: %s; 发票金额: %s元; 发票号: %s' %
                (invoice.detail, str(invoice.money), invoice.invoice_num)), msg_channel=3)
    else:
        action_msg = u'消息提醒'

    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": invoice.client_order,
                     "send_type": send_type,
                     "invoices": invoices}
    medium_invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s 打款发票开具申请] 已发送邮件给 %s ' %
          (invoice.client_order, ', '.join(to_emails)), 'info')
    return redirect(url_for("saler_medium_invoice.index", order_id=invoice.client_order.id))
