# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from flask import Blueprint, request, redirect, abort, url_for, g, jsonify
from flask import json, render_template as tpl, flash, current_app
from sqlalchemy import and_
from wtforms import SelectMultipleField
from libs.wtf import Form
from forms.order import (ClientOrderForm, MediumOrderForm,
                         FrameworkOrderForm, DoubanOrderForm,
                         AssociatedDoubanOrderForm,
                         MediumFrameworkOrderForm,
                         ClientMediumOrderForm)

from models.client import Client, Group, Agent, AgentRebate
from models.medium import Medium, MediumGroup, Media
from models.order import Order, MediumOrderExecutiveReport
from models.client_order import (CONTRACT_STATUS_APPLYCONTRACT, CONTRACT_STATUS_APPLYPASS,
                                 CONTRACT_STATUS_APPLYREJECT, CONTRACT_STATUS_APPLYPRINT,
                                 CONTRACT_STATUS_PRINTED, CONTRACT_STATUS_MEDIA, CONTRACT_STATUS_CN,
                                 STATUS_DEL, STATUS_ON, CONTRACT_STATUS_NEW, CONTRACT_STATUS_DELETEAPPLY,
                                 CONTRACT_STATUS_DELETEAGREE, CONTRACT_STATUS_DELETEPASS,
                                 CONTRACT_STATUS_PRE_FINISH, CONTRACT_STATUS_FINISH, CONTRACT_STATUS_CHECKCONTRACT,
                                 CONTRACT_STATUS_DELETEFINANCE, EditClientOrder, EditOrder, BackEditClientOrder,
                                 EDIT_CONTRACT_STATUS_CN)
from models.client_order import ClientOrder, ClientOrderExecutiveReport, IntentionOrder, COMPLETE_PERCENT_CN
from models.client_medium_order import ClientMediumOrder
from models.framework_order import FrameworkOrder
from models.medium_framework_order import MediumFrameworkOrder
from models.douban_order import DoubanOrder, DoubanOrderExecutiveReport
from models.associated_douban_order import AssociatedDoubanOrder
from models.user import (User, TEAM_LOCATION_CN, TEAM_TYPE_DESIGNER,
                         TEAM_TYPE_PLANNER, TEAM_TYPE_OPERATER, TEAM_TYPE_OPERATER_LEADER)
from models.excel import Excel
from models.attachment import Attachment
from models.download import (download_excel_table_by_doubanorders,
                             download_excel_table_by_frameworkorders)

from libs.email_signals import zhiqu_contract_apply_signal, zhiqu_edit_contract_apply_signal
from libs.paginator import Paginator
from controllers.tools import get_download_response
from controllers.helpers.order_helpers import write_client_excel, write_frameworkorder_excel
from libs.date_helpers import get_monthes_pre_days

order_bp = Blueprint('order', __name__, template_folder='../templates/order')


ORDER_PAGE_NUM = 50


class ReplaceSalersForm(Form):
    replace_salers = SelectMultipleField(u'替代销售', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ReplaceSalersForm, self).__init__(*args, **kwargs)
        self.replace_salers.choices = [
            (m.id, m.name) for m in User.all_active()]


@order_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('order.my_orders'))


######################
# client order
######################
@order_bp.route('/new_order', methods=['GET', 'POST'])
def new_order():
    form = ClientOrderForm(request.form)
    mediums = [{'id': m.id, 'name': m.name}for m in Media.all()]
    if request.method == 'POST' and form.validate():
        if ClientOrder.query.filter_by(campaign=form.campaign.data).count() > 0:
            flash(u'campaign名称已存在，请更换其他名称!', 'danger')
            return redirect(url_for("order.new_order"))
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        order = ClientOrder.add(agent=Agent.get(form.agent.data),
                                client=Client.get(form.client.data),
                                subject=form.subject.data,
                                campaign=form.campaign.data,
                                money=float(form.money.data or 0),
                                client_start=form.client_start.data,
                                client_end=form.client_end.data,
                                reminde_date=form.reminde_date.data,
                                direct_sales=User.gets(form.direct_sales.data),
                                agent_sales=User.gets(form.agent_sales.data),
                                assistant_sales=User.gets(form.assistant_sales.data),
                                contract_type=form.contract_type.data,
                                resource_type=form.resource_type.data,
                                sale_type=form.sale_type.data,
                                creator=g.user,
                                create_time=datetime.now(),
                                finish_time=datetime.now(),
                                self_agent_rebate=str(self_rebate) + '-' + str(self_rabate_value))
        order.add_comment(g.user,
                          u"新建了客户订单:%s - %s - %s" % (
                              order.agent.name,
                              order.client.name,
                              order.campaign
                          ))
        medium_ids = request.values.getlist('media')
        medium_moneys = request.values.getlist('medium-money')
        if medium_ids and medium_moneys and len(medium_ids) == len(medium_moneys):
            for x in range(len(medium_ids)):
                media = Media.get(medium_ids[x])
                mo = Order.add(campaign=order.campaign,
                               media=media,
                               medium_group=MediumGroup.get(1),
                               sale_money=float(medium_moneys[x] or 0),
                               medium_money=0,
                               medium_money2=0,
                               medium_start=order.client_start,
                               medium_end=order.client_end,
                               creator=g.user)
                order.medium_orders = order.medium_orders + [mo]
                order.add_comment(g.user, u"新建了媒体订单: %s %s元" %
                                  (media.name, mo.sale_money))
        order.save()
        if g.user.is_super_leader() or g.user.is_contract():
            contract_status_change(order, 3, [], '')
            flash(u'新建合同成功，等待合同管理员分配合同号!', 'success')
        else:
            flash(u'新建客户订单成功, 请上传合同和排期!', 'success')
            salers = order.direct_sales + order.agent_sales + order.assistant_sales
            leaders = []
            for k in salers:
                leaders += k.team_leaders
            to_users = salers + [order.creator, g.user]
            emails = [k.email for k in list(set(leaders))]
            context = {
                "to_other": emails,
                "sender": g.user,
                "to_users": to_users,
                "action_msg": u'新建订单',
                "order": order,
                "info": '',
                "action": 0
            }
            zhiqu_contract_apply_signal.send(current_app._get_current_object(), context=context, douban_type=False)
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


def _reload_status_executive_report(order):
    reports = []
    if order.__tablename__ == 'bra_douban_order':
        reports = DoubanOrderExecutiveReport.query.filter_by(douban_order=order)

    elif order.__tablename__ == 'bra_client_order':
        reports = list(ClientOrderExecutiveReport.query.filter_by(client_order=order))
        reports += list(MediumOrderExecutiveReport.query.filter_by(client_order=order))
    for r in reports:
        r.status = order.status
        r.contract_status = order.contract_status
        r.save()
    return


def _insert_executive_report(order, rtype):
    if order.contract == '' or order.contract_status not in [2, 4, 5, 10, 19, 20]:
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
    client_form.subject.data = order.subject or 1
    client_form.campaign.data = order.campaign
    client_form.money.data = order.money
    client_form.client_start.data = order.client_start
    client_form.client_end.data = order.client_end
    client_form.reminde_date.data = order.reminde_date
    client_form.direct_sales.data = [u.id for u in order.direct_sales]
    client_form.agent_sales.data = [u.id for u in order.agent_sales]
    client_form.assistant_sales.data = [u.id for u in order.assistant_sales]
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
    medium_form.medium_money.data = order.medium_money
    medium_form.medium_money.hidden = True
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
        if g.user.is_super_leader():
            pass
        else:
            abort(404)
    client_form = get_client_form(order)
    replace_saler_form = ReplaceSalersForm()
    replace_saler_form.replace_salers.data = [
        k.id for k in order.replace_sales]
    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        if info_type == 0:
            if not order.can_admin(g.user):
                flash(u'您没有编辑权限! 请联系该订单的创建者或者销售同事!', 'danger')
            else:
                client_form = ClientOrderForm(request.form)
                replace_saler_form = ReplaceSalersForm(request.form)
                if client_form.validate():
                    order.agent = Agent.get(client_form.agent.data)
                    order.client = Client.get(client_form.client.data)
                    order.subject = client_form.subject.data
                    order.campaign = client_form.campaign.data
                    order.money = float(client_form.money.data or 0)
                    order.client_start = client_form.client_start.data
                    order.client_end = client_form.client_end.data
                    order.client_start_year = client_form.client_start.data.year
                    order.client_end_year = client_form.client_end.data.year
                    order.reminde_date = client_form.reminde_date.data
                    order.direct_sales = User.gets(
                        client_form.direct_sales.data)
                    order.agent_sales = User.gets(client_form.agent_sales.data)
                    order.assistant_sales = User.gets(client_form.assistant_sales.data)
                    order.contract_type = client_form.contract_type.data
                    order.resource_type = client_form.resource_type.data
                    order.sale_type = client_form.sale_type.data
                    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_leader():
                        order.replace_sales = User.gets(
                            replace_saler_form.replace_salers.data)
                    order.self_agent_rebate = str(self_rebate) + '-' + str(self_rabate_value)
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
                flash(u'[%s]合同号更新成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s-致趣: %s\n\n" % (
                    order.agent.name, order.contract)
                for mo in order.medium_orders:
                    msg = msg + u"致趣-%s: %s\n\n" % (mo.media.name, mo.medium_contract or "")
                for o in order.associated_douban_orders:
                    msg = msg + u"%s-豆瓣: %s\n\n" % (o.medium_order.media.name, o.contract or "")
                to_users = order.direct_sales + order.assistant_sales + order.agent_sales + [order.creator, g.user]
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
    new_medium_form.medium_money.hidden = True
    new_medium_form.discount.hidden = True

    new_associated_douban_form = AssociatedDoubanOrderForm()
    new_associated_douban_form.medium_order.choices = [(mo.id, "%s (%s)" % (mo.name,
                                                                            mo.start_date_cn + '-' +
                                                                            str(mo.sale_money)))
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
               'tab_id': tab_id or 1,
               'replace_saler_form': replace_saler_form,
               'medium_groups': MediumGroup.all(),
               'medias': Media.all()}
    return tpl('order_detail_info.html', **context)


@order_bp.route('/order/<order_id>/new_medium', methods=['GET', 'POST'])
def order_new_medium(order_id):
    co = ClientOrder.get(order_id)
    if not co:
        abort(404)
    form = MediumOrderForm(request.form)
    if request.method == 'POST':
        medium_group_id = request.values.get('medium_group', 0)
        media_id = request.values.get('media', 0)
        mo = Order.add(campaign=co.campaign,
                       medium_group=MediumGroup.get(medium_group_id),
                       media=Media.get(media_id),
                       medium_money=float(form.medium_money.data or 0),
                       medium_money2=float(form.medium_money2.data or 0),
                       sale_money=float(form.sale_money.data or 0),
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
                       (mo.media.name, mo.sale_money, mo.medium_money2))
        flash(u'[媒体订单]新建成功!', 'success')
        _insert_executive_report(mo, 'reload')
        return redirect(mo.info_path())
    return tpl('order_new_medium.html', form=form)


@order_bp.route('/order/medium_order/<mo_id>/', methods=['POST'])
def medium_order(mo_id):
    mo = Order.get(mo_id)
    if not mo:
        abort(404)
    form = MediumOrderForm(request.form)
    last_status = mo.finish_status
    finish_status = int(request.values.get('finish_status', 1))
    medium_group_id = request.values.get('medium_group', 0)
    media_id = request.values.get('media', 0)
    if g.user.is_super_leader() or g.user.is_media() or g.user.is_media_leader():
        mo.medium_group = MediumGroup.get(medium_group_id)
        mo.media = Media.get(media_id)
    if mo.client_order.contract_status in [0, 1, 6]:
        mo.medium_group = MediumGroup.get(medium_group_id)
        mo.media = Media.get(media_id)
    self_medium_rebate = int(request.values.get('self_medium_rebate', 0))
    self_medium_rabate_value = float(request.values.get('self_medium_rabate_value', 0))
    mo.medium_money = float(form.medium_money.data or 0)
    mo.medium_money2 = float(form.medium_money2.data or 0)
    mo.sale_money = float(form.sale_money.data or 0)
    mo.medium_CPM = form.medium_CPM.data
    mo.sale_CPM = form.sale_CPM.data
    mo.medium_start = form.medium_start.data
    mo.medium_end = form.medium_end.data
    mo.operaters = User.gets(form.operaters.data)
    mo.designers = User.gets(form.designers.data)
    mo.planers = User.gets(form.planers.data)
    mo.discount = form.discount.data
    mo.finish_status = finish_status
    if finish_status == 0 and last_status != 0:
        mo.finish_time = datetime.now()
    mo.self_medium_rebate = str(self_medium_rebate) + '-' + str(self_medium_rabate_value)
    mo.save()
    mo.client_order.add_comment(
        g.user, u"更新了媒体订单: %s %s %s" % (mo.media.name, mo.sale_money, mo.medium_money2))
    if finish_status == 0 and last_status != 0:
        mo.client_order.add_comment(g.user, u"%s 媒体订单已归档" % (mo.media.name))
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
    sale_CPM = int(request.values.get('sale_CPM', 0))
    self_medium_rebate = int(request.values.get('self_medium_rebate', 0))
    self_medium_rabate_value = float(request.values.get('self_medium_rabate_value', 0))
    if cpm != '':
        cpm = int(round(float(cpm)))
        if mo.medium_CPM != cpm:
            mo.client_order.add_comment(
                g.user, u"更新了媒体订单: %s 的实际量%s CPM" % (mo.media.name, cpm))
        mo.medium_CPM = cpm
    if sale_CPM != 0:
        if mo.sale_CPM != sale_CPM:
            mo.client_order.add_comment(
                g.user, u"更新了媒体订单: %s 的预估量%s CPM" % (mo.media.name, sale_CPM))
        mo.sale_CPM = sale_CPM
    if medium_money != '':
        medium_money = float(medium_money)
        if mo.medium_money != medium_money:
            mo.client_order.add_comment(
                g.user, u"更新了媒体订单: %s 的分成金额%s " % (mo.media.name, medium_money))
        mo.medium_money = medium_money
    mo.self_medium_rebate = str(self_medium_rebate) + '-' + str(self_medium_rabate_value)
    finish_status = int(request.values.get('finish_status', 1))
    # 归档前合同状态
    last_status = mo.finish_status
    mo.finish_status = finish_status
    if finish_status == 0 and last_status != 0:
        mo.finish_time = datetime.now()
        mo.client_order.add_comment(g.user, u" %s 媒体订单已归档" % (mo.media.name))
    elif finish_status == 1 and last_status == 0:
        mo.client_order.add_comment(g.user, u" %s 媒体订单取消归档" % (mo.media.name))
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
                                   money=float(form.money.data or 0),
                                   creator=g.user)
    ao.medium_order.client_order.add_comment(g.user,
                                             u"新建了关联豆瓣订单: %s - %s - %s" % (
                                                 ao.medium_order.media.name,
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
    ao.money = float(form.money.data or 0)
    ao.save()
    ao.medium_order.client_order.add_comment(g.user,
                                             u"更新了关联豆瓣订单: %s - %s - %s" % (
                                                 ao.medium_order.media.name,
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
    if order.__tablename__ == 'bra_medium_framework_order':
        salers = order.medium_users
    else:
        salers = order.direct_sales + order.agent_sales + order.assistant_sales
    leaders = []
    for k in salers:
        leaders += k.team_leaders
    to_users = salers + [order.creator, g.user]
    emails += [k.email for k in list(set(leaders))]

    # 判断客户金额是否等于媒体售卖金额总和
    if action in [1, 2]:
        if order.__tablename__ == 'bra_client_order':
            medium_orders = order.medium_orders
            if order.money != sum([o.sale_money for o in medium_orders]):
                flash(u'客户合同金额与媒体合同售卖金额总和不符，请确认后进行审批!', 'danger')
                return redirect(order.info_path())
    if action == 1:
        order.contract_status = CONTRACT_STATUS_MEDIA
        action_msg = u"申请利润分配"
        to_users = to_users + order.leaders + User.medias()
    elif action == 2:
        if order.__tablename__ == 'bra_client_order':
            medium_groups = [k.medium_group.id for k in order.medium_orders]
            if 1 in medium_groups:
                flash(u'请媒介分配媒体供应商!', 'danger')
                return redirect(order.info_path())
        elif order.__tablename__ == 'bra_client_medium_order':
            if order.medium_group.id == 1:
                flash(u'请媒介分配媒体供应商!', 'danger')
                return redirect(order.info_path())
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
        action_msg = u"撤单申请"
        order.contract_status = CONTRACT_STATUS_DELETEAPPLY
        to_users = to_users + order.leaders + User.medias() + User.contracts()
    elif action == 8:
        action_msg = u"区域Leader确认撤单, 请财务确认"
        order.contract_status = CONTRACT_STATUS_DELETEAGREE
        to_users = to_users + order.leaders + User.medias() + User.contracts() + User.finances()
    elif action == 81:
        action_msg = u'财务确认撤单，请黄亮确认'
        order.contract_status = CONTRACT_STATUS_DELETEFINANCE
        to_users = to_users + order.leaders + User.medias() + User.contracts()
    elif action == 9:
        action_msg = u"同意撤单"
        order.contract_status = CONTRACT_STATUS_DELETEPASS
        order.status = STATUS_DEL
        to_users = User.media_leaders() + User.contracts() + User.super_leaders() + User.finances()
        if order.__tablename__ == 'bra_douban_order' and order.contract:
            to_users += User.douban_contracts()
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
        to_users = to_users + order.leaders + User.medias() + User.contracts()
    elif action == 21:
        self_rebate = int(request.values.get('self_rebate', '0'))
        self_rebate_value = float(request.values.get('self_rabate_value', '0'))
        order.contract_status = CONTRACT_STATUS_APPLYPASS
        order.self_agent_rebate = str(self_rebate) + '-' + str(self_rebate_value)
        action_msg = u"审批通过"
        to_users = to_users + order.leaders + User.contracts()
        _insert_executive_report(order, '')
    elif action == 100:
        action_msg = u"提醒审批合同"
        to_users = to_users + order.leaders + User.contracts()
    elif action == 10:
        action_msg = u"审批合同通过"
        order.contract_status = CONTRACT_STATUS_CHECKCONTRACT
        to_users = to_users + order.leaders + User.contracts()
        _insert_executive_report(order, '')
    elif action == 0:
        order.contract_status = CONTRACT_STATUS_NEW
        order.insert_reject_time()
        action_msg = u"合同被驳回，请从新提交审核"
        _delete_executive_report(order)
    elif action == 113:
        order.contract_status = CONTRACT_STATUS_APPLYPASS
        action_msg = u"已取消合同归档，请重新上传合同"
        _delete_executive_report(order)
    order.save()
    # 重置报表状态
    _reload_status_executive_report(order)
    flash(u'[%s] %s ' % (order.name, action_msg), 'success')
    if order.__tablename__ == 'bra_douban_order' and order.contract_status == 4 and action == 5:
        to_users += User.douban_contracts()
    context = {
        "to_other": emails,
        "sender": g.user,
        "to_users": to_users,
        "action_msg": action_msg,
        "order": order,
        "info": msg,
        "action": order.contract_status
    }
    douban_type = False
    if order.__tablename__ == 'bra_douban_order' and order.contract_status == 4 and action == 5:
        douban_type = True
    zhiqu_contract_apply_signal.send(current_app._get_current_object(), context=context, douban_type=douban_type)
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
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or \
            g.user.is_media_leader() or g.user.is_finance() or g.user.is_aduit() or g.user.is_operater_leader():
        orders = ClientOrder.all()
    elif g.user.is_leader():
        orders = [
            o for o in ClientOrder.all() if g.user.location in o.locations]
    else:
        orders = ClientOrder.get_order_by_user(g.user)

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
    return display_orders(orders, u'我的新媒体订单', status_id)


def display_orders(orders, title, status_id=-1):
    year = str(request.values.get('year', datetime.now().year))
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        if status_id == 30:
            orders = [o for o in orders if o.medium_status == 0]
        elif status_id == 28:
            orders = [o for o in orders if o.contract_status != 20]
        elif status_id == 29:
            orders = [o for o in orders if o.medium_status != 0]
        elif status_id == 31:
            orders = [o for o in orders if o.back_money_status == 0]
        elif status_id == 32:
            orders = [o for o in orders if o.back_money_status != 0 and o.contract]
        elif status_id == 33:
            orders = [o for o in orders if o.invoice_pass_sum != float(o.money) and o.contract]
        elif status_id == 34:
            orders = [o for o in orders if o.invoice_pass_sum == float(o.money)]
        elif status_id == 35:
            orders = [o for o in orders if o.contract_status == 2]
        elif status_id == 36:
            orders = [o for o in orders if o.contract_status in [4, 5, 10, 19, 20]]
        else:
            orders = [o for o in orders if o.contract_status == status_id]
    orders = [o for o in orders if o.client_start.year == int(year) or o.client_end.year == int(year)]
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
        params = '&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s&year=%s' % (
            orderby, search_info, location_id, status_id, str(year))
        return tpl('orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   search_info=search_info, page=page,
                   orderby=orderby, now_date=datetime.now().date(),
                   params=params, year=year)


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
                                   money=float(form.money.data or 0),
                                   client_start=form.client_start.data,
                                   client_end=form.client_end.data,
                                   reminde_date=form.reminde_date.data,
                                   direct_sales=User.gets(
                                       form.direct_sales.data),
                                   agent_sales=User.gets(
                                       form.agent_sales.data),
                                   assistant_sales=User.gets(form.assistant_sales.data),
                                   contract_type=form.contract_type.data,
                                   creator=g.user,
                                   inad_rebate=form.inad_rebate.data,
                                   douban_rebate=form.douban_rebate.data,
                                   finish_time=datetime.now(),
                                   create_time=datetime.now())
        order.add_comment(g.user, u"新建了该代理框架订单")
        flash(u'新建代理框架订单成功, 请上传合同!', 'success')
        # 框架合同同步甲方返点信息
        # _insert_agent_rebate(order)
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
    flash(u"代理框架订单: %s 已删除" % (order.group.name), 'danger')
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
    flash(u"代理框架订单: %s 已恢复" % (order.group.name), 'success')
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
    framework_form.assistant_sales.data = [u.id for u in order.assistant_sales]
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
                flash(u'您没有编辑权限! 请联系该代理框架的创建者或者销售同事!', 'danger')
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
                    order.client_start_year = framework_form.client_start.data.year
                    order.client_end_year = framework_form.client_end.data.year
                    order.reminde_date = framework_form.reminde_date.data
                    order.direct_sales = User.gets(
                        framework_form.direct_sales.data)
                    order.agent_sales = User.gets(
                        framework_form.agent_sales.data)
                    order.assistant_sales = User.gets(
                        framework_form.assistant_sales.data)
                    order.contract_type = framework_form.contract_type.data
                    order.inad_rebate = framework_form.inad_rebate.data
                    order.douban_rebate = framework_form.douban_rebate.data
                    order.save()
                    order.add_comment(g.user, u"更新了该代理框架订单")
                    flash(u'[代理框架订单]%s 保存成功!' % order.name, 'success')

                    # 框架合同同步甲方返点信息
                    # _insert_agent_rebate(order)
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
                to_users = order.direct_sales + order.assistant_sales +\
                    order.agent_sales + [order.creator, g.user]
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
    return tpl('framework_detail_info.html', **context)


@order_bp.route('/my_framework_orders', methods=['GET'])
def my_framework_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or g.user.is_media_leader() or\
            g.user.is_aduit() or g.user.is_finance():
        orders = FrameworkOrder.all()
        if g.user.is_admin() or g.user.is_contract() or g.user.is_finance():
            pass
        elif g.user.is_super_leader():
            orders = [o for o in orders if o.contract_status ==
                      CONTRACT_STATUS_APPLYCONTRACT]
        elif g.user.is_media() or g.user.is_media_leader():
            orders = [
                o for o in orders if o.contract_status == CONTRACT_STATUS_MEDIA]
    elif g.user.is_leader():
        orders = [
            o for o in FrameworkOrder.all() if g.user.location in o.locations]
    else:
        orders = FrameworkOrder.get_order_by_user(g.user)
    return framework_display_orders(orders, u'我的代理框架订单')


@order_bp.route('/framework_orders', methods=['GET'])
def framework_orders():
    orders = FrameworkOrder.all()
    return framework_display_orders(orders, u'代理框架订单列表')


@order_bp.route('/framework_delete_orders', methods=['GET'])
def framework_delete_orders():
    orders = FrameworkOrder.delete_all()
    return framework_display_orders(orders, u'已删除的代理框架订单列表')


def framework_display_orders(orders, title):
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.now().year))
    orders = [k for k in orders if k.client_start.year == year or k.client_end.year == year]
    if 'download' == request.args.get('action', ''):
        return write_frameworkorder_excel(orders)
    else:
        paginator = Paginator(orders, ORDER_PAGE_NUM)
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(paginator.num_pages)
        return tpl('frameworks.html', title=title, orders=orders, page=page, year=year)


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
# medium framework order
######################
@order_bp.route('/new_medium_framework_order', methods=['GET', 'POST'])
def new_medium_framework_order():
    form = MediumFrameworkOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = MediumFrameworkOrder.add(medium_groups=MediumGroup.gets(form.medium_groups.data),
                                         description=form.description.data,
                                         money=float(form.money.data or 0),
                                         client_start=form.client_start.data,
                                         client_end=form.client_end.data,
                                         medium_users=User.gets(
                                             form.medium_users.data),
                                         contract_type=form.contract_type.data,
                                         creator=g.user,
                                         inad_rebate=form.inad_rebate.data,
                                         finish_time=datetime.now(),
                                         create_time=datetime.now())
        order.add_comment(g.user, u"新建了该媒体框架订单")
        flash(u'新建媒体框架订单成功, 请上传合同!', 'success')
        return redirect(url_for("order.medium_framework_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
    return tpl('new_medium_framework_order.html', form=form)


@order_bp.route('/medium_framework_order/<order_id>/delete', methods=['GET'])
def medium_framework_delete(order_id):
    order = MediumFrameworkOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"媒体框架订单: %s 已删除" % (order.group.name), 'danger')
    order.status = STATUS_DEL
    order.save()
    return redirect(url_for("order.my_medium_framework_orders"))


@order_bp.route('/medium_framework_order/<order_id>/recovery', methods=['GET'])
def medium_framework_recovery(order_id):
    order = MediumFrameworkOrder.get(order_id)
    if not order:
        abort(404)
    if not g.user.is_super_admin():
        abort(402)
    flash(u"媒体框架订单: %s 已恢复" % (order.mediums_names), 'success')
    order.status = STATUS_ON
    order.save()
    return redirect(url_for("order.medium_framework_delete_orders"))


def get_medium_framework_form(order):
    framework_form = MediumFrameworkOrderForm()
    framework_form.medium_groups.data = [a.id for a in order.medium_groups]
    framework_form.description.data = order.description
    framework_form.money.data = order.money
    framework_form.client_start.data = order.client_start
    framework_form.client_end.data = order.client_end
    framework_form.medium_users.data = [u.id for u in order.medium_users]
    framework_form.contract_type.data = order.contract_type
    framework_form.inad_rebate.data = order.inad_rebate or 0.0
    return framework_form


@order_bp.route('/my_medium_framework_orders', methods=['GET'])
def my_medium_framework_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media_leader() or\
            g.user.is_finance() or g.user.is_aduit():
        orders = MediumFrameworkOrder.all()
        if g.user.is_admin() or g.user.is_contract() or g.user.is_finance():
            pass
        elif g.user.is_super_leader():
            orders = [o for o in orders if o.contract_status ==
                      CONTRACT_STATUS_APPLYCONTRACT]
        elif g.user.is_media_leader():
            pass
    else:
        orders = MediumFrameworkOrder.get_order_by_user(g.user)
    return medium_framework_display_orders(orders, u'我的媒体框架订单')


@order_bp.route('/medium_framework_orders', methods=['GET'])
def medium_framework_orders():
    orders = MediumFrameworkOrder.all()
    return medium_framework_display_orders(orders, u'媒体框架订单列表')


@order_bp.route('/medium_framework_delete_orders', methods=['GET'])
def medium_framework_delete_orders():
    orders = MediumFrameworkOrder.delete_all()
    return framework_display_orders(orders, u'已删除的媒体框架订单列表')


def medium_framework_display_orders(orders, title):
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.now().year))
    orders = [k for k in orders if k.client_start.year == year or k.client_end.year == year]
    if 'download' == request.args.get('action', ''):
        filename = (
            "%s-%s.xls" % (u"媒体框架订单", datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
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
        return tpl('medium_frameworks.html', title=title, orders=orders, page=page, year=year)


@order_bp.route('/medium_framework_order/<order_id>/contract', methods=['POST'])
def medium_framework_order_contract(order_id):
    order = MediumFrameworkOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('order.medium_framework_orders'))
    return redirect(url_for("order.medium_framework_order_info", order_id=order.id))


@order_bp.route('/medium_framework_order/<order_id>/info', methods=['GET', 'POST'])
def medium_framework_order_info(order_id):
    order = MediumFrameworkOrder.get(order_id)
    if not order or order.status == 0:
        abort(404)
    framework_form = get_medium_framework_form(order)

    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        if info_type == 0:
            if not order.can_admin(g.user) and not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系该媒体框架的创建者或者销售同事!', 'danger')
            else:
                framework_form = MediumFrameworkOrderForm(request.form)
                medium_groups = MediumGroup.gets(framework_form.medium_groups.data)
                if framework_form.validate():
                    order.medium_groups = medium_groups
                    order.description = framework_form.description.data
                    order.money = framework_form.money.data
                    order.client_start = framework_form.client_start.data
                    order.client_end = framework_form.client_end.data
                    order.client_start_year = framework_form.client_start.data.year
                    order.client_end_year = framework_form.client_end.data.year
                    order.medium_users = User.gets(
                        framework_form.medium_users.data)
                    order.contract_type = framework_form.contract_type.data
                    order.inad_rebate = framework_form.inad_rebate.data
                    order.save()
                    order.add_comment(g.user, u"更新了该媒体框架订单")
                    flash(u'[媒体框架订单]%s 保存成功!' % order.name, 'success')

                    # 框架合同同步甲方返点信息
                    # _insert_agent_rebate(order)
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:致趣: %s" % (order.contract)
                to_users = order.medium_users + [order.creator, g.user]
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
    return tpl('medium_framework_detail_info.html', **context)


######################
#  douban order
######################
@order_bp.route('/new_douban_order', methods=['GET', 'POST'])
def new_douban_order():
    form = DoubanOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        order = DoubanOrder.add(client=Client.get(form.client.data),
                                agent=Agent.get(form.agent.data),
                                campaign=form.campaign.data,
                                money=float(form.money.data or 0),
                                medium_CPM=form.medium_CPM.data,
                                sale_CPM=form.sale_CPM.data,
                                client_start=form.client_start.data,
                                client_end=form.client_end.data,
                                reminde_date=form.reminde_date.data,
                                direct_sales=User.gets(form.direct_sales.data),
                                agent_sales=User.gets(form.agent_sales.data),
                                assistant_sales=User.gets(form.assistant_sales.data),
                                operaters=User.gets(form.operaters.data),
                                designers=User.gets(form.designers.data),
                                planers=User.gets(form.planers.data),
                                contract_type=form.contract_type.data,
                                resource_type=form.resource_type.data,
                                sale_type=form.sale_type.data,
                                creator=g.user,
                                create_time=datetime.now(),
                                finish_time=datetime.now(),
                                self_agent_rebate=str(self_rebate) + '-' + str(self_rabate_value))
        order.add_comment(g.user, u"新建了该直签豆瓣订单")
        if g.user.is_super_leader() or g.user.is_contract():
            contract_status_change(order, 3, [], '')
            flash(u'新建豆瓣订单成功, 等待合同管理员分配合同号!', 'success')
        else:
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
    sale_CPM = int(request.values.get('sale_CPM', 0))
    if cpm != 0:
        order.medium_CPM = cpm
        order.add_comment(
            g.user, u"更新了直签豆瓣订单: %s 的实际量%s CPM" % (order.name, order.medium_CPM))
    if sale_CPM != 0:
        if order.sale_CPM != sale_CPM:
            order.sale_CPM = sale_CPM
            order.add_comment(
                g.user, u"更新了直签豆瓣订单: %s 的预估量%s CPM" % (order.name, order.sale_CPM))
    order.save()
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
    form.assistant_sales.data = [u.id for u in order.assistant_sales]
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
    replace_saler_form = ReplaceSalersForm()
    replace_saler_form.replace_salers.data = [
        k.id for k in order.replace_sales]
    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        if info_type == 0:
            if not order.can_admin(g.user):
                flash(u'您没有编辑权限! 请联系该订单的创建者或者销售同事!', 'danger')
            else:
                form = DoubanOrderForm(request.form)
                replace_saler_form = ReplaceSalersForm(request.form)
                if form.validate():
                    order.client = Client.get(form.client.data)
                    order.agent = Agent.get(form.agent.data)
                    order.campaign = form.campaign.data
                    order.money = float(form.money.data or 0)
                    order.sale_CPM = form.sale_CPM.data
                    order.medium_CPM = form.medium_CPM.data
                    order.client_start = form.client_start.data
                    order.client_end = form.client_end.data
                    order.client_start_year = form.client_start.data.year
                    order.client_end_year = form.client_end.data.year
                    order.reminde_date = form.reminde_date.data
                    order.direct_sales = User.gets(form.direct_sales.data)
                    order.agent_sales = User.gets(form.agent_sales.data)
                    order.assistant_sales = User.gets(form.assistant_sales.data)
                    order.operaters = User.gets(form.operaters.data)
                    order.designers = User.gets(form.designers.data)
                    order.planers = User.gets(form.planers.data)
                    order.contract_type = form.contract_type.data
                    order.resource_type = form.resource_type.data
                    order.sale_type = form.sale_type.data
                    if g.user.is_super_admin() or g.user.is_contract():
                        order.replace_sales = User.gets(
                            replace_saler_form.replace_salers.data)
                    order.self_agent_rebate = str(self_rebate) + '-' + str(self_rabate_value)
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
                to_users = order.direct_sales + order.assistant_sales +\
                    order.agent_sales + [order.creator, g.user]
                context = {'order': order,
                           'sender': g.user,
                           'action_msg': action_msg,
                           'info': msg,
                           'to_users': to_users}
                zhiqu_contract_apply_signal.send(
                    current_app._get_current_object(), context=context)
                order.add_comment(g.user, u"更新了合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'douban_form': form,
               'order': order,
               'now_date': datetime.now(),
               'reminder_emails': reminder_emails,
               'replace_saler_form': replace_saler_form}
    return tpl('douban_detail_info.html', **context)


@order_bp.route('/my_douban_orders', methods=['GET'])
def my_douban_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or\
            g.user.is_media_leader() or g.user.is_finance() or g.user.is_aduit() or g.user.is_operater_leader():
        orders = DoubanOrder.all()
    elif g.user.is_leader():
        orders = [
            o for o in DoubanOrder.all() if g.user.location in o.locations]
    else:
        orders = DoubanOrder.get_order_by_user(g.user)

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
    search_info = request.args.get('searchinfo', '').strip()
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.now().year))
    # page = max(1, page)
    # start = (page - 1) * ORDER_PAGE_NUM
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        if status_id == 31:
            orders = [o for o in orders if o.back_money_status == 0]
        elif status_id == 28:
            orders = [o for o in orders if o.contract_status != 20]
        elif status_id == 32:
            orders = [o for o in orders if o.back_money_status != 0 and o.contract]
        elif status_id == 35:
            orders = [o for o in orders if o.contract_status == 2]
        elif status_id == 36:
            orders = [o for o in orders if o.contract_status in [4, 5, 10, 19, 20]]
        else:
            orders = [o for o in orders if o.contract_status == status_id]
    orders = [o for o in orders if o.client_start.year == int(year) or o.client_end.year == int(year)]
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
                   params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s&year=%s' %
                   (orderby, search_info, location_id, status_id, str(year)),
                   year=year)


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


@order_bp.route('/medium_framework_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def medium_framework_attach_status(order_id, attachment_id, status):
    order = MediumFrameworkOrder.get(order_id)
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
    if order.__tablename__ == 'bra_medium_framework_order':
        to_users = order.medium_users + [order.creator, g.user] + User.contracts()
    else:
        to_users = order.direct_sales + order.agent_sales + \
            order.assistant_sales + [order.creator, g.user] + User.contracts()
    action_msg = u"%s文件:%s-%s" % (attachment.type_cn, attachment.filename, attachment.status_cn)
    msg = u"文件名:%s\n状态:%s\n如有疑问, 请联系合同管理员" % (
        attachment.filename, attachment.status_cn)

    context = {'order': order,
               'sender': g.user,
               'action_msg': action_msg,
               'info': msg,
               'to_users': to_users}
    zhiqu_contract_apply_signal.send(
        current_app._get_current_object(), context=context)


@order_bp.route('/intention_order', methods=['GET'])
def intention_order():
    orders = [k for k in IntentionOrder.all() if k.status == 0]
    year = str(request.values.get('year', datetime.now().year))
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    medium_id = int(request.args.get('medium_id', -1))
    page = int(request.args.get('p', 1))

    if g.user.is_super_leader():
        orders = orders
    elif g.user.is_leader():
        orders = [o for o in orders if g.user.location in o.locations]
    else:
        orders = IntentionOrder.get_order_by_user(g.user)

    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    orders = [o for o in orders if o.client_start.year ==
              int(year) or o.client_end.year == int(year)]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower().strip() in o.search_info.lower()]
    if medium_id != -1:
        orders = [o for o in orders if o.medium_id == medium_id]
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    paginator = Paginator(orders, ORDER_PAGE_NUM)
    try:
        orders = paginator.page(page)
    except:
        orders = paginator.page(paginator.num_pages)
    for k in orders.object_list:
        k.L_50 = 0
        k.U_50 = 0
        k.S_80 = 0
        if k.complete_percent == 1:
            k.L_50 = k.money
        elif k.complete_percent == 2:
            k.U_50 = k.money
        elif k.complete_percent == 3:
            k.S_80 = k.money
    params = '&searchinfo=%s&selected_location=%s&year=%s&medium_id=%s' % (
        search_info, location_id, str(year), str(medium_id))
    return tpl('intention_index.html', orders=orders,
               locations=select_locations, location_id=location_id,
               search_info=search_info, page=page, medias=Media.all(),
               now_date=datetime.now().date(), medium_id=medium_id,
               params=params, year=year)


class AgentForm(Form):
    agent_sales = SelectMultipleField(u'渠道销售', coerce=int)

    def __init__(self, *args, **kwargs):
        super(AgentForm, self).__init__(*args, **kwargs)
        self.agent_sales.choices = [(m.id, m.name) for m in User.sales()]


class DirectForm(Form):
    direct_sales = SelectMultipleField(u'直客销售', coerce=int)

    def __init__(self, *args, **kwargs):
        super(DirectForm, self).__init__(*args, **kwargs)
        self.direct_sales.choices = [(m.id, m.name) for m in User.sales()]


@order_bp.route('/intention_order/create', methods=['GET', 'POST'])
def intention_order_create():
    if request.method == 'POST':
        now_date = datetime.now()
        start_time = request.values.get(
            'client_start', now_date.strftime('%Y-%m-%d'))
        end_time = request.values.get(
            'client_end', now_date.strftime('%Y-%m-%d'))
        start_date = datetime.strptime(start_time, '%Y-%m-%d')
        end_date = datetime.strptime(end_time, '%Y-%m-%d')
        pre_month_days = get_monthes_pre_days(start_date, end_date)
        ex_money_data = []
        for k in pre_month_days:
            month_cn = k['month'].strftime('%Y-%m')
            money = float(request.values.get(month_cn + '_money', 0))
            ex_money_data.append({'money': money, 'month_cn': month_cn})
        media_id = int(request.values.get('media_id'))
        agent = request.values.get('agent', '')
        client = request.values.get('client', '')
        campaign = request.values.get('campaign', '')
        complete_percent = int(request.values.get('complete_percent', 1))
        money = sum([k['money'] for k in ex_money_data])
        client_start = start_time
        client_end = end_time
        direct_sales = request.values.getlist('direct_sales')
        agent_sales = request.values.getlist('agent_sales')
        intention_order = IntentionOrder.add(
            medium_group_id=1,
            media_id=media_id,
            agent=agent,
            client=client,
            campaign=campaign,
            complete_percent=complete_percent,
            money=money,
            client_start=datetime.strptime(client_start, '%Y-%m-%d'),
            client_end=datetime.strptime(client_end, '%Y-%m-%d'),
            direct_sales=User.gets(direct_sales),
            agent_sales=User.gets(agent_sales),
            creator=g.user,
            status=0,
            ex_money=json.dumps(ex_money_data),
            create_time=datetime.now()
        )
        msg = u"新建了洽谈订单:代理/直客：%s 客户：%s campaign：%s 预估程度：%s 预估金额：%s" % (
            agent, client, campaign, COMPLETE_PERCENT_CN[complete_percent], str(money))
        intention_order.add_comment(g.user, msg, msg_channel=11)
        flash('添加成功', 'success')
        return redirect(url_for('order.intention_order_update', intention_id=intention_order.id))
    return tpl('intention_create.html', direct_form=DirectForm(),
               agent_form=AgentForm(), agent=Agent.all(), client=Client.all(),
               medias=Media.all(), COMPLETE_PERCENT_CN=COMPLETE_PERCENT_CN,
               medium_groups=MediumGroup.all())


@order_bp.route('/intention_order/<intention_id>/delete', methods=['GET', 'POST'])
def intention_order_delete(intention_id):
    order = IntentionOrder.get(intention_id)
    order.status = -1
    order.save()
    return redirect(url_for('order.intention_order'))


@order_bp.route('/intention_order/<intention_id>/update', methods=['GET', 'POST'])
def intention_order_update(intention_id):
    intention_order = IntentionOrder.get(intention_id)
    ex_user = list(intention_order.direct_sales) + list(intention_order.agent_sales) + \
        [intention_order.creator] + list(User.super_admin_leaders())
    if g.user not in ex_user:
        return abort(403)
    direct_form = DirectForm()
    agent_form = AgentForm()
    direct_form.direct_sales.data = [
        u.id for u in intention_order.direct_sales]
    agent_form.agent_sales.data = [u.id for u in intention_order.agent_sales]

    is_data_agent = Agent.query.filter_by(name=intention_order.agent).first()
    is_data_client = Client.query.filter_by(
        name=intention_order.client).first()
    if request.method == 'POST':
        now_date = datetime.now()
        start_time = request.values.get(
            'client_start', now_date.strftime('%Y-%m-%d'))
        end_time = request.values.get(
            'client_end', now_date.strftime('%Y-%m-%d'))
        start_date = datetime.strptime(start_time, '%Y-%m-%d')
        end_date = datetime.strptime(end_time, '%Y-%m-%d')
        pre_month_days = get_monthes_pre_days(start_date, end_date)
        ex_money_data = []
        for k in pre_month_days:
            month_cn = k['month'].strftime('%Y-%m')
            money = float(request.values.get(month_cn + '_money', 0))
            ex_money_data.append({'money': money, 'month_cn': month_cn})
        media_id = int(request.values.get('media_id'))
        agent = request.values.get('agent', '')
        client = request.values.get('client', '')
        campaign = request.values.get('campaign', '')
        complete_percent = int(request.values.get('complete_percent', 1))
        money = sum([k['money'] for k in ex_money_data])
        client_start = start_time
        client_end = end_time
        direct_sales = request.values.getlist('direct_sales')
        agent_sales = request.values.getlist('agent_sales')
        intention_order.media_id = media_id
        intention_order.agent = agent
        intention_order.client = client
        intention_order.campaign = campaign
        intention_order.complete_percent = complete_percent
        intention_order.money = money
        intention_order.client_start = datetime.strptime(
            client_start, '%Y-%m-%d')
        intention_order.client_end = datetime.strptime(client_end, '%Y-%m-%d')
        intention_order.direct_sales = User.gets(direct_sales)
        intention_order.agent_sales = User.gets(agent_sales)
        intention_order.creator = g.user
        intention_order.ex_money = json.dumps(ex_money_data)
        intention_order.create_time = datetime.now()
        intention_order.save()
        msg = u"修改了洽谈订单:代理/直客：%s 客户：%s campaign：%s 预估程度：%s 预估金额：%s" % (
            agent, client, campaign, COMPLETE_PERCENT_CN[complete_percent], str(money))
        intention_order.add_comment(g.user, msg, msg_channel=11)
        flash('修改成功', 'success')
        return redirect(url_for('order.intention_order_update', intention_id=intention_order.id))
    if intention_order.ex_money:
        intention_order.ex_money_data = json.loads(intention_order.ex_money)
    else:
        start_date = datetime.strptime(intention_order.start_date_cn, '%Y-%m-%d')
        end_date = datetime.strptime(intention_order.end_date_cn, '%Y-%m-%d')
        pre_month_days = get_monthes_pre_days(start_date, end_date)
        intention_order.ex_money_data = [{'money': 0, 'month_cn': k[
            'month'].strftime('%Y-%m')} for k in pre_month_days]
    return tpl('intention_update.html', direct_form=direct_form, intention_order=intention_order,
               agent_form=agent_form, agent=Agent.all(), client=Client.all(),
               is_data_agent=is_data_agent, is_data_client=is_data_client,
               medias=Media.all(), COMPLETE_PERCENT_CN=COMPLETE_PERCENT_CN,
               medium_groups=MediumGroup.all())


@order_bp.route('/ex_time', methods=['GET'])
def order_ex_time():
    now_date = datetime.now().strftime('%Y-%m-%d')
    start_time = request.values.get('start_time', now_date)
    end_time = request.values.get('end_time', now_date)
    start_time = datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.strptime(end_time, '%Y-%m-%d')
    pre_month_days = get_monthes_pre_days(start_time, end_time)
    for k in pre_month_days:
        k['month_cn'] = k['month'].strftime('%Y-%m')
    return jsonify({'ret': True, 'data': pre_month_days})


@order_bp.route('/intention_order/<iid>/in_real', methods=['GET'])
def intention_order_in_real(iid):
    intention_order = IntentionOrder.get(iid)
    is_data_agent = Agent.query.filter_by(name=intention_order.agent).first()
    is_data_client = Client.query.filter_by(
        name=intention_order.client).first()
    reminde_date = intention_order.client_start + timedelta(days=90)
    if intention_order.media_id == 0:
        order = DoubanOrder.add(agent=is_data_agent,
                                client=is_data_client,
                                campaign=intention_order.campaign,
                                money=float(intention_order.money),
                                client_start=intention_order.client_start,
                                client_end=intention_order.client_end,
                                medium_CPM=0,
                                sale_CPM=0,
                                reminde_date=reminde_date,
                                direct_sales=intention_order.direct_sales,
                                agent_sales=intention_order.agent_sales,
                                assistant_sales=[],
                                operaters=[],
                                designers=[],
                                planers=[],
                                contract_type=0,
                                resource_type=0,
                                sale_type=0,
                                creator=g.user,
                                create_time=datetime.now(),
                                finish_time=datetime.now())
        order.add_comment(g.user, u"新建了该直签豆瓣订单")
        intention_order.order_id = '0-' + str(order.id)
    else:
        order = ClientOrder.add(agent=is_data_agent,
                                client=is_data_client,
                                campaign=intention_order.campaign,
                                money=float(intention_order.money),
                                client_start=intention_order.client_start,
                                client_end=intention_order.client_end,
                                reminde_date=reminde_date,
                                direct_sales=intention_order.direct_sales,
                                agent_sales=intention_order.agent_sales,
                                assistant_sales=[],
                                contract_type=0,
                                resource_type=0,
                                sale_type=0,
                                creator=g.user,
                                create_time=datetime.now(),
                                finish_time=datetime.now())
        order.add_comment(g.user,
                          u"新建了客户订单:%s - %s - %s" % (
                              order.agent.name,
                              order.client.name,
                              order.campaign
                          ))
        mo = Order.add(campaign=order.campaign,
                       medium_group=MediumGroup.get(intention_order.medium_group_id),
                       media=Media.get(intention_order.media_id),
                       sale_money=intention_order.money,
                       medium_money=0,
                       medium_money2=intention_order.money,
                       medium_start=order.client_start,
                       medium_end=order.client_end,
                       creator=g.user)
        order.medium_orders = order.medium_orders + [mo]
        order.add_comment(g.user, u"新建了媒体订单: %s %s元" %
                          (mo.media.name, intention_order.money))
        order.save()
        flash(u'新建客户订单成功, 请上传合同和排期!', 'success')
        intention_order.order_id = '1-' + str(order.id)
    intention_order.add_comment(g.user, '已完成一键下单', msg_channel=11)
    intention_order.status = 1
    intention_order.save()
    return redirect(order.info_path())


######################
#  client medium order
######################
@order_bp.route('/new_client_medium_order', methods=['GET', 'POST'])
def new_client_medium_order():
    form = ClientMediumOrderForm(request.form)
    if request.method == 'POST':
        if ClientMediumOrder.query.filter_by(campaign=form.campaign.data).count() > 0:
            flash(u'campaign名称已存在，请更换其他名称!', 'danger')
            return redirect(url_for("order.new_client_medium_order"))
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        order = ClientMediumOrder.add(client=Client.get(form.client.data),
                                      agent=Agent.get(form.agent.data),
                                      campaign=form.campaign.data,
                                      money=float(form.money.data or 0),
                                      medium_CPM=form.medium_CPM.data,
                                      sale_CPM=form.sale_CPM.data,
                                      client_start=form.client_start.data,
                                      client_end=form.client_end.data,
                                      reminde_date=form.reminde_date.data,
                                      direct_sales=User.gets(form.direct_sales.data),
                                      agent_sales=User.gets(form.agent_sales.data),
                                      assistant_sales=User.gets(form.assistant_sales.data),
                                      operaters=User.gets(form.operaters.data),
                                      designers=User.gets(form.designers.data),
                                      planers=User.gets(form.planers.data),
                                      contract_type=form.contract_type.data,
                                      resource_type=form.resource_type.data,
                                      sale_type=form.sale_type.data,
                                      creator=g.user,
                                      create_time=datetime.now(),
                                      finish_time=datetime.now(),
                                      medium_group=MediumGroup.get(1),
                                      media=Media.get(form.media.data),
                                      medium_money=form.medium_money.data,
                                      self_agent_rebate=str(self_rebate) + '-' + str(self_rabate_value))
        order.add_comment(g.user, u"新建了直签媒体订单")
        flash(u'新建订单成功, 请上传合同!', 'success')
        return redirect(url_for("order.client_medium_order_info", order_id=order.id))
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('new_client_medium_order.html', form=form)


def get_client_medium_order_form(order):
    form = ClientMediumOrderForm()
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
    form.assistant_sales.data = [u.id for u in order.assistant_sales]
    form.operaters.data = [u.id for u in order.operaters]
    form.designers.data = [u.id for u in order.designers]
    form.planers.data = [u.id for u in order.planers]
    form.contract_type.data = order.contract_type
    form.resource_type.data = order.resource_type
    form.sale_type.data = order.sale_type
    form.medium_group.data = order.medium_group_id
    form.media.data = order.media.id
    form.medium_money.data = order.medium_money
    return form


@order_bp.route('/client_medium_order/<order_id>/info', methods=['GET', 'POST'])
def client_medium_order_info(order_id):
    order = ClientMediumOrder.get(order_id)
    form = get_client_medium_order_form(order)
    replace_saler_form = ReplaceSalersForm()
    replace_saler_form.replace_salers.data = [
        k.id for k in order.replace_sales]
    if request.method == 'POST':
        info_type = int(request.values.get('info_type', '0'))
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        if info_type == 0:
            if not order.can_admin(g.user):
                flash(u'您没有编辑权限! 请联系该订单的创建者或者销售同事!', 'danger')
            else:
                form = ClientMediumOrderForm(request.form)
                replace_saler_form = ReplaceSalersForm(request.form)
                if form.validate():
                    order.client = Client.get(form.client.data)
                    order.agent = Agent.get(form.agent.data)
                    order.campaign = form.campaign.data
                    order.money = float(form.money.data or 0)
                    order.sale_CPM = form.sale_CPM.data
                    order.medium_CPM = form.medium_CPM.data
                    order.client_start = form.client_start.data
                    order.client_end = form.client_end.data
                    order.client_start_year = form.client_start.data.year
                    order.client_end_year = form.client_end.data.year
                    order.reminde_date = form.reminde_date.data
                    order.direct_sales = User.gets(form.direct_sales.data)
                    order.agent_sales = User.gets(form.agent_sales.data)
                    order.assistant_sales = User.gets(form.assistant_sales.data)
                    order.operaters = User.gets(form.operaters.data)
                    order.designers = User.gets(form.designers.data)
                    order.planers = User.gets(form.planers.data)
                    order.contract_type = form.contract_type.data
                    order.resource_type = form.resource_type.data
                    order.sale_type = form.sale_type.data
                    order.medium_group = MediumGroup.get(form.medium_group.data)
                    order.media = Media.get(form.media.data)
                    order.medium_money = form.medium_money.data
                    order.self_agent_rebate = str(self_rebate) + '-' + str(self_rabate_value)
                    if g.user.is_super_admin() or g.user.is_contract():
                        order.replace_sales = User.gets(
                            replace_saler_form.replace_salers.data)
                    order.save()
                    order.add_comment(g.user, u"更新了该订单信息")
                    flash(u'[直签媒体订单]%s 保存成功!' % order.name, 'success')
        elif info_type == 2:
            if not g.user.is_contract():
                flash(u'您没有编辑权限! 请联系合同管理员!', 'danger')
            else:
                order.contract = request.values.get("base_contract", "")
                order.save()
                flash(u'[%s]合同号保存成功!' % order.name, 'success')

                action_msg = u"合同号更新"
                msg = u"新合同号如下:\n\n%s" % (order.contract)
                to_users = order.direct_sales + order.assistant_sales +\
                    order.agent_sales + [order.creator, g.user]
                context = {'order': order,
                           'sender': g.user,
                           'action_msg': action_msg,
                           'info': msg,
                           'to_users': to_users}
                zhiqu_contract_apply_signal.send(
                    current_app._get_current_object(), context=context)
                order.add_comment(g.user, u"更新了合同号, %s" % msg)

    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    context = {'client_medium_form': form,
               'order': order,
               'now_date': datetime.now(),
               'reminder_emails': reminder_emails,
               'replace_saler_form': replace_saler_form}
    return tpl('client_medium_order_detail_info.html', **context)


@order_bp.route('/my_client_medium_orders', methods=['GET'])
def my_client_medium_orders():
    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or \
            g.user.is_media_leader() or g.user.is_finance() or g.user.is_aduit():
        orders = ClientMediumOrder.all()
    elif g.user.is_leader():
        orders = [
            o for o in ClientMediumOrder.all() if g.user.location in o.locations]
    else:
        orders = ClientMediumOrder.get_order_by_user(g.user)

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
    return client_medium_display_orders(orders, u'直签媒体订单', status_id)


def client_medium_display_orders(orders, title, status_id=-1):
    year = str(request.values.get('year', datetime.now().year))
    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        if status_id == 28:
            orders = [o for o in orders if o.contract_status != 20]
        elif status_id == 31:
            orders = [o for o in orders if o.back_money_status == 0]
        elif status_id == 32:
            orders = [o for o in orders if o.back_money_status != 0]
        elif status_id == 33:
            orders = [o for o in orders if o.invoice_pass_sum != float(o.money)]
        elif status_id == 34:
            orders = [o for o in orders if o.invoice_pass_sum == float(o.money)]
        else:
            orders = [o for o in orders if o.contract_status == status_id]
    orders = [o for o in orders if o.client_start.year == int(year) or o.client_end.year == int(year)]
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
        params = '&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s&year=%s' % (
            orderby, search_info, location_id, status_id, str(year))
        return tpl('client_medium_orders.html', title=title, orders=orders,
                   locations=select_locations, location_id=location_id,
                   statuses=select_statuses, status_id=status_id,
                   search_info=search_info, page=page,
                   orderby=orderby, now_date=datetime.now().date(),
                   params=params, year=year)


@order_bp.route('/client_medium_order/<order_id>/contract', methods=['POST'])
def client_medium_order_contract(order_id):
    order = ClientMediumOrder.get(order_id)
    if not order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    contract_status_change(order, action, emails, msg)
    order = ClientMediumOrder.get(order_id)
    if order.contract_status == CONTRACT_STATUS_DELETEPASS:
        return redirect(url_for('order.my_client_medium_orders'))
    return redirect(order.info_path())


@order_bp.route('/client_medium_order/<order_id>/attachment/<attachment_id>/<status>', methods=['GET'])
def client_medium_attach_status(order_id, attachment_id, status):
    order = ClientMediumOrder.get(order_id)
    attachment_status_change(order, attachment_id, status)
    return redirect(order.info_path())


#################
# 自动改单
#################
@order_bp.route('/edit_client_order', methods=['GET'])
def edit_client_order():
    search_info = request.args.get('search_info', '')
    location = int(request.args.get('location', 0))
    status = int(request.values.get('status', -1))
    page = int(request.args.get('p', 1))
    orders = list(EditClientOrder.all())

    if g.user.is_super_leader() or g.user.is_contract() or g.user.is_media() or \
            g.user.is_media_leader() or g.user.is_finance():
        orders = list(EditClientOrder.all())
    elif g.user.is_leader():
        orders = [o for o in EditClientOrder.all() if g.user.location in o.locations]
    else:
        orders = EditClientOrder.get_order_by_user(g.user)
    if status == -1:
        if g.user.is_super_leader():
            status = 0
        elif g.user.is_media_leader() or g.user.is_media():
            orders = [order for order in orders if order.contract_status == 2]
            status = 2
        elif g.user.is_leader() or g.user.is_media_leader():
            orders = [order for order in orders if order.contract_status == 3]
            status = 3
        elif g.user.is_contract():
            orders = [order for order in orders if order.contract_status == 4]
            status = 4
        elif g.user.is_finance():
            orders = [order for order in orders if order.contract_status == 5]
            status = 5
        else:
            orders = [order for order in orders if order.contract_status == 0]
            status = 0
    else:
        if status:
            orders = [order for order in orders if order.contract_status == status]
        else:
            pass
    if location:
        orders = [order for order in orders if location in order.locations]
    if search_info:
        orders = [order for order in orders if search_info.lower() in order.search_info.lower()]

    paginator = Paginator(orders, ORDER_PAGE_NUM)
    try:
        orders = paginator.page(page)
    except:
        orders = paginator.page(paginator.num_pages)
    params = '&searchinfo=%s&location=%s&status=%s' % (search_info, location, status)
    return tpl('edit_client_orders.html', orders=orders, search_info=search_info, page=page, params=params,
               location=location, status=status, EDIT_CONTRACT_STATUS_CN=EDIT_CONTRACT_STATUS_CN.items())


@order_bp.route('/edit_client_order/<edit_order_id>/info', methods=['GET', 'POST'])
def edit_client_order_info(edit_order_id):
    edit_order = EditClientOrder.get(edit_order_id)
    order = edit_order.client_order
    if request.method == 'POST':
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        edit_order.agent = Agent.get(request.values.get('agent'))
        edit_order.subject = int(request.values.get('subject', 1))
        edit_order.client = Client.get(request.values.get('client'))
        edit_order.campaign = request.values.get('campaign')
        edit_order.money = float(request.values.get('money', 0.0))
        edit_order.client_start = request.values.get('client_start')
        edit_order.client_end = request.values.get('client_end')
        edit_order.reminde_date = request.values.get('reminde_date')
        edit_order.direct_sales = User.gets(request.values.getlist('direct_sales'))
        edit_order.agent_sales = User.gets(request.values.getlist('agent_sales'))
        edit_order.assistant_sales = User.gets(request.values.getlist('assistant_sales'))
        edit_order.contract_type = request.values.get('contract_type')
        edit_order.resource_type = request.values.get('resource_type')
        edit_order.sale_type = request.values.get('sale_type')
        edit_order.creator = g.user
        edit_order.finish_time = datetime.now()
        edit_order.self_agent_rebate = str(self_rebate) + '-' + str(self_rabate_value)
        edit_order.save()
        for m in edit_order.medium_orders:
            self_medium_rebate = int(request.values.get('self_medium_rebate_' + str(m.id), 0))
            self_medium_rabate_value = float(request.values.get('self_medium_rabate_value_' + str(m.id), 0))
            m.media = Media.get(request.values.get('media_' + str(m.id)))
            m.medium_group = MediumGroup.get(request.values.get('medium_group_' + str(m.id)))
            m.sale_money = float(request.values.get('sale_money_' + str(m.id), 0.0))
            m.medium_money2 = float(request.values.get('medium_money2_' + str(m.id), 0.0))
            m.medium_start = request.values.get('medium_start_' + str(m.id), datetime.today())
            m.medium_end = request.values.get('medium_end_' + str(m.id), datetime.today())
            m.creator = g.user
            m.medium_CPM = request.values.get('medium_CPM_' + str(m.id), 0.0)
            m.sale_CPM = request.values.get('sale_CPM_' + str(m.id), 0.0)
            m.operaters = User.gets(request.values.getlist('operaters_' + str(m.id)))
            m.designers = User.gets(request.values.getlist('designers_' + str(m.id)))
            m.planers = User.gets(request.values.getlist('planers_' + str(m.id)))
            m.self_medium_rebate = str(self_medium_rebate) + '-' + str(self_medium_rabate_value)
            m.save()
        edit_order.add_comment(g.user, u"修改了申请修改客户订单:%s - %s - %s" %
                               (edit_order.agent.name,
                                edit_order.client.name,
                                edit_order.campaign),
                               msg_channel=15)
        return redirect(url_for('order.edit_client_order_info', edit_order_id=edit_order.id))
    operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
    designers = User.gets_by_team_type(TEAM_TYPE_DESIGNER)
    planers = User.gets_by_team_type(TEAM_TYPE_PLANNER)
    salers = User.sales()
    return tpl('edit_client_order_info.html', order=order, edit_order=edit_order,
               medium_groups=MediumGroup.all(), medias=Media.all(), salers=salers,
               operaters=operaters, designers=designers, planers=planers,
               agents=Agent.all(), clients=Client.all(), reminder_emails=User.all_active())


@order_bp.route('/edit_client_order/<edit_order_id>/delete', methods=['GET'])
def edit_client_order_delete(edit_order_id):
    if g.user.is_super_leader():
        EditClientOrder.get(edit_order_id).delete()
    return redirect(url_for('order.edit_client_order'))


@order_bp.route('/edit_client_order/<edit_order_id>/contract', methods=['POST'])
def edit_client_order_contract(edit_order_id):
    edit_order = EditClientOrder.get(edit_order_id)
    if edit_order.contract_status == 10:
        flash(u'已完成改单，请不要重复确认!', 'success')
        return redirect(edit_order.info_path())
    if not edit_order:
        abort(404)
    action = int(request.values.get('action'))
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    salers = edit_order.direct_sales + edit_order.agent_sales + edit_order.assistant_sales
    leaders = []
    for k in salers:
        leaders += k.team_leaders
    to_users = salers + [edit_order.creator, g.user]
    emails += [k.email for k in list(set(leaders))]

    if action in [2, 3]:
        medium_orders = edit_order.medium_orders
        if edit_order.money != sum([o.sale_money for o in medium_orders]):
            flash(u'客户合同金额与媒体合同售卖金额总和不符，请确认后进行审批!', 'danger')
            return redirect(edit_order.info_path())
        for m in medium_orders:
            if m.start_date_cn < edit_order.start_date_cn:
                flash(u'媒体合同的执行时间必须在客户合同执行时间内，请确认后进行审批!', 'danger')
                return redirect(edit_order.info_path())
            if m.end_date_cn > edit_order.end_date_cn:
                flash(u'媒体合同的执行时间必须在客户合同执行时间内，请确认后进行审批', 'danger')
                return redirect(edit_order.info_path())
    # 判断客户金额是否等于媒体售卖金额总和
    if action == 2:
        edit_order.contract_status = 2
        action_msg = u"申请媒介审批"
        to_users = to_users + edit_order.leaders + User.medias() + User.media_leaders()
    elif action == 12:
        action_msg = u"提醒媒介确认"
        to_users = to_users + edit_order.leaders + User.medias() + User.media_leaders()
    elif action == 3:
        action_msg = u"申请区域总监审批"
        edit_order.contract_status = 3
        to_users = to_users + edit_order.leaders
    elif action == 13:
        action_msg = u"提醒区域总监是审批"
        to_users = to_users + edit_order.leaders
    elif action == 4:
        edit_order.contract_status = 4
        action_msg = u"申请合同管理员审批"
        to_users = to_users + edit_order.leaders + User.contracts()
    elif action == 14:
        action_msg = u"提醒合同管理员审批"
        to_users = to_users + edit_order.leaders + User.contracts()
    elif action == 5:
        edit_order.contract_status = 5
        action_msg = u"申请财务审批"
        to_users = to_users + edit_order.leaders + User.finances()
    elif action == 15:
        action_msg = u"提醒财务审批"
        to_users = to_users + edit_order.leaders + User.finances()
    elif action == 31:
        edit_order.contract_status = 1
        action_msg = u"媒介驳回了您的改单申请"
        to_users = to_users + edit_order.leaders
        BackEditClientOrder.add(edit_client_order=edit_order,
                                user=edit_order.creator,
                                create_time=datetime.today())
    elif action == 41:
        edit_order.contract_status = 1
        action_msg = u"区域总监驳回了您的改单申请"
        to_users = to_users + edit_order.leaders
        BackEditClientOrder.add(edit_client_order=edit_order,
                                user=edit_order.creator,
                                create_time=datetime.today())
    elif action == 51:
        edit_order.contract_status = 1
        action_msg = u"合同管理员驳回了您的改单申请"
        to_users = to_users + edit_order.leaders
        BackEditClientOrder.add(edit_client_order=edit_order,
                                user=edit_order.creator,
                                create_time=datetime.today())
    elif action == 101:
        edit_order.contract_status = 1
        action_msg = u"财务驳回了您的改单申请"
        to_users = to_users + edit_order.leaders
        BackEditClientOrder.add(edit_client_order=edit_order,
                                user=edit_order.creator,
                                create_time=datetime.today())
    elif action == 10:
        action_msg = u"确认改单"
        edit_order.contract_status = 10
        to_users = to_users + edit_order.leaders + User.finances()
        # 确认改单后修改原始订单
        client_order = edit_order.client_order
        comment_msg = u'自动改单：\n\r客户合同修改项: \n\r'
        if client_order.agent != edit_order.agent:
            comment_msg += u'    修改代理/直客：%s（原：%s）\n\r' % (edit_order.agent.name, client_order.agent.name)
        if client_order.client != edit_order.client:
            comment_msg += u'    修改客户名称：%s（原：%s）\n\r' % (edit_order.client.name, client_order.client.name)
        if client_order.subject != edit_order.subject:
            comment_msg += u'    修改我方签约主体：%s（原：%s）\n\r' % (edit_order.subject_cn, client_order.subject_cn)
        if client_order.campaign != edit_order.campaign:
            comment_msg += u'    修改Campaign名称：%s（原：%s）\n\r' % (edit_order.campaign, client_order.campaign)
        if client_order.money != edit_order.money:
            comment_msg += u'    修改合同金额：%s（原：%s）\n\r' % (edit_order.money, client_order.money)
        if client_order.client_start != edit_order.client_start:
            comment_msg += u'    修改执行开始：%s（原：%s）\n\r' % (edit_order.start_date_cn, client_order.start_date_cn)
        if client_order.client_end != edit_order.client_end:
            comment_msg += u'    修改执行结束：%s（原：%s）\n\r' % (edit_order.end_date_cn, client_order.end_date_cn)
        if client_order.reminde_date != edit_order.reminde_date:
            comment_msg += u'    修改回款日期：%s（原：%s）\n\r' % (edit_order.reminde_date_cn, client_order.reminde_date_cn)
        if client_order.direct_sales != edit_order.direct_sales:
            comment_msg += u'    修改直客销售：%s（原：%s）\n\r' % (edit_order.direct_sales_names, client_order.direct_sales_names)
        if client_order.agent_sales != edit_order.agent_sales:
            comment_msg += u'    修改渠道销售：%s（原：%s）\n\r' % (edit_order.agent_sales_names, client_order.agent_sales_names)
        if client_order.assistant_sales != edit_order.assistant_sales:
            comment_msg += u'    修改销售助理：%s（原：%s）\n\r' % \
                (edit_order.assistant_sales_names,
                 client_order.assistant_sales_names)
        if client_order.contract_type != edit_order.contract_type:
            comment_msg += u'    修改合同模板类型：%s（原：%s）\n\r' % (edit_order.contract_type_cn, client_order.contract_type_cn)
        if client_order.resource_type != edit_order.resource_type:
            comment_msg += u'    修改售卖类型：%s（原：%s）\n\r' % (edit_order.resource_type_cn, client_order.resource_type_cn)
        if client_order.sale_type != edit_order.sale_type:
            comment_msg += u'    修改代理/直客：%s（原：%s）\n\r' % (edit_order.sale_type_cn, client_order.sale_type_cn)
        if client_order.self_agent_rebate != edit_order.self_agent_rebate:
            if int(client_order.self_agent_rebate_value['status']):
                o_msg = str(client_order.self_agent_rebate_value['value'])
            else:
                o_msg = u'无单笔返点'
            if int(edit_order.self_agent_rebate_value['status']):
                n_msg = str(edit_order.self_agent_rebate_value['value'])
            else:
                n_msg = u'无单笔返点'
            comment_msg += u'    修改单笔返点：%s（原：%s）\n\r' % (n_msg, o_msg)
        client_order.agent = edit_order.agent
        client_order.subject = edit_order.subject
        client_order.client = edit_order.client
        client_order.campaign = edit_order.campaign
        client_order.money = edit_order.money
        client_order.client_start = edit_order.client_start
        client_order.client_end = edit_order.client_end
        client_order.reminde_date = edit_order.reminde_date
        client_order.direct_sales = edit_order.direct_sales
        client_order.agent_sales = edit_order.agent_sales
        client_order.assistant_sales = edit_order.assistant_sales
        client_order.contract_type = edit_order.contract_type
        client_order.resource_type = edit_order.resource_type
        client_order.sale_type = edit_order.sale_type
        client_order.self_agent_rebate = edit_order.self_agent_rebate
        client_order.save()
        for m in edit_order.medium_orders:
            order = m.order
            comment_msg += '%s-%s 媒体合同修改项：\n\r' % (m.medium_group.name, m.media.name)
            if order.medium_group != m.medium_group:
                comment_msg += u'    修改媒体供应商：%s（原：%s）\n\r' % (m.medium_group.name, order.medium_group.name)
            if order.media != m.media:
                comment_msg += u'    修改投放媒体：%s（原：%s）\n\r' % (m.media.name, order.media.name)
            if order.sale_money != m.sale_money:
                comment_msg += u'    修改售卖金额：%s（原：%s）\n\r' % (m.sale_money, order.sale_money)
            if order.medium_money2 != m.medium_money2:
                comment_msg += u'    修改媒体金额：%s（原：%s）\n\r' % (m.medium_money2, order.medium_money2)
            if order.sale_CPM != m.sale_CPM:
                comment_msg += u'    修改预估量：%s（原：%s）\n\r' % (m.sale_CPM, order.sale_CPM)
            if order.medium_CPM != m.medium_CPM:
                comment_msg += u'    修改实际量：%s（原：%s）\n\r' % (m.medium_CPM, order.medium_CPM)
            if order.medium_start != m.medium_start:
                comment_msg += u'    修改执行开始：%s（原：%s）\n\r' % (m.start_date_cn, order.start_date_cn)
            if order.medium_end != m.medium_end:
                comment_msg += u'    修改执行结束：%s（原：%s）\n\r' % (m.end_date_cn, order.end_date_cn)
            if order.operaters != m.operaters:
                comment_msg += u'    修改执行人员：%s（原：%s）\n\r' % (m.operater_names, order.operater_names)
            if order.designers != m.designers:
                comment_msg += u'    修改设计人员：%s（原：%s）\n\r' % (m.designers_names, order.designers_names)
            if order.planers != m.planers:
                comment_msg += u'    修改策划人员：%s（原：%s）\n\r' % (m.planers_names, order.planers_names)
            if order.self_medium_rebate != m.self_medium_rebate:
                if int(order.self_medium_rebate_value['status']):
                    o_msg = str(order.self_medium_rebate_value['value'])
                else:
                    o_msg = u'无单笔返点'
                if int(m.self_medium_rebate_value['status']):
                    n_msg = str(m.self_medium_rebate_value['value'])
                else:
                    n_msg = u'无单笔返点'
                comment_msg += u'    修改单笔返点：%s（原：%s）\n\r' % (n_msg, o_msg)
            order.media = m.media
            order.medium_group = m.medium_group
            order.sale_money = m.sale_money
            order.medium_money2 = m.medium_money2
            order.medium_start = m.medium_start
            order.medium_end = m.medium_end
            order.medium_CPM = m.medium_CPM
            order.sale_CPM = m.sale_CPM
            order.operaters = m.operaters
            order.designers = m.designers
            order.planers = m.planers
            order.self_medium_rebate = m.self_medium_rebate
            order.save()
        comment_msg += u'by %s \n\r' % (edit_order.creator.name)
        edit_order.add_comment(g.user, comment_msg, msg_channel=15)
        client_order.add_comment(g.user, comment_msg)
        _insert_executive_report(client_order, 'reload')
    edit_order.save()
    flash(u'[%s] %s ' % (edit_order.name, action_msg), 'success')
    context = {
        "to_other": emails,
        "sender": g.user,
        "to_users": to_users,
        "action_msg": action_msg,
        "order": edit_order,
        "info": msg,
        "action": action
    }
    zhiqu_edit_contract_apply_signal.send(current_app._get_current_object(), context=context)
    edit_order.add_comment(g.user, u"%s \n\r\n\r %s" % (action_msg, msg), msg_channel=15)
    return redirect(url_for('order.edit_client_order_info', edit_order_id=edit_order_id))


@order_bp.route('/edit_client_order/<order_id>/create', methods=['GET', 'POST'])
def edit_client_order_create(order_id):
    order = ClientOrder.get(order_id)
    edit_order_count = EditClientOrder.query.filter(and_(EditClientOrder.contract_status != 10,
                                                    EditClientOrder.client_order == order)).count()
    if edit_order_count > 0:
        flash('对不起，该订单正在申请修改，请在订单修改完成后再进行修改申请', 'danger')
        return redirect(url_for('order.order_info', order_id=order.id, tab_id=1))
    if request.method == 'POST':
        self_rebate = int(request.values.get('self_rebate', 0))
        self_rabate_value = float(request.values.get('self_rabate_value', 0))
        edit_order = EditClientOrder.add(client_order=order,
                                         contract=order.contract,
                                         agent=Agent.get(request.values.get('agent')),
                                         subject=int(request.values.get('subject', 1)),
                                         client=Client.get(request.values.get('client')),
                                         campaign=request.values.get('campaign'),
                                         money=float(request.values.get('money', 0.0)),
                                         client_start=request.values.get('client_start'),
                                         client_end=request.values.get('client_end'),
                                         reminde_date=request.values.get('reminde_date'),
                                         direct_sales=User.gets(request.values.getlist('direct_sales')),
                                         agent_sales=User.gets(request.values.getlist('agent_sales')),
                                         assistant_sales=User.gets(request.values.getlist('assistant_sales')),
                                         contract_type=request.values.get('contract_type'),
                                         resource_type=request.values.get('resource_type'),
                                         sale_type=request.values.get('sale_type'),
                                         creator=g.user,
                                         contract_status=1,
                                         create_time=datetime.now(),
                                         finish_time=datetime.now(),
                                         self_agent_rebate=str(self_rebate) + '-' + str(self_rabate_value))
        edit_medium_orders = []
        for m in order.medium_orders:
            self_medium_rebate = int(request.values.get('self_medium_rebate_' + str(m.id), 0))
            self_medium_rabate_value = float(request.values.get('self_medium_rabate_value_' + str(m.id), 0))
            mo = EditOrder.add(order=m,
                               medium_contract=m.medium_contract,
                               campaign=edit_order.campaign,
                               media=Media.get(request.values.get('media_' + str(m.id))),
                               medium_group=MediumGroup.get(request.values.get('medium_group_' + str(m.id))),
                               sale_money=float(request.values.get('sale_money_' + str(m.id), 0.0)),
                               medium_money2=float(request.values.get('medium_money2_' + str(m.id), 0.0)),
                               medium_start=request.values.get('medium_start_' + str(m.id), datetime.today()),
                               medium_end=request.values.get('medium_end_' + str(m.id), datetime.today()),
                               creator=g.user,
                               medium_CPM=request.values.get('medium_CPM_' + str(m.id), 0.0),
                               sale_CPM=request.values.get('sale_CPM_' + str(m.id), 0.0),
                               operaters=User.gets(request.values.getlist('operaters_' + str(m.id))),
                               designers=User.gets(request.values.getlist('designers_' + str(m.id))),
                               planers=User.gets(request.values.getlist('planers_' + str(m.id))),
                               self_medium_rebate=str(self_medium_rebate) + '-' + str(self_medium_rabate_value))
            edit_medium_orders.append(mo)
        edit_order.medium_orders = edit_medium_orders
        edit_order.save()
        edit_order.add_comment(g.user, u"申请修改客户订单:%s - %s - %s" %
                               (edit_order.agent.name, edit_order.client.name, edit_order.campaign),
                               msg_channel=15)
        flash('请尽快发出申请，以便完成改单', 'success')
        return redirect(url_for('order.edit_client_order_info', edit_order_id=edit_order.id))
    operaters = User.gets_by_team_type(TEAM_TYPE_OPERATER) + User.gets_by_team_type(TEAM_TYPE_OPERATER_LEADER)
    designers = User.gets_by_team_type(TEAM_TYPE_DESIGNER)
    planers = User.gets_by_team_type(TEAM_TYPE_PLANNER)
    salers = User.sales()
    return tpl('edit_client_order_create.html', order=order,
               medium_groups=MediumGroup.all(), medias=Media.all(), salers=salers,
               operaters=operaters, designers=designers, planers=planers,
               agents=Agent.all(), clients=Client.all())
