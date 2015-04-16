# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.client_order import ClientOrder
from models.douban_order import DoubanOrder
from models.outsource import (
    OutSource, OUTSOURCE_STATUS_APPLY_MONEY, OUTSOURCE_STATUS_PAIED, INVOICE_RATE, DoubanOutSource)
from models.user import User
from libs.signals import outsource_apply_signal
from controllers.finance.helpers.pay_helpers import write_excel
from controllers.tools import get_download_response


finance_pay_bp = Blueprint(
    'finance_pay', __name__, template_folder='../../templates/finance')


@finance_pay_bp.route('/', methods=['GET'])
def index():
    orders = [k for k in list(ClientOrder.all()) if k.get_outsources_by_status(
        OUTSOURCE_STATUS_APPLY_MONEY)]
    return tpl('/finance/pay/index.html', orders=orders)


@finance_pay_bp.route('/douban', methods=['GET'])
def douban_index():
    orders = [k for k in list(DoubanOrder.all()) if k.get_outsources_by_status(
        OUTSOURCE_STATUS_APPLY_MONEY)]
    return tpl('/finance/pay/douban_index.html', orders=orders)


@finance_pay_bp.route('/pass', methods=['GET'])
def index_pass():
    type = request.values.get('type', '')
    if type == 'douban':
        title = u'申请通过的直签豆瓣订单打款'
        orders = [k for k in list(DoubanOrder.all()) if k.get_outsources_by_status(
            OUTSOURCE_STATUS_PAIED)]
    else:
        title = u'申请通过的客户订单打款'
        orders = [k for k in list(ClientOrder.all()) if k.get_outsources_by_status(
            OUTSOURCE_STATUS_PAIED)]

    dtype = request.args.get('dtype', '')
    if dtype == 'excel':
        xls = write_excel(list(orders), type)
        response = get_download_response(
            xls, ("%s-%s.xls" % (u"申请过的打款信息", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8'))
        return response
    return tpl('/finance/pay/index_pass.html', orders=orders, title=title, type=type)


@finance_pay_bp.route('/<order_id>/info', methods=['GET'])
def info(order_id):
    order = ClientOrder.get(order_id)
    if not order:
        abort(404)
    outsources_data = {
        'PAIED': [{'outsource': x} for x in order.get_outsources_by_status(OUTSOURCE_STATUS_PAIED)],
        'APPLY_MONEY': [{'outsource': x} for x in order.get_outsources_by_status(OUTSOURCE_STATUS_APPLY_MONEY)],
    }
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/pay/info.html', order=order,
               outsources_data=outsources_data, reminder_emails=reminder_emails)


@finance_pay_bp.route('/<order_id>/douban_info', methods=['GET'])
def douban_info(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    outsources_data = {
        'PAIED': [{'outsource': x} for x in order.get_outsources_by_status(OUTSOURCE_STATUS_PAIED)],
        'APPLY_MONEY': [{'outsource': x} for x in order.get_outsources_by_status(OUTSOURCE_STATUS_APPLY_MONEY)],
    }
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/pay/douban_info.html', order=order,
               outsources_data=outsources_data, reminder_emails=reminder_emails)


@finance_pay_bp.route('/<outsource_id>/pay_num', methods=['POST'])
def outsource_pay_num(outsource_id):
    type = request.values.get('type', '')
    if type == 'douban':
        outsource = DoubanOutSource.get(outsource_id)
    else:
        outsource = OutSource.get(outsource_id)
    if not outsource:
        abort(404)
    if outsource.invoice:
        pay_num = outsource.num
    else:
        pay_num = outsource.num * float(1 - INVOICE_RATE)
    pay_num = request.values.get('pay_num', pay_num)
    outsource.pay_num = pay_num
    outsource.save()
    flash(u'保存成功!', 'success')
    if type == 'douban':
        outsource.douban_order.add_comment(g.user,
                                           u"更新了外包:\n\r%s 打款金额%s" % (
                                               outsource.name, str(outsource.pay_num)),
                                           msg_channel=2)
    else:
        outsource.client_order.add_comment(g.user,
                                           u"更新了外包:\n\r%s 打款金额%s" % (
                                               outsource.name, str(outsource.pay_num)),
                                           msg_channel=2)
    if type == 'douban':
        return redirect(url_for("finance_pay.douban_info", order_id=outsource.douban_order.id))
    else:
        return redirect(url_for("finance_pay.info", order_id=outsource.client_order.id))


@finance_pay_bp.route('/<outsource_id>/back', methods=['GET'])
def outsource_back(outsource_id):
    type = request.values.get('type', '')
    if type == 'douban':
        outsource = DoubanOutSource.get(outsource_id)
    else:
        outsource = OutSource.get(outsource_id)

    outsource.status = OUTSOURCE_STATUS_APPLY_MONEY
    outsource.create_time = datetime.date.today()
    outsource.save()
    flash(u'外包款项撤回，名称:%s打款金额%s' %
          (outsource.name, str(outsource.pay_num)), 'success')
    if type == 'douban':
        outsource.douban_order.add_comment(
            g.user, u'外包款项撤回，名称%s打款金额%s' % (outsource.name, str(outsource.pay_num)), msg_channel=2)
    else:
        outsource.client_order.add_comment(
            g.user, u'外包款项撤回，名称%s打款金额%s' % (outsource.name, str(outsource.pay_num)), msg_channel=2)

    if type == 'douban':
        order = outsource.douban_order
    else:
        order = outsource.medium_order.client_order

    if type == 'douban':
        to_users = outsource.douban_order.direct_sales + outsource.douban_order.agent_sales + \
            [outsource.douban_order.creator, g.user] + \
            User.operater_leaders() + outsource.douban_order.operater_users
    else:
        to_users = outsource.client_order.direct_sales + outsource.client_order.agent_sales + \
            [outsource.client_order.creator, g.user] + \
            User.operater_leaders() + outsource.client_order.operater_users

    to_emails = list(set([x.email for x in to_users]))
    title = u'【费用报备】%s-%s-%s' % (order.contract or u'无合同号', order.jiafang_name, u'外包款项撤回')
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": u'外包款项撤回',
                     "msg": u'',
                     "order": order,
                     "title": title,
                     "to_users": ','.join([k.name for k in order.agent_sales] + [k.name for k in order.operater_users]),
                     "outsources": [outsource]}
    outsource_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    if type == 'douban':
        return redirect(url_for("finance_pay.douban_info", order_id=outsource.douban_order.id))
    else:
        return redirect(url_for("finance_pay.info", order_id=outsource.client_order.id))


@finance_pay_bp.route('/<outsource_id>/pass', methods=['POST'])
def outsource_pass(outsource_id):
    type = request.values.get('type', '')
    if type == 'douban':
        outsource = DoubanOutSource.get(outsource_id)
    else:
        outsource = OutSource.get(outsource_id)
    if not outsource:
        abort(404)
    outsources_ids = request.values.getlist('outsources')

    if type == 'douban':
        outsources = DoubanOutSource.gets(outsources_ids)
    else:
        outsources = OutSource.gets(outsources_ids)

    if not outsources:
        abort(403)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    action = int(request.values.get('action', 0))

    if type == 'douban':
        to_users = outsource.douban_order.direct_sales + outsource.douban_order.agent_sales + \
            [outsource.douban_order.creator, g.user] + User.operater_leaders()
    else:
        to_users = outsource.client_order.direct_sales + outsource.client_order.agent_sales + \
            [outsource.client_order.creator, g.user] + User.operater_leaders()
    to_emails = list(set(emails + [x.email for x in to_users]))

    if action != 10:
        outsource_status = OUTSOURCE_STATUS_PAIED
        action_msg = u'外包款已打'
        for outsource in outsources:
            outsource.status = outsource_status
            outsource.create_time = datetime.date.today()
            outsource.save()
            flash(u'外包款已打，名称:%s打款金额%s' %
                  (outsource.name, str(outsource.pay_num)), 'success')
            if type == 'douban':
                outsource.douban_order.add_comment(
                    g.user, u'外包款已打，名称%s打款金额%s' % (outsource.name, str(outsource.pay_num)), msg_channel=2)
            else:
                outsource.client_order.add_comment(
                    g.user, u'外包款已打，名称%s打款金额%s' % (outsource.name, str(outsource.pay_num)), msg_channel=2)
    else:
        action_msg = u'消息提醒'

    if type == 'douban':
        order = outsource.douban_order
    else:
        order = outsource.medium_order.client_order

    title = u'【费用报备】%s-%s-%s' % (order.contract or u'无合同号', order.jiafang_name, action_msg)
    apply_context = {"sender": g.user,
                     "to": to_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order,
                     "title": title,
                     "to_users": ','.join([k.name for k in order.agent_sales] + [k.name for k in order.operater_users]),
                     "outsources": outsources}
    outsource_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    if type == 'douban':
        return redirect(url_for("finance_pay.douban_info", order_id=outsource.douban_order.id))
    else:
        return redirect(url_for("finance_pay.info", order_id=outsource.client_order.id))
