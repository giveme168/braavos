# -*- coding: utf-8 -*-
from flask import request, redirect, Blueprint, url_for, flash, g, abort
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.invoice import Invoice, INVOICE_STATUS_NORMAL
from forms.invoice import InvoiceForm

saler_invoice_bp = Blueprint(
    'saler_invoice', __name__, template_folder='../../templates/saler')


@saler_invoice_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    new_invoice_form = InvoiceForm()
    new_invoice_form.client_order.choices = [(order.id, order.client.name)]
    new_invoice_form.company.data = order.agent.name
    new_invoice_form.bank.data = order.agent.bank
    new_invoice_form.bank_id.data = order.agent.bank_num
    new_invoice_form.address.data = order.agent.address
    new_invoice_form.phone.data = order.agent.phone_num
    return tpl('/saler/invoice/index.html', order=order, new_invoice_form=new_invoice_form)


@saler_invoice_bp.route('/<order_id>/new', methods=['POST'])
def new_invoice(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    form = InvoiceForm(request.form)
    form.client_order.choices = [(order.id, order.client.name)]
    if request.method == 'POST' and form.validate():
        if not form.tax_id.data:
            flash(u"新建发票失败，公司名称不能为空", 'danger')
        elif not form.detail.data:
            flash(u"新建发票失败，发票内容不能为空", 'danger')
        elif not form.money.data:
            flash(u"新建发票失败，发票金额不能为空", 'danger')
        else:
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
                                  creator=g.user)
            invoice.save()
            flash(u'新建发票(%s)成功!' % form.company.data, 'success')
    else:
        for k in form.errors:
            flash(u"新建发票失败，%s" % (form.errors[k][0]), 'danger')
    return redirect(url_for("saler_invoice.index", order_id=order_id))
