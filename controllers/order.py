# -*- coding: utf-8 -*-
import StringIO
import mimetypes
from werkzeug.datastructures import Headers
from datetime import datetime, timedelta

from flask import Blueprint, request, redirect, abort, url_for, g, Response
from flask import render_template as tpl, json, jsonify, flash

from forms.order import (ClientOrderForm, MediumOrderForm,
                         FrameworkOrderForm, DoubanOrderForm,
                         AssociatedDoubanOrderForm)
from forms.item import ItemForm

from models.client import Client, Group, Agent
from models.medium import Medium, AdPosition
from models.item import (AdItem, AdSchedule, SALE_TYPE_CN, ITEM_STATUS_NEW,
                         ITEM_STATUS_ACTION_CN, ChangeStateApply, ITEM_STATUS_ARCHIVE,
                         ITEM_STATUS_LEADER_ACTIONS,
                         ITEM_STATUS_ACTION_PRE_ORDER,
                         ITEM_STATUS_ACTION_ORDER_APPLY)
from models.order import Order
from models.client_order import (CONTRACT_STATUS_APPLYCONTRACT, CONTRACT_STATUS_APPLYPASS,
                                 CONTRACT_STATUS_APPLYREJECT, CONTRACT_STATUS_APPLYPRINT,
                                 CONTRACT_STATUS_PRINTED, CONTRACT_STATUS_CN)
from models.client_order import ClientOrder
from models.framework_order import FrameworkOrder
from models.douban_order import DoubanOrder
from models.associated_douban_order import AssociatedDoubanOrder
from models.user import User
from models.consts import DATE_FORMAT, TIME_FORMAT
from models.excel import Excel
from models.material import Material
from models.attachment import Attachment

from libs.signals import order_apply_signal, reply_apply_signal, contract_apply_signal

order_bp = Blueprint('order', __name__, template_folder='../templates/order')


STATUS_APPLLY = (ITEM_STATUS_ACTION_PRE_ORDER, ITEM_STATUS_ACTION_ORDER_APPLY)
ORDER_PAGE_NUM = 50


@order_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('order.my_orders'))


######################
#### client order
######################
@order_bp.route('/new_order', methods=['GET', 'POST'])
def new_order():
    form = ClientOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = ClientOrder.add(agent=Agent.get(form.agent.data),
                                client=Client.get(form.client.data),
                                campaign=form.campaign.data,
                                money=form.money.data,
                                client_start=form.client_start.data,
                                client_end=form.client_end.data,
                                reminde_date=form.reminde_date.data,
                                direct_sales=User.gets(form.direct_sales.data),
                                agent_sales=User.gets(form.agent_sales.data),
                                contract_type=form.contract_type.data,
                                resource_type=form.resource_type.data,
                                sale_type=form.sale_type.data,
                                creator=g.user,
                                create_time=datetime.now())
        flash(u'新建客户订单成功, 请补充媒体订单和上传合同!', 'success')
        return redirect(url_for("order.order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('new_order.html', form=form)


def get_client_form(order):
    client_form = ClientOrderForm()
    client_form.agent.data = order.agent.id
    client_form.client.data = order.client.id
    client_form.campaign.data = order.campaign
    client_form.money.data = order.money
    client_form.client_start.data = order.client_start
    client_form.client_end.data = order.client_end
    client_form.reminde_date.data = order.reminde_date
    client_form.direct_sales.data = [u.id for u in order.direct_sales]
    client_form.agent_sales.data = [u.id for u in order.agent_sales]
    client_form.contract_type.data = order.contract_type
    client_form.resource_type.data = order.resource_type
    client_form.sale_type.data = order.sale_type
    return client_form


def get_medium_form(order):
    medium_form = MediumOrderForm()
    medium_form.medium.choices = [(order.medium.id, order.medium.name)]
    medium_form.medium.data = order.medium.id
    medium_form.medium_money.data = order.medium_money
    medium_form.sale_money.data = order.sale_money
    medium_form.medium_start.data = order.medium_start
    medium_form.medium_end.data = order.medium_end
    medium_form.operaters.data = [u.id for u in order.operaters]
    medium_form.designers.data = [u.id for u in order.designers]
    medium_form.planers.data = [u.id for u in order.planers]
    medium_form.discount.data = order.discount
    return medium_form


def get_associated_douban_form(order, client_order):
    form = AssociatedDoubanOrderForm()
    form.medium_order.choices = [(mo.id, mo.name) for mo in client_order.medium_orders]
    form.medium_order.data = order.medium_order.id
    form.campaign.data = order.campaign
    form.money.data = order.money
    return form


@order_bp.route('/order/<order_id>/info', methods=['GET', 'POST'])
def order_info(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    client_form = get_client_form(order)
    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        if info_type == 0:
            if not order.can_admin(g.user):
                flash(u'您没有编辑权限! 请联系该订单的创建者或者销售同事!', 'danger')
            else:
                client_form = ClientOrderForm(request.form)
                if client_form.validate():
                    order.agent = Agent.get(client_form.agent.data)
                    order.client = Client.get(client_form.client.data)
                    order.campaign = client_form.campaign.data
                    order.money = client_form.money.data
                    order.client_start = client_form.client_start.data
                    order.client_end = client_form.client_end.data
                    order.reminde_date = client_form.reminde_date.data
                    order.direct_sales = User.gets(client_form.direct_sales.data)
                    order.agent_sales = User.gets(client_form.agent_sales.data)
                    order.contract_type = client_form.contract_type.data
                    order.resource_type = client_form.resource_type.data
                    order.sale_type = client_form.sale_type.data
                    order.save()
                    flash(u'[客户订单]%s 保存成功!' % order.name, 'success')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                for mo in order.medium_orders:
                    mo.medium_contract = request.values.get("medium_contract_%s" % mo.id, "")
                    mo.save()
                for o in order.associated_douban_orders:
                    o.contract = request.values.get("douban_contract_%s" % o.id, "")
                    o.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-致趣: %s\n" % (order.agent.name, order.contract)
                for mo in order.medium_orders:
                    msg = msg + u"致趣-%s: %s\n" % (mo.medium.name, mo.medium_contract or "")
                for o in order.associated_douban_orders:
                    msg = msg + u"%s-豆瓣: %s\n" % (o.medium_order.medium.name, o.contract or "")
                to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(apply_context)
                flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')

    new_medium_form = MediumOrderForm()
    new_medium_form.medium_start.data = order.client_start
    new_medium_form.medium_end.data = order.client_end
    new_associated_douban_form = AssociatedDoubanOrderForm()
    new_associated_douban_form.medium_order.choices = [(mo.id, mo.name) for mo in order.medium_orders]
    new_associated_douban_form.campaign.data = order.campaign
    reminder_emails = [(u.name, u.email) for u in User.leaders() + User.contracts() + User.admins()]
    context = {'client_form': client_form,
               'new_medium_form': new_medium_form,
               'medium_forms': [(get_medium_form(mo), mo) for mo in order.medium_orders],
               'new_associated_douban_form': new_associated_douban_form,
               'associated_douban_forms': [(get_associated_douban_form(o, order), o) for o in order.associated_douban_orders],
               'order': order,
               'reminder_emails': reminder_emails}
    return tpl('order_detail_info.html', **context)


@order_bp.route('/order/<order_id>/new_medium', methods=['GET', 'POST'])
def order_new_medium(order_id):
    co = ClientOrder.get(order_id)
    if not co:
        abort(404)
    form = MediumOrderForm(request.form)
    if request.method == 'POST':
        mo = Order.add(campaign=co.campaign,
                       medium=Medium.get(form.medium.data),
                       medium_money=form.medium_money.data,
                       sale_money=form.sale_money.data,
                       medium_start=form.medium_start.data,
                       medium_end=form.medium_end.data,
                       operaters=User.gets(form.operaters.data),
                       designers=User.gets(form.designers.data),
                       planers=User.gets(form.planers.data),
                       discount=form.discount.data,
                       creator=g.user)
        co.medium_orders = co.medium_orders + [mo]
        co.save()
        flash(u'[媒体订单]新建成功!', 'success')
        return redirect(mo.info_path())
    return tpl('order_new_medium.html', form=form)


@order_bp.route('/order/medium_order/<mo_id>/', methods=['POST'])
def medium_order(mo_id):
    mo = Order.get(mo_id)
    if not mo:
        abort(404)
    form = MediumOrderForm(request.form)
    mo.medium_money = form.medium_money.data
    mo.sale_money = form.sale_money.data
    mo.medium_start = form.medium_start.data
    mo.medium_end = form.medium_end.data
    mo.operaters = User.gets(form.operaters.data)
    mo.designers = User.gets(form.designers.data)
    mo.planers = User.gets(form.planers.data)
    mo.discount = form.discount.data
    mo.save()
    flash(u'[媒体订单]%s 保存成功!' % mo.name, 'success')
    return redirect(mo.info_path())


@order_bp.route('/order/new_associated_douban_order', methods=['POST'])
def new_associated_douban_order():
    form = AssociatedDoubanOrderForm(request.form)
    ao = AssociatedDoubanOrder.add(medium_order=Order.get(form.medium_order.data),
                                   campaign=form.campaign.data,
                                   money=form.money.data,
                                   creator=g.user)
    flash(u'[关联豆瓣订单]新建成功!', 'success')
    return redirect(ao.info_path())


@order_bp.route('/order/associated_douban_order/<order_id>/', methods=['POST'])
def associated_douban_order(order_id):
    ao = AssociatedDoubanOrder.get(order_id)
    if not ao:
        abort(404)
    form = AssociatedDoubanOrderForm(request.form)
    ao.medium_order = Order.get(form.medium_order.data)
    ao.campaign = form.campaign.data
    ao.money = form.money.data
    ao.save()
    flash(u'[关联豆瓣订单]%s 保存成功!' % ao.name, 'success')
    return redirect(ao.info_path())


@order_bp.route('/order/<order_id>/<step>/', methods=['GET'])
def order_detail(order_id, step):
    order = Order.get(order_id)
    if not order:
        abort(404)
    leaders = [(m.id, m.name) for m in User.leaders()]
    context = {'leaders': leaders,
               'order': order,
               'step': step,
               'SALE_TYPE_CN': SALE_TYPE_CN
               }
    return tpl('order_detail_schedule.html', **context)


@order_bp.route('/order/<order_id>/items', methods=['GET'])
def order_items(order_id):
    order = Order.get(order_id)
    if not order:
        abort(404)
    context = {'order': order,
               'SALE_TYPE_CN': SALE_TYPE_CN}
    return tpl('order_detail_ordered.html', **context)


@order_bp.route('/client_order/<order_id>/contract', methods=['POST'])
def client_order_contract(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    return redirect(url_for("order.order_info", order_id=order.id))


def contract_status_change(order, action, emails, msg):
    action_msg = ''
    if action == 0:
        order.contract_status = CONTRACT_STATUS_APPLYCONTRACT
        action_msg = u"申请合同号审批"
    elif action == 1:
        order.contract_status = CONTRACT_STATUS_APPLYPRINT
        action_msg = u"申请打印合同"
    elif action == 2:
        order.contract_status = CONTRACT_STATUS_APPLYPASS
        action_msg = u"合同号申请被通过"
    elif action == 3:
        order.contract_status = CONTRACT_STATUS_APPLYREJECT
        action_msg = u"合同号申请未被通过"
    elif action == 4:
        order.contract_status = CONTRACT_STATUS_PRINTED
        action_msg = u"合同打印完毕"
    order.save()
    flash(u'[%s] %s ' % (order.name, action_msg), 'success')
    #  发送邮件
    to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
    if action == 2:
        to_users = to_users + User.contracts()
    to_emails = list(set(emails + [x.email for x in to_users]))
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order}
    contract_apply_signal.send(apply_context)
    flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')


@order_bp.route('/orders', methods=['GET'])
def orders():
    orders = list(ClientOrder.all())
    return display_orders(orders, u'客户订单列表')


@order_bp.route('/my_orders', methods=['GET'])
def my_orders():
    orders = ClientOrder.get_order_by_user(g.user)
    return display_orders(orders, u'我的客户订单列表')


def display_orders(orders, title):
    sortby = request.args.get('sortby', '')
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    medium_id = int(request.args.get('selected_medium', '0'))
    group_id = int(request.args.get('selected_group', '0'))
    status_id = int(request.args.get('selected_status', '-1'))
    reverse = orderby != 'asc'
    page = int(request.args.get('p', 1))
    page = max(1, page)
    start = (page - 1) * ORDER_PAGE_NUM
    orders_len = len(orders)
    if medium_id:
        orders = [o for o in orders if medium_id in o.medium_ids]
    if group_id:
        orders = [o for o in orders if o.agent and o.agent.group and group_id == o.agent.group.id]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [o for o in orders if search_info in o.name]
    if sortby and orders_len and hasattr(orders[0], sortby):
        orders = sorted(orders, key=lambda x: getattr(x, sortby), reverse=reverse)
    select_mediums = [(m.id, m.name) for m in Medium.all()]
    select_mediums.insert(0, (0, u'全部媒体'))
    select_groups = [(g.id, g.name) for g in Group.all()]
    select_groups.insert(0, (0, u'全部甲方集团'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    if 0 <= start < orders_len:
        orders = orders[start:min(start + ORDER_PAGE_NUM, orders_len)]
    else:
        orders = []
    return tpl('orders.html', orders=orders,
               mediums=select_mediums, medium_id=medium_id,
               groups=select_groups, group_id=group_id,
               statuses=select_statuses, status_id=status_id,
               sortby=sortby, orderby=orderby,
               search_info=search_info, page=page)


######################
#### framework order
######################
@order_bp.route('/new_framework_order', methods=['GET', 'POST'])
def new_framework_order():
    form = FrameworkOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = FrameworkOrder.add(group=Group.get(form.group.data),
                                   description=form.description.data,
                                   money=form.money.data,
                                   client_start=form.client_start.data,
                                   client_end=form.client_end.data,
                                   reminde_date=form.reminde_date.data,
                                   direct_sales=User.gets(form.direct_sales.data),
                                   agent_sales=User.gets(form.agent_sales.data),
                                   contract_type=form.contract_type.data,
                                   creator=g.user,
                                   create_time=datetime.now())
        flash(u'新建框架订单成功, 请上传合同!', 'success')
        return redirect(url_for("order.framework_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('new_framework_order.html', form=form)


def get_framework_form(order):
    framework_form = FrameworkOrderForm()
    framework_form.group.data = order.group.id
    framework_form.description.data = order.description
    framework_form.money.data = order.money
    framework_form.client_start.data = order.client_start
    framework_form.client_end.data = order.client_end
    framework_form.reminde_date.data = order.reminde_date
    framework_form.direct_sales.data = [u.id for u in order.direct_sales]
    framework_form.agent_sales.data = [u.id for u in order.agent_sales]
    framework_form.contract_type.data = order.contract_type
    return framework_form


@order_bp.route('/framework_order/<order_id>/info', methods=['GET', 'POST'])
def framework_order_info(order_id):
    order = FrameworkOrder.get(order_id)
    if not order:
        abort(404)
    framework_form = get_framework_form(order)

    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        if info_type == 0:
            if not order.can_admin(g.user):
                flash(u'您没有编辑权限! 请联系该框架的创建者或者销售同事!', 'danger')
            else:
                framework_form = FrameworkOrderForm(request.form)
                if framework_form.validate():
                    order.group = Group.get(framework_form.group.data)
                    order.description = framework_form.description.data
                    order.money = framework_form.money.data
                    order.client_start = framework_form.client_start.data
                    order.client_end = framework_form.client_end.data
                    order.reminde_date = framework_form.reminde_date.data
                    order.direct_sales = User.gets(framework_form.direct_sales.data)
                    order.agent_sales = User.gets(framework_form.agent_sales.data)
                    order.contract_type = framework_form.contract_type.data
                    order.save()
                    flash(u'[框架订单]%s 保存成功!' % order.name, 'success')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-致趣: %s\n" % (order.group.name, order.contract)
                to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(apply_context)
                flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')

    reminder_emails = [(u.name, u.email) for u in User.leaders() + User.contracts() + User.admins()]
    context = {'framework_form': framework_form,
               'order': order,
               'reminder_emails': reminder_emails}
    return tpl('framework_detail_info.html', **context)


@order_bp.route('/framework_orders', methods=['GET'])
def framework_orders():
    orders = list(FrameworkOrder.all())
    return framework_display_orders(orders, u'框架订单列表')


def framework_display_orders(orders, title):
    page = int(request.args.get('p', 1))
    page = max(1, page)
    start = (page - 1) * ORDER_PAGE_NUM
    orders_len = len(orders)
    if 0 <= start < orders_len:
        orders = orders[start:min(start + ORDER_PAGE_NUM, orders_len)]
    else:
        orders = []
    return tpl('frameworks.html', orders=orders, page=page)


@order_bp.route('/framework_order/<order_id>/contract', methods=['POST'])
def framework_order_contract(order_id):
    order = FrameworkOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    return redirect(url_for("order.framework_order_info", order_id=order.id))


######################
####  douban order
######################
@order_bp.route('/new_douban_order', methods=['GET', 'POST'])
def new_douban_order():
    form = DoubanOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = DoubanOrder.add(client=Client.get(form.client.data),
                                agent=Agent.get(form.agent.data),
                                campaign=form.campaign.data,
                                money=form.money.data,
                                client_start=form.client_start.data,
                                client_end=form.client_end.data,
                                reminde_date=form.reminde_date.data,
                                direct_sales=User.gets(form.direct_sales.data),
                                agent_sales=User.gets(form.agent_sales.data),
                                operaters=User.gets(form.operaters.data),
                                designers=User.gets(form.designers.data),
                                planers=User.gets(form.planers.data),
                                contract_type=form.contract_type.data,
                                resource_type=form.resource_type.data,
                                sale_type=form.sale_type.data,
                                creator=g.user,
                                create_time=datetime.now())
        flash(u'新建豆瓣订单成功, 请上传合同!', 'success')
        return redirect(url_for("order.douban_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('new_douban_order.html', form=form)


def get_douban_form(order):
    form = DoubanOrderForm()
    form.client.data = order.client.id
    form.agent.data = order.agent.id
    form.campaign.data = order.campaign
    form.money.data = order.money
    form.client_start.data = order.client_start
    form.client_end.data = order.client_end
    form.reminde_date.data = order.reminde_date
    form.direct_sales.data = [u.id for u in order.direct_sales]
    form.agent_sales.data = [u.id for u in order.agent_sales]
    form.operaters.data = [u.id for u in order.operaters]
    form.designers.data = [u.id for u in order.designers]
    form.planers.data = [u.id for u in order.planers]
    form.contract_type.data = order.contract_type
    form.resource_type.data = order.resource_type
    form.sale_type.data = order.sale_type
    return form


@order_bp.route('/douban_order/<order_id>/info', methods=['GET', 'POST'])
def douban_order_info(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    form = get_douban_form(order)

    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        if info_type == 0:
            if not order.can_admin(g.user):
                flash(u'您没有编辑权限! 请联系该订单的创建者或者销售同事!', 'danger')
            else:
                form = FrameworkOrderForm(request.form)
                if form.validate():
                    order.client = Client.get(form.client.data)
                    order.agent = Agent.get(form.agent.data)
                    order.campaign = form.campaign.data
                    order.money = form.money.data
                    order.client_start = form.client_start.data
                    order.client_end = form.client_end.data
                    order.reminde_date = form.reminde_date.data
                    order.direct_sales = User.gets(form.direct_sales.data)
                    order.agent_sales = User.gets(form.agent_sales.data)
                    order.operaters = User.gets(form.operaters.data),
                    order.designers = User.gets(form.designers.data),
                    order.planers = User.gets(form.planers.data),
                    order.contract_type = form.contract_type.data
                    order.resource_type = form.resource_type.data
                    order.sale_type = form.sale_type.data
                    order.save()
                    flash(u'[豆瓣订单]%s 保存成功!' % order.name, 'success')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-豆瓣: %s\n" % (order.agent.name, order.contract)
                to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(apply_context)
                flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')

    reminder_emails = [(u.name, u.email) for u in User.leaders() + User.contracts() + User.admins()]
    context = {'douban_form': form,
               'order': order,
               'reminder_emails': reminder_emails}
    return tpl('douban_detail_info.html', **context)


@order_bp.route('/my_douban_orders', methods=['GET'])
def my_douban_orders():
    orders = DoubanOrder.get_order_by_user(g.user)
    return douban_display_orders(orders, u'我的豆瓣订单列表')


@order_bp.route('/douban_orders', methods=['GET'])
def douban_orders():
    orders = list(DoubanOrder.all())
    return douban_display_orders(orders, u'直签豆瓣订单列表')


def douban_display_orders(orders, title):
    page = int(request.args.get('p', 1))
    page = max(1, page)
    start = (page - 1) * ORDER_PAGE_NUM
    orders_len = len(orders)
    if 0 <= start < orders_len:
        orders = orders[start:min(start + ORDER_PAGE_NUM, orders_len)]
    else:
        orders = []
    return tpl('douban_orders.html', orders=orders, page=page)


@order_bp.route('/douban_order/<order_id>/contract', methods=['POST'])
def douban_order_contract(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    return redirect(url_for("order.douban_order_info", order_id=order.id))


######################
#### items
######################
@order_bp.route('/items', methods=['GET'])
def items():
    items = AdItem.all()
    return tpl('items.html', items=items)


@order_bp.route('/materials', methods=['GET'])
def materials():
    materials = Material.all()
    return tpl('materials.html', materials=materials)


@order_bp.route('/order/<order_id>/new_item/<type>')
def new_item(order_id, type):
    order = Order.get(order_id)
    if not order:
        abort(404)
    if not order.can_admin(g.user):
        flash(u'您没有创建排期的权限, 请联系订单创建者和销售同事!', 'danger')
        return redirect(url_for('order.order_detail', order_id=order.id, step=0))
    start_date = datetime.today()
    end_date = start_date + timedelta(days=30)
    positions = [(x.id, x.display_name) for x in order.medium.positions]
    return tpl('new_item.html', order=order, positions=positions,
               start_date=start_date, end_date=end_date, type=type,
               SALE_TYPE_CN=SALE_TYPE_CN, SPECIAL_SALE_CN={0: u"否", 1: u"是"})


def check_schedules_post(data):
    """检查排期数据是否合法"""
    try:
        items = json.loads(data)
    except ValueError:
        return '1', "JSON数据格式出错啦"
    else:
        status = 0
        msg = ''
        for item in items:
            position = AdPosition.get(item['position'])
            for (date_str, num_str) in item['schedule'].items():
                _date = datetime.strptime(date_str, DATE_FORMAT).date()
                num = int(num_str)
                if position.can_order_num(_date) < num:
                    status = 1
                    msg += u'%s 最多只能预订 %s \n' % (position.display_name, position.can_order_num(_date))
    return status, msg


def add_schedules(order, data):
    """新增订单项, 排期项"""
    items = json.loads(data)
    for item in items:
        position = AdPosition.get(item['position'])
        ad_item = AdItem.add(order=order, sale_type=item['sale_type'], special_sale=item['special_sale'],
                             position=position, creator=g.user, create_time=datetime.now())
        ad_item.price = position.price
        ad_item.description = item['description']
        ad_item.item_status = ITEM_STATUS_NEW
        ad_item.save()
        for (date_str, num_str) in item['schedule'].items():
            _date = datetime.strptime(date_str, DATE_FORMAT).date()
            num = int(num_str)
            AdSchedule.add(item=ad_item, num=num, date=_date)


@order_bp.route('/order/<order_id>/schedules_post/', methods=["POST"])
def schedules_post(order_id):
    """AJAX 提交排期数据"""
    order = Order.get(order_id)
    if not order:
        abort(404)
    data = request.values.get('data')
    status, msg = check_schedules_post(data)
    if not status:
        add_schedules(order, data)
        flash(u'排期提交成功!', 'success')
    return jsonify({'status': status, 'msg': msg})


@order_bp.route('/schedule_info/', methods=['GET'])
def schedule_info():
    """ajax 获取排期数据"""
    start_date = datetime.strptime(request.values.get('start'), DATE_FORMAT).date()
    end_date = datetime.strptime(request.values.get('end'), DATE_FORMAT).date()
    position = AdPosition.get(request.values.get('position'))
    return jsonify(position.get_schedule(start_date, end_date))


@order_bp.route('/position_list', methods=['GET'])
def position_list():
    # order = Order.get(request.values.get('order'))
    # sale_type = request.values.get('sale_type')
    # special_sale = request.values.get('special_sale')
    return jsonify([(p.id, p.display_name) for p in AdPosition.all()])


@order_bp.route('/item/<item_id>/materials', methods=["GET", "POST"])
def item_materials(item_id):
    item = AdItem.get(item_id)
    if not item:
        abort(404)
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        item.sale_type = form.sale_type.data
        item.special_sale = form.special_sale.data
        item.description = form.description.data
        item.ad_type = form.ad_type.data
        item.price = form.price.data
        item.priority = form.priority.data
        item.speed = form.speed.data
        item.item_status = form.item_status.data
        item.status = form.status.data
        item.save()
        flash(u'保存成功!', 'success')
    else:
        form.order.data = item.order.name
        form.sale_type.data = item.sale_type
        form.special_sale.data = item.special_sale
        form.position.data = item.position.name
        form.description.data = item.description
        form.ad_type.data = item.ad_type
        form.price.data = item.price
        form.priority.data = item.priority
        form.speed.data = item.speed
        form.item_status.data = item.item_status
        form.status.data = item.status
        form.creator.data = item.creator.name

        form.order.readonly = True
        form.position.readonly = True
        form.creator.readonly = True
    if not g.user.is_admin():
        form.disable_all()
    return tpl('item.html', form=form, item=item)


@order_bp.route('/item/<item_id>/schedule', methods=["GET", "POST"])
def item_schedule(item_id):
    item = AdItem.get(item_id)
    if not item:
        abort(404)
    return tpl('item_schadule.html', item=item)


@order_bp.route('/item/<item_id>/schedule_simple_update', methods=["POST"])
def schedule_simple_update(item_id):
    item = AdItem.get(item_id)
    if not item:
        return jsonify({'msg': u"出错啦, 排期不存在"})
    data = request.values.get('data')
    msg = ""
    status = 0
    schedules_info = json.loads(data)
    flag = False
    for date_str, num in schedules_info.items():
        _date = datetime.strptime(date_str, DATE_FORMAT).date()
        if not item.position.check_order_num(_date, num):
            msg = date_str + u"预订量超过最大可预订量"
            status = 1
    if not status:
        for date_str, num in schedules_info.items():
            _date = datetime.strptime(date_str, DATE_FORMAT).date()
            _schedule = item.schedule_by_date(_date)
            if _schedule:
                if num == 0:
                    flag = True
                    _schedule.delete()
                else:
                    if _schedule.num != num:
                        _schedule.num = num
                        flag = True
                        _schedule.save()
            elif num != 0:
                flag = True
                _schedule = AdSchedule.add(item, num, _date)
        if flag:
            if item.schedule_sum:
                item.change_to_previous_status()
                msg = u"排期修改成功!当前状态回退至上一状态!"
                if item.item_status == ITEM_STATUS_NEW:
                    msg = u'排期更改成功!预下单状态不变更!'
            else:
                item.item_status = ITEM_STATUS_ARCHIVE
                item.save()
                msg = u"当前订单项所有排期总量为0,自动归档!"
        else:
            msg = u"当前订单项排期未做修改"
    return jsonify({'msg': msg, 'status': status})


@order_bp.route('/schedule/<schedule_id>/update', methods=["POST"])
def schedule_update(schedule_id):
    schedule = AdSchedule.get(schedule_id)
    if not schedule:
        abort(404)
    schedule.date = datetime.strptime(request.form.get('date'), DATE_FORMAT).date()
    schedule.start = datetime.strptime(request.form.get('start'), TIME_FORMAT).time()
    schedule.end = datetime.strptime(request.form.get('end'), TIME_FORMAT).time()
    schedule.num = request.form.get('num')
    schedule.save()
    flash(u'投放安排保存成功!', 'success')
    return redirect(url_for("order.item_detail", item_id=schedule.item.id))


@order_bp.route('/schedule/<schedule_id>/delete')
def schedule_delete(schedule_id):
    schedule = AdSchedule.get(schedule_id)
    if not schedule:
        abort(404)
    item = schedule.item
    schedule.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("order.item_detail", item_id=item.id))


@order_bp.route('/order/<order_id>/items/update/<step>', methods=['POST'])
def items_status_update(order_id, step):
    order = Order.get(order_id)
    if not order:
        abort(404)
    item_ids = request.form.getlist('item_id')
    leaders = request.form.getlist('leader')
    if not item_ids:
        flash(u"请选择订单项")
    else:
        action = int(request.form.get('action'))
        if action in STATUS_APPLLY:
            if not leaders:
                flash(u"请选择Leader")
                return redirect(url_for('order.order_detail', order_id=order.id, step=step))
            else:
                apply = ChangeStateApply(step, action, [User.get(m).email for m in leaders], order)
                order_apply_signal.send(apply)
                flash(u"请在2个自然日内与审核Leaer联系")
        if action in ITEM_STATUS_LEADER_ACTIONS:
            apply = ChangeStateApply(
                step,
                action,
                [order.creator.email],
                order)
            reply_apply_signal.send(apply)
        items = AdItem.gets(item_ids)
        AdItem.update_items_with_action(items, action, g.user)
        msg = '\n\n'.join(['%s : %s' % (item.name, ITEM_STATUS_ACTION_CN[action]) for item in items])
        order.add_comment(g.user, msg)
        flash(u'%s个排期项%s。请将理由在留言板上留言说明' % (len(items), ITEM_STATUS_ACTION_CN[action]))
        step = AdItem.get_next_step(step, action)
    return redirect(url_for('order.order_detail', order_id=order.id, step=step))


@order_bp.route('/schedule_file/<order_id>', methods=['GET', 'POST'])
def export_schedule(order_id):
    order = Order.get(order_id)
    filename = ("%s-%s.xls" % (order.name, datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
    xls = Excel().write_excle(order.excel_table)
    response = get_download_response(xls, filename)
    return response


def get_download_response(xls, filename):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    xls.save(output)
    response.data = output.getvalue()
    mimetype_tuple = mimetypes.guess_type(filename)
    response_headers = Headers({
        'Pragma': "public",
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Cache-Control': 'private',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
    response.headers = response_headers
    response.set_cookie('fileDownload', 'true', path='/')
    return response


###################
##### attachment
###################
@order_bp.route('/client_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def client_attach_status(order_id, attachment_id, status):
    order = ClientOrder.get(order_id)
    attachment_status_change(order, attachment_id, status)
    return redirect(order.info_path())


@order_bp.route('/medium_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def medium_attach_status(order_id, attachment_id, status):
    order = Order.get(order_id)
    attachment_status_change(order.client_order, attachment_id, status)
    return redirect(order.info_path())


@order_bp.route('/framework_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def framework_attach_status(order_id, attachment_id, status):
    order = FrameworkOrder.get(order_id)
    attachment_status_change(order, attachment_id, status)
    return redirect(order.info_path())


@order_bp.route('/douban_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def douban_attach_status(order_id, attachment_id, status):
    order = DoubanOrder.get(order_id)
    attachment_status_change(order, attachment_id, status)
    return redirect(order.info_path())


@order_bp.route('/associated_douban_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def associated_douban_attach_status(order_id, attachment_id, status):
    order = AssociatedDoubanOrder.get(order_id)
    attachment_status_change(order.medium_order.client_order, attachment_id, status)
    return redirect(order.info_path())


def attachment_status_change(order, attachment_id, status):
    attachment = Attachment.get(attachment_id)
    attachment.attachment_status = status
    attachment.save()
    attachment_status_email(order, attachment)


def attachment_status_email(order, attachment):
    to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
    to_emails = list(set([x.email for x in to_users]))
    action_msg = u"%s文件:%s-%s" % (attachment.type_cn, attachment.filename, attachment.status_cn)
    msg = u"文件名:%s\n状态:%s\n如有疑问, 请联系合同管理员" % (attachment.filename, attachment.status_cn)
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order}
    contract_apply_signal.send(apply_context)
