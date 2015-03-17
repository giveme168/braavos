# -*- coding: utf-8 -*-
import StringIO
import mimetypes
from werkzeug.datastructures import Headers
from datetime import datetime, timedelta

from flask import Blueprint, request, redirect, abort, url_for, g, Response
from flask import render_template as tpl, json, jsonify, flash, current_app

from forms.order import (ClientOrderForm, MediumOrderForm,
                         FrameworkOrderForm, DoubanOrderForm,
                         AssociatedDoubanOrderForm)
from forms.item import ItemForm
from forms.outsource import OutsourceForm

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
                                 CONTRACT_STATUS_PRINTED, CONTRACT_STATUS_MEDIA, CONTRACT_STATUS_CN)
from models.client_order import ClientOrder
from models.framework_order import FrameworkOrder
from models.douban_order import DoubanOrder
from models.associated_douban_order import AssociatedDoubanOrder
from models.outsource import OutSource, OutSourceTarget
from models.user import User, TEAM_LOCATION_CN
from models.consts import DATE_FORMAT, TIME_FORMAT
from models.excel import Excel
from models.material import Material
from models.attachment import Attachment
from models.download import (download_excel_table_by_clientorders,
                             download_excel_table_by_doubanorders,
                             download_excel_table_by_frameworkorders)

from libs.signals import order_apply_signal, reply_apply_signal, contract_apply_signal, outsource_contract_apply_signal

order_bp = Blueprint('order', __name__, template_folder='../templates/order')


STATUS_APPLLY = (ITEM_STATUS_ACTION_PRE_ORDER, ITEM_STATUS_ACTION_ORDER_APPLY)
ORDER_PAGE_NUM = 50


@order_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('order.my_orders'))


######################
# client order
######################
@order_bp.route('/new_order', methods=['GET', 'POST'])
def new_order():
    form = ClientOrderForm(request.form)
    mediums = [(m.id, m.name) for m in Medium.all()]
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
        order.add_comment(g.user,
                          u"新建了客户订单:%s - %s - %s" % (
                              order.agent.name,
                              order.client.name,
                              order.campaign
                          ))
        medium_ids = request.values.getlist('medium')
        medium_moneys = request.values.getlist('medium-money')
        if medium_ids and medium_moneys and len(medium_ids) == len(medium_moneys):
            for x in range(len(medium_ids)):
                medium = Medium.get(medium_ids[x])
                mo = Order.add(campaign=order.campaign,
                               medium=medium,
                               sale_money=medium_moneys[x],
                               medium_money=0,
                               medium_money2=0,
                               medium_start=order.client_start,
                               medium_end=order.client_end,
                               creator=g.user)
                order.medium_orders = order.medium_orders + [mo]
                order.add_comment(g.user, u"新建了媒体订单: %s %s元" % (medium.name, mo.sale_money))
            order.save()
        flash(u'新建客户订单成功, 请上传合同和排期!', 'success')
        return redirect(order.info_path())
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('new_order.html', form=form, mediums=mediums)


@order_bp.route('/order/<order_id>/delete', methods=['GET'])
def order_delete(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"客户订单: %s-%s 已删除" % (order.client.name, order.campaign), 'danger')
    order.delete()
    return redirect(url_for("order.my_orders"))


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
    medium_form.medium_money2.data = order.medium_money2
    medium_form.sale_money.data = order.sale_money
    medium_form.medium_CPM.data = order.medium_CPM
    medium_form.sale_CPM.data = order.sale_CPM
    medium_form.medium_start.data = order.medium_start
    medium_form.medium_end.data = order.medium_end
    medium_form.operaters.data = [u.id for u in order.operaters]
    medium_form.designers.data = [u.id for u in order.designers]
    medium_form.planers.data = [u.id for u in order.planers]
    medium_form.discount.data = order.discount
    medium_form.discount.hidden = True
    return medium_form


@order_bp.route('/order/<order_id>/info/<tab_id>', methods=['GET', 'POST'])
def order_info(order_id, tab_id=1):
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
                    order.add_comment(g.user, u"更新了客户订单")
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
                msg = u"新合同号如下:\n\n%s-致趣: %s\n\n" % (order.agent.name, order.contract)
                for mo in order.medium_orders:
                    msg = msg + u"致趣-%s: %s\n\n" % (mo.medium.name, mo.medium_contract or "")
                for o in order.associated_douban_orders:
                    msg = msg + u"%s-豆瓣: %s\n\n" % (o.medium_order.medium.name, o.contract or "")
                to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(current_app._get_current_object(), apply_context=apply_context)
                flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')

                order.add_comment(g.user, u"更新合同号, %s" % msg)

    new_medium_form = MediumOrderForm()
    new_medium_form.medium_start.data = order.client_start
    new_medium_form.medium_end.data = order.client_end
    new_medium_form.discount.hidden = True

    new_associated_douban_form = AssociatedDoubanOrderForm()
    new_associated_douban_form.medium_order.choices = [(mo.id, "%s-%s" % (mo.name, mo.start_date_cn))
                                                       for mo in order.medium_orders]
    new_associated_douban_form.campaign.data = order.campaign

    new_outsource_form = OutsourceForm()
    new_outsource_form.medium_order.choices = [(mo.id, mo.medium.name) for mo in order.medium_orders]

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'client_form': client_form,
               'new_medium_form': new_medium_form,
               'medium_forms': [(get_medium_form(mo), mo) for mo in order.medium_orders],
               'new_associated_douban_form': new_associated_douban_form,
               'new_outsource_form': new_outsource_form,
               'order': order,
               'reminder_emails': reminder_emails,
               'tab_id': int(tab_id)}
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
                       medium_money2=form.medium_money2.data,
                       sale_money=form.sale_money.data,
                       medium_CPM=form.medium_CPM.data,
                       sale_CPM=form.sale_CPM.data,
                       medium_start=form.medium_start.data,
                       medium_end=form.medium_end.data,
                       operaters=User.gets(form.operaters.data),
                       designers=User.gets(form.designers.data),
                       planers=User.gets(form.planers.data),
                       discount=form.discount.data,
                       creator=g.user)
        co.medium_orders = co.medium_orders + [mo]
        co.save()
        co.add_comment(g.user, u"新建了媒体订单: %s %s %s" % (mo.medium.name, mo.sale_money, mo.medium_money))
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
    mo.medium_money2 = form.medium_money2.data
    mo.sale_money = form.sale_money.data
    mo.medium_CPM = form.medium_CPM.data
    mo.sale_CPM = form.sale_CPM.data
    mo.medium_start = form.medium_start.data
    mo.medium_end = form.medium_end.data
    mo.operaters = User.gets(form.operaters.data)
    mo.designers = User.gets(form.designers.data)
    mo.planers = User.gets(form.planers.data)
    mo.discount = form.discount.data
    mo.save()
    mo.client_order.add_comment(g.user, u"更新了媒体订单: %s %s %s" % (mo.medium.name, mo.sale_money, mo.medium_money))
    flash(u'[媒体订单]%s 保存成功!' % mo.name, 'success')
    return redirect(mo.info_path())


@order_bp.route('/order/new_associated_douban_order', methods=['POST'])
def new_associated_douban_order():
    form = AssociatedDoubanOrderForm(request.form)
    ao = AssociatedDoubanOrder.add(medium_order=Order.get(form.medium_order.data),
                                   campaign=form.campaign.data,
                                   money=form.money.data,
                                   creator=g.user)
    ao.medium_order.client_order.add_comment(g.user,
                                             u"新建了关联豆瓣订单: %s - %s - %s" % (
                                                 ao.medium_order.medium.name,
                                                 ao.campaign, ao.money))
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
    ao.medium_order.client_order.add_comment(g.user,
                                             u"更新了关联豆瓣订单: %s - %s - %s" % (
                                                 ao.medium_order.medium.name,
                                                 ao.campaign, ao.money))
    flash(u'[关联豆瓣订单]%s 保存成功!' % ao.name, 'success')
    return redirect(ao.info_path())


######################
# outsource
######################
@order_bp.route('/new_outsource', methods=['POST'])
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


@order_bp.route('/outsource/<outsource_id>/status', methods=['POST'])
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


@order_bp.route('/outsource/<outsource_id>', methods=['POST'])
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


@order_bp.route('/client_order/<order_id>/contract', methods=['POST'])
def client_order_contract(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    return redirect(order.info_path())


def contract_status_change(order, action, emails, msg):
    action_msg = ''
    #  发送邮件
    to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
    if action == 1:
        order.contract_status = CONTRACT_STATUS_MEDIA
        action_msg = u"申请利润分配"
        to_users = to_users + order.leaders + User.medias()
    elif action == 2:
        order.contract_status = CONTRACT_STATUS_APPLYCONTRACT
        action_msg = u"申请审批"
        to_users = to_users + order.leaders
    elif action == 3:
        order.contract_status = CONTRACT_STATUS_APPLYPASS
        action_msg = u"审批通过"
        to_users = to_users + order.leaders + User.contracts()
    elif action == 4:
        order.contract_status = CONTRACT_STATUS_APPLYREJECT
        action_msg = u"审批未被通过"
    elif action == 5:
        order.contract_status = CONTRACT_STATUS_APPLYPRINT
        action_msg = u"申请打印合同"
        to_users = to_users + User.contracts()
    elif action == 6:
        order.contract_status = CONTRACT_STATUS_PRINTED
        action_msg = u"合同打印完毕"
    elif action == 7:
        action_msg = u"消息提醒"
    order.save()
    flash(u'[%s] %s ' % (order.name, action_msg), 'success')

    to_emails = list(set(emails + [x.email for x in to_users]))
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order}
    contract_apply_signal.send(current_app._get_current_object(), apply_context=apply_context)
    flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')
    order.add_comment(g.user, u"%s \n\n %s" % (action_msg, msg))


@order_bp.route('/orders', methods=['GET'])
def orders():
    orders = list(ClientOrder.all())
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1
    return display_orders(orders, u'新媒体订单列表', status_id)


@order_bp.route('/my_orders', methods=['GET'])
def my_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media():
        orders = list(ClientOrder.all())
    elif g.user.is_leader():
        orders = [o for o in ClientOrder.all() if g.user.location in o.locations]
    else:
        orders = ClientOrder.get_order_by_user(g.user)

    if not request.args.get('selected_status'):
        if g.user.is_admin():
            status_id = -1
        elif g.user.is_super_leader():
            orders = [o for o in orders if o.contract_status == CONTRACT_STATUS_APPLYCONTRACT]
            status_id = CONTRACT_STATUS_APPLYCONTRACT
        elif g.user.is_leader():
            orders = [o for o in orders if (o.contract_status == CONTRACT_STATUS_APPLYCONTRACT and
                                            g.user.location in o.locations)]
            status_id = CONTRACT_STATUS_APPLYCONTRACT
        elif g.user.is_contract():
            orders = [o for o in orders if o.contract_status in [CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYPRINT]]
            status_id = CONTRACT_STATUS_APPLYPASS
        elif g.user.is_media():
            orders = [o for o in orders if o.contract_status == CONTRACT_STATUS_MEDIA]
            status_id = CONTRACT_STATUS_MEDIA
        else:
            status_id = -1
    else:
        status_id = int(request.args.get('selected_status'))
    return display_orders(orders, u'我的新媒体订单', status_id)


def display_orders(orders, title, status_id=-1):
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
        orders = sorted(orders, key=lambda x: getattr(x, sortby), reverse=reverse)
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    if 0 <= start < orders_len:
        orders = orders[start:min(start + ORDER_PAGE_NUM, orders_len)]
    else:
        orders = []
    if 'download' == request.args.get('action', ''):
        filename = ("%s-%s.xls" % (u"新媒体订单", datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = Excel().write_excle(download_excel_table_by_clientorders(orders))
        response = get_download_response(xls, filename)
        return response
    else:
        return tpl('orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   sortby=sortby, orderby=orderby,
                   search_info=search_info, page=page)


######################
# framework order
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
        order.add_comment(g.user, u"新建了该框架订单")
        flash(u'新建框架订单成功, 请上传合同!', 'success')
        return redirect(url_for("order.framework_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('new_framework_order.html', form=form)


@order_bp.route('/framework_order/<order_id>/delete', methods=['GET'])
def framework_delete(order_id):
    order = FrameworkOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"框架订单: %s 已删除" % (order.group.name), 'danger')
    order.delete()
    return redirect(url_for("order.my_framework_orders"))


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
                    order.add_comment(g.user, u"更新了该框架订单")
                    flash(u'[框架订单]%s 保存成功!' % order.name, 'success')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-致趣: %s\n\n" % (order.group.name, order.contract)
                to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(current_app._get_current_object(), apply_context=apply_context)
                flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')
                order.add_comment(g.user, u"更新合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'framework_form': framework_form,
               'order': order,
               'reminder_emails': reminder_emails}
    return tpl('framework_detail_info.html', **context)


@order_bp.route('/my_framework_orders', methods=['GET'])
def my_framework_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media():
        orders = list(FrameworkOrder.all())
        if g.user.is_admin():
            pass
        elif g.user.is_super_leader():
            orders = [o for o in orders if o.contract_status == CONTRACT_STATUS_APPLYCONTRACT]
        elif g.user.is_contract():
            orders = [o for o in orders if o.contract_status in [CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYPRINT]]
        elif g.user.is_media():
            orders = [o for o in orders if o.contract_status == CONTRACT_STATUS_MEDIA]
    elif g.user.is_leader():
        orders = [o for o in FrameworkOrder.all() if g.user.location in o.locations]
        orders = [o for o in orders if (o.contract_status == CONTRACT_STATUS_APPLYCONTRACT and
                                        g.user.location in o.locations)]
    else:
        orders = FrameworkOrder.get_order_by_user(g.user)
    return framework_display_orders(orders, u'我的框架订单')


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
    if 'download' == request.args.get('action', ''):
        filename = ("%s-%s.xls" % (u"框架订单", datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = Excel().write_excle(download_excel_table_by_frameworkorders(orders))
        response = get_download_response(xls, filename)
        return response
    else:
        return tpl('frameworks.html', title=title, orders=orders, page=page)


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
#  douban order
######################
@order_bp.route('/new_douban_order', methods=['GET', 'POST'])
def new_douban_order():
    form = DoubanOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = DoubanOrder.add(client=Client.get(form.client.data),
                                agent=Agent.get(form.agent.data),
                                campaign=form.campaign.data,
                                money=form.money.data,
                                medium_CPM=form.medium_CPM.data,
                                sale_CPM=form.sale_CPM.data,
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
        order.add_comment(g.user, u"新建了该直签豆瓣订单")
        flash(u'新建豆瓣订单成功, 请上传合同!', 'success')
        return redirect(url_for("order.douban_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('new_douban_order.html', form=form)


@order_bp.route('/douban_order/<order_id>/delete', methods=['GET'])
def douban_order_delete(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"豆瓣订单: %s-%s 已删除" % (order.client.name, order.campaign), 'danger')
    order.delete()
    return redirect(url_for("order.my_douban_orders"))


def get_douban_form(order):
    form = DoubanOrderForm()
    form.client.data = order.client.id
    form.agent.data = order.agent.id
    form.campaign.data = order.campaign
    form.money.data = order.money
    form.medium_CPM.data = order.medium_CPM
    form.sale_CPM.data = order.sale_CPM
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
                form = DoubanOrderForm(request.form)
                if form.validate():
                    order.client = Client.get(form.client.data)
                    order.agent = Agent.get(form.agent.data)
                    order.campaign = form.campaign.data
                    order.money = form.money.data
                    order.sale_CPM = form.sale_CPM.data
                    order.medium_CPM = form.medium_CPM.data
                    order.client_start = form.client_start.data
                    order.client_end = form.client_end.data
                    order.reminde_date = form.reminde_date.data
                    order.direct_sales = User.gets(form.direct_sales.data)
                    order.agent_sales = User.gets(form.agent_sales.data)
                    order.operaters = User.gets(form.operaters.data)
                    order.designers = User.gets(form.designers.data)
                    order.planers = User.gets(form.planers.data)
                    order.contract_type = form.contract_type.data
                    order.resource_type = form.resource_type.data
                    order.sale_type = form.sale_type.data
                    order.save()
                    order.add_comment(g.user, u"更新了该订单信息")
                    flash(u'[豆瓣订单]%s 保存成功!' % order.name, 'success')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-豆瓣: %s\n\n" % (order.agent.name, order.contract)
                to_users = order.direct_sales + order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(current_app._get_current_object(), apply_context=apply_context)
                flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')
                order.add_comment(g.user, u"更新了合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'douban_form': form,
               'order': order,
               'reminder_emails': reminder_emails}
    return tpl('douban_detail_info.html', **context)


@order_bp.route('/my_douban_orders', methods=['GET'])
def my_douban_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media():
        orders = list(DoubanOrder.all())
    elif g.user.is_leader():
        orders = [o for o in DoubanOrder.all() if g.user.location in o.locations]
    else:
        orders = DoubanOrder.get_order_by_user(g.user)

    if not request.args.get('selected_status'):
        if g.user.is_admin():
            status_id = -1
        elif g.user.is_super_leader():
            orders = [o for o in orders if o.contract_status == CONTRACT_STATUS_APPLYCONTRACT]
            status_id = CONTRACT_STATUS_APPLYCONTRACT
        elif g.user.is_leader():
            orders = [o for o in orders if (o.contract_status == CONTRACT_STATUS_APPLYCONTRACT and
                                            g.user.location in o.locations)]
            status_id = CONTRACT_STATUS_APPLYCONTRACT
        elif g.user.is_contract():
            orders = [o for o in orders if o.contract_status in [CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYPRINT]]
            status_id = CONTRACT_STATUS_APPLYPASS
        elif g.user.is_media():
            orders = [o for o in orders if o.contract_status == CONTRACT_STATUS_MEDIA]
            status_id = CONTRACT_STATUS_MEDIA
        else:
            status_id = -1
    else:
        status_id = int(request.args.get('selected_status'))
    return douban_display_orders(orders, u'我的直签豆瓣订单', status_id)


@order_bp.route('/douban_orders', methods=['GET'])
def douban_orders():
    orders = list(DoubanOrder.all())
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1
    return douban_display_orders(orders, u'全部直签豆瓣订单', status_id)


def douban_display_orders(orders, title, status_id=-1):
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
        orders = sorted(orders, key=lambda x: getattr(x, sortby), reverse=reverse)

    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    if 0 <= start < orders_len:
        orders = orders[start:min(start + ORDER_PAGE_NUM, orders_len)]
    else:
        orders = []
    if 'download' == request.args.get('action', ''):
        filename = ("%s-%s.xls" % (u"直签豆瓣订单", datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = Excel().write_excle(download_excel_table_by_doubanorders(orders))
        response = get_download_response(xls, filename)
        return response
    else:
        return tpl('douban_orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   sortby=sortby, orderby=orderby,
                   search_info=search_info, page=page)


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
# items
######################
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
                order_apply_signal.send(current_app._get_current_object(), change_state_apply=apply)
                flash(u"请在2个自然日内与审核Leaer联系")
        if action in ITEM_STATUS_LEADER_ACTIONS:
            apply = ChangeStateApply(
                step,
                action,
                [order.creator.email],
                order)
            reply_apply_signal.send(current_app._get_current_object(), change_state_apply=apply)
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
# attachment
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
    contract_apply_signal.send(current_app._get_current_object(), apply_context=apply_context)
