# -*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl, flash, g, current_app

from models.outsource import OutSourceTarget, OutSource
from models.client_order import ClientOrder
from models.order import Order
from models.user import User
from models.outsource import (OUTSOURCE_STATUS_NEW, OUTSOURCE_STATUS_APPLY_LEADER,
                              OUTSOURCE_STATUS_PASS, OUTSOURCE_STATUS_APPLY_MONEY,
                              OUTSOURCE_STATUS_EXCEED, INVOICE_RATE)
from forms.outsource import OutSourceTargetForm, OutsourceForm
from libs.signals import outsource_apply_signal

outsource_bp = Blueprint(
    'outsource', __name__, template_folder='../templates/outsource')


@outsource_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('outsource.client_orders'))


@outsource_bp.route('/targets', methods=['GET'])
def targets():
    targets = OutSourceTarget.all()
    return tpl('targets.html', targets=targets)


@outsource_bp.route('/new_target', methods=['GET', 'POST'])
def new_target():
    form = OutSourceTargetForm(request.form)
    if request.method == 'POST' and form.validate():
        target = OutSourceTarget.add(name=form.name.data,
                                     bank=form.bank.data,
                                     card=form.card.data,
                                     alipay=form.alipay.data,
                                     contract=form.contract.data,
                                     type=form.type.data,
                                     remark=form.remark.data)
        flash(u'新建外包收款方(%s)成功!' % target.name, 'success')
        return redirect(url_for("outsource.target_detail", target_id=target.id))
    return tpl('target.html', form=form, title=u"新建收款方")


@outsource_bp.route('/client/<target_id>', methods=['GET', 'POST'])
def target_detail(target_id):
    target = OutSourceTarget.get(target_id)
    if not target:
        abort(404)
    form = OutSourceTargetForm(request.form)
    if request.method == 'POST' and form.validate():
        target.name = form.name.data
        target.bank = form.bank.data
        target.card = form.card.data
        target.alipay = form.alipay.data
        target.contract = form.contract.data
        target.remark = form.remark.data
        target.type = form.type.data
        target.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = target.name
        form.bank.data = target.bank
        form.card.data = target.card
        form.alipay.data = target.alipay
        form.contract.data = target.contract
        form.remark.data = target.remark
        form.type.data = target.type
    return tpl('target.html', form=form, title=u"收款方-" + target.name)


@outsource_bp.route('/client_orders', methods=['GET'])
def client_orders():
    if any([g.user.is_super_leader(),
            g.user.is_operater_leader(),
            g.user.is_contract(),
            g.user.is_media()]):
        orders = list(ClientOrder.all())
    elif g.user.is_leader():
        orders = [
            o for o in ClientOrder.all() if g.user.location in o.locations]
    else:
        orders = ClientOrder.get_order_by_user(g.user)
    return tpl('client_orders.html', title=u"我的外包", orders=orders)


@outsource_bp.route('/apply_client_orders', methods=['GET'])
def apply_client_orders():
    orders = [o for o in ClientOrder.all() if o.get_outsources_by_status(1)]
    return tpl('client_orders.html', title=u"申请中的外包", orders=orders)


@outsource_bp.route('/client_order/<order_id>/outsources', methods=['GET', 'POST'])
def client_outsources(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    new_outsource_form = OutsourceForm()
    new_outsource_form.medium_order.choices = [
        (mo.id, mo.medium.name) for mo in order.medium_orders]
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'new_outsource_form': new_outsource_form,
               'reminder_emails': reminder_emails,
               'order': order}
    return tpl('client_outsources.html', **context)


@outsource_bp.route('/new_outsource', methods=['POST'])
def new_outsource():
    form = OutsourceForm(request.form)
    if form.invoice.data == 'True':
        pay_num = form.num.data
    else:
        pay_num = form.num.data * float(1 - INVOICE_RATE)
    outsource = OutSource.add(target=OutSourceTarget.get(form.target.data),
                              medium_order=Order.get(form.medium_order.data),
                              num=form.num.data,
                              type=form.type.data,
                              subtype=form.subtype.data,
                              remark=form.remark.data,
                              invoice=form.invoice.data,
                              pay_num=pay_num)
    flash(u'新建外包成功!', 'success')
    outsource.client_order.add_comment(g.user,
                                       u"""新建外包:\n\r %s""" % outsource.name,
                                       msg_channel=2)
    return redirect(outsource.info_path())


@outsource_bp.route('/outsource/<outsource_id>', methods=['POST'])
def outsource(outsource_id):
    outsource = OutSource.get(outsource_id)
    if not outsource:
        abort(404)
    form = OutsourceForm(request.form)
    if form.invoice.data == 'True':
        pay_num = form.num.data
    else:
        pay_num = form.num.data * float(1 - INVOICE_RATE)
    outsource.target = OutSourceTarget.get(form.target.data)
    outsource.medium_order = Order.get(form.medium_order.data)
    outsource.num = form.num.data
    outsource.type = form.type.data
    outsource.subtype = form.subtype.data
    outsource.remark = form.remark.data
    outsource.invoice = form.invoice.data
    outsource.pay_num = pay_num
    outsource.save()
    flash(u'保存成功!', 'success')
    outsource.client_order.add_comment(g.user,
                                       u"更新了外包:\n\r%s" % outsource.name,
                                       msg_channel=2)
    return redirect(outsource.info_path())


@outsource_bp.route('/client_order/<order_id>/outsource_status', methods=['POST'])
def outsource_status(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    outsource_ids = request.values.getlist('outsources')
    outsources = OutSource.gets(outsource_ids)
    if not outsources:
        abort(403)
    action = int(request.values.get('action', 0))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')

    to_users = order.direct_sales + order.agent_sales + \
        [order.creator, g.user] + User.operater_leaders()
    try:
        outsource_apply_user = User.outsource_leaders_email(
            order.agent_sales[0])
    except:
        outsource_apply_user = []
    outsource_percent = (
        sum([k.pay_num for k in outsources]) + order.outsources_sum) / order.money

    if action == 0:
        if outsource_percent >= 0.02:
            next_status = OUTSOURCE_STATUS_EXCEED
            action_msg = u'外包款超过2%，申请审批'
        else:
            next_status = OUTSOURCE_STATUS_APPLY_LEADER
            action_msg = u'申请审批'
    elif action == 1:
        next_status = OUTSOURCE_STATUS_PASS
        action_msg = u'审批通过'
    elif action == 2:
        next_status = OUTSOURCE_STATUS_NEW
        action_msg = u'拒绝通过'
    elif action == 3:
        next_status = OUTSOURCE_STATUS_APPLY_MONEY
        action_msg = u'申请打款'
        to_users += User.finances()
    else:
        action_msg = u'消息提醒'
    if action < 4:
        for outsource in outsources:
            outsource.status = next_status
            outsource.save()
    flash(u'[%s 外包流程] %s ' % (order.name, action_msg), 'success')
    order.add_comment(g.user,
                      u"%s:\n\r%s\n\r%s" % (
                          action_msg, "\n\r".join([o.name for o in outsources]), msg),
                      msg_channel=2)
    to_emails = list(
        set(emails + [x.email for x in to_users] + outsource_apply_user))
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order,
                     "outsources": outsources}
    outsource_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s 外包流程] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')
    return redirect(url_for("outsource.client_outsources", order_id=order.id))
