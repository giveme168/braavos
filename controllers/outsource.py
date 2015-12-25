# -*- coding: UTF-8 -*-
import datetime
from flask import Blueprint, request, redirect, abort, url_for, json
from flask import render_template as tpl, flash, g, current_app

from models.outsource import (OutSourceTarget, OutSource, DoubanOutSource, MergerPersonalOutSource,
                              MergerOutSource, MergerDoubanOutSource, OutSourceExecutiveReport,
                              MergerDoubanPersonalOutSource)
from models.client_order import ClientOrder, CONTRACT_STATUS_CN
from models.order import Order
from models.douban_order import DoubanOrder
from models.user import (User, TEAM_TYPE_OPERATER, TEAM_TYPE_OPERATER_LEADER, TEAM_LOCATION_CN,
                         TEAM_TYPE_LEADER, TEAM_LOCATION_HUANAN, TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG)
from models.outsource import (OUTSOURCE_STATUS_NEW, OUTSOURCE_STATUS_APPLY_LEADER,
                              OUTSOURCE_STATUS_PASS, OUTSOURCE_STATUS_APPLY_MONEY,
                              OUTSOURCE_STATUS_EXCEED, INVOICE_RATE, OUTSOURCE_STATUS_PAIED,
                              MERGER_OUTSOURCE_STATUS_APPLY, MERGER_OUTSOURCE_STATUS_APPLY_MONEY)
from forms.outsource import OutSourceTargetForm, OutsourceForm, DoubanOutsourceForm, MergerOutSourceForm
from libs.email_signals import outsource_distribute_signal, outsource_apply_signal, merger_outsource_apply_signal
from libs.paginator import Paginator

outsource_bp = Blueprint(
    'outsource', __name__, template_folder='../templates/outsource/')


ORDER_PAGE_NUM = 50


def _insert_executive_report(order, rtype=None):
    outsources = order.get_outsources_by_status(
        2) + order.get_outsources_by_status(4)
    if order.__tablename__ == 'bra_douban_order':
        otype = 2
    else:
        otype = 1
    if rtype == 'reload':
        for k in outsources:
            OutSourceExecutiveReport.query.filter_by(
                outsource_id=k.id, otype=otype).delete()
    for k in outsources:
        for i in k.pre_month_money():
            if not OutSourceExecutiveReport.query.filter_by(outsource_id=k.id,
                                                            otype=otype, month_day=i['month']).first():
                OutSourceExecutiveReport.add(target=k.target,
                                             outsource_id=k.id,
                                             otype=otype,
                                             type=k.type,
                                             subtype=k.subtype,
                                             invoice=k.invoice,
                                             num=i['num'],
                                             pay_num=i['pay_num'],
                                             create_time=datetime.datetime.now(),
                                             month_day=i['month'],
                                             days=i['days'])

    return


@outsource_bp.route('/order/<order_id>/executive_report', methods=['GET'])
def executive_report(order_id):
    otype = request.values.get('otype', 'ClientOrder')
    if otype == 'DoubanOrder':
        order = DoubanOrder.get(order_id)
    else:
        order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_admin():
        abort(402)
    _insert_executive_report(order, request.values.get('rtype', None))
    if otype == 'ClientOrder':
        return redirect(url_for("outsource.client_orders"))
    else:
        return redirect(url_for("outsource.douban_orders"))


@outsource_bp.route('/client_orders_distribute', methods=['GET', 'POST'])
def client_orders_distribute():
    if request.method == 'POST':
        order_id = request.values.get('order_id', '')
        operator = request.values.get('operater_ids', '')
        order = ClientOrder.get(order_id)
        if operator:
            operater_users = User.gets(operator.split(','))
            to_users = operater_users
            for k in order.medium_orders:
                k.operaters = operater_users
                k.save()
        else:
            for k in order.medium_orders:
                k.operaters = []
                k.save()
            to_users = []
        if to_users:
            context = {"to_users": to_users + [g.user],
                       "operater_users": operater_users,
                       "action_msg": u'分配执行人员',
                       "info": '',
                       "order": order}
            outsource_distribute_signal.send(
                current_app._get_current_object(), context=context)
        return redirect(url_for('outsource.client_orders_distribute'))

    orders = [k for k in ClientOrder.all() if k.medium_orders]
    operaters = User.gets_by_team_type(
        TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
    return display_orders(orders, 'client_orders_distribute.html', title=u"客户订单分配", operaters=operaters)


@outsource_bp.route('/douban_orders_distribute', methods=['GET', 'POST'])
def douban_orders_distribute():
    if request.method == 'POST':
        order_id = request.values.get('order_id', '')
        operator = request.values.get('operater_ids', '')
        order = DoubanOrder.get(order_id)
        if operator:
            operater_users = User.gets(operator.split(','))
            to_users = operater_users
            order.operaters = operater_users
        else:
            order.operaters = []
            to_users = []
        order.save()
        if to_users:
            context = {"to_users": to_users + [g.user],
                       "operater_users": operater_users,
                       "action_msg": u'分配执行人员',
                       "info": '',
                       "order": order}
            outsource_distribute_signal.send(
                current_app._get_current_object(), context=context)
        return redirect(url_for('outsource.douban_orders_distribute'))

    orders = DoubanOrder.all()
    operaters = User.gets_by_team_type(
        TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
    return display_orders(orders, 'douban_orders_distribute.html', title=u"直签豆瓣订单分配", operaters=operaters)


def display_orders(orders, template, title, operaters):
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    status = request.args.get('status', '')
    page = int(request.args.get('p', 1))

    if g.user.team.type == TEAM_TYPE_LEADER:
        status = 'apply'
        location_id = g.user.team.location

    # 盖新的查看内容
    if int(g.user.id) == 15:
        status = 'apply_upper'
        location_id = [TEAM_LOCATION_HUABEI, TEAM_LOCATION_HUADONG]

    # Oscar的查看内容
    if int(g.user.id) == 16:
        status = 'apply_upper'
        location_id = TEAM_LOCATION_HUANAN

    if isinstance(location_id, list):
        orders = [o for o in orders if len(
            set(location_id) & set(o.locations)) > 0]
    elif location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]

    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower() in o.search_info.lower()]

    if status == 'apply':
        orders = [o for o in orders if o.get_outsources_by_status(1)]
    if status == 'apply_upper':
        orders = [o for o in orders if o.get_outsources_by_status(5)]
    if status == 'pass':
        orders = [o for o in orders if o.get_outsources_by_status(2)]
    if status == 'money':
        orders = [o for o in orders if o.get_outsources_by_status(3)]
    if status == 'pay':
        orders = [o for o in orders if o.get_outsources_by_status(4)]

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
    return tpl(template, title=title, orders=orders,
               locations=select_locations, location_id=location_id,
               statuses=select_statuses, status_id=status_id,
               orderby=orderby or 'create_time', status=status,
               search_info=search_info, page=page, operaters=operaters,
               params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s' %
                      (orderby or 'create_time', search_info, location_id, status_id))


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
        if OutSourceTarget.query.filter_by(name=form.name.data).first():
            flash(u'新建外包收款方(%s)失败，已存在该收款方!' % form.name.data, 'danger')
            return redirect(url_for("outsource.new_target"))
        target = OutSourceTarget.add(name=form.name.data,
                                     bank=form.bank.data,
                                     card=form.card.data,
                                     alipay=form.alipay.data,
                                     contract=form.contract.data,
                                     type=form.type.data,
                                     otype=form.otype.data,
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
        if OutSourceTarget.query.filter_by(name=form.name.data).first() and target.name != form.name.data:
            flash(u'修改失败，已存在该收款方!', 'danger')
            return redirect(url_for("outsource.target_detail", target_id=target_id))
        target.name = form.name.data
        target.bank = form.bank.data
        target.card = form.card.data
        target.alipay = form.alipay.data
        target.contract = form.contract.data
        target.remark = form.remark.data
        target.type = form.type.data
        target.otype = form.otype.data
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
        form.otype.data = target.otype or 1
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
    order = Order.get(form.medium_order.data)
    try:
        int(form.num.data)
    except:
        flash(u'保存失败，金额必须为数字!', 'danger')
        return redirect(url_for("outsource.client_outsources", order_id=order.client_order.id))
    outsource = OutSource.add(target=OutSourceTarget.get(form.target.data),
                              medium_order=order,
                              num=form.num.data,
                              type=form.type.data,
                              subtype=form.subtype.data,
                              remark=form.remark.data,
                              invoice=False,
                              pay_num=form.num.data,)
    flash(u'新建外包成功!', 'success')
    outsource.client_order.add_comment(g.user,
                                       u"""新建外包:\n\r %s""" % outsource.name,
                                       msg_channel=2)
    return redirect(outsource.info_path())


@outsource_bp.route('/new_douban_outsource', methods=['POST'])
def new_douban_outsource():
    form = DoubanOutsourceForm(request.form)
    order = DoubanOrder.get(form.douban_order.data)
    try:
        int(form.num.data)
    except:
        flash(u'保存失败，金额必须为数字!', 'danger')
        return redirect(url_for("outsource.douban_outsources", order_id=order.id))
    outsource = DoubanOutSource.add(target=OutSourceTarget.get(form.target.data),
                                    douban_order=order,
                                    num=form.num.data,
                                    type=form.type.data,
                                    subtype=form.subtype.data,
                                    remark=form.remark.data,
                                    invoice=False,
                                    pay_num=form.num.data)
    flash(u'新建外包成功!', 'success')
    outsource.douban_order.add_comment(g.user,
                                       u"""新建外包:\n\r %s""" % outsource.name,
                                       msg_channel=2)
    return redirect(outsource.info_path())


@outsource_bp.route('/outsource/<outsource_id>/delete', methods=['GET'])
def outsource_delete(outsource_id):
    type = request.values.get('type', '')
    if type == 'douban':
        outsource = DoubanOutSource.get(outsource_id)
    else:
        outsource = OutSource.get(outsource_id)

    if type == "douban":
        outsource.douban_order.add_comment(g.user,
                                           u"删除了外包:\n\r%s" % outsource.name,
                                           msg_channel=2)
    else:
        outsource.client_order.add_comment(g.user,
                                           u"删除了外包:\n\r%s" % outsource.name,
                                           msg_channel=2)
    url = outsource.info_path()
    outsource.delete()
    return redirect(url)


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
    try:
        int(form.num.data)
    except:
        flash(u'保存失败，金额必须为数字!', 'danger')
        return redirect(outsource.info_path())
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
            current_app._get_current_object(), context=apply_context)
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

    action = int(request.values.get('action', 0))
    # emails = request.values.getlist('email')
    msg = request.values.get('msg', '')

    to_users = order.direct_sales + order.agent_sales + \
        [order.creator, g.user] + order.operater_users
    try:
        outsource_apply_user = User.outsource_leaders_email(
            (order.agent_sales + order.direct_sales)[0])
    except:
        outsource_apply_user = []
    outsources_ids = set(outsource_ids) | set(
        [str(k.id) for k in order.apply_outsources()])
    if type == 'douban':
        total_outsources = DoubanOutSource.gets(outsources_ids)
        outsources = DoubanOutSource.gets(outsource_ids)
    else:
        total_outsources = OutSource.gets(outsources_ids)
        outsources = OutSource.gets(outsource_ids)
    if not outsources:
        abort(403)

    if order.money:
        outsource_percent = sum(
            [k.pay_num for k in total_outsources]) / float(order.money)
    else:
        outsource_percent = sum([k.pay_num for k in total_outsources]) / 1

    if action == 0:
        if outsource_percent >= 0.02:
            next_status = OUTSOURCE_STATUS_EXCEED
            action_msg = u'外包费用超过2%，申请审批'
        else:
            next_status = OUTSOURCE_STATUS_APPLY_LEADER
            action_msg = u'外包费用申请审批'
        # to_users_name = ','.join(
        #     [k.name for k in outsource_apply_user] + [k.name for k in order.operater_users])

    elif action == 1:
        next_status = OUTSOURCE_STATUS_PASS
        action_msg = u'外包费用审批通过'
        # to_users_name = ','.join(
        #     [k.name for k in order.agent_sales] + [k.name for k in order.operater_users])
    elif action == 2:
        next_status = OUTSOURCE_STATUS_NEW
        action_msg = u'外包费用拒绝通过'
        # to_users_name = ','.join(
        #     [k.name for k in order.agent_sales] + [k.name for k in order.operater_users])
    elif action == 3:
        next_status = OUTSOURCE_STATUS_APPLY_MONEY
        action_msg = u'外包费用申请打款'
        # to_users_name = ','.join([k.name for k in User.operater_leaders()])
    elif action == 100:
        # to_users_name = ','.join([k.name for k in outsource_apply_user] + [k.name for k in order.operater_users])
        outsources_json = json.loads(
            request.values.get('outsource_json', '[]'))
        outsources = []
        # 先修改外包金额
        for k in outsources_json:
            if type == 'douban':
                outsource = DoubanOutSource.get(k['id'])
            else:
                outsource = OutSource.get(k['id'])
            outsource.num = k['num']
            outsource.target = OutSourceTarget.get(k['target'])
            outsource.type = k['type']
            outsource.subtype = k['subtype']
            outsource.remark = k['remark']
            outsource.pay_num = k['num']
            # outsource.status = next_status
            outsource.save()
            outsources.append(outsource)
        # 根据修改后的金额，计算是否超过占比
        outsource_percent = float(order.outsources_percent) / 100
        if outsource_percent >= 0.02:
            action_msg = u'外包费用超过2%，修改并申请审批'
            next_status = OUTSOURCE_STATUS_EXCEED
        else:
            action_msg = u'外包费用修改并重新申请审批'
            next_status = OUTSOURCE_STATUS_APPLY_LEADER
        for k in outsources_json:
            if type == 'douban':
                outsource = DoubanOutSource.get(k['id'])
            else:
                outsource = OutSource.get(k['id'])
            outsource.status = next_status
            outsource.save()
    else:
        action_msg = u'外包费用消息提醒'

    if action < 4:
        for outsource in outsources:
            outsource.status = next_status
            outsource.save()
        if action == 1:
            _insert_executive_report(order, rtype='reload')
    order.add_comment(g.user,
                      u"%s:\n\r%s\n\r%s" % (
                          action_msg, "\n\r".join([o.name for o in outsources]), msg),
                      msg_channel=2)
    # to_emails = list(set(emails + [x.email for x in to_users] + [k.email for k in outsource_apply_user]))
    apply_context = {"to_users": to_users + outsource_apply_user,
                     "outsource_apply_user": outsource_apply_user,
                     "action_msg": action_msg,
                     "info": msg,
                     "order": order,
                     "action": action,
                     "outsource_percent": outsource_percent,
                     "outsources": outsources}

    outsource_apply_signal.send(
        current_app._get_current_object(), context=apply_context)
    if type == 'douban':
        return redirect(url_for("outsource.douban_outsources", order_id=order.id))
    else:
        return redirect(url_for("outsource.client_outsources", order_id=order.id))


@outsource_bp.route('/merger_client_target', methods=['GET'])
def merger_client_target():
    targets = [k for k in OutSourceTarget.all() if k.otype in [1, None]]
    personal_targets = [k for k in OutSourceTarget.all() if k.otype == 2]
    return tpl('merger_client_target.html', targets=targets, personal_targets=personal_targets,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS)


@outsource_bp.route('/merger_douban_target', methods=['GET'])
def merger_douban_target():
    targets = [k for k in OutSourceTarget.all() if k.otype in [1, None]]
    personal_targets = [k for k in OutSourceTarget.all() if k.otype == 2]
    return tpl('merger_douban_target.html', targets=targets, personal_targets=personal_targets,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS)


@outsource_bp.route('/update_personal_pay_num', methods=['POST'])
def update_personal_pay_num():
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
        return redirect(url_for("outsource.merget_douban_target_personal_info"))
    else:
        return redirect(url_for("outsource.merget_client_target_personal_info"))


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


@outsource_bp.route('/merger_client_target/<target_id>/apply', methods=['GET', 'POST'])
def merget_client_target_apply(target_id):
    action = int(request.values.get('action', 1))
    outsource_ids = request.values.getlist('outsources')
    if int(target_id) == 0:
        merger_clients = MergerPersonalOutSource.gets(outsource_ids)
    else:
        merger_clients = MergerOutSource.gets(outsource_ids)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    if action == 1:
        sub_title = u"申请外包合并打款"
    elif action == -1:
        for k in merger_clients:
            for o in k.outsources:
                o.status = OUTSOURCE_STATUS_PASS
                o.save()
        sub_title = u"驳回外包合并打款"
    elif action == 2:
        sub_title = u'批准外包合并打款'
        for k in merger_clients:
            k.status = MERGER_OUTSOURCE_STATUS_APPLY_MONEY
            k.save()

    title = u'【费用报备】%s' % (sub_title)
    for k in merger_clients:
        apply_context = {"sender": g.user,
                         "to": emails,
                         "msg": msg,
                         "title": title,
                         "action": action,
                         "merger_outsource": k}
        merger_outsource_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        if action == -1:
            k.delete()
    flash(sub_title, 'success')
    if int(target_id) == 0:
        return redirect(url_for("outsource.merget_client_target_personal_info"))
    return redirect(url_for("outsource.merget_client_target_info", target_id=target_id))


@outsource_bp.route('/merger_douban_target/personal/info', methods=['GET', 'POST'])
def merget_douban_target_personal_info():
    if request.method == 'POST':
        outsource_ids = request.values.getlist('outsources')
        outsources = DoubanOutSource.gets(outsource_ids)
        emails = request.values.getlist('email')
        msg = request.values.get('msg', '')
        merger_outsources = []
        for o in outsources:
            o.status = OUTSOURCE_STATUS_APPLY_MONEY
            o.create_time = datetime.date.today()
            o.save()
        merger_outsource = MergerDoubanPersonalOutSource.add(outsources=outsources,
                                                             invoice=request.values.get(
                                                                 'invoice', ''),
                                                             pay_num=request.values.get(
                                                                 'pay_num', 0),
                                                             num=request.values.get(
                                                                 'num', 0),
                                                             remark=request.values.get(
                                                                 'remark', ''),
                                                             status=1)
        merger_outsource.save()
        merger_outsources.append(merger_outsource)
        flash(u'合并付款申请成功', 'success')
        title = u'【费用报备】%s' % (u'合并付款申请审批')
        for k in merger_outsources:
            apply_context = {"sender": g.user,
                             "to": emails,
                             "msg": msg,
                             "title": title,
                             "action": -1,
                             "merger_outsource": k}
            merger_outsource_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        return redirect(url_for("outsource.merget_douban_target_personal_info"))
    apply_outsources = DoubanOutSource.get_personal_outsources(2)
    # 审核中的合并付款
    apply_merger_outsources = MergerDoubanPersonalOutSource.get_outsource_by_status(
        MERGER_OUTSOURCE_STATUS_APPLY)
    m_outsources = []
    for k in apply_merger_outsources:
        m_outsources += k.outsources
    apply_money_outsources = [
        k for k in DoubanOutSource.get_personal_outsources(3) if k not in m_outsources]

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    form = MergerOutSourceForm(request.form)
    return tpl('merger_douban_target_personal_info.html',
               apply_outsources=apply_outsources, reminder_emails=reminder_emails,
               apply_merger_outsources=apply_merger_outsources,
               apply_money_outsources=apply_money_outsources,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS,
               form=form, INVOICE_RATE=INVOICE_RATE)


@outsource_bp.route('/merger_client_target/personal/info', methods=['GET', 'POST'])
def merget_client_target_personal_info():
    if request.method == 'POST':
        outsource_ids = request.values.getlist('outsources')
        outsources = OutSource.gets(outsource_ids)
        emails = request.values.getlist('email')
        msg = request.values.get('msg', '')
        merger_outsources = []
        for o in outsources:
            o.status = OUTSOURCE_STATUS_APPLY_MONEY
            o.create_time = datetime.date.today()
            o.save()
        merger_outsource = MergerPersonalOutSource.add(outsources=outsources,
                                                       invoice=request.values.get(
                                                           'invoice', ''),
                                                       pay_num=request.values.get(
                                                           'pay_num', 0),
                                                       num=request.values.get(
                                                           'num', 0),
                                                       remark=request.values.get(
                                                           'remark', ''),
                                                       status=1)
        merger_outsource.save()
        merger_outsources.append(merger_outsource)
        flash(u'合并付款申请成功', 'success')
        title = u'【费用报备】%s' % (u'合并付款申请审批')
        for k in merger_outsources:
            apply_context = {"sender": g.user,
                             "to": emails,
                             "msg": msg,
                             "title": title,
                             "action": -1,
                             "merger_outsource": k}
            merger_outsource_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        return redirect(url_for("outsource.merget_client_target_personal_info"))
    apply_outsources = OutSource.get_personal_outsources(2)
    # 审核中的合并付款
    apply_merger_outsources = MergerPersonalOutSource.get_outsource_by_status(
        MERGER_OUTSOURCE_STATUS_APPLY)
    m_outsources = []
    for k in apply_merger_outsources:
        m_outsources += k.outsources
    apply_money_outsources = [
        k for k in OutSource.get_personal_outsources(3) if k not in m_outsources]

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    form = MergerOutSourceForm(request.form)
    return tpl('merger_client_target_personal_info.html',
               apply_outsources=apply_outsources, reminder_emails=reminder_emails,
               apply_merger_outsources=apply_merger_outsources,
               apply_money_outsources=apply_money_outsources,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS,
               form=form, INVOICE_RATE=INVOICE_RATE)


@outsource_bp.route('/merger_client_target/<target_id>/info', methods=['GET', 'POST'])
def merget_client_target_info(target_id):
    target = OutSourceTarget.get(target_id)
    if request.method == 'POST':
        form = MergerOutSourceForm(request.form)
        outsource_ids = request.values.getlist('outsources')
        outsources = OutSource.gets(outsource_ids)
        emails = request.values.getlist('email')
        msg = request.values.get('msg', '')
        action = int(request.values.get('action', 1))
        merger_outsources = []
        if action == 1:
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
            merger_outsources.append(merger_outsource)
        elif action == 2:
            for o in outsources:
                o.status = OUTSOURCE_STATUS_APPLY_MONEY
                o.create_time = datetime.date.today()
                o.save()
                merger_outsource = MergerOutSource.add(target=target,
                                                       outsources=[o],
                                                       invoice=False,
                                                       pay_num=o.pay_num,
                                                       num=o.pay_num,
                                                       remark=o.remark,
                                                       status=1)
                merger_outsources.append(merger_outsource)
        flash(u'合并付款申请成功', 'success')
        title = u'【费用报备】%s' % (u'合并付款申请审批')
        for k in merger_outsources:
            apply_context = {"sender": g.user,
                             "to": emails,
                             "msg": msg,
                             "title": title,
                             "action": 1,
                             "merger_outsource": k}
            merger_outsource_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        return redirect(url_for("outsource.merget_client_target_info", target_id=target_id))

    apply_outsources = OutSource.get_outsources_by_target(target_id, 2)
    apply_money_outsources = OutSource.get_outsources_by_target(target_id, 3)
    paid_outsources = OutSource.get_outsources_by_target(target_id, 4)
    apply_merger_outsources = MergerOutSource.get_outsources_by_status(
        MERGER_OUTSOURCE_STATUS_APPLY, target_id=target_id)

    # 在流程中的合并付款中的外包项不用出现再正在付款中
    m_outsources = []
    for k in apply_merger_outsources:
        m_outsources += k.outsources
    apply_money_outsources = [k for k in OutSource.get_outsources_by_target(
        target_id, 3) if k not in m_outsources]
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    form = MergerOutSourceForm(request.form)
    return tpl('merger_client_target_info.html', target=target,
               apply_outsources=apply_outsources, reminder_emails=reminder_emails,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS,
               form=form, INVOICE_RATE=INVOICE_RATE,
               apply_merger_outsources=apply_merger_outsources,
               apply_money_outsources=apply_money_outsources,
               paid_outsources=paid_outsources)


@outsource_bp.route('/merget_douban_target_apply/<target_id>/apply', methods=['GET', 'POST'])
def merget_douban_target_apply(target_id):
    action = int(request.values.get('action', 1))
    outsource_ids = request.values.getlist('outsources')
    if int(target_id) == 0:
        merger_clients = MergerDoubanPersonalOutSource.gets(outsource_ids)
    else:
        merger_clients = MergerDoubanOutSource.gets(outsource_ids)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    if action == 1:
        sub_title = u"申请外包打款审批"
    elif action == -1:
        for k in merger_clients:
            for o in k.outsources:
                o.status = OUTSOURCE_STATUS_PASS
                o.save()
        sub_title = u"驳回外包打款"
    elif action == 2:
        sub_title = u'批准外包打款'
        for k in merger_clients:
            k.status = MERGER_OUTSOURCE_STATUS_APPLY_MONEY
            k.save()
    for k in merger_clients:
        title = u'【费用报备】%s' % (sub_title)
        apply_context = {"sender": g.user,
                         "to": emails,
                         "msg": msg,
                         "title": title,
                         "action": action,
                         "merger_outsource": k}
        merger_outsource_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        if action == -1:
            k.delete()
    flash(sub_title, 'success')
    if int(target_id) == 0:
        return redirect(url_for("outsource.merget_douban_target_personal_info"))
    return redirect(url_for("outsource.merget_douban_target_info", target_id=target_id))


@outsource_bp.route('/merger_douban_target/<target_id>/info', methods=['GET', 'POST'])
def merget_douban_target_info(target_id):
    target = OutSourceTarget.get(target_id)
    if request.method == 'POST':
        form = MergerOutSourceForm(request.form)
        outsource_ids = request.values.getlist('outsources')
        outsources = DoubanOutSource.gets(outsource_ids)
        emails = request.values.getlist('email')
        msg = request.values.get('msg', '')
        action = int(request.values.get('action', 1))
        merger_outsources = []
        if action == 1:
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
            merger_outsources.append(merger_outsource)
        elif action == 2:
            for o in outsources:
                o.status = OUTSOURCE_STATUS_APPLY_MONEY
                o.create_time = datetime.date.today()
                o.save()
                merger_outsource = MergerDoubanOutSource.add(target=target,
                                                             outsources=[o],
                                                             invoice=False,
                                                             pay_num=o.pay_num,
                                                             num=o.pay_num,
                                                             remark=o.remark,
                                                             status=1)
                merger_outsource.save()
                merger_outsources.append(merger_outsource)
        flash(u'合并付款申请成功', 'success')
        title = u'【费用报备】%s' % (u'合并付款申请审批')
        for k in merger_outsources:
            apply_context = {"sender": g.user,
                             "to": emails,
                             "msg": msg,
                             "title": title,
                             "action": 1,
                             "merger_outsource": k}
            merger_outsource_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        return redirect(url_for("outsource.merget_douban_target_info", target_id=target_id))
    apply_outsources = DoubanOutSource.get_outsources_by_target(target_id, 2)
    paid_outsources = DoubanOutSource.get_outsources_by_target(target_id, 4)
    apply_merger_outsources = MergerDoubanOutSource.get_outsources_by_status(
        MERGER_OUTSOURCE_STATUS_APPLY, target_id=target_id)
    # 在流程中的合并付款中的外包项不用出现再正在付款中
    m_outsources = []
    for k in apply_merger_outsources:
        m_outsources += k.outsources
    apply_money_outsources = [k for k in DoubanOutSource.get_outsources_by_target(target_id, 3)
                              if k not in m_outsources]

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    form = MergerOutSourceForm(request.form)
    return tpl('merger_douban_target_info.html', target=target, reminder_emails=reminder_emails,
               OUTSOURCE_STATUS_APPLY_MONEY=OUTSOURCE_STATUS_APPLY_MONEY,
               OUTSOURCE_STATUS_PAIED=OUTSOURCE_STATUS_PAIED,
               OUTSOURCE_STATUS_PASS=OUTSOURCE_STATUS_PASS,
               form=form, INVOICE_RATE=INVOICE_RATE,
               apply_merger_outsources=apply_merger_outsources,
               apply_money_outsources=apply_money_outsources,
               paid_outsources=paid_outsources, apply_outsources=apply_outsources)
