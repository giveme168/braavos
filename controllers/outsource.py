# -*- coding: UTF-8 -*-
import datetime
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl, flash, g, current_app

from models.outsource import OutSourceTarget, OutSource, DoubanOutSource, MergerOutSource, MergerDoubanOutSource
from models.client_order import ClientOrder, CONTRACT_STATUS_CN
from models.order import Order
from models.douban_order import DoubanOrder
from models.user import User, TEAM_TYPE_OPERATER, TEAM_LOCATION_CN
from models.outsource import (OUTSOURCE_STATUS_NEW, OUTSOURCE_STATUS_APPLY_LEADER,
                              OUTSOURCE_STATUS_PASS, OUTSOURCE_STATUS_APPLY_MONEY,
                              OUTSOURCE_STATUS_EXCEED, INVOICE_RATE, OUTSOURCE_STATUS_PAIED)
from forms.outsource import OutSourceTargetForm, OutsourceForm, DoubanOutsourceForm, MergerOutSourceForm
from libs.signals import outsource_apply_signal, outsource_distribute_signal, merger_outsource_apply_signal

outsource_bp = Blueprint(
    'outsource', __name__, template_folder='../templates/outsource/')


ORDER_PAGE_NUM = 50


@outsource_bp.route('/client_orders_distribute', methods=['GET', 'POST'])
def client_orders_distribute():
    if request.method == 'POST':
        order_id = request.values.get('order_id', '')
        operator = request.values.get('operater_ids', '')
        order = Order.get(order_id)
        if operator:
            operater_users = User.gets(operator.split(','))
            order.operaters = operater_users
            to_emails = [k.email for k in operater_users]
        else:
            order.operaters = []
            to_emails = []
        order.save()
        if to_emails:
            apply_context = {"sender": g.user,
                             "to": to_emails + [g.user.email],
                             "action_msg": '',
                             "msg": '',
                             "order": order.client_order}
            outsource_distribute_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        return redirect(url_for('outsource.client_orders_distribute'))

    orders = [k for k in ClientOrder.all() if k.medium_orders]
    operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER)
    return display_orders(orders, 'client_orders_distribute.html', title=u"客户订单分配", operaters=operaters)


@outsource_bp.route('/douban_orders_distribute', methods=['GET', 'POST'])
def douban_orders_distribute():
    if request.method == 'POST':
        order_id = request.values.get('order_id', '')
        operator = request.values.get('operater_ids', '')
        order = DoubanOrder.get(order_id)
        if operator:
            operater_users = User.gets(operator.split(','))
            order.operaters = operater_users
            to_emails = [k.email for k in operater_users]
        else:
            order.operaters = []
            to_emails = []
        order.save()
        if to_emails:
            apply_context = {"sender": g.user,
                             "to": to_emails + [g.user.email],
                             "action_msg": '',
                             "msg": '',
                             "order": order}
            outsource_distribute_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        return redirect(url_for('outsource.douban_orders_distribute'))

    orders = DoubanOrder.all()
    operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER)
    return display_orders(orders, 'douban_orders_distribute.html', title=u"直签豆瓣订单分配", operaters=operaters)


def display_orders(orders, template, title, operaters):
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1
    sortby = request.args.get('sortby', '')
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    reverse = orderby != 'asc'
    page = int(request.args.get('p', 1))
    page = max(1, page)
    start = (page - 1) * ORDER_PAGE_NUM
    orders_len = len(orders)
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [o for o in orders if search_info in o.search_info]
    if sortby and orders_len and hasattr(orders[0], sortby):
        orders = sorted(
            orders, key=lambda x: getattr(x, sortby), reverse=reverse)
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    if 0 <= start < orders_len:
        orders = orders[start:min(start + ORDER_PAGE_NUM, orders_len)]
    else:
        orders = []
    return tpl(template, title=title, orders=orders,
               locations=select_locations, location_id=location_id,
               statuses=select_statuses, status_id=status_id,
               sortby=sortby, orderby=orderby,
               search_info=search_info, page=page, operaters=operaters)


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
        orders = [k for k in ClientOrder.all() if k.medium_orders]
    elif g.user.is_leader():
        orders = [
            o for o in ClientOrder.all() if g.user.location in o.locations and o.medium_orders]
    else:
        orders = [
            k for k in ClientOrder.get_order_by_user(g.user) if k.medium_orders]
    return display_orders(orders, 'client_orders.html', title=u"我的媒体外包", operaters=[])


@outsource_bp.route('/douban_orders', methods=['GET'])
def douban_orders():
    if any([g.user.is_super_leader(),
            g.user.is_operater_leader(),
            g.user.is_contract(),
            g.user.is_media()]):
        orders = list(DoubanOrder.all())
    elif g.user.is_leader():
        orders = [
            o for o in DoubanOrder.all() if g.user.location in o.locations]
    else:
        orders = DoubanOrder.get_order_by_user(g.user)
    return display_orders(orders, 'o_douban_orders.html', title=u"我的直签豆瓣外包", operaters=[])


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


@outsource_bp.route('/douban_order/<order_id>/outsources', methods=['GET', 'POST'])
def douban_outsources(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    new_outsource_form = DoubanOutsourceForm()
    new_outsource_form.douban_order.choices = [(order.id, order.name)]
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'new_outsource_form': new_outsource_form,
               'reminder_emails': reminder_emails,
               'order': order}
    return tpl('douban_outsources.html', **context)


@outsource_bp.route('/new_outsource', methods=['POST'])
def new_outsource():
    form = OutsourceForm(request.form)
    outsource = OutSource.add(target=OutSourceTarget.get(form.target.data),
                              medium_order=Order.get(form.medium_order.data),
                              num=form.num.data,
                              type=form.type.data,
                              subtype=form.subtype.data,
                              remark=form.remark.data,
                              invoice=True,
                              pay_num=form.num.data,)
    flash(u'新建外包成功!', 'success')
    outsource.client_order.add_comment(g.user,
                                       u"""新建外包:\n\r %s""" % outsource.name,
                                       msg_channel=2)
    return redirect(outsource.info_path())


@outsource_bp.route('/new_douban_outsource', methods=['POST'])
def new_douban_outsource():
    form = DoubanOutsourceForm(request.form)
    outsource = DoubanOutSource.add(target=OutSourceTarget.get(form.target.data),
                                    douban_order=DoubanOrder.get(
                                        form.douban_order.data),
                                    num=form.num.data,
                                    type=form.type.data,
                                    subtype=form.subtype.data,
                                    remark=form.remark.data,
                                    invoice=True,
                                    pay_num=form.num.data)
    flash(u'新建外包成功!', 'success')
    outsource.douban_order.add_comment(g.user,
                                       u"""新建外包:\n\r %s""" % outsource.name,
                                       msg_channel=2)
    return redirect(outsource.info_path())


@outsource_bp.route('/outsource/<outsource_id>', methods=['POST'])
def outsource(outsource_id):
    type = request.values.get('type', '')
    if type == 'douban':
        outsource = DoubanOutSource.get(outsource_id)
    else:
        outsource = OutSource.get(outsource_id)
    if not outsource:
        abort(404)
    if type == 'douban':
        form = DoubanOutsourceForm(request.form)
    else:
        form = OutsourceForm(request.form)

    outsource.target = OutSourceTarget.get(form.target.data)
    if type == 'douban':
        outsource.douban_order = DoubanOrder.get(form.douban_order.data)
    else:
        outsource.medium_order = Order.get(form.medium_order.data)
    outsource.num = form.num.data
    outsource.type = form.type.data
    outsource.subtype = form.subtype.data
    outsource.remark = form.remark.data
    outsource.invoice = True
    outsource.pay_num = form.num.data
    outsource.save()
    flash(u'保存成功!', 'success')
    if type == "douban":
        outsource.douban_order.add_comment(g.user,
                                           u"更新了外包:\n\r%s" % outsource.name,
                                           msg_channel=2)
    else:
        outsource.client_order.add_comment(g.user,
                                           u"更新了外包:\n\r%s" % outsource.name,
                                           msg_channel=2)
    if type == 'douban':
        order = outsource.douban_order
    else:
        order = outsource.medium_order.client_order

    if outsource.status not in [0, 4]:
        to_users = order.direct_sales + order.agent_sales + \
            [order.creator, g.user] + order.operater_users
        try:
            outsource_apply_user = User.outsource_leaders_email(
                order.agent_sales[0])
        except:
            outsource_apply_user = []

        if outsource.status in [1, 2, 5]:
            to_users_name = ','.join(
                [k.name for k in order.operater_users] + [k.name for k in order.agent_sales])
        elif outsource.status == 3:
            to_users += User.finances()
            to_users_name = ','.join(
                [k.name for k in User.finances()] + [k.name for k in order.operater_users])

        to_emails = list(
            set([x.email for x in to_users] + [k.email for k in outsource_apply_user]))
        title = u'【费用报备】%s-%s-%s' % (order.contract or u'无合同号', order.jiafang_name, u'修改外包信息')
        apply_context = {"sender": g.user,
                         "to": to_emails,
                         "action_msg": u'修改外包信息',
                         "msg": '',
                         "order": order,
                         "title": title,
                         "to_users": to_users_name,
                         "outsources": [outsource]}

        outsource_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
    return redirect(outsource.info_path())


@outsource_bp.route('/client_order/<order_id>/outsource_status', methods=['POST'])
def outsource_status(order_id):
    type = request.values.get('type', '')
    if type == 'douban':
        order = DoubanOrder.get(order_id)
    else:
        order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    outsource_ids = request.values.getlist('outsources')
    if type == 'douban':
        outsources = DoubanOutSource.gets(outsource_ids)
    else:
        outsources = OutSource.gets(outsource_ids)
    if not outsources:
        abort(403)
    action = int(request.values.get('action', 0))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')

    to_users = order.direct_sales + order.agent_sales + \
        [order.creator, g.user] + order.operater_users
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
        to_users_name = ','.join(
            [k.name for k in outsource_apply_user] + [k.name for k in order.operater_users])

    elif action == 1:
        next_status = OUTSOURCE_STATUS_PASS
        action_msg = u'审批通过'
        to_users_name = ','.join(
            [k.name for k in order.agent_sales] + [k.name for k in order.operater_users])
    elif action == 2:
        next_status = OUTSOURCE_STATUS_NEW
        action_msg = u'拒绝通过'
        to_users_name = ','.join(
            [k.name for k in order.agent_sales] + [k.name for k in order.operater_users])
    elif action == 3:
        next_status = OUTSOURCE_STATUS_APPLY_MONEY
        action_msg = u'申请打款'
        to_users_name = ','.join([k.name for k in User.operater_leaders()])
    else:
        action_msg = u'消息提醒'

    if action < 4:
        for outsource in outsources:
            outsource.status = next_status
            outsource.save()
    order.add_comment(g.user,
                      u"%s:\n\r%s\n\r%s" % (
                          action_msg, "\n\r".join([o.name for o in outsources]), msg),
                      msg_channel=2)
    to_emails = list(
        set(emails + [x.email for x in to_users] + [k.email for k in outsource_apply_user]))
    title = u'【费用报备】%s-%s-%s' % (order.contract or u'无合同号', order.jiafang_name, action_msg)
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order,
                     "title": title,
                     "to_users": to_users_name,
                     "outsources": outsources}

    outsource_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)

    flash(title, 'success')
    flash(u'已发送邮件给 %s ' % (', '.join(to_emails)), 'info')

    if type == 'douban':
        return redirect(url_for("outsource.douban_outsources", order_id=order.id))
    else:
        return redirect(url_for("outsource.client_outsources", order_id=order.id))


@outsource_bp.route('/merger_client_target', methods=['GET'])
def merger_client_target():
    targets = OutSourceTarget.all()
    return tpl('merger_client_target.html', targets=targets,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS)


@outsource_bp.route('/merger_douban_target', methods=['GET'])
def merger_douban_target():
    targets = OutSourceTarget.all()
    return tpl('merger_douban_target.html', targets=targets,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS)


@outsource_bp.route('/update_pay_num', methods=['POST'])
def update_pay_num():
    type = request.values.get('type', '')
    outsource_id = request.values.get('outsource_id')
    pay_num = request.values.get('update_pay_num', 0)
    if type == 'douban':
        outsource = DoubanOutSource.get(outsource_id)
    else:
        outsource = OutSource.get(outsource_id)
    outsource.pay_num = pay_num
    outsource.save()
    flash(u'修改实际付款金额:%s 成功' % (str(pay_num)), 'success')
    if type == 'douban':
        return redirect(url_for("outsource.merget_douban_target_info",
                                target_id=outsource.target.id, status=outsource.status))
    else:
        return redirect(url_for("outsource.merget_client_target_info",
                                target_id=outsource.target.id, status=outsource.status))


@outsource_bp.route('/merger_client_target/<target_id>/info/<status>', methods=['GET', 'POST'])
def merget_client_target_info(target_id, status):
    target = OutSourceTarget.get(target_id)
    if request.method == 'POST':
        form = MergerOutSourceForm(request.form)
        outsource_ids = request.values.getlist('outsources')
        outsources = OutSource.gets(outsource_ids)
        emails = request.values.getlist('email')
        msg = request.values.get('msg', '')
        for o in outsources:
            o.status = OUTSOURCE_STATUS_APPLY_MONEY
            o.create_time = datetime.date.today()
            o.save()

        merger_outsource = MergerOutSource.add(target=target,
                                               outsources=outsources,
                                               invoice=form.invoice.data,
                                               pay_num=form.pay_num.data,
                                               num=form.num.data,
                                               remark=form.remark.data,
                                               status=1)
        merger_outsource.save()
        flash(u'合并付款成功', 'success')
        title = u'【费用报备】%s' % (u'申请打款')
        apply_context = {"sender": g.user,
                         "to": [k.email for k in User.finances() +
                                User.super_leaders() + User.operater_leaders()] + emails,
                         "action_msg": u'申请打款',
                         "msg": msg,
                         "title": title,
                         "to_users": ','.join([k.name for k in User.finances()]),
                         "invoice": form.invoice.data,
                         "remark": form.remark.data,
                         "outsources": outsources}
        merger_outsource_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        flash(u'已发送邮件给 %s ' % (', '.join(apply_context['to'])), 'info')
        return redirect(url_for("outsource.merget_client_target_info", target_id=target_id, status=status))
        '''
        try:
            outsource_apply_user = User.outsource_leaders_email(
                order.agent_sales[0])
        except:
            outsource_apply_user = []

        to_emails = list(
            set(emails + [x.email for x in User.finances()] + [k.email for k in outsource_apply_user]))

        title = u'【费用报备】%s-%s-%s' % (order.contract or u'无合同号',
                                     order.jiafang_name, action_msg)
        apply_context = {"sender": g.user,
                         "to": to_emails,
                         "action_msg": u'申请打款',
                         "msg": msg,
                         "order": order,
                         "title": title,
                         "to_users": to_users_name,
                         "outsources": outsources}

        outsource_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        '''

    outsources = OutSource.get_outsources_by_target(target_id, status)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    form = MergerOutSourceForm(request.form)
    return tpl('merger_client_target_info.html', target=target, status=int(status),
               outsources=outsources, reminder_emails=reminder_emails,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS,
               form=form, INVOICE_RATE=INVOICE_RATE)


@outsource_bp.route('/merger_douban_target/<target_id>/info/<status>', methods=['GET', 'POST'])
def merget_douban_target_info(target_id, status):
    target = OutSourceTarget.get(target_id)
    if request.method == 'POST':
        form = MergerOutSourceForm(request.form)
        outsource_ids = request.values.getlist('outsources')
        outsources = DoubanOutSource.gets(outsource_ids)
        emails = request.values.getlist('email')
        msg = request.values.get('msg', '')
        for o in outsources:
            o.status = OUTSOURCE_STATUS_APPLY_MONEY
            o.create_time = datetime.date.today()
            o.save()

        merger_outsource = MergerDoubanOutSource.add(target=target,
                                                     outsources=outsources,
                                                     invoice=form.invoice.data,
                                                     pay_num=form.pay_num.data,
                                                     num=form.num.data,
                                                     remark=form.remark.data,
                                                     status=1)
        merger_outsource.save()
        flash(u'合并付款成功', 'success')
        title = u'【费用报备】%s' % (u'申请打款')
        apply_context = {"sender": g.user,
                         "to": [k.email for k in User.finances() +
                                User.super_leaders() + User.operater_leaders()] + emails,
                         "action_msg": u'申请打款',
                         "msg": msg,
                         "title": title,
                         "to_users": ','.join([k.name for k in User.finances()]),
                         "invoice": form.invoice.data,
                         "remark": form.remark.data,
                         "outsources": outsources}
        merger_outsource_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        flash(u'已发送邮件给 %s ' % (', '.join(apply_context['to'])), 'info')
        return redirect(url_for("outsource.merget_douban_target_info", target_id=target_id, status=status))
    outsources = DoubanOutSource.get_outsources_by_target(target_id, status)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    form = MergerOutSourceForm(request.form)
    return tpl('merger_douban_target_info.html', target=target, status=int(status),
               outsources=outsources, reminder_emails=reminder_emails,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS,
               form=form, INVOICE_RATE=INVOICE_RATE)
