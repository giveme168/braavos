# -*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl, flash, g, current_app

from models.outsource import OutSourceTarget, OutSource
from models.client_order import ClientOrder
from models.order import Order
from models.user import User
from forms.outsource import OutSourceTargetForm, OutsourceForm
from libs.signals import outsource_contract_apply_signal

outsource_bp = Blueprint('outsource', __name__, template_folder='../templates/outsource')


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
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media():
        orders = list(ClientOrder.all())
    elif g.user.is_leader():
        orders = [o for o in ClientOrder.all() if g.user.location in o.locations]
    else:
        orders = ClientOrder.get_order_by_user(g.user)
    return tpl('client_orders.html', orders=orders)


@outsource_bp.route('/client_order/<order_id>/outsources', methods=['GET', 'POST'])
def client_outsources(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    new_outsource_form = OutsourceForm()
    new_outsource_form.medium_order.choices = [(mo.id, mo.medium.name) for mo in order.medium_orders]
    context = {'new_outsource_form': new_outsource_form,
               'order': order}
    return tpl('client_outsources.html', **context)


@outsource_bp.route('/new_outsource', methods=['POST'])
def new_outsource():
    form = OutsourceForm(request.form)
    outsource = OutSource.add(target=OutSourceTarget.get(form.target.data),
                              medium_order=Order.get(form.medium_order.data),
                              num=form.num.data,
                              type=form.type.data,
                              subtype=form.subtype.data,
                              remark=form.remark.data)
    flash(u'新建外包成功!', 'success')
    return redirect(outsource.info_path())


@outsource_bp.route('/outsource/<outsource_id>', methods=['POST'])
def outsource(outsource_id):
    outsource = OutSource.get(outsource_id)
    if not outsource:
        abort(404)
    form = OutsourceForm(request.form)
    outsource.target = OutSourceTarget.get(form.target.data)
    outsource.medium_order = Order.get(form.medium_order.data)
    outsource.num = form.num.data
    outsource.type = form.type.data
    outsource.subtype = form.subtype.data
    outsource.remark = form.remark.data
    outsource.save()
    flash(u'保存成功!', 'success')
    return redirect(outsource.info_path())


@outsource_bp.route('/outsource/<outsource_id>/status', methods=['POST'])
def outsource_status(outsource_id):
    outsource = OutSource.get(outsource_id)
    if not outsource:
        abort(404)
    action = int(request.values.get('action', 0))
    emails = request.values.getlist('email', [])
    msg = request.values.get('msg', '')
    orders = outsource.medium_order.client_orders
    to_users = [g.user]
    for order in orders:
        to_users += order.direct_sales + order.agent_sales + [order.creator] + order.leaders
    if action == 1:
        outsource.status = 1
        action_msg = u'申请审批'
    elif action == 10:
        outsource.status = 10
        action_msg = u'申请通过'
        to_users += User.contracts()
    outsource.save()
    flash(u'[%s] %s ' % (outsource.name, action_msg), 'success')
    to_emails = list(set(emails + [x.email for x in to_users]))
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "outsource": outsource}
    outsource_contract_apply_signal.send(current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s] 已发送邮件给 %s ' % (outsource.name, ', '.join(to_emails)), 'info')
    outsource.add_comment(g.user, u"%s \n\n %s" % (action_msg, msg))
    return redirect(outsource.info_path())
