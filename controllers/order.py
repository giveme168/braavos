# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, request, redirect, abort, url_for, g
from flask import render_template as tpl, flash, current_app

from forms.order import (ClientOrderForm, MediumOrderForm,
                         FrameworkOrderForm, DoubanOrderForm,
                         AssociatedDoubanOrderForm)

from models.client import Client, Group, Agent, AgentRebate
from models.medium import Medium
from models.order import Order, MediumOrderExecutiveReport
from models.client_order import (CONTRACT_STATUS_APPLYCONTRACT, CONTRACT_STATUS_APPLYPASS,
                                 CONTRACT_STATUS_APPLYREJECT, CONTRACT_STATUS_APPLYPRINT,
                                 CONTRACT_STATUS_PRINTED, CONTRACT_STATUS_MEDIA, CONTRACT_STATUS_CN,
                                 STATUS_DEL, STATUS_ON, CONTRACT_STATUS_NEW, CONTRACT_STATUS_DELETEAPPLY,
                                 CONTRACT_STATUS_DELETEAGREE, CONTRACT_STATUS_DELETEPASS)
from models.client_order import ClientOrder, ClientOrderExecutiveReport
from models.framework_order import FrameworkOrder
from models.douban_order import DoubanOrder, DoubanOrderExecutiveReport
from models.associated_douban_order import AssociatedDoubanOrder
from models.user import User, TEAM_LOCATION_CN
from models.excel import Excel
from models.attachment import Attachment
from models.download import (download_excel_table_by_doubanorders,
                             download_excel_table_by_frameworkorders)

from libs.signals import contract_apply_signal
from libs.paginator import Paginator
from controllers.tools import get_download_response
from controllers.data_query.helpers.outsource_helpers import write_client_excel

order_bp = Blueprint('order', __name__, template_folder='../templates/order')


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
        if ClientOrder.query.filter_by(campaign=form.campaign.data).count() > 0:
            flash(u'campaign名称已存在，请更换其他名称!', 'danger')
            return redirect(url_for("order.new_order"))
        order = ClientOrder.add(agent=Agent.get(form.agent.data),
                                client=Client.get(form.client.data),
                                campaign=form.campaign.data,
                                money=int(round(float(form.money.data or 0))),
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
                               sale_money=int(
                                   round(float(medium_moneys[x] or 0))),
                               medium_money=0,
                               medium_money2=0,
                               medium_start=order.client_start,
                               medium_end=order.client_end,
                               creator=g.user)
                order.medium_orders = order.medium_orders + [mo]
                order.add_comment(g.user, u"新建了媒体订单: %s %s元" %
                                  (medium.name, mo.sale_money))
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
    order.status = STATUS_DEL
    order.save()
    return redirect(url_for("order.my_orders"))


@order_bp.route('/order/<order_id>/medium_order/<medium_id>/delete', methods=['GET'])
def medium_order_delete(order_id, medium_id):
    order = Order.get(medium_id)
    MediumOrderExecutiveReport.query.filter_by(order=order).delete()
    order.delete()
    return redirect(url_for("order.order_info", order_id=order_id, tab_id=1))


def _delete_executive_report(order):
    if order.__tablename__ == 'bra_douban_order':
        DoubanOrderExecutiveReport.query.filter_by(douban_order=order).delete()
    elif order.__tablename__ == 'bra_client_order':
        ClientOrderExecutiveReport.query.filter_by(client_order=order).delete()
        MediumOrderExecutiveReport.query.filter_by(client_order=order).delete()
    return


def _insert_executive_report(order, rtype):
    if order.contract == '' or order.contract_status not in [2, 4, 5]:
        return False
    if order.__tablename__ == 'bra_douban_order':
        if rtype:
            DoubanOrderExecutiveReport.query.filter_by(
                douban_order=order).delete()
        for k in order.pre_month_money():
            if not DoubanOrderExecutiveReport.query.filter_by(douban_order=order, month_day=k['month']).first():
                er = DoubanOrderExecutiveReport.add(douban_order=order,
                                                    money=k['money'],
                                                    month_day=k['month'],
                                                    days=k['days'],
                                                    create_time=None)
                er.save()
    elif order.__tablename__ == 'bra_client_order':
        if rtype:
            ClientOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
            MediumOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
        for k in order.pre_month_money():
            if not ClientOrderExecutiveReport.query.filter_by(client_order=order, month_day=k['month']).first():
                er = ClientOrderExecutiveReport.add(client_order=order,
                                                    money=k['money'],
                                                    month_day=k['month'],
                                                    days=k['days'],
                                                    create_time=None)
                er.save()
        for k in order.medium_orders:
            for i in k.pre_month_medium_orders_money():
                if not MediumOrderExecutiveReport.query.filter_by(client_order=order,
                                                                  order=k, month_day=i['month']).first():
                    er = MediumOrderExecutiveReport.add(client_order=order,
                                                        order=k,
                                                        medium_money=i[
                                                            'medium_money'],
                                                        medium_money2=i[
                                                            'medium_money2'],
                                                        sale_money=i[
                                                            'sale_money'],
                                                        month_day=i['month'],
                                                        days=i['days'],
                                                        create_time=None)
                    er.save()
    elif order.__tablename__ == 'bra_order':
        if rtype:
            MediumOrderExecutiveReport.query.filter_by(order=order).delete()
        for i in order.pre_month_medium_orders_money():
            if not MediumOrderExecutiveReport.query.filter_by(client_order=order.client_order,
                                                              order=order, month_day=i['month']).first():
                er = MediumOrderExecutiveReport.add(client_order=order.client_order,
                                                    order=order,
                                                    medium_money=i[
                                                        'medium_money'],
                                                    medium_money2=i[
                                                        'medium_money2'],
                                                    sale_money=i[
                                                        'sale_money'],
                                                    month_day=i['month'],
                                                    days=i['days'],
                                                    create_time=None)
                er.save()
    return True


@order_bp.route('/order/<order_id>/executive_report', methods=['GET'])
def executive_report(order_id):
    rtype = request.values.get('rtype', '')
    otype = request.values.get('otype', 'ClientOrder')
    if otype == 'DoubanOrder':
        order = DoubanOrder.get(order_id)
    else:
        order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin() or not g.user.is_media() or not g.user.is_contract() or not g.user.is_media_leader():
        abort(402)
    _insert_executive_report(order, rtype)
    if order.__tablename__ == 'bra_douban_order':
        return redirect(url_for("order.my_douban_orders"))
    else:
        return redirect(url_for("order.my_orders"))


@order_bp.route('/order/<order_id>/recovery', methods=['GET'])
def order_recovery(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"客户订单: %s-%s 已恢复" % (order.client.name, order.campaign), 'success')
    order.status = STATUS_ON
    order.save()
    return redirect(url_for("order.delete_orders"))


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


def get_medium_form(order, user=None):
    medium_form = MediumOrderForm()
    if user.is_super_leader() or user.is_media() or user.is_media_leader():
        medium_form.medium.choices = [
            (medium.id, medium.name) for medium in Medium.all()]
    else:
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
    if not order or order.status == 0:
        if g.user.is_super_admin():
            pass
        else:
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
                    order.money = int(round(float(client_form.money.data or 0)))
                    order.client_start = client_form.client_start.data
                    order.client_end = client_form.client_end.data
                    order.reminde_date = client_form.reminde_date.data
                    order.direct_sales = User.gets(
                        client_form.direct_sales.data)
                    order.agent_sales = User.gets(client_form.agent_sales.data)
                    order.contract_type = client_form.contract_type.data
                    order.resource_type = client_form.resource_type.data
                    order.sale_type = client_form.sale_type.data
                    order.save()
                    order.add_comment(g.user, u"更新了客户订单")
                    flash(u'[客户订单]%s 保存成功!' % order.name, 'success')
                    _insert_executive_report(order, 'reload')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                _insert_executive_report(order, '')
                for mo in order.medium_orders:
                    mo.medium_contract = request.values.get(
                        "medium_contract_%s" % mo.id, "")
                    mo.save()
                for o in order.associated_douban_orders:
                    o.contract = request.values.get(
                        "douban_contract_%s" % o.id, "")
                    o.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-致趣: %s\n\n" % (
                    order.agent.name, order.contract)
                for mo in order.medium_orders:
                    msg = msg + \
                        u"致趣-%s: %s\n\n" % (mo.medium.name, mo.medium_contract or "")
                for o in order.associated_douban_orders:
                    msg = msg + \
                        u"%s-豆瓣: %s\n\n" % (o.medium_order.medium.name, o.contract or "")
                to_users = order.direct_sales + \
                    order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(
                    current_app._get_current_object(), apply_context=apply_context)
                flash(u'[%s] 已发送邮件给 %s ' %
                      (order.name, ', '.join(to_emails)), 'info')

                order.add_comment(g.user, u"更新合同号, %s" % msg)

    new_medium_form = MediumOrderForm()
    new_medium_form.medium_start.data = order.client_start
    new_medium_form.medium_end.data = order.client_end
    new_medium_form.discount.hidden = True

    new_associated_douban_form = AssociatedDoubanOrderForm()
    new_associated_douban_form.medium_order.choices = [(mo.id, "%s-%s" % (mo.name, mo.start_date_cn))
                                                       for mo in order.medium_orders]
    new_associated_douban_form.campaign.data = order.campaign

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'client_form': client_form,
               'new_medium_form': new_medium_form,
               'medium_forms': [(get_medium_form(mo, g.user), mo) for mo in order.medium_orders],
               'new_associated_douban_form': new_associated_douban_form,
               'order': order,
               'reminder_emails': reminder_emails,
               'now_date': datetime.now(),
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
                       medium_money=int(
                           round(float(form.medium_money.data or 0))),
                       medium_money2=int(
                           round(float(form.medium_money2.data or 0))),
                       sale_money=int(round(float(form.sale_money.data or 0))),
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
        co.add_comment(g.user, u"新建了媒体订单: %s %s %s" %
                       (mo.medium.name, mo.sale_money, mo.medium_money))
        flash(u'[媒体订单]新建成功!', 'success')
        return redirect(mo.info_path())
    return tpl('order_new_medium.html', form=form)


@order_bp.route('/order/medium_order/<mo_id>/', methods=['POST'])
def medium_order(mo_id):
    mo = Order.get(mo_id)
    if not mo:
        abort(404)
    form = MediumOrderForm(request.form)
    if g.user.is_super_leader() or g.user.is_media() or g.user.is_media_leader():
        mo.medium = Medium.get(form.medium.data)
    mo.medium_money = int(round(float(form.medium_money.data or 0)))
    mo.medium_money2 = int(round(float(form.medium_money2.data or 0)))
    mo.sale_money = int(round(float(form.sale_money.data or 0)))
    mo.medium_CPM = form.medium_CPM.data
    mo.sale_CPM = form.sale_CPM.data
    mo.medium_start = form.medium_start.data
    mo.medium_end = form.medium_end.data
    mo.operaters = User.gets(form.operaters.data)
    mo.designers = User.gets(form.designers.data)
    mo.planers = User.gets(form.planers.data)
    mo.discount = form.discount.data
    mo.save()
    mo.client_order.add_comment(
        g.user, u"更新了媒体订单: %s %s %s" % (mo.medium.name, mo.sale_money, mo.medium_money))
    flash(u'[媒体订单]%s 保存成功!' % mo.name, 'success')
    _insert_executive_report(mo, 'reload')
    return redirect(mo.info_path())


@order_bp.route('/order/medium_order/<medium_id>/edit_cpm', methods=['POST'])
def order_medium_edit_cpm(medium_id):
    mo = Order.get(medium_id)
    if not mo:
        abort(404)
    cpm = request.values.get('cpm', '')
    medium_money = request.values.get('medium_money', '')
    if cpm != '':
        cpm = int(round(float(cpm)))
        if mo.medium_CPM != cpm:
            mo.client_order.add_comment(
                g.user, u"更新了媒体订单: %s 的实际量%s CPM" % (mo.medium.name, cpm))
        mo.medium_CPM = cpm
    if medium_money != '':
        medium_money = int(round(float(medium_money)))
        if mo.medium_money != medium_money:
            mo.client_order.add_comment(
                g.user, u"更新了媒体订单: %s 的分成金额%s " % (mo.medium.name, medium_money))
        mo.medium_money = medium_money
    mo.save()
    if medium_money != '':
        _insert_executive_report(mo, 'reload')
    flash(u'[媒体订单]%s 保存成功!' % mo.name, 'success')
    return redirect(mo.info_path())


@order_bp.route('/order/new_associated_douban_order', methods=['POST'])
def new_associated_douban_order():
    form = AssociatedDoubanOrderForm(request.form)
    ao = AssociatedDoubanOrder.add(medium_order=Order.get(form.medium_order.data),
                                   campaign=form.campaign.data,
                                   money=int(
                                       round(float(form.money.data or 0))),
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
    ao.money = int(round(float(form.money.data or 0)))
    ao.save()
    ao.medium_order.client_order.add_comment(g.user,
                                             u"更新了关联豆瓣订单: %s - %s - %s" % (
                                                 ao.medium_order.medium.name,
                                                 ao.campaign, ao.money))
    flash(u'[关联豆瓣订单]%s 保存成功!' % ao.name, 'success')
    return redirect(ao.info_path())


@order_bp.route('/client_order/<order_id>/contract', methods=['POST'])
def client_order_contract(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    order = ClientOrder.get(order_id)
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('order.my_orders'))
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
        _insert_executive_report(order, '')
    elif action == 4:
        order.contract_status = CONTRACT_STATUS_APPLYREJECT
        action_msg = u"审批未被通过"
        to_users = to_users + User.medias()
    elif action == 5:
        order.contract_status = CONTRACT_STATUS_APPLYPRINT
        action_msg = u"申请打印合同"
        to_users = to_users + User.contracts() + order.leaders
    elif action == 6:
        order.contract_status = CONTRACT_STATUS_PRINTED
        action_msg = u"合同打印完毕"
    elif action == 7:
        action_msg = u"撤单申请，请部门leader确认"
        order.contract_status = CONTRACT_STATUS_DELETEAPPLY
        to_users = to_users + order.leaders + User.medias() + User.contracts()
    elif action == 8:
        action_msg = u"确认撤单，请super_leader同意"
        order.contract_status = CONTRACT_STATUS_DELETEAGREE
        to_users = to_users + order.leaders + User.medias() + User.contracts()
    elif action == 9:
        action_msg = u"同意撤单"
        order.contract_status = CONTRACT_STATUS_DELETEPASS
        order.status = STATUS_DEL
        to_users = to_users + order.leaders + User.medias() + User.contracts()
        if order.__tablename__ == 'bra_douban_order' and order.contract:
            to_users += User.douban_contracts()
        _delete_executive_report(order)
    elif action == 0:
        order.contract_status = CONTRACT_STATUS_NEW
        order.insert_reject_time()
        action_msg = u"合同被驳回，请从新提交审核"
        _delete_executive_report(order)
    order.save()
    flash(u'[%s] %s ' % (order.name, action_msg), 'success')
    to_emails = list(set(emails + [x.email for x in to_users]))
    if order.__tablename__ == 'bra_douban_order' and order.contract_status == 4 and action == 5:
        to_emails = list(
            set([k.email for k in User.douban_contracts()] + to_emails))
# 关联豆瓣订单 申请打印 不发送豆瓣管理员
#    elif (order.__tablename__ == 'bra_client_order'
#          and order.associated_douban_orders and order.contract_status == 4 and action == 5):
#        to_emails = list(
#            set([k.email for k in User.douban_contracts()] + to_emails))
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order}
    contract_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context, action=action)
    flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')
    order.add_comment(g.user, u"%s \n\r\n\r %s" % (action_msg, msg))


@order_bp.route('/orders', methods=['GET'])
def orders():
    orders = ClientOrder.all()
    status_id = int(request.args.get('selected_status', -1))
    return display_orders(orders, u'新媒体订单列表', status_id)


@order_bp.route('/delete_orders', methods=['GET'])
def delete_orders():
    orders = ClientOrder.delete_all()
    status_id = int(request.args.get('selected_status', -1))
    return display_orders(orders, u'已删除订单列表', status_id)


@order_bp.route('/my_orders', methods=['GET'])
def my_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or g.user.is_media_leader():
        orders = ClientOrder.all()
    elif g.user.is_leader():
        orders = [
            o for o in ClientOrder.all() if g.user.location in o.locations]
    else:
        orders = ClientOrder.get_order_by_user(g.user)

    if not request.args.get('selected_status'):
        if g.user.is_admin():
            status_id = -1
        elif g.user.is_super_leader():
            status_id = -1
        elif g.user.is_leader():
            orders = [o for o in orders if g.user.location in o.locations]
            status_id = -1
        elif g.user.is_contract():
            orders = [o for o in orders if o.contract_status in [
                CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYPRINT]]
            status_id = CONTRACT_STATUS_APPLYPASS
        elif g.user.is_media() or g.user.is_media_leader():
            orders = [
                o for o in orders if o.contract_status in [CONTRACT_STATUS_MEDIA, CONTRACT_STATUS_APPLYREJECT]]
            status_id = CONTRACT_STATUS_MEDIA
        else:
            status_id = -1
    else:
        status_id = int(request.args.get('selected_status'))
    return display_orders(orders, u'我的新媒体订单', status_id)


def display_orders(orders, title, status_id=-1):
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')
    search_medium = int(request.args.get('search_medium', 0))

    if start_time and not end_time:
        start_time = datetime.strptime(start_time, '%Y-%m-%d').date()
        orders = [k for k in orders if k.create_time.date() >= start_time]
    elif not start_time and end_time:
        end_time = datetime.strptime(end_time, '%Y-%m-%d').date()
        orders = [k for k in orders if k.create_time.date() <= end_time]
    elif start_time and end_time:
        start_time = datetime.strptime(start_time, '%Y-%m-%d').date()
        end_time = datetime.strptime(end_time, '%Y-%m-%d').date()
        orders = [k for k in orders if k.create_time.date(
        ) >= start_time and k.create_time.date() <= end_time]

    if search_medium > 0:
        orders = [k for k in orders if search_medium in k.medium_ids]
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower().strip() in o.search_info.lower()]
    if orderby and len(orders):
        orders = sorted(
            orders, key=lambda x: getattr(x, orderby), reverse=True)
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    if 'download' == request.args.get('action', ''):
        return write_client_excel(orders)
    else:
        paginator = Paginator(orders, ORDER_PAGE_NUM)
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(paginator.num_pages)
        params = '&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s\
        &start_time=%s&end_time=%s&search_medium=%s' % (
            orderby, search_info, location_id, status_id, start_time, end_time, search_medium)
        return tpl('orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   search_info=search_info, page=page, mediums=Medium.all(),
                   orderby=orderby, now_date=datetime.now().date(),
                   start_time=start_time, end_time=end_time, search_medium=search_medium,
                   params=params)


######################
# framework order
######################
@order_bp.route('/new_framework_order', methods=['GET', 'POST'])
def new_framework_order():
    form = FrameworkOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = FrameworkOrder.add(group=Group.get(form.group.data),
                                   agents=Agent.gets(form.agents.data),
                                   description=form.description.data,
                                   money=int(
                                       round(float(form.money.data or 0))),
                                   client_start=form.client_start.data,
                                   client_end=form.client_end.data,
                                   reminde_date=form.reminde_date.data,
                                   direct_sales=User.gets(
                                       form.direct_sales.data),
                                   agent_sales=User.gets(form.agent_sales.data),
                                   contract_type=form.contract_type.data,
                                   creator=g.user,
                                   inad_rebate=form.inad_rebate.data,
                                   douban_rebate=form.douban_rebate.data,
                                   create_time=datetime.now())
        order.add_comment(g.user, u"新建了该框架订单")
        flash(u'新建框架订单成功, 请上传合同!', 'success')
        # 框架合同同步甲方返点信息
        _insert_agent_rebate(order)
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
    order.status = STATUS_DEL
    order.save()
    return redirect(url_for("order.my_framework_orders"))


@order_bp.route('/framework_order/<order_id>/recovery', methods=['GET'])
def framework_recovery(order_id):
    order = FrameworkOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"框架订单: %s 已恢复" % (order.group.name), 'success')
    order.status = STATUS_ON
    order.save()
    return redirect(url_for("order.framework_delete_orders"))


def get_framework_form(order):
    framework_form = FrameworkOrderForm()
    framework_form.group.data = order.group.id
    framework_form.agents.data = [a.id for a in order.agents]
    framework_form.description.data = order.description
    framework_form.money.data = order.money
    framework_form.client_start.data = order.client_start
    framework_form.client_end.data = order.client_end
    framework_form.reminde_date.data = order.reminde_date
    framework_form.direct_sales.data = [u.id for u in order.direct_sales]
    framework_form.agent_sales.data = [u.id for u in order.agent_sales]
    framework_form.contract_type.data = order.contract_type
    framework_form.inad_rebate.data = order.inad_rebate or 0.0
    framework_form.douban_rebate.data = order.douban_rebate or 0.0
    return framework_form


################
# 导入甲方返点信息
################
def _insert_agent_rebate(order):
    agents = order.agents
    start_date = order.start_date.replace(month=1, day=1)
    inad_rebate = order.inad_rebate
    douban_rebate = order.douban_rebate

    for agent in agents:
        agent_rebate = AgentRebate.query.filter_by(
            agent=agent, year=start_date).first()
        if agent_rebate:
            agent_rebate.inad_rebate = inad_rebate
            agent_rebate.douban_rebate = douban_rebate
            agent_rebate.create_time = datetime.now()
            agent_rebate.creator = g.user
            agent_rebate.save()
        else:
            AgentRebate.add(agent=agent,
                            douban_rebate=douban_rebate,
                            inad_rebate=inad_rebate,
                            year=start_date,
                            creator=g.user,
                            create_time=datetime.now())
    return


@order_bp.route('/framework_order/<order_id>/info', methods=['GET', 'POST'])
def framework_order_info(order_id):
    order = FrameworkOrder.get(order_id)
    if not order or order.status == 0:
        abort(404)
    framework_form = get_framework_form(order)

    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        if info_type == 0:
            if not order.can_admin(g.user) and not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系该框架的创建者或者销售同事!', 'danger')
            else:
                framework_form = FrameworkOrderForm(request.form)
                agents = Agent.gets(framework_form.agents.data)
                if framework_form.validate():
                    order.group = Group.get(framework_form.group.data)
                    order.agents = agents
                    order.description = framework_form.description.data
                    order.money = framework_form.money.data
                    order.client_start = framework_form.client_start.data
                    order.client_end = framework_form.client_end.data
                    order.reminde_date = framework_form.reminde_date.data
                    order.direct_sales = User.gets(
                        framework_form.direct_sales.data)
                    order.agent_sales = User.gets(
                        framework_form.agent_sales.data)
                    order.contract_type = framework_form.contract_type.data
                    order.inad_rebate = framework_form.inad_rebate.data
                    order.douban_rebate = framework_form.douban_rebate.data
                    order.save()
                    order.add_comment(g.user, u"更新了该框架订单")
                    flash(u'[框架订单]%s 保存成功!' % order.name, 'success')

                    # 框架合同同步甲方返点信息
                    _insert_agent_rebate(order)
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.douban_contract = request.values.get(
                    "douban_contract", "")
                order.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-致趣: %s\n\n豆瓣合同号: %s" % (
                    order.group.name, order.contract, order.douban_contract)
                to_users = order.direct_sales + \
                    order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(
                    current_app._get_current_object(), apply_context=apply_context)
                flash(u'[%s] 已发送邮件给 %s ' %
                      (order.name, ', '.join(to_emails)), 'info')
                order.add_comment(g.user, u"更新合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'framework_form': framework_form,
               'order': order,
               'now_date': datetime.now(),
               'reminder_emails': reminder_emails}
    return tpl('framework_detail_info.html', **context)


@order_bp.route('/my_framework_orders', methods=['GET'])
def my_framework_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or g.user.is_media_leader():
        orders = FrameworkOrder.all()
        if g.user.is_admin():
            pass
        elif g.user.is_super_leader():
            orders = [o for o in orders if o.contract_status ==
                      CONTRACT_STATUS_APPLYCONTRACT]
        elif g.user.is_contract():
            orders = [o for o in orders if o.contract_status in [
                CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYPRINT]]
        elif g.user.is_media() or g.user.is_media_leader():
            orders = [
                o for o in orders if o.contract_status == CONTRACT_STATUS_MEDIA]
    elif g.user.is_leader():
        orders = [
            o for o in FrameworkOrder.all() if g.user.location in o.locations]
    else:
        orders = FrameworkOrder.get_order_by_user(g.user)
    return framework_display_orders(orders, u'我的框架订单')


@order_bp.route('/framework_orders', methods=['GET'])
def framework_orders():
    orders = FrameworkOrder.all()
    return framework_display_orders(orders, u'框架订单列表')


@order_bp.route('/framework_delete_orders', methods=['GET'])
def framework_delete_orders():
    orders = FrameworkOrder.delete_all()
    return framework_display_orders(orders, u'已删除的框架订单列表')


def framework_display_orders(orders, title):
    page = int(request.args.get('p', 1))
    if 'download' == request.args.get('action', ''):
        filename = (
            "%s-%s.xls" % (u"框架订单", datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = Excel().write_excle(
            download_excel_table_by_frameworkorders(orders))
        response = get_download_response(xls, filename)
        return response
    else:
        paginator = Paginator(orders, ORDER_PAGE_NUM)
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(paginator.num_pages)
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
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('order.framework_orders'))
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
                                money=int(round(float(form.money.data or 0))),
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
    order.status = STATUS_DEL
    order.save()
    return redirect(url_for("order.my_douban_orders"))


@order_bp.route('/douban_order/<order_id>/recovery', methods=['GET'])
def douban_order_recovery(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"豆瓣订单: %s-%s 已恢复" % (order.client.name, order.campaign), 'success')
    order.status = STATUS_ON
    order.save()
    return redirect(url_for("order.douban_delete_orders"))


@order_bp.route('/douban_order/<order_id>/edit_cpm', methods=['POST'])
def douban_order_edit_cpm(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    cpm = int(round(float(request.values.get('cpm', 0))))
    order.medium_CPM = cpm
    order.save()
    order.add_comment(
        g.user, u"更新了直签豆瓣订单: %s 的实际量%s CPM" % (order.name, order.medium_CPM))
    flash(u'[直签豆瓣订单]%s 更新成功!' % order.name, 'success')
    return redirect(url_for("order.douban_order_info", order_id=order.id))


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
    if not order or order.status == 0:
        if g.user.is_super_admin():
            pass
        else:
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
                    order.money = int(round(float(form.money.data or 0)))
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
                    _insert_executive_report(order, 'reload')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                _insert_executive_report(order, '')
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-豆瓣: %s\n\n" % (
                    order.agent.name, order.contract)
                to_users = order.direct_sales + \
                    order.agent_sales + [order.creator, g.user]
                to_emails = [x.email for x in set(to_users)]
                apply_context = {"sender": g.user,
                                 "to": to_emails,
                                 "action_msg": action_msg,
                                 "msg": msg,
                                 "order": order}
                contract_apply_signal.send(
                    current_app._get_current_object(), apply_context=apply_context)
                flash(u'[%s] 已发送邮件给 %s ' %
                      (order.name, ', '.join(to_emails)), 'info')
                order.add_comment(g.user, u"更新了合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'douban_form': form,
               'order': order,
               'now_date': datetime.now(),
               'reminder_emails': reminder_emails}
    return tpl('douban_detail_info.html', **context)


@order_bp.route('/my_douban_orders', methods=['GET'])
def my_douban_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or g.user.is_media_leader():
        orders = DoubanOrder.all()
    elif g.user.is_leader():
        orders = [
            o for o in DoubanOrder.all() if g.user.location in o.locations]
    else:
        orders = DoubanOrder.get_order_by_user(g.user)

    if not request.args.get('selected_status'):
        if g.user.is_admin():
            status_id = -1
        elif g.user.is_super_leader():
            status_id = -1
        elif g.user.is_leader():
            orders = [o for o in orders if g.user.location in o.locations]
            status_id = -1
        elif g.user.is_contract():
            orders = [o for o in orders if o.contract_status in [
                CONTRACT_STATUS_APPLYPASS, CONTRACT_STATUS_APPLYPRINT]]
            status_id = CONTRACT_STATUS_APPLYPASS
        elif g.user.is_media() or g.user.is_media_leader():
            orders = [
                o for o in orders if o.contract_status == CONTRACT_STATUS_MEDIA]
            status_id = CONTRACT_STATUS_MEDIA
        else:
            status_id = -1
    else:
        status_id = int(request.args.get('selected_status'))
    return douban_display_orders(orders, u'我的直签豆瓣订单', status_id)


@order_bp.route('/douban_orders', methods=['GET'])
def douban_orders():
    orders = DoubanOrder.all()
    status_id = int(request.args.get('selected_status', -1))
    return douban_display_orders(orders, u'全部直签豆瓣订单', status_id)


@order_bp.route('/douban_delete_orders', methods=['GET'])
def douban_delete_orders():
    orders = DoubanOrder.delete_all()
    status_id = int(request.args.get('selected_status', -1))
    return douban_display_orders(orders, u'已删除的直签豆瓣订单', status_id)


def douban_display_orders(orders, title, status_id=-1):
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
    if 'download' == request.args.get('action', ''):
        filename = (
            "%s-%s.xls" % (u"直签豆瓣订单", datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = Excel().write_excle(
            download_excel_table_by_doubanorders(orders))
        response = get_download_response(xls, filename)
        return response
    else:
        paginator = Paginator(orders, ORDER_PAGE_NUM)
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(paginator.num_pages)
        return tpl('douban_orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   orderby=orderby, now_date=datetime.now().date(),
                   search_info=search_info, page=page,
                   params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s' %
                   (orderby, search_info, location_id, status_id))


@order_bp.route('/douban_order/<order_id>/contract', methods=['POST'])
def douban_order_contract(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    order = DoubanOrder.get(order_id)
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('order.douban_orders'))
    return redirect(url_for("order.douban_order_info", order_id=order.id))


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
    attachment_status_change(
        order.medium_order.client_order, attachment_id, status)
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
    msg = u"文件名:%s\n状态:%s\n如有疑问, 请联系合同管理员" % (
        attachment.filename, attachment.status_cn)
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order}
    contract_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
