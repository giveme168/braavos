# -*- coding: utf-8 -*-
import datetime
from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.user import TEAM_LOCATION_CN
from models.client_order import ClientOrder, CONTRACT_STATUS_CN
from models.invoice import (MediumInvoice, INVOICE_TYPE_CN, MEDIUM_INVOICE_STATUS_CN, MEDIUM_INVOICE_STATUS_PASS,
                            MediumInvoicePay)
from forms.invoice import MediumInvoiceForm
from models.user import User
from libs.signals import medium_invoice_apply_signal
from libs.paginator import Paginator
from controllers.saler.client_order.medium_invoice import (new_invoice as _new_invoice,
                                                           update_invoice as _update_invoice, get_invoice_from)


finance_client_order_medium_pay_bp = Blueprint(
    'finance_client_order_medium_pay', __name__, template_folder='../../templates/finance/client_order')
ORDER_PAGE_NUM = 50


@finance_client_order_medium_pay_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = list(ClientOrder.all())
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1

    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    # page = max(1, page)
    # start = (page - 1) * ORDER_PAGE_NUM
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
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
    return tpl('/finance/client_order/medium_pay/index.html', orders=orders, title=u'申请中的媒体打款',
               locations=select_locations, location_id=location_id,
               statuses=select_statuses, status_id=status_id,
               orderby=orderby, now_date=datetime.date.today(),
               search_info=search_info, page=page,
               params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s' %
                      (orderby, search_info, location_id, status_id))


@finance_client_order_medium_pay_bp.route('/pass', methods=['GET'])
def index_pass():
    if not g.user.is_finance():
        abort(404)
    orders = set([
        invoicepay.medium_invoice.client_order for invoicepay in
        MediumInvoicePay.get_medium_invoices_status(MEDIUM_INVOICE_STATUS_PASS)])
    return tpl('/finance/client_order/medium_pay/index.html', orders=orders, title=u'已打的款媒体信息')


@finance_client_order_medium_pay_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    if not g.user.is_finance():
        abort(404)
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    invoices = MediumInvoice.query.filter_by(client_order=order)
    reminder_emails = [(u.id, u.name) for u in User.all_active()]
    new_invoice_form = MediumInvoiceForm()
    new_invoice_form.client_order.choices = [(order.id, order.client.name)]
    new_invoice_form.medium.choices = [(k.id, k.name)for k in order.mediums]
    new_invoice_form.add_time.data = datetime.date.today()
    return tpl('/finance/client_order/medium_pay/info.html', order=order, invoices=invoices,
               new_invoice_form=new_invoice_form, reminder_emails=reminder_emails,
               MEDIUM_INVOICE_STATUS_CN=MEDIUM_INVOICE_STATUS_CN, INVOICE_TYPE_CN=INVOICE_TYPE_CN)


@finance_client_order_medium_pay_bp.route('/<invoice_id>/pay_info', methods=['GET'])
def pay_info(invoice_id):
    if not g.user.is_finance():
        abort(404)
    invoice = MediumInvoice.get(invoice_id)
    form = get_invoice_from(invoice)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/client_order/medium_pay/pay_info.html',
               form=form, invoice=invoice, reminder_emails=reminder_emails,
               INVOICE_TYPE_CN=INVOICE_TYPE_CN)


@finance_client_order_medium_pay_bp.route('/<invoice_id>/pay_num', methods=['POST'])
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
    return redirect(url_for("finance_client_order_medium_pay.info", order_id=invoice.client_order.id))


@finance_client_order_medium_pay_bp.route('/<invoice_id>/pass', methods=['POST'])
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
    return redirect(url_for("finance_client_order_medium_pay.pay_info", invoice_id=invoice_id))


@finance_client_order_medium_pay_bp.route('/<order_id>/order/new', methods=['POST'])
def new_invoice(order_id, redirect_endpoint='finance_client_order_medium_pay.info'):
    return _new_invoice(order_id, redirect_endpoint)


@finance_client_order_medium_pay_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id, redirect_endpoint='finance_client_order_medium_pay.info'):
    return _update_invoice(invoice_id, redirect_endpoint)
