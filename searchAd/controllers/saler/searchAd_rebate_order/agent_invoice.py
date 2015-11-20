# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app, jsonify
from flask import render_template as tpl

from searchAd.models.rebate_order import searchAdRebateOrder
from searchAd.models.rebate_order_invoice import (searchAdRebateAgentInvoice, INVOICE_TYPE_CN, AGENT_INVOICE_BOOL_INVOICE_CN,
                                                  AGENT_INVOICE_STATUS_NORMAL, AGENT_INVOICE_STATUS_APPLY,
                                                  AGENT_INVOICE_STATUS_CN,
                                                  searchAdAgentInvoicePay, AGENT_INVOICE_STATUS_AGREE)
from models.user import User
from searchAd.models.client import searchAdAgent
from searchAd.forms.invoice import RebateAgentInvoiceForm as AgentInvoiceForm
from libs.signals import agent_invoice_apply_signal


searchAd_saler_rebate_order_agent_invoice_bp = Blueprint(
    'searchAd_saler_rebate_order_agent_invoice', __name__, template_folder='../../../../templates')


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<order_id>/order', methods=['GET'])
def index(order_id):
    order = searchAdRebateOrder.get(order_id)
    if not order:
        abort(404)
    invoices = searchAdRebateAgentInvoice.query.filter_by(rebate_order=order)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    new_invoice_form = AgentInvoiceForm()
    new_invoice_form.rebate_order.choices = [(order.id, order.client.name)]
    new_invoice_form.agent.choices = [(k.id, k.name)for k in order.agents]
    new_invoice_form.add_time.data = datetime.date.today()
    return tpl('/saler/searchAd_rebate_order/agent/index.html', order=order, reminder_emails=reminder_emails,
               new_invoice_form=new_invoice_form, invoices=invoices,
               AGENT_INVOICE_STATUS_CN=AGENT_INVOICE_STATUS_CN, INVOICE_TYPE_CN=INVOICE_TYPE_CN)


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<order_id>/order/new', methods=['POST'])
def new_invoice(order_id, redirect_endpoint='searchAd_saler_rebate_order_agent_invoice.index'):
    order = searchAdRebateOrder.get(order_id)
    if not order:
        abort(404)
    form = AgentInvoiceForm(request.form)
    form.rebate_order.choices = [(order.id, order.client.name)]
    form.agent.choices = [(order.id, order.client.name) for k in order.agents]
    form.bool_invoice.choices = AGENT_INVOICE_BOOL_INVOICE_CN.items()
    # if order.agent_money < order.agents_invoice_sum + float(form.money.data):
    #    flash(u'新建打款发票失败，发票超过代理总金额!', 'danger')
    #    return redirect(url_for(redirect_endpoint, order_id=order_id))
    if request.method == 'POST':
        invoice = searchAdRebateAgentInvoice.add(rebate_order=order,
                                           agent=searchAdAgent.get(
                                               form.agent.data),
                                           company=form.company.data,
                                           tax_id=form.tax_id.data,
                                           address=form.address.data,
                                           phone=form.phone.data,
                                           bank_id=form.bank_id.data,
                                           bank=form.bank.data,
                                           detail=form.detail.data,
                                           money=form.money.data,
                                           pay_money=form.money.data,
                                           invoice_type=form.invoice_type.data,
                                           invoice_status=AGENT_INVOICE_STATUS_NORMAL,
                                           creator=g.user,
                                           invoice_num=form.invoice_num.data,
                                           add_time=form.add_time.data,
                                           bool_invoice=form.bool_invoice.data)
        invoice.save()
        flash(u'新建打款发票(%s)成功!' % form.company.data, 'success')
        order.add_comment(g.user, u"添加打款发票申请信息：%s" % (
            u'发票内容: %s; 发票金额: %s元; 发票号: %s' % (invoice.detail, str(invoice.money), invoice.invoice_num)), msg_channel=5)
    else:
        for k in form.errors:
            flash(u"新建打款发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for(redirect_endpoint, order_id=order_id))


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<invoice_id>/invoice', methods=['POST', 'GET'])
def invoice(invoice_id):
    invoice = searchAdRebateAgentInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    form = get_invoice_form(invoice)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/saler/searchAd_rebate_order/agent/invoice.html', form=form, invoice=invoice, reminder_emails=reminder_emails,
               INVOICE_TYPE_CN=INVOICE_TYPE_CN, AGENT_INVOICE_STATUS_CN=AGENT_INVOICE_STATUS_CN)


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<invoice_id>/invoice/pay/new', methods=['POST'])
def new_invoice_pay(invoice_id):
    money = float(request.values.get('money', 0))
    pay_time = request.values.get('pay_time', '')
    detail = request.values.get('detail', '')
    mi = searchAdRebateAgentInvoice.get(invoice_id)
    # if mi.pay_invoice_money + money > mi.money:
    #     flash(u'付款金额大于发票金额，请重新填写!', 'danger')
    # return
    # redirect(url_for('searchAd_saler_rebate_order_agent_invoice.invoice',
    # invoice_id=invoice_id))
    pay = searchAdAgentInvoicePay.add(money=money,
                                      agent_invoice=mi,
                                      pay_time=pay_time,
                                      pay_status=0,
                                      detail=detail)
    pay.save()
    flash(u'添加已打款信息成功!', 'success')
    mi.rebate_order.add_comment(g.user, u"添加已打款信息  发票号：%s  打款金额：%s元  打款时间：%s" % (
        mi.invoice_num, str(money), pay_time), msg_channel=5)
    return redirect(url_for('searchAd_saler_rebate_order_agent_invoice.invoice', invoice_id=invoice_id))


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<invoice_id>/invoice/pay/<invoice_pay_id>/update', methods=['POST'])
def update_invoice_pay(invoice_id, invoice_pay_id):
    money = float(request.values.get('money', 0))
    pay_time = request.values.get('pay_time', '')
    detail = request.values.get('detail', '')
    pay = searchAdAgentInvoicePay.get(invoice_pay_id)
    mi = searchAdRebateAgentInvoice.get(invoice_id)
    # if mi.pay_invoice_money - pay.money + money > mi.money:
    #     flash(u'付款金额大于发票金额，请重新填写!', 'danger')
    # return
    # redirect(url_for('searchAd_saler_rebate_order_agent_invoice.invoice',
    # invoice_id=invoice_id))
    pay.money = money
    pay.pay_time = pay_time
    pay.detail = detail
    pay.save()
    return redirect(url_for('searchAd_saler_rebate_order_agent_invoice.invoice', invoice_id=invoice_id))


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<invoice_id>/invoice/pay/<invoice_pay_id>/delete', methods=['GET'])
def delete_invoice_pay(invoice_id, invoice_pay_id):
    pay = searchAdAgentInvoicePay.get(invoice_pay_id)
    money = pay.money
    mi = searchAdRebateAgentInvoice.get(invoice_id)
    pay.delete()
    mi.rebate_order.add_comment(g.user, u"删除已打款信息  发票号：%s  打款金额：%s元" % (
        mi.invoice_num, str(money)), msg_channel=5)
    flash(u'删除已打款信息成功!', 'success')
    return redirect(url_for('searchAd_saler_rebate_order_agent_invoice.invoice', invoice_id=invoice_id))


def get_invoice_form(invoice):
    invoice_form = AgentInvoiceForm()
    invoice_form.rebate_order.choices = [
        (invoice.rebate_order.id, invoice.rebate_order.client.name)]

    invoice_form.agent.choices = [(invoice.agent.id, invoice.agent.name)]
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


def get_invoice_from(invoice):
    return get_invoice_form(invoice)


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id, redirect_endpoint='searchAd_saler_rebate_order_agent_invoice.index'):
    invoice = searchAdRebateAgentInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    form = AgentInvoiceForm(request.form)
    form.rebate_order.choices = [
        (invoice.rebate_order.id, invoice.rebate_order.name)]
    form.agent.choices = [(invoice.agent.id, invoice.agent.name)]
    form.bool_invoice.bool_invoice = AGENT_INVOICE_BOOL_INVOICE_CN.items()
    # order = invoice.rebate_order
    # if order.agent_money < order.agents_invoice_sum + float(form.money.data):
    #    flash(u'新建打款发票失败，发票超过代理总金额!', 'danger')
    #    return redirect(url_for(redirect_endpoint, order_id=order.id))
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
            invoice.pay_money = form.money.data,
            invoice.invoice_type = form.invoice_type.data,
            invoice.invoice_num = form.invoice_num.data,
            invoice.creator = g.user
            invoice.create_time = datetime.date.today()
            invoice.add_time = form.add_time.data
            invoice.bool_invoice = form.bool_invoice.data
            invoice.save()
            flash(u'修改打款发票(%s)成功!' % form.company.data, 'success')
            invoice.rebate_order.add_comment(g.user, u"修改打款发票信息,%s" % (
                u'打款发票内容: %s; 发票金额: %s元; 发票号: %s' %
                (invoice.detail, str(invoice.money), invoice.invoice_num)), msg_channel=5)
    else:
        for k in form.errors:
            flash(u"修改打款发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for(redirect_endpoint, order_id=invoice.rebate_order.id))


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<invoice_id>/apply_pay', methods=['POST'])
def apply_pay(invoice_id):
    agent_invoice = searchAdRebateAgentInvoice.get(invoice_id)
    if not agent_invoice:
        abort(404)
    invoice_pay_ids = request.values.getlist('invoices')
    invoice_pays = searchAdAgentInvoicePay.gets(invoice_pay_ids)
    if not invoice_pays:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))
    to_users = agent_invoice.rebate_order.sales + \
        [agent_invoice.rebate_order.creator, g.user] + \
        agent_invoice.rebate_order.leaders
    to_emails = list(set(emails + [x.email for x in to_users]))
    if action == 2:
        action_msg = u'代理打款申请'
        for invoice in invoice_pays:
            invoice.pay_status = AGENT_INVOICE_STATUS_APPLY
            invoice.save()
            flash(u'[%s代理申请打款，打款金额: %s, 发票号: %s]  %s ' %
                  (invoice.agent_invoice.company, invoice.money,
                   invoice.agent_invoice.invoice_num, invoice.detail), 'success')

            invoice.agent_invoice.rebate_order.add_comment(g.user, u"%s,%s" % (
                action_msg, u'[%s代理申请打款，打款金额: %s, 发票号: %s]  %s ' %
                (invoice.agent_invoice.company, invoice.money,
                    invoice.agent_invoice.invoice_num, invoice.detail)), msg_channel=5)
        send_type = "saler"
    elif action == 3:
        action_msg = u'同意代理订单打款申请，请财务打款'
        to_emails += [k.email for k in User.finances()]
        for invoice in invoice_pays:
            invoice.pay_status = AGENT_INVOICE_STATUS_AGREE
            invoice.save()
            flash(u'[同意%s代理订单打款申请，打款金额: %s, 发票号: %s]  %s ' %
                  (invoice.agent_invoice.company, invoice.money,
                   invoice.agent_invoice.invoice_num, invoice.detail), 'success')

            invoice.agent_invoice.rebate_order.add_comment(g.user, u"%s,%s" % (
                action_msg, u'[%s代理同意打款，打款金额: %s, 发票号: %s]  %s ' %
                (invoice.agent_invoice.company, invoice.money,
                    invoice.agent_invoice.invoice_num, invoice.detail)), msg_channel=5)
        send_type = "finance"
    else:
        action_msg = u'消息提醒'

    apply_context = {"sender": g.user,
                     "title": action_msg,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "invoice": agent_invoice,
                     "send_type": send_type,
                     "invoice_pays": invoice_pays}
    agent_invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s 打款发票开具申请] 已发送邮件给 %s ' %
          (agent_invoice.rebate_order, ', '.join(to_emails)), 'info')
    return redirect(url_for('searchAd_saler_rebate_order_agent_invoice.invoice', invoice_id=invoice_id))


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<invoice_id>/apply', methods=['POST'])
def apply_invoice(invoice_id):
    invoice = searchAdRebateAgentInvoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoices_ids = request.values.getlist('invoices')
    invoices = searchAdRebateAgentInvoice.gets(invoices_ids)
    if not invoices:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))
    to_users = invoice.rebate_order.sales + \
        [invoice.rebate_order.creator, g.user] + \
        invoice.rebate_order.leaders
    to_emails = list(set(emails + [x.email for x in to_users]))

    send_type = "saler"
    if action == 2:
        invoice_status = AGENT_INVOICE_STATUS_APPLY
        action_msg = u'打款发票开具申请'
    if action != 10:
        for invoice in invoices:
            invoice.invoice_status = invoice_status
            invoice.save()
            flash(u'[%s 打款发票申请，发票金额: %s, 发票号: %s]  %s ' %
                  (invoice.company, invoice.money, invoice.invoice_num, action_msg), 'success')
            invoice.rebate_order.add_comment(g.user, u"%s,%s" % (
                action_msg, u'打款发票内容: %s; 发票金额: %s元; 发票号: %s' %
                (invoice.detail, str(invoice.money), invoice.invoice_num)), msg_channel=5)
    else:
        action_msg = u'消息提醒'

    apply_context = {"sender": g.user,
                     "title": action_msg,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": invoice.rebate_order,
                     "send_type": send_type,
                     "invoices": invoices}
    agent_invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s 打款发票开具申请] 已发送邮件给 %s ' %
          (invoice.rebate_order, ', '.join(to_emails)), 'info')
    return redirect(url_for("searchAd_saler_rebate_order_agent_invoice.index", order_id=invoice.rebate_order.id))


@searchAd_saler_rebate_order_agent_invoice_bp.route('/<agent_id>/tax_info', methods=['POST'])
def tax_info(agent_id):
    agent = searchAdAgent.get(agent_id)
    return jsonify(agent.tax_info)
