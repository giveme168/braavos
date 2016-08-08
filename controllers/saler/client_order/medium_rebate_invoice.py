# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl
from models.medium import Media, MediumGroup
from models.client_order import ClientOrder
from models.invoice import (MediumRebateInvoice, INVOICE_STATUS_CN, INVOICE_TYPE_CN,
                            INVOICE_STATUS_NORMAL, INVOICE_STATUS_PASS,
                            INVOICE_STATUS_APPLY, INVOICE_STATUS_APPLYPASS,
                            INVOICE_STATUS_FAIL)
from models.user import User
from forms.invoice import MediumRebateInvoiceForm
from libs.email_signals import medium_rebate_invoice_apply_signal


saler_client_order_medium_rebate_invoice_bp = Blueprint(
    'saler_client_order_medium_rebate_invoice', __name__, template_folder='../../templates/saler')


@saler_client_order_medium_rebate_invoice_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    client_order = ClientOrder.get(order_id)
    if not client_order:
        abort(404)
    invoices = MediumRebateInvoice.query.filter_by(client_order=client_order)
    invoices_data = {
        'PASS': [{'invoice': x, 'form': get_invoice_from(client_order, x)} for x in
                 invoices if x.invoice_status == INVOICE_STATUS_PASS],
        'NORMAL': [{'invoice': x, 'form': get_invoice_from(client_order, x)} for x in
                   invoices if x.invoice_status == INVOICE_STATUS_NORMAL],
        'APPLY': [{'invoice': x, 'form': get_invoice_from(client_order, x)} for x in
                  invoices if x.invoice_status == INVOICE_STATUS_APPLY],
        'APPLYPASS': [{'invoice': x, 'form': get_invoice_from(client_order, x)} for x in
                      invoices if x.invoice_status == INVOICE_STATUS_APPLYPASS],
        'FAIL': [{'invoice': x, 'form': get_invoice_from(client_order, x)} for x in
                 invoices if x.invoice_status == INVOICE_STATUS_FAIL],
    }
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    new_invoice_form = get_invoice_from(client_order, invoice=None)
    return tpl('/saler/client_order/medium_rebate_invoice/index.html', order=client_order,
               invoices_data=invoices_data, new_invoice_form=new_invoice_form,
               INVOICE_STATUS_CN=INVOICE_STATUS_CN, reminder_emails=reminder_emails,
               INVOICE_TYPE_CN=INVOICE_TYPE_CN)


def get_invoice_from(client_order, invoice=None):
    invoice_form = MediumRebateInvoiceForm()
    if invoice:
        invoice_form.client_order.choices = [
            (invoice.client_order.id, invoice.client_order.client.name)]
        invoice_form.media.choices = [(medium.id, medium.name) for medium in invoice.client_order.medias]
        invoice_form.medium_group.choices = [(medium.id, medium.name) for medium in invoice.client_order.medium_groups]
        if invoice:
            invoice_form.media.data = invoice.media.id
            invoice_form.medium_group.data = invoice.medium_group.id
        invoice_form.company.data = invoice.company
        invoice_form.bank.data = invoice.bank
        invoice_form.bank_id.data = invoice.bank_id
        invoice_form.address.data = invoice.address
        invoice_form.phone.data = invoice.phone
        invoice_form.tax_id.data = invoice.tax_id
        invoice_form.money.data = invoice.money
        invoice_form.detail.data = invoice.detail
        invoice_form.invoice_type.data = invoice.invoice_type
        invoice_form.back_time.data = invoice.back_time.strftime('%Y-%m-%d') \
            if invoice.back_time else datetime.date.today()
    else:
        invoice_form.client_order.choices = [(client_order.id, client_order.client.name)]
        invoice_form.media.choices = [(medium.id, medium.name) for medium in client_order.medias]
        invoice_form.medium_group.choices = [(medium.id, medium.name) for medium in client_order.medium_groups]
        invoice_form.back_time.data = datetime.date.today()
    return invoice_form


@saler_client_order_medium_rebate_invoice_bp.route('/<order_id>/order/new', methods=['POST'])
def new_invoice(order_id, redirect_epoint='saler_client_order_medium_rebate_invoice.index'):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    form = MediumRebateInvoiceForm(request.form)
    form.client_order.choices = [(order.id, order.client.name)]
    form.medium_group.choices = [(m.id, m.name) for m in order.medium_groups]
    form.media.choices = [(medium.id, medium.name) for medium in order.medias]
    if request.method == 'POST':
        media = Media.get(form.media.data)
        # if float(form.money.data) > float(order.get_medium_rebate_money(medium) -
        #                                   order.get_medium_rebate_invoice_apply_sum(medium) -
        #                                   order.get_medium_rebate_invoice_pass_sum(medium)):
        #     flash(u"新建发票失败，您申请的发票超过了媒体:%s 返点金额: %s" % (medium.name, order.get_medium_rebate_money(medium)), 'danger')
        #     return redirect(url_for(redirect_epoint, order_id=order_id))
        invoice = MediumRebateInvoice.add(client_order=order,
                                          medium_group=MediumGroup.get(request.values.get('medium_group')),
                                          media=media,
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
        order.add_comment(g.user, u"添加发票申请信息：%s" % (
            u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=6)
    else:
        for k in form.errors:
            flash(u"新建发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for(redirect_epoint, order_id=order_id))


@saler_client_order_medium_rebate_invoice_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id):
    invoice = MediumRebateInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    form = MediumRebateInvoiceForm(request.form)
    form.client_order.choices = [
        (invoice.client_order.id, invoice.client_order.client.name)]
    form.medium_group.choices = [(medium.id, medium.name) for medium in invoice.client_order.medium_groups]
    form.media.choices = [(medium.id, medium.name) for medium in invoice.client_order.medias]
    if request.method == 'POST':
        back_time = request.values.get('back_time', datetime.date.today())
        if not form.company.data:
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
                u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=6)
    else:
        for k in form.errors:
            flash(u"修改发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("saler_client_order_medium_rebate_invoice.index", order_id=invoice.client_order.id))


@saler_client_order_medium_rebate_invoice_bp.route('/<invoice_id>/apply', methods=['POST'])
def apply_invoice(invoice_id):
    invoice = MediumRebateInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoices_ids = request.values.getlist('invoices')
    invoices = MediumRebateInvoice.gets(invoices_ids)
    if not invoices:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))
    to_users = User.medias() + User.media_leaders() + User.super_leaders()
    send_type = "saler"
    if action == 2:
        invoice_status = INVOICE_STATUS_APPLY
        action_msg = u'媒体返点发票开具申请'
    elif action == 3:
        to_users += User.finances()
        invoice_status = INVOICE_STATUS_APPLYPASS
        action_msg = u'同意媒体返点发票开具申请'
        send_type = "finance"
    elif action == 4:
        invoice_status = INVOICE_STATUS_FAIL
        action_msg = u'媒体返点发票开具申请未通过'
    if action != 10:
        for invoice in invoices:
            invoice.invoice_status = invoice_status
            invoice.create_time = datetime.date.today()
            invoice.save()
            flash(u'[%s 发票开具申请，发票金额%s]  %s ' %
                  (invoice.company, invoice.money, action_msg), 'success')
            invoice.client_order.add_comment(g.user, u"%s,%s" % (
                action_msg, u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=6)
    else:
        action_msg = u'消息提醒'

    context = {"to_users": to_users,
               "to_other": emails,
               "action_msg": action_msg,
               "info": msg,
               "order": invoice.client_order,
               "send_type": send_type,
               "action": action,
               "invoices": invoices
               }
    medium_rebate_invoice_apply_signal.send(
        current_app._get_current_object(), context=context)
    return redirect(url_for("saler_client_order_medium_rebate_invoice.index", order_id=invoice.client_order.id))
