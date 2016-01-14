# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, request, redirect, abort, url_for, g
from flask import render_template as tpl, flash, current_app
from wtforms import SelectMultipleField
from libs.wtf import Form

from models.user import User, TEAM_LOCATION_CN
from models.excel import Excel
from models.attachment import Attachment

# from models.download import (download_excel_table_by_doubanorders,
#                             download_excel_table_by_frameworkorders)

from ..models.client import searchAdClient, searchAdGroup, searchAdAgent, searchAdAgentRebate
from ..models.medium import searchAdMedium
from ..models.order import searchAdOrder, searchAdMediumOrderExecutiveReport
from searchAd.models.rebate_order import searchAdRebateOrder, searchAdRebateOrderExecutiveReport
from ..models.client_order import searchAdClientOrder, searchAdClientOrderExecutiveReport
from ..models.framework_order import searchAdFrameworkOrder

from ..models.client_order import (CONTRACT_STATUS_APPLYCONTRACT, CONTRACT_STATUS_APPLYPASS,
                                   CONTRACT_STATUS_APPLYREJECT, CONTRACT_STATUS_APPLYPRINT,
                                   CONTRACT_STATUS_PRINTED, CONTRACT_STATUS_MEDIA, CONTRACT_STATUS_CN,
                                   STATUS_DEL, STATUS_ON, CONTRACT_STATUS_NEW, CONTRACT_STATUS_DELETEAPPLY,
                                   CONTRACT_STATUS_DELETEAGREE, CONTRACT_STATUS_DELETEPASS,
                                   CONTRACT_STATUS_PRE_FINISH, CONTRACT_STATUS_FINISH)
from ..forms.order import ClientOrderForm, MediumOrderForm, FrameworkOrderForm, RebateOrderForm

from libs.signals import contract_apply_signal
from libs.email_signals import zhiqu_contract_apply_signal
from libs.paginator import Paginator
from controllers.tools import get_download_response
from controllers.data_query.helpers.outsource_helpers import write_searchAd_client_excel

searchAd_order_bp = Blueprint(
    'searchAd_order', __name__, template_folder='../../templates/searchAdorder')

ORDER_PAGE_NUM = 50


def _delete_executive_report(order):
    if order.__tablename__ == 'searchad_bra_rebate_order':
        searchAdRebateOrderExecutiveReport.query.filter_by(
            rebate_order=order).delete()
    elif order.__tablename__ == 'searchAd_bra_client_order':
        searchAdClientOrderExecutiveReport.query.filter_by(
            client_order=order).delete()
        searchAdMediumOrderExecutiveReport.query.filter_by(
            client_order=order).delete()
    return


def _insert_executive_report(order, rtype):
    if order.contract_status not in [2, 4, 5, 20]:
        return False
    if order.__tablename__ == 'searchad_bra_rebate_order':
        if rtype:
            searchAdRebateOrderExecutiveReport.query.filter_by(
                rebate_order=order).delete()
        for k in order.pre_month_money():
            if not searchAdRebateOrderExecutiveReport.query.filter_by(rebate_order=order, month_day=k['month']).first():
                er = searchAdRebateOrderExecutiveReport.add(rebate_order=order,
                                                            money=k['money'],
                                                            month_day=k[
                                                                'month'],
                                                            days=k['days'],
                                                            create_time=None)
                er.save()
    elif order.__tablename__ == 'searchAd_bra_client_order':
        if rtype:
            searchAdClientOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
            searchAdMediumOrderExecutiveReport.query.filter_by(
                client_order=order).delete()
        for k in order.pre_month_money():
            if not searchAdClientOrderExecutiveReport.query.filter_by(client_order=order, month_day=k['month']).first():
                er = searchAdClientOrderExecutiveReport.add(client_order=order,
                                                            money=k['money'],
                                                            month_day=k[
                                                                'month'],
                                                            days=k['days'],
                                                            create_time=None)
                er.save()
        for k in order.medium_orders:
            for i in k.pre_month_medium_orders_money():
                if not searchAdMediumOrderExecutiveReport.query.filter_by(client_order=order,
                                                                          order=k, month_day=i['month']).first():
                    er = searchAdMediumOrderExecutiveReport.add(client_order=order,
                                                                order=k,
                                                                medium_money=0,
                                                                medium_money2=i[
                                                                    'medium_money2'],
                                                                sale_money=i[
                                                                    'sale_money'],
                                                                month_day=i[
                                                                    'month'],
                                                                days=i['days'],
                                                                create_time=None)
                    er.save()
    elif order.__tablename__ == 'searchAd_bra_order':
        if rtype:
            searchAdMediumOrderExecutiveReport.query.filter_by(
                order=order).delete()
        for i in order.pre_month_medium_orders_money():
            if not searchAdMediumOrderExecutiveReport.query.filter_by(client_order=order.client_order,
                                                                      order=order, month_day=i['month']).first():
                er = searchAdMediumOrderExecutiveReport.add(client_order=order.client_order,
                                                            order=order,
                                                            medium_money=0,
                                                            medium_money2=i[
                                                                'medium_money2'],
                                                            sale_money=i[
                                                                'sale_money'],
                                                            month_day=i[
                                                                'month'],
                                                            days=i['days'],
                                                            create_time=None)
                er.save()
    return True


@searchAd_order_bp.route('/order/<order_id>/executive_report', methods=['GET'])
def executive_report(order_id):
    rtype = request.values.get('rtype', '')
    order = searchAdClientOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    _insert_executive_report(order, rtype)
    if order.__tablename__ == 'searchad_bra_rebate_order':
        return redirect(url_for("searchAd_order.rebate_orders"))
    else:
        return redirect(url_for("searchAd_order.searchAd_orders"))


@searchAd_order_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('searchAd_order.my_searchAd_orders'))


@searchAd_order_bp.route("/new_order", methods=['GET', 'POST'])
def new_searchAd_order():
    form = ClientOrderForm(request.form)
    mediums = [(m.id, m.name) for m in searchAdMedium.all()]
    if request.method == 'POST' and form.validate():
        if searchAdClientOrder.query.filter_by(campaign=form.campaign.data).count() > 0:
            flash(u'campaign名称已存在，请更换其他名称!', 'danger')
            return redirect(url_for("searchAd_order.new_searchAd_order"))
        # 超级管理员新建合同直接为审批通过
        if g.user.is_super_admin():
            contract_status = 2
        else:
            contract_status = 0
        order = searchAdClientOrder.add(agent=searchAdAgent.get(form.agent.data),
                                        framework_order_id=form.framework_order_id.data,
                                        client=searchAdClient.get(
                                            form.client.data),
                                        campaign=form.campaign.data,
                                        money=int(
                                            round(float(form.money.data or 0))),
                                        client_start=form.client_start.data,
                                        client_end=form.client_end.data,
                                        reminde_date=form.reminde_date.data,
                                        direct_sales=User.gets(
                                            form.direct_sales.data),
                                        agent_sales=[],
                                        contract_status=contract_status,
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
        sale_moneys = request.values.getlist('sale_money')
        medium_money2s = request.values.getlist('medium_money2')
        if medium_ids and sale_moneys and medium_money2s and len(medium_ids) == len(sale_moneys) == len(medium_money2s):
            for x in range(len(medium_ids)):
                medium = searchAdMedium.get(medium_ids[x])
                mo = searchAdOrder.add(campaign=order.campaign,
                                       medium=medium,
                                       sale_money=int(
                                           round(float(sale_moneys[x] or 0))),
                                       medium_money=0,
                                       medium_money2=int(
                                           round(float(medium_money2s[x] or 0))),
                                       medium_start=order.client_start,
                                       medium_end=order.client_end,
                                       creator=g.user)
                order.medium_orders = order.medium_orders + [mo]
                order.add_comment(g.user, u"新建了媒体订单: %s %s元" %
                                  (medium.name, mo.sale_money))
        order.save()
        flash(u'新建客户订单成功, 请上传合同和排期!', 'success')
        if g.user.is_super_admin():
            _insert_executive_report(order, 'reload')
        return redirect(order.info_path())
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('searchad_new_searchad_order.html', form=form, mediums=mediums)


@searchAd_order_bp.route('/orders', methods=['GET'])
def searchAd_orders():
    orders = searchAdClientOrder.all()
    status_id = int(request.args.get('selected_status', -1))
    return display_orders(orders, u'搜索广告订单列表', status_id)


@searchAd_order_bp.route('/order/<order_id>/info/<tab_id>', methods=['GET', 'POST'])
def order_info(order_id, tab_id=1):
    order = searchAdClientOrder.get(order_id)
    if not order or order.status == 0:
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
                    order.agent = searchAdAgent.get(client_form.agent.data)
                    order.framework_order_id = client_form.framework_order_id.data,
                    order.client = searchAdClient.get(client_form.client.data)
                    order.campaign = client_form.campaign.data
                    order.money = int(
                        round(float(client_form.money.data or 0)))
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
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-致趣: %s\n\n" % (
                    order.agent.name, order.contract)
                for mo in order.medium_orders:
                    msg = msg + \
                        u"致趣-%s: %s\n\n" % (mo.medium.name,
                                            mo.medium_contract or "")
                to_users = order.direct_sales + \
                    order.agent_sales + [order.creator, g.user]

                context = {'order': order,
                           'sender': g.user,
                           'action_msg': action_msg,
                           'info': msg,
                           'to_users': to_users}
                zhiqu_contract_apply_signal.send(
                    current_app._get_current_object(), context=context)
                order.add_comment(g.user, u"更新合同号, %s" % msg)

    new_medium_form = MediumOrderForm()
    new_medium_form.medium_start.data = order.client_start
    new_medium_form.medium_end.data = order.client_end
    new_medium_form.discount.hidden = True

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'client_form': client_form,
               'new_medium_form': new_medium_form,
               'medium_forms': [(get_medium_form(mo, g.user), mo) for mo in order.medium_orders],
               'order': order,
               'reminder_emails': reminder_emails,
               'now_date': datetime.now(),
               'tab_id': int(tab_id)}
    return tpl('searchad_order_detail_info.html', **context)


@searchAd_order_bp.route('/order/<order_id>/new_medium', methods=['GET', 'POST'])
def order_new_medium(order_id):
    co = searchAdClientOrder.get(order_id)
    if not co:
        abort(404)
    form = MediumOrderForm(request.form)
    if request.method == 'POST':
        mo = searchAdOrder.add(campaign=co.campaign,
                               medium=searchAdMedium.get(form.medium.data),
                               medium_money=int(
                                   round(float(form.medium_money.data or 0))),
                               medium_money2=int(
                                   round(float(form.medium_money2.data or 0))),
                               sale_money=int(
                                   round(float(form.sale_money.data or 0))),
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
        _insert_executive_report(mo, 'reload')
        return redirect(mo.info_path())
    return tpl('searchAd_order_new_medium.html', form=form)


@searchAd_order_bp.route('/order/medium_order/<mo_id>/', methods=['POST'])
def medium_order(mo_id):
    mo = searchAdOrder.get(mo_id)
    if not mo:
        abort(404)
    form = MediumOrderForm(request.form)
    if g.user.is_super_leader() or g.user.is_media() or g.user.is_media_leader():
        mo.medium = searchAdMedium.get(form.medium.data)
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


@searchAd_order_bp.route('/order/medium_order/<medium_id>/edit_cpm', methods=['POST'])
def order_medium_edit_cpm(medium_id):
    mo = searchAdOrder.get(medium_id)
    if not mo:
        abort(404)
    cpm = request.values.get('cpm', '')
#    medium_money = request.values.get('medium_money', '')
    if cpm != '':
        cpm = int(round(float(cpm)))
        if mo.medium_CPM != cpm:
            mo.client_order.add_comment(
                g.user, u"更新了媒体订单: %s 的实际量%s CPM" % (mo.medium.name, cpm))
        mo.medium_CPM = cpm
#    if medium_money != '':
#        medium_money = int(round(float(medium_money)))
#        if mo.medium_money != medium_money:
#            mo.client_order.add_comment(
#                g.user, u"更新了媒体订单: %s 的分成金额%s " % (mo.medium.name, medium_money))
#        mo.medium_money = medium_money
    mo.save()
    if medium_money != '':
        _insert_executive_report(mo, 'reload')
    flash(u'[媒体订单]%s 保存成功!' % mo.name, 'success')
    return redirect(mo.info_path())


@searchAd_order_bp.route('/order/<order_id>/medium_order/<medium_id>/delete', methods=['GET'])
def medium_order_delete(order_id, medium_id):
    order = searchAdOrder.get(medium_id)
    searchAdMediumOrderExecutiveReport.query.filter_by(order=order).delete()
    order.delete()
    return redirect(order.info_path())


@searchAd_order_bp.route('/client_order/<order_id>/contract', methods=['POST'])
def client_order_contract(order_id):
    order = searchAdClientOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    order = searchAdClientOrder.get(order_id)
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('searchAd_order.my_searchAd_orders'))
    return redirect(order.info_path())


def contract_status_change(order, action, emails, msg):
    action_msg = ''
    #  发送邮件
    if order.__tablename__ in ['bra_searchAd_framework_order', 'searchad_bra_rebate_order']:
        to_users = order.sales + [order.creator, g.user]
    else:
        to_users = order.direct_sales + \
            order.agent_sales + [order.creator, g.user]
    if action == 1:
        order.contract_status = CONTRACT_STATUS_MEDIA
        action_msg = u"申请利润分配"
        to_users = to_users + order.leaders
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
        to_users = to_users
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
        to_users = to_users + order.leaders + User.contracts()
    elif action == 8:
        action_msg = u"确认撤单，请super_leader同意"
        order.contract_status = CONTRACT_STATUS_DELETEAGREE
        to_users = to_users + order.leaders + User.contracts()
    elif action == 9:
        action_msg = u"同意撤单"
        order.contract_status = CONTRACT_STATUS_DELETEPASS
        order.status = STATUS_DEL
        to_users = to_users + order.leaders + User.contracts()
        _delete_executive_report(order)
    elif action == 19:
        msg = request.values.get('finish_msg', '')
        finish_time = request.values.get('finish_time', datetime.now())
        action_msg = u"项目归档(预)"
        order.contract_status = CONTRACT_STATUS_PRE_FINISH
        order.finish_time = finish_time
        to_users = to_users + order.leaders + User.contracts()
    elif action == 20:
        msg = request.values.get('finish_msg', '')
        finish_time = request.values.get('finish_time', datetime.now())
        action_msg = u"项目归档（确认）"
        order.contract_status = CONTRACT_STATUS_FINISH
        order.finish_time = finish_time
        to_users = to_users + order.leaders + User.contracts()
    elif action == 0:
        order.contract_status = CONTRACT_STATUS_NEW
        order.insert_reject_time()
        action_msg = u"合同被驳回，请从新提交审核"
        _delete_executive_report(order)
    order.save()
    flash(u'[%s] %s ' % (order.name, action_msg), 'success')
    context = {
        "to_other": emails,
        "sender": g.user,
        "to_users": to_users,
        "action_msg": action_msg,
        "order": order,
        "info": msg,
        "action": order.contract_status
    }
    zhiqu_contract_apply_signal.send(
        current_app._get_current_object(), context=context)
    order.add_comment(g.user, u"%s \n\r\n\r %s" % (action_msg, msg))


@searchAd_order_bp.route('/my_orders', methods=['GET'])
def my_searchAd_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or g.user.is_media_leader() or g.user.is_aduit():
        orders = searchAdClientOrder.all()
    elif g.user.is_leader():
        orders = [
            o for o in searchAdClientOrder.all() if g.user.location in o.locations]
    else:
        orders = searchAdClientOrder.get_order_by_user(g.user)
    if not request.args.get('selected_status'):
        if g.user.is_admin():
            status_id = -1
        elif g.user.is_super_leader() or g.user.is_aduit():
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
    return display_orders(orders, u'我的搜索广告订单', status_id)


def display_orders(orders, title, status_id=-1):
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')
    year = int(request.values.get('year', datetime.now().year))
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
    orders = [k for k in orders if k.client_start.year == year or k.client_end == year]
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
        return write_searchAd_client_excel(orders)
    else:
        paginator = Paginator(orders, ORDER_PAGE_NUM)
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(paginator.num_pages)
        params = '&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s\
        &start_time=%s&end_time=%s&search_medium=%s&year=%s' % (
            orderby, search_info, location_id, status_id, start_time, end_time, search_medium, str(year))
        return tpl('searchad_orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   search_info=search_info, page=page, mediums=searchAdMedium.all(),
                   orderby=orderby, now_date=datetime.now().date(),
                   start_time=start_time, end_time=end_time, search_medium=search_medium,
                   params=params, year=year)


@searchAd_order_bp.route('/order/<order_id>/recovery', methods=['GET'])
def order_recovery(order_id):
    order = searchAdClientOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"客户订单: %s-%s 已恢复" % (order.client.name, order.campaign), 'success')
    order.status = STATUS_ON
    order.save()
    return redirect(url_for("searchAd_order.delete_orders"))


@searchAd_order_bp.route('/order/<order_id>/delete', methods=['GET'])
def order_delete(order_id):
    order = searchAdClientOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"客户订单: %s-%s 已删除" % (order.client.name, order.campaign), 'danger')
    order.status = STATUS_DEL
    order.save()
    return redirect(url_for("searchAd_order.my_searchAd_orders"))


@searchAd_order_bp.route('/delete_orders', methods=['GET'])
def delete_orders():
    orders = searchAdClientOrder.delete_all()
    status_id = int(request.args.get('selected_status', -1))
    return display_orders(orders, u'已删除搜索广告订单列表', status_id)


###################
# attachment
###################
@searchAd_order_bp.route('/client_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def client_attach_status(order_id, attachment_id, status):
    order = searchAdClientOrder.get(order_id)
    attachment_status_change(order, attachment_id, status)
    return redirect(order.info_path())


@searchAd_order_bp.route('/rebate_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def rebate_attach_status(order_id, attachment_id, status):
    order = searchAdRebateOrder.get(order_id)
    attachment_status_change(order, attachment_id, status)
    return redirect(order.info_path())


@searchAd_order_bp.route('/medium_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def medium_attach_status(order_id, attachment_id, status):
    order = searchAdOrder.get(order_id)
    attachment_status_change(order.client_order, attachment_id, status)
    return redirect(order.info_path())


@searchAd_order_bp.route('/framework_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def framework_attach_status(order_id, attachment_id, status):
    order = searchAdFrameworkOrder.get(order_id)
    attachment_status_change(order, attachment_id, status)
    return redirect(order.info_path())


def attachment_status_change(order, attachment_id, status):
    attachment = Attachment.get(attachment_id)
    attachment.attachment_status = status
    attachment.save()
    attachment_status_email(order, attachment)


def attachment_status_email(order, attachment):
    if order.__tablename__ in ['bra_searchAd_framework_order', 'searchad_bra_rebate_order']:
        to_users = order.sales + [order.creator, g.user]
    else:
        to_users = order.direct_sales + \
            order.agent_sales + [order.creator, g.user]
    action_msg = u"%s文件:%s-%s" % (attachment.type_cn,
                                  attachment.filename, attachment.status_cn)
    msg = u"文件名:%s\n状态:%s\n如有疑问, 请联系合同管理员" % (
        attachment.filename, attachment.status_cn)
    context = {'order': order,
               'sender': g.user,
               'action_msg': action_msg,
               'info': msg,
               'to_users': to_users}
    zhiqu_contract_apply_signal.send(
        current_app._get_current_object(), context=context)


def get_client_form(order):
    client_form = ClientOrderForm()
    client_form.framework_order_id.data = order.framework_order_id
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
    client_form.agent_sales.hidden = True
    return client_form


def get_medium_form(order, user=None):
    medium_form = MediumOrderForm()
    if user.is_super_leader() or user.is_media() or user.is_media_leader():
        medium_form.medium.choices = [
            (medium.id, medium.name) for medium in searchAdMedium.all()]
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
    medium_form.medium_money.hidden = True
    return medium_form


######################
# framework order
######################
@searchAd_order_bp.route('/new_framework_order', methods=['GET', 'POST'])
def new_framework_order():
    form = FrameworkOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        # 超级管理员新建合同直接为审批通过
        if g.user.is_super_admin():
            contract_status = 2
        else:
            contract_status = 0
        order = searchAdFrameworkOrder.add(agent=searchAdAgent.get(form.agent.data),
                                           description=form.description.data,
                                           money=int(
            round(float(form.money.data or 0))),
            client_start=form.client_start.data,
            client_end=form.client_end.data,
            reminde_date=form.reminde_date.data,
            sales=User.gets(form.sales.data),
            contract_type=form.contract_type.data,
            creator=g.user,
            rebate=form.rebate.data,
            contract_status=contract_status,
            create_time=datetime.now())
        order.add_comment(g.user, u"新建了框架订单")
        flash(u'新建框架订单成功, 请上传合同!', 'success')
        return redirect(url_for("searchAd_order.framework_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('/searchAdorder/searchad_new_framework_order.html', form=form)


@searchAd_order_bp.route('/framework_order/<order_id>/delete', methods=['GET'])
def framework_delete(order_id):
    order = searchAdFrameworkOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"框架订单: %s 已删除" % (order.agent.name), 'danger')
    order.status = STATUS_DEL
    order.save()
    return redirect(url_for("searchAd_order.my_framework_orders"))


@searchAd_order_bp.route('/framework_order/<order_id>/recovery', methods=['GET'])
def framework_recovery(order_id):
    order = searchAdFrameworkOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"框架订单: %s 已恢复" % (order.agent.name), 'success')
    order.status = STATUS_ON
    order.save()
    return redirect(url_for("searchAd_order.framework_delete_orders"))


def get_framework_form(order):
    framework_form = FrameworkOrderForm()
    framework_form.agent.data = order.agent.id
    framework_form.description.data = order.description
    framework_form.money.data = order.money
    framework_form.client_start.data = order.client_start
    framework_form.client_end.data = order.client_end
    framework_form.reminde_date.data = order.reminde_date
    framework_form.sales.data = [u.id for u in order.sales]
    framework_form.contract_type.data = order.contract_type
    framework_form.rebate.data = order.rebate or 0.0
    return framework_form


@searchAd_order_bp.route('/framework_order/<order_id>/info', methods=['GET', 'POST'])
def framework_order_info(order_id):
    order = searchAdFrameworkOrder.get(order_id)
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
                agent = searchAdAgent.get(framework_form.agent.data)
                if framework_form.validate():
                    order.agent = agent
                    order.description = framework_form.description.data
                    order.money = framework_form.money.data
                    order.client_start = framework_form.client_start.data
                    order.client_end = framework_form.client_end.data
                    order.reminde_date = framework_form.reminde_date.data
                    order.sales = User.gets(framework_form.sales.data)
                    order.contract_type = framework_form.contract_type.data
                    order.rebate = framework_form.rebate.data
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
                msg = u"新合同号如下:\n\n%s-致趣: %s" % (
                    order.agent.name, order.contract)
                to_users = order.sales + [order.creator, g.user]
                context = {'order': order,
                           'sender': g.user,
                           'action_msg': action_msg,
                           'info': msg,
                           'to_users': to_users}
                zhiqu_contract_apply_signal.send(
                    current_app._get_current_object(), context=context)
                order.add_comment(g.user, u"更新合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'framework_form': framework_form,
               'order': order,
               'now_date': datetime.now(),
               'reminder_emails': reminder_emails}
    return tpl('searchad_framework_detail_info.html', **context)


@searchAd_order_bp.route('/my_framework_orders', methods=['GET'])
def my_framework_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or g.user.is_media_leader() or g.user.is_aduit():
        orders = searchAdFrameworkOrder.all()
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
            o for o in searchAdFrameworkOrder.all() if g.user.location in o.locations]
    else:
        orders = searchAdFrameworkOrder.get_order_by_user(g.user)
    return framework_display_orders(orders, u'我的框架订单')


@searchAd_order_bp.route('/framework_orders', methods=['GET'])
def framework_orders():
    orders = searchAdFrameworkOrder.all()
    return framework_display_orders(orders, u'框架订单列表')


@searchAd_order_bp.route('/framework_delete_orders', methods=['GET'])
def framework_delete_orders():
    orders = searchAdFrameworkOrder.delete_all()
    return framework_display_orders(orders, u'已删除的框架订单列表')


def framework_display_orders(orders, title):
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.now().year))
    orders = [k for k in orders if k.client_start.year == year or k.client_end == year]
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
        return tpl('searchad_frameworks.html', title=title, orders=orders, page=page, year=year)


@searchAd_order_bp.route('/framework_order/<order_id>/contract', methods=['POST'])
def framework_order_contract(order_id):
    order = searchAdFrameworkOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('searchAd_order.framework_orders'))
    return redirect(url_for("searchAd_order.framework_order_info", order_id=order.id))


######################
#  rebate order
######################
@searchAd_order_bp.route('/new_rebate_order', methods=['GET', 'POST'])
def new_rebate_order():
    form = RebateOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = searchAdRebateOrder.add(client=searchAdClient.get(form.client.data),
                                        agent=searchAdAgent.get(
                                            form.agent.data),
                                        campaign=form.campaign.data,
                                        money=int(
                                            round(float(form.money.data or 0))),
                                        medium_CPM=form.medium_CPM.data,
                                        sale_CPM=form.sale_CPM.data,
                                        client_start=form.client_start.data,
                                        client_end=form.client_end.data,
                                        reminde_date=form.reminde_date.data,
                                        sales=User.gets(form.sales.data),
                                        operaters=User.gets(
                                            form.operaters.data),
                                        designers=User.gets(
                                            form.designers.data),
                                        planers=User.gets(form.planers.data),
                                        contract_type=form.contract_type.data,
                                        resource_type=form.resource_type.data,
                                        sale_type=form.sale_type.data,
                                        creator=g.user,
                                        create_time=datetime.now(),
                                        finish_time=datetime.now())
        order.add_comment(g.user, u"新建了该返点订单")
        flash(u'新建返点订单成功, 请上传合同!', 'success')
        return redirect(url_for("searchAd_order.rebate_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('/searchAdorder/searchad_new_rebate_order.html', form=form)


@searchAd_order_bp.route('/rebate_order/<order_id>/delete', methods=['GET'])
def rebate_order_delete(order_id):
    order = searchAdRebateOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"返点订单: %s-%s 已删除" % (order.client.name, order.campaign), 'danger')
    order.status = STATUS_DEL
    order.save()
    return redirect(url_for("searchAd_order.my_rebate_orders"))


@searchAd_order_bp.route('/rebate_order/<order_id>/recovery', methods=['GET'])
def rebate_order_recovery(order_id):
    order = searchAdRebateOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"返点订单: %s-%s 已恢复" % (order.client.name, order.campaign), 'success')
    order.status = STATUS_ON
    order.save()
    return redirect(url_for("searchAd_order.rebate_delete_orders"))


@searchAd_order_bp.route('/rebate_order/<order_id>/edit_cpm', methods=['POST'])
def rebate_order_edit_cpm(order_id):
    order = searchAdRebateOrder.get(order_id)
    if not order:
        abort(404)
    cpm = int(round(float(request.values.get('cpm', 0))))
    sale_CPM = int(request.values.get('sale_CPM', 0))
    if cpm != 0:
        order.medium_CPM = cpm
        order.add_comment(
            g.user, u"更新了单点订单: %s 的实际量%s CPM" % (order.name, order.medium_CPM))
    if sale_CPM != 0:
        if order.sale_CPM != sale_CPM:
            order.sale_CPM = sale_CPM
            order.add_comment(
                g.user, u"更新了返点订单: %s 的预估量%s CPM" % (order.name, order.sale_CPM))
    order.save()
    flash(u'[返点订单]%s 更新成功!' % order.name, 'success')
    return redirect(url_for("searchAd_order.rebate_order_info", order_id=order.id))


def get_rebate_form(order):
    form = RebateOrderForm()
    form.client.data = order.client.id
    form.agent.data = order.agent.id
    form.campaign.data = order.campaign
    form.money.data = order.money
    form.medium_CPM.data = order.medium_CPM
    form.sale_CPM.data = order.sale_CPM
    form.client_start.data = order.client_start
    form.client_end.data = order.client_end
    form.reminde_date.data = order.reminde_date
    form.sales.data = [u.id for u in order.sales]
    form.operaters.data = [u.id for u in order.operaters]
    form.designers.data = [u.id for u in order.designers]
    form.planers.data = [u.id for u in order.planers]
    form.contract_type.data = order.contract_type
    form.resource_type.data = order.resource_type
    form.sale_type.data = order.sale_type
    return form


class ReplaceSalersForm(Form):
    replace_salers = SelectMultipleField(u'替代销售', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ReplaceSalersForm, self).__init__(*args, **kwargs)
        self.replace_salers.choices = [
            (m.id, m.name) for m in User.all_active()]


@searchAd_order_bp.route('/rebate_order/<order_id>/info', methods=['GET', 'POST'])
def rebate_order_info(order_id):
    order = searchAdRebateOrder.get(order_id)
    if not order or order.status == 0:
        if g.user.is_super_admin():
            pass
        else:
            abort(404)
    form = get_rebate_form(order)
    replace_saler_form = ReplaceSalersForm()
    replace_saler_form.replace_salers.data = [
        k.id for k in order.replace_sales]
    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        if info_type == 0:
            if not order.can_admin(g.user):
                flash(u'您没有编辑权限! 请联系该订单的创建者或者销售同事!', 'danger')
            else:
                form = RebateOrderForm(request.form)
                replace_saler_form = ReplaceSalersForm(request.form)
                if form.validate():
                    order.client = searchAdClient.get(form.client.data)
                    order.agent = searchAdAgent.get(form.agent.data)
                    order.campaign = form.campaign.data
                    order.money = int(round(float(form.money.data or 0)))
                    order.sale_CPM = form.sale_CPM.data
                    order.medium_CPM = form.medium_CPM.data
                    order.client_start = form.client_start.data
                    order.client_end = form.client_end.data
                    order.reminde_date = form.reminde_date.data
                    order.sales = User.gets(form.sales.data)
                    order.operaters = User.gets(form.operaters.data)
                    order.designers = User.gets(form.designers.data)
                    order.planers = User.gets(form.planers.data)
                    order.contract_type = form.contract_type.data
                    order.resource_type = form.resource_type.data
                    order.sale_type = form.sale_type.data
                    if g.user.is_super_admin():
                        order.replace_sales = User.gets(
                            replace_saler_form.replace_salers.data)
                    order.save()
                    order.add_comment(g.user, u"更新了该订单信息")
                    flash(u'[返点订单]%s 保存成功!' % order.name, 'success')
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
                msg = u"新合同号如下:\n\n%s-: %s\n\n" % (
                    order.agent.name, order.contract)
                to_users = order.sales + [order.creator, g.user]
                context = {'order': order,
                           'sender': g.user,
                           'action_msg': action_msg,
                           'info': msg,
                           'to_users': to_users}
                zhiqu_contract_apply_signal.send(
                    current_app._get_current_object(), context=context)
                order.add_comment(g.user, u"更新了合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'rebate_form': form,
               'order': order,
               'now_date': datetime.now(),
               'reminder_emails': reminder_emails,
               'replace_saler_form': replace_saler_form}
    return tpl('/searchAdorder/searchad_rebate_detail_info.html', **context)


@searchAd_order_bp.route('/my_rebate_orders', methods=['GET'])
def my_rebate_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or g.user.is_media_leader() or g.user.is_aduit():
        orders = searchAdRebateOrder.all()
    elif g.user.is_leader():
        orders = [
            o for o in searchAdRebateOrder.all() if g.user.location in o.locations]
    else:
        orders = searchAdRebateOrder.get_order_by_user(g.user)

    if not request.args.get('selected_status'):
        if g.user.is_admin():
            status_id = -1
        elif g.user.is_super_leader() or g.user.is_aduit():
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
    return rebate_display_orders(orders, u'我的返点订单', status_id)


@searchAd_order_bp.route('/rebate_orders', methods=['GET'])
def rebate_orders():
    orders = searchAdRebateOrder.all()
    status_id = int(request.args.get('selected_status', -1))
    return rebate_display_orders(orders, u'全部返点订单', status_id)


@searchAd_order_bp.route('/rebate_delete_orders', methods=['GET'])
def rebate_delete_orders():
    orders = searchAdRebateOrder.delete_all()
    status_id = int(request.args.get('selected_status', -1))
    return rebate_display_orders(orders, u'已删除的返点订单', status_id)


def rebate_display_orders(orders, title, status_id=-1):
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.now().year))
    # page = max(1, page)
    # start = (page - 1) * ORDER_PAGE_NUM
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower() in o.search_info.lower()]
    orders = [k for k in orders if k.client_start.year == year or k.client_end.year == year]
    if orderby and len(orders):
        orders = sorted(
            orders, key=lambda x: getattr(x, orderby), reverse=True)

    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    if 'download' == request.args.get('action', ''):
        filename = (
            "%s-%s.xls" % (u"返点订单", datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        '''
        xls = Excel().write_excle(
            download_excel_table_by_doubanorders(orders))
        '''
        response = get_download_response(xls, filename)
        return response
    else:
        paginator = Paginator(orders, ORDER_PAGE_NUM)
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(paginator.num_pages)
        return tpl('/searchAdorder/searchad_rebate_orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   orderby=orderby, now_date=datetime.now().date(),
                   search_info=search_info, page=page, year=year,
                   params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s&year=%s' %
                   (orderby, search_info, location_id, status_id, year))


@searchAd_order_bp.route('/rebate_order/<order_id>/contract', methods=['POST'])
def rebate_order_contract(order_id):
    order = searchAdRebateOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    order = searchAdRebateOrder.get(order_id)
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('searchAd_order.rebate_orders'))
    return redirect(url_for("searchAd_order.rebate_order_info", order_id=order.id))
