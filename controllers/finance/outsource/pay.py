# -*- coding: utf-8 -*-
import datetime
import operator

from flask import request, redirect, Blueprint, url_for, flash, g, abort, current_app
from flask import render_template as tpl

from models.outsource import (
    OutSource, OUTSOURCE_STATUS_APPLY_MONEY, OUTSOURCE_STATUS_PAIED, MergerDoubanOutSource,
    INVOICE_RATE, DoubanOutSource, MergerOutSource, MERGER_OUTSOURCE_STATUS_PAIED,
    MergerDoubanPersonalOutSource, MergerPersonalOutSource,
    OutSourceTarget)
from models.user import User
from libs.signals import outsource_apply_signal, merger_outsource_apply_signal
# from controllers.finance.helpers.pay_helpers import write_excel
# from controllers.tools import get_download_response
from libs.mail import mail


finance_outsource_pay_bp = Blueprint(
    'finance_outsource_pay', __name__, template_folder='../../templates/finance/outsource')


@finance_outsource_pay_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    targets = [{
        'id': k.id,
        'name': k.name, 'type_cn': k.type_cn, 'bank': k.bank,
        'card': k.card, 'alipay': k.alipay, 'contract': k.contract,
        'unpay': len(k.merger_client_order_outsources_by_status(2)),
        'pay': len(k.merger_client_order_outsources_by_status(0))}
        for k in OutSourceTarget.all() if k.otype in [1, None]]
    personal_targets = {'unpay': MergerPersonalOutSource.query.filter_by(status=2).count(),
                        'pay': MergerPersonalOutSource.query.filter_by(status=0).count()}

    targets = sorted(targets, key=operator.itemgetter('unpay'), reverse=True)
    return tpl('/finance/outsource/pay/index.html', targets=targets, personal_targets=personal_targets)


@finance_outsource_pay_bp.route('/<target_id>/info', methods=['GET'])
def info(target_id):
    if not g.user.is_finance():
        abort(404)
    if int(target_id) == 0:
        target = None
        apply_money_merger_outsources = list(
            MergerPersonalOutSource.query.filter_by(status=2))
        paid_merger_outsources = list(
            MergerPersonalOutSource.query.filter_by(status=0))
    else:
        target = OutSourceTarget.get(target_id)
        apply_money_merger_outsources = target.merger_client_order_outsources_by_status(
            2)
        paid_merger_outsources = target.merger_client_order_outsources_by_status(
            0)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/outsource/pay/info.html', target=target, reminder_emails=reminder_emails,
               apply_money_merger_outsources=apply_money_merger_outsources,
               paid_merger_outsources=paid_merger_outsources)


@finance_outsource_pay_bp.route('/merget_client_target/<target_id>/paid', methods=['GET', 'POST'])
def merget_client_target_paid(target_id):
    if not g.user.is_finance():
        abort(404)
    action = int(request.values.get('action', 1))
    outsource_ids = request.values.getlist('outsources')
    if int(target_id) == 0:
        merger_clients = MergerPersonalOutSource.gets(outsource_ids)
    else:
        merger_clients = MergerOutSource.gets(outsource_ids)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    pay_time = request.values.get(
        'pay_time', datetime.datetime.now().strftime('%Y-%m-%d'))
    if action == 0:
        sub_title = u"外包已打款"
        for k in merger_clients:
            for o in k.outsources:
                o.status = OUTSOURCE_STATUS_PAIED
                o.invoice = k.invoice
                o.create_time = datetime.datetime.strptime(pay_time, '%Y-%m-%d')
                o.save()
            k.status = MERGER_OUTSOURCE_STATUS_PAIED
            k.save()
            title = u'【费用报备】%s' % (sub_title)
            apply_context = {"sender": g.user,
                             "to": emails,
                             "msg": msg,
                             "title": title,
                             "action": action,
                             "merger_outsource": k}
            merger_outsource_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        flash(sub_title, 'success')
    return redirect(url_for("finance_outsource_pay.info", target_id=target_id))


@finance_outsource_pay_bp.route('/merget_douban_target/<target_id>/paid', methods=['GET', 'POST'])
def merget_douban_target_paid(target_id):
    if not g.user.is_finance():
        abort(404)
    action = int(request.values.get('action', 1))
    outsource_ids = request.values.getlist('outsources')
    if int(target_id) == 0:
        merger_clients = MergerDoubanPersonalOutSource.gets(outsource_ids)
    else:
        merger_clients = MergerDoubanOutSource.gets(outsource_ids)
    emails = request.values.getlist('email')
    msg = request.values.get('msg', '')
    pay_time = request.values.get(
        'pay_time', datetime.datetime.now().strftime('%Y-%m-%d'))
    if action == 0:
        sub_title = u"外包已打款"
        for k in merger_clients:
            for o in k.outsources:
                o.status = OUTSOURCE_STATUS_PAIED
                o.invoice = k.invoice
                o.create_time = datetime.datetime.strptime(pay_time, '%Y-%m-%d')
                o.save()
            k.status = MERGER_OUTSOURCE_STATUS_PAIED
            k.save()
            title = u'【费用报备】%s' % (sub_title)
            apply_context = {"sender": g.user,
                             "to": emails,
                             "msg": msg,
                             "title": title,
                             "action": action,
                             "merger_outsource": k}
            merger_outsource_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        flash(sub_title, 'success')
    return redirect(url_for("finance_outsource_pay.douban_info", target_id=target_id))


@finance_outsource_pay_bp.route('/<merger_id>/pass', methods=['GET'])
def merger_outsources_pass(merger_id):
    if not g.user.is_finance():
        abort(404)
    type = request.values.get('type', '')
    if type == 'douban':
        merger = MergerDoubanOutSource.get(merger_id)
    else:
        merger = MergerOutSource.get(merger_id)
    merger.status = MERGER_OUTSOURCE_STATUS_PAIED
    merger.create_time = datetime.date.today()
    for k in merger.outsources:
        k.status = OUTSOURCE_STATUS_PAIED
        k.invoice = merger.invoice
        k.create_time = datetime.date.today()
        k.save()
    merger.save()
    flash(u'打款成功!', 'success')
    title = u'【费用报备】%s' % (u'打款成功')
    if type == 'douban':
        url = mail.app.config['DOMAIN'] + url_for(
            'outsource.merget_douban_target_info', target_id=merger.target.id, status=OUTSOURCE_STATUS_PAIED)
    else:
        url = mail.app.config['DOMAIN'] + url_for(
            'outsource.merget_client_target_info', target_id=merger.target.id, status=OUTSOURCE_STATUS_PAIED)
    apply_context = {"sender": g.user,
                     "url": url,
                     "to": [k.email for k in User.operater_leaders() + User.finances()],
                     "action_msg": u'打款成功',
                     "msg": '',
                     "title": title,
                     "to_users": ','.join([k.name for k in User.operater_leaders()]),
                     "invoice": str(merger.invoice),
                     "remark": merger.remark,
                     "outsources": merger.outsources}
    merger_outsource_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    flash(u'已发送邮件给 %s ' % (', '.join(apply_context['to'])), 'info')
    if type == 'douban':
        return redirect(url_for("finance_outsource_pay.douban_index"))
    else:
        return redirect(url_for("finance_outsource_pay.index"))


@finance_outsource_pay_bp.route('/douban', methods=['GET'])
def douban_index():
    if not g.user.is_finance():
        abort(404)
    targets = [{
        'id': k.id,
        'name': k.name, 'type_cn': k.type_cn, 'bank': k.bank,
        'card': k.card, 'alipay': k.alipay, 'contract': k.contract,
        'unpay': len(k.merger_douban_order_outsources_by_status(2)),
        'pay': len(k.merger_douban_order_outsources_by_status(0))}
        for k in OutSourceTarget.all() if k.otype in [1, None]]
    personal_targets = {'unpay': MergerDoubanPersonalOutSource.query.filter_by(status=2).count(),
                        'pay': MergerDoubanPersonalOutSource.query.filter_by(status=0).count()}
    targets = sorted(targets, key=operator.itemgetter('unpay'), reverse=True)
    return tpl('/finance/outsource/pay/douban_index.html', targets=targets, personal_targets=personal_targets)


@finance_outsource_pay_bp.route('/pass', methods=['GET'])
def index_pass():
    if not g.user.is_finance():
        abort(404)
    type = request.values.get('type', '')
    if type == 'douban':
        merger_outsources = MergerDoubanOutSource.get_outsources_by_status(
            MERGER_OUTSOURCE_STATUS_PAIED)
    else:
        merger_outsources = MergerOutSource.get_outsources_by_status(
            MERGER_OUTSOURCE_STATUS_PAIED)
    return tpl('/finance/outsource/pay/index_pass.html', merger_outsources=merger_outsources)


@finance_outsource_pay_bp.route('/<target_id>/douban_info', methods=['GET'])
def douban_info(target_id):
    if not g.user.is_finance():
        abort(404)
    if int(target_id) == 0:
        target = None
        apply_money_merger_outsources = list(
            MergerDoubanPersonalOutSource.query.filter_by(status=2))
        paid_merger_outsources = list(
            MergerDoubanPersonalOutSource.query.filter_by(status=0))
    else:
        target = OutSourceTarget.get(target_id)
        apply_money_merger_outsources = target.merger_douban_order_outsources_by_status(
            2)
        paid_merger_outsources = target.merger_douban_order_outsources_by_status(
            0)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/finance/outsource/pay/douban_info.html', target=target, reminder_emails=reminder_emails,
               apply_money_merger_outsources=apply_money_merger_outsources,
               paid_merger_outsources=paid_merger_outsources)


@finance_outsource_pay_bp.route('/<outsource_id>/pay_num', methods=['POST'])
def outsource_pay_num(outsource_id):
    if not g.user.is_finance():
        abort(404)
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
        return redirect(url_for("finance_outsource_pay.douban_info", order_id=outsource.douban_order.id))
    else:
        return redirect(url_for("finance_outsource_pay.info", order_id=outsource.client_order.id))


@finance_outsource_pay_bp.route('/<outsource_id>/back', methods=['GET'])
def outsource_back(outsource_id):
    if not g.user.is_finance():
        abort(404)
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
        return redirect(url_for("finance_outsource_pay.douban_info", order_id=outsource.douban_order.id))
    else:
        return redirect(url_for("finance_outsource_pay.info", order_id=outsource.client_order.id))


@finance_outsource_pay_bp.route('/<outsource_id>/pass', methods=['POST'])
def outsource_pass(outsource_id):
    if not g.user.is_finance():
        abort(404)
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
        return redirect(url_for("finance_outsource_pay.douban_info", order_id=outsource.douban_order.id))
    else:
        return redirect(url_for("finance_outsource_pay.info", order_id=outsource.client_order.id))
