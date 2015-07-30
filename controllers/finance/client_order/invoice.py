# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.user import User, TEAM_LOCATION_CN
from models.client_order import ClientOrder, CONTRACT_STATUS_CN
from models.invoice import (Invoice, INVOICE_STATUS_CN,
                            INVOICE_TYPE_CN, INVOICE_STATUS_PASS,
                            INVOICE_STATUS_APPLYPASS)
from libs.signals import invoice_apply_signal
from libs.paginator import Paginator
from forms.invoice import InvoiceForm
from controllers.finance.helpers.invoice_helpers import write_excel
from controllers.tools import get_download_response


finance_client_order_invoice_bp = Blueprint(
    'finance_client_order_invoice', __name__, template_folder='../../templates/finance/client_order')


ORDER_PAGE_NUM = 50


@finance_client_order_invoice_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = set([
        invoice.client_order for invoice in Invoice.get_invoices_status(INVOICE_STATUS_APPLYPASS)])
    return tpl('/finance/client_order/invoice/index.html', orders=orders)


@finance_client_order_invoice_bp.route('/pass', methods=['GET'])
def index_pass():
    if not g.user.is_finance():
        abort(404)
    orders = list(ClientOrder.all())
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
        orders = set([invoice.client_order for invoice in Invoice.get_invoices_status(
            INVOICE_STATUS_PASS)])
        xls = write_excel(list(orders))
        response = get_download_response(
            xls, ("%s-%s.xls" % (u"申请过的发票信息", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8'))
        return response
    return tpl('/finance/client_order/invoice/index_pass.html', orders=orders, locations=select_locations,
               location_id=location_id, statuses=select_statuses, orderby=orderby,
               now_date=datetime.date.today(), search_info=search_info, page=page,
               params='&orderby=%s&searchinfo=%s&selected_location=%s' %
                      (orderby, search_info, location_id))


@finance_client_order_invoice_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    if not g.user.is_finance():
        abort(404)
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
    new_invoice_form = InvoiceForm()
    new_invoice_form.client_order.choices = [(order.id, order.client.name)]
    new_invoice_form.company.data = order.agent.name
    new_invoice_form.bank.data = order.agent.bank
    new_invoice_form.bank_id.data = order.agent.bank_num
    new_invoice_form.address.data = order.agent.address
    new_invoice_form.phone.data = order.agent.phone_num
    new_invoice_form.tax_id.data = order.agent.tax_num
    new_invoice_form.back_time.data = datetime.date.today()
    return tpl('/finance/client_order/invoice/info.html', order=order,
               invoices_data=invoices_data, INVOICE_STATUS_CN=INVOICE_STATUS_CN,
               reminder_emails=reminder_emails, INVOICE_TYPE_CN=INVOICE_TYPE_CN,
               new_invoice_form=new_invoice_form)


@finance_client_order_invoice_bp.route('/<order_id>/order/new', methods=['POST'])
def new_invoice(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    form = InvoiceForm(request.form)
    form.client_order.choices = [(order.id, order.client.name)]
    if request.method == 'POST' and form.validate():
        if int(form.money.data) > (int(order.money) - int(order.invoice_apply_sum) - int(order.invoice_pass_sum)):
            flash(u"新建发票失败，您申请的发票超过了合同总额", 'danger')
            return redirect(url_for("finance_client_order_invoice.info", order_id=order_id))
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
                              creator=g.user,
                              invoice_status=0,
                              invoice_num=request.values.get(
                                  'new_invoice_num', ''),
                              back_time=form.back_time.data)
        invoice.save()
        flash(u'开发票(%s)成功!' % form.company.data, 'success')
        order.add_comment(g.user, u"已开发票信息：%s" % (
            u'发票内容: %s; 发票金额: %s元' % (invoice.detail, str(invoice.money))), msg_channel=1)
    else:
        for k in form.errors:
            flash(u"新建发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("finance_client_order_invoice.info", order_id=order.id))


@finance_client_order_invoice_bp.route('/<invoice_id>/update', methods=['POST'])
def update_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
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
            flash(u"修改发票失败，公司名称不能为空", 'danger')
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
                u'发票内容: %s; 发票号: %s; 发票金额: %s元' % (invoice.detail, invoice_num, str(invoice.money))), msg_channel=1)
    return redirect(url_for("finance_client_order_invoice.info", order_id=invoice.client_order.id))


@finance_client_order_invoice_bp.route('/<invoice_id>/invoice_num', methods=['POST'])
def invoice_num(invoice_id):
    if not g.user.is_finance():
        abort(404)
    invoice = Invoice.get(invoice_id)
    if not invoice:
        abort(404)
    invoice_num = request.values.get('invoice_num', '')
    invoice.invoice_num = invoice_num
    invoice.save()
    flash(u'保存成功!', 'success')
    invoice.client_order.add_comment(
        g.user, u"%s" % (u'更新了发票号: %s;' % (invoice.invoice_num)), msg_channel=1)
    return redirect(url_for("finance_client_order_invoice.info", order_id=invoice.client_order.id))


@finance_client_order_invoice_bp.route('/<invoice_id>/pass', methods=['POST'])
def pass_invoice(invoice_id):
    if not g.user.is_finance():
        abort(404)
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
                     "title": action_msg,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": invoice.client_order,
                     "send_type": "saler",
                     "invoices": invoices,
                     "url": invoice.client_order.finance_invoice_path()}
    invoice_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s 发票已开] 已发送邮件给 %s ' %
          (invoice.client_order, ', '.join(to_emails)), 'info')
    return redirect(url_for("finance_client_order_invoice.info", order_id=invoice.client_order.id))


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
