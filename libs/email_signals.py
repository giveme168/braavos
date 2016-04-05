#-*- coding: UTF-8 -*-
import datetime

from flask import url_for, g, flash
from libs.mail import send_simple_mail, send_attach_mail, send_html_mail, mail
from blinker import Namespace

from models.user import User
from models.account.data import PersonNotice

braavos_signals = Namespace()

password_changed_signal = braavos_signals.signal('password_changed')
add_comment_signal = braavos_signals.signal('add_comment')
zhiqu_contract_apply_signal = braavos_signals.signal('zhiqu_contract_apply')
medium_invoice_apply_signal = braavos_signals.signal('medium_invoice_apply')
agent_invoice_apply_signal = braavos_signals.signal('agent_invoice_apply')
invoice_apply_signal = braavos_signals.signal('invoice_apply')
medium_rebate_invoice_apply_signal = braavos_signals.signal(
    'medium_rebate_invoice_apply')
framework_douban_contract_apply_signal = braavos_signals.signal(
    'framework_douban_contract_apply')
douban_contract_apply_signal = braavos_signals.signal('douban_contract_apply')
outsource_distribute_signal = braavos_signals.signal('outsource_distribute')
outsource_apply_signal = braavos_signals.signal('outsource_apply')
merger_outsource_apply_signal = braavos_signals.signal(
    'merger_outsource_apply')
account_leave_apply_signal = braavos_signals.signal('account_leave_apply')
account_out_apply_signal = braavos_signals.signal('account_out_apply')
planning_bref_signal = braavos_signals.signal('planning_bref')
account_kpi_apply_signal = braavos_signals.signal('account_kpi_apply')
back_money_apply_signal = braavos_signals.signal('back_money_apply')
medium_back_money_apply_signal = braavos_signals.signal('medium_back_money_apply')


def _get_active_user(send_users):
    active_users = User.all_active()
    send_users = [k for k in send_users if k in active_users]
    return list(set(send_users))


def _get_active_user_email(send_users):
    send_users = _get_active_user(send_users)
    return [k.email for k in send_users]


def _get_active_user_name(send_users):
    send_users = _get_active_user(send_users)
    return [k.name for k in send_users]


def _insert_person_notcie(send_users, title, content):
    for k in list(set(send_users)):
        PersonNotice.add(
            title=title,
            content=content,
            user=k,
            create_time=datetime.datetime.now(),
        )


def password_changed(sender, user):
    send_simple_mail(u'InAd帐号密码重设通知',
                     recipients=[user.email],
                     body=u'您的InAd帐号密码已经被重新设置, 如果不是您的操作, 请联系广告平台管理员')


def add_comment(sender, comment, msg_channel=0):
    send_simple_mail(u'InAd留言提醒[%s]' % comment.target.name,
                     recipients=[
                         u.email for u in comment.target.get_mention_users(except_user=comment.creator, msg_channel=msg_channel)],
                     body=(u'%s的新留言:\n\n %s' % (comment.creator.name, comment.msg)))


def contract_apply_douban(sender, apply_context):
    """豆瓣直签豆瓣、关联豆瓣订单 发送豆瓣合同管理员"""
    order = apply_context['order']
    file_paths = []
    if order.get_last_contract():
        file_paths.append(order.get_last_contract().real_path)
    if order.get_last_schedule():
        file_paths.append(order.get_last_schedule().real_path)
    douban_contracts = User.douban_contracts()
    to_users = [k.email for k in User.douban_contracts()] + \
        _get_active_user_email(User.contracts()) + \
        _get_active_user_email(order.direct_sales + order.agent_sales + [order.creator])
    send_attach_mail(u'【合同流程】%s-%s' % (order.name, apply_context['action_msg']),
                     recipients=to_users,
                     body=order.douban_contract_email_info(
                         title=u"请帮忙打印合同, 谢谢~"),
                     file_paths=file_paths)


def zhiqu_contract_apply(sender, context, douban_type=False):
    order = context['order']
    to_users = context['to_users']
    action_msg = context['action_msg']
    info = context['info']
    to_other = []
    if context.has_key('to_other'):
        to_other = context['to_other']
    if context.has_key('action'):
        action = context['action']
    else:
        action = None
    if order.__tablename__ == 'bra_douban_order' and order.contract_status == 4 and douban_type:
        contract_apply_douban(sender, context)
    if action and int(action) == 1:
        if order.__tablename__ == 'bra_medium_framework_order':
            leader_users = [k for k in to_users if k.team.type in [20]]
        else:
            leader_users = [k for k in to_users if k.team.type in [9]]
        action_info = u'请' + ','.join(_get_active_user_name(leader_users)) +\
            u'进行审批'
    elif action and int(action) == 3:
        action_info = order.creator.name + u'您的订单被拒绝，请核查订单，从新发送申请'
    elif action and int(action) == 2:
        contract_users = [k for k in to_users if k.team.type in [10]]
        action_info = u'请' + ','.join(_get_active_user_name(contract_users)) +\
            u'进行合同号分配'
    elif action and int(action) == 4:
        contract_users = [k for k in to_users if k.team.type in [10]]
        if douban_type:
            action_info = u'合同打印请求已发给豆瓣，请相关人员等待'
        else:
            action_info = u'请' + ','.join(_get_active_user_name(contract_users)) +\
                u'进行合同打印'
    elif action and int(action) == 5:
        if order.__tablename__ == 'bra_medium_framework_order':
            salers = order.medium_users + [order.creator]
        else:
            salers = order.direct_sales + order.agent_sales + [order.creator]
        action_info = ','.join(_get_active_user_name(salers)) + u'您的合同打印完成'
    elif action and int(action) == 6:
        medium_users = [k for k in to_users if k.team.type in [12, 20]]
        action_info = u'请' + ','.join(_get_active_user_name(medium_users)) +\
            u'进行利润分配'
    elif action and int(action) == 7:
        leader_users = [k for k in to_users if k.team.type in [9]]
        action_info = u'请' + ','.join(_get_active_user_name(leader_users)) +\
            u'进行撤单审批'
    elif action and int(action) == 8:
        action_info = u'请黄亮进行确认撤单审批'
    elif action and int(action) == 9:
        action_info = u'合同已撤单'
    elif action and int(action) == 19:
        contract_users = [k for k in to_users if k.team.type in [10]]
        action_info = u'请' + ','.join(_get_active_user_name(contract_users)) +\
            u'进行合同确认归档'
    elif action and int(action) == 20:
        if order.__tablename__ == 'bra_medium_framework_order':
            salers = order.medium_users + [order.creator]
        else:
            salers = order.direct_sales + order.agent_sales + [order.creator]
        action_info = ','.join(_get_active_user_name(salers)) + u'您的合同已确认归档'
    else:
        action_info = ''
    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_framework_order':
        title = u"【框架订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_douban_order':
        title = u"【直签豆瓣订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchAd_bra_client_order':
        title = u"【搜索业务普通订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_searchAd_framework_order':
        title = u"【搜索业务框架订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchad_bra_rebate_order':
        title = u"【搜索业务返点订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_medium_framework_order':
        title = u"【媒体框架订单-合同流程】- %s" % (order.name)
    else:
        title = u"【合同流程】- %s" % (order.name)

    url = mail.app.config['DOMAIN'] + order.info_path()
    body = u"""
<h3 style="color:red;">流程状态: %s
<br/>%s<br/>订单链接地址: %s</h3>
<p><h4>状态信息:</h4>
%s</p>
<p><h4>订单信息:</h4>
%s</p>

<p><h4>留言如下:</h4>
    <br/>%s</p>

<p>by %s</p>
""" % (action_msg, action_info, url, info, order.email_info, info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users) + to_other, body=body.replace('\n', '<br/>'))


def medium_invoice_apply(sender, context):
    order = context['order']
    invoice = context['invoice']
    to_users = context['to_users']
    action_msg = context['action_msg']
    invoice_pays = context['invoice_pays']
    info = context['info']
    to_other = []
    if context.has_key('to_other'):
        to_other = context['to_other']
    invoice_info = u"发票信息: " + invoice.detail + u'; 发票金额: ' + \
        str(invoice.money) + u'; 发票号: ' + invoice.invoice_num + \
        u'; 未打款金额: ' + str(invoice.get_unpay_money)
    if invoice.invoice_num == '88888888':
        invoice_info += u'; 未开发票'
    invoice_pay_info = "\n".join(
        [u'打款金额: ' + str(o.money) + u'; 打款时间: ' + o.pay_time_cn + u'; 留言信息: ' + o.detail for o in invoice_pays])

    if context['send_type'] == "saler":
        url = mail.app.config[
            'DOMAIN'] + '/saler/client_order/medium_invoice/%s/invoice' % (invoice.id)
        action_info = u'请黄亮审批媒体打款'
    elif context['send_type'] == 'end':
        url = mail.app.config[
            'DOMAIN'] + '/saler/client_order/medium_invoice/%s/invoice' % (invoice.id)
        action_info = u'媒体款项已打款'
    else:
        url = mail.app.config[
            'DOMAIN'] + '/finance/client_order/medium_pay/%s/info' % (invoice.client_order_id)
        finance_users = [k for k in to_users if k.team.type in [13]]
        action_info = u'黄亮已同意媒体打款，请' + \
            ', '.join(_get_active_user_name(finance_users)) + u'打款'

    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
    else:
        title = u"【合同流程】- %s" % (order.name)
    body = u"""
<h3 style="color:red;">流程状态: %s
<br/>%s<br/>订单链接地址: %s</h3>
<p><h4>状态信息:</h4>
发票信息:%s<br/>打款信息:<br/>%s</p>
<p><h4>订单信息:</h4>
%s</p>

<p><h4>留言如下:</h4>
    <br/>%s</p>

<p>by %s</p>
""" % (action_msg, action_info, url, invoice_info, invoice_pay_info, order.email_info, info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users) + to_other, body=body.replace('\n', '<br/>'))


def agent_invoice_apply(sender, context):
    order = context['order']
    invoice = context['invoice']
    to_users = context['to_users']
    action_msg = context['action_msg']
    invoice_pays = context['invoice_pays']
    info = context['info']
    to_other = []
    if context.has_key('to_other'):
        to_other = context['to_other']
    invoice_info = u"发票信息: " + invoice.detail + u'; 发票金额: ' + \
        str(invoice.money) + u'; 发票号: ' + invoice.invoice_num + \
        u'; 未打款金额: ' + str(invoice.get_unpay_money)
    if invoice.invoice_num == '88888888':
        invoice_info += u'; 未开发票'
    invoice_pay_info = "\n".join(
        [u'打款金额: ' + str(o.money) + u'; 打款时间: ' + o.pay_time_cn + u'; 留言信息: ' + o.detail for o in invoice_pays])
    if context['send_type'] == "saler":
        url = mail.app.config[
            'DOMAIN'] + '/saler/client_order/agent_invoice/%s/invoice' % (invoice.id)
        action_info = u'请黄亮审批代理返点打款'
    elif context['send_type'] == 'end':
        url = mail.app.config[
            'DOMAIN'] + '/saler/client_order/agent_invoice/%s/invoice' % (invoice.id)
        action_info = u'代理返点已打款'
    else:
        url = mail.app.config[
            'DOMAIN'] + '/finance/client_order/agent_pay/%s/info' % (invoice.client_order_id)
        finance_users = [k for k in to_users if k.team.type in [13]]
        action_info = u'黄亮已同意代理返点打款，请' + \
            ', '.join(_get_active_user_name(finance_users)) + u'打款'

    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
    else:
        title = u"【合同流程】- %s" % (order.name)
    body = u"""
<h3 style="color:red;">流程状态: %s
<br/>%s<br/>订单链接地址: %s</h3>
<p><h4>状态信息:</h4>
发票信息:%s<br/>打款信息:<br/>%s</p>
<p><h4>订单信息:</h4>
%s</p>

<p><h4>留言如下:</h4>
    <br/>%s</p>

<p>by %s</p>
""" % (action_msg, action_info, url, invoice_info, invoice_pay_info, order.email_info, info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users) + to_other, body=body.replace('\n', '<br/>'))


def invoice_apply(sender, context):
    to_users = context['to_users']
    order = context['order']
    action = context['action']
    action_msg = context['action_msg']
    info = context['info']
    invoices = context['invoices']
    to_other = []
    if context.has_key('to_other'):
        to_other = context['to_other']
    invoice_info = "\n".join(
        [u'发票内容: ' + o.detail + u'; 发票金额' + str(o.money) for o in invoices])
    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchAd_bra_client_order':
        title = u"【搜索业务普通订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchad_bra_rebate_order':
        title = u"【搜索业务返点订单-合同流程】- %s" % (order.name)
    else:
        title = u"【合同流程】- %s" % (order.name)

    if context['send_type'] == "saler":
        if order.__tablename__ == 'bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/client_order/invoice/%s/order' % (order.id)
        elif order.__tablename__ == 'searchAd_bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/searchAd_order/invoice/%s/order' % (order.id)
        elif order.__tablename__ == 'searchad_bra_rebate_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/searchAd_rebate_order/invoice/%s/order' % (order.id)
        if action == 2:
            leader_users = [k for k in to_users if k.team.type in [9]]
            if 148 in [k.id for k in to_users]:
                leader_users += [k for k in User.all() if k.team.type == 20]
            action_info = u'请' + ','.join(_get_active_user_name(leader_users)) +\
                u'进行客户发票审批'
        else:
            salers = order.direct_sales + order.agent_sales + [order.creator]
            action_info = ','.join(
                _get_active_user_name(salers)) + u'您的客户发票被拒绝'
    elif context['send_type'] == 'end':
        if order.__tablename__ == 'bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/client_order/invoice/%s/order' % (order.id)
        elif order.__tablename__ == 'searchAd_bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/searchAd_order/invoice/%s/order' % (order.id)
        elif order.__tablename__ == 'searchad_bra_rebate_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/searchAd_rebate_order/invoice/%s/order' % (order.id)
        salers = order.direct_sales + order.agent_sales + [order.creator]
        action_info = ','.join(_get_active_user_name(salers)) + u'您的客户发票已开'
        invoice_info = "\n".join(
            [u'发票内容: ' + o.detail + u'; 发票号: ' + o.invoice_num + u'; 发票金额' + str(o.money) for o in invoices])
    else:
        if order.__tablename__ == 'bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/finance/client_order/invoice/%s/info' % (order.id)
        elif order.__tablename__ == 'searchAd_bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/finance/searchAd_order/invoice/%s/info' % (order.id)
        elif order.__tablename__ == 'searchad_bra_rebate_order':
            url = mail.app.config[
                'DOMAIN'] + '/finance/searchAd_rebate_order/invoice/%s/info' % (order.id)
        finance_users = [k for k in to_users if k.team.type in [13]]
        action_info = u'区域总监已同意客户发票申请，请' + \
            ', '.join(_get_active_user_name(finance_users)) + u'开具客户发票'

    body = u"""
<h3 style="color:red;">流程状态: %s
<br/>%s<br/>订单链接地址: %s</h3>
<p><h4>状态信息:</h4>
发票信息:%s</p>
<p><h4>订单信息:</h4>
%s</p>

<p><h4>留言如下:</h4>
    <br/>%s</p>

<p>by %s</p>
""" % (action_msg, action_info, url, invoice_info, order.email_info, info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users) + to_other, body=body.replace('\n', '<br/>'))


def medium_rebate_invoice_apply(sender, context):
    to_users = context['to_users']
    order = context['order']
    action = context['action']
    action_msg = context['action_msg']
    info = context['info']
    invoices = context['invoices']
    invoice_info = "\n".join(
        [u'发票内容: ' + o.detail + u'; 发票金额' + str(o.money) for o in invoices])
    to_other = []
    if context.has_key('to_other'):
        to_other = context['to_other']
    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchAd_bra_client_order':
        title = u"【搜索业务普通订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchad_bra_rebate_order':
        title = u"【搜索业务返点订单-合同流程】- %s" % (order.name)
    else:
        title = u"【合同流程】- %s" % (order.name)
    if context['send_type'] == "saler":
        if order.__tablename__ == 'bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/client_order/medium_rebate_invoice/%s/order' % (order.id)
        elif order.__tablename__ == 'searchAd_bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/searchAd_order/medium_rebate_invoice/%s/order' % (order.id)
        if action == 2:
            action_info = u'请黄亮进行媒体返点发票审批'
        else:
            action_info = u'您的媒体返点发票被拒绝'
    elif context['send_type'] == 'end':
        if order.__tablename__ == 'bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/client_order/medium_rebate_invoice/%s/order' % (order.id)
        elif order.__tablename__ == 'searchAd_bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/saler/searchAd_order/medium_rebate_invoice/%s/order' % (order.id)
        action_info = u'您的媒体返点发票已开'
        invoice_info = "\n".join(
            [u'发票内容: ' + o.detail + u'; 发票号: ' + o.invoice_num + u'; 发票金额' + str(o.money) for o in invoices])
    else:
        if order.__tablename__ == 'bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/finance/client_order/medium_rebate_invoice/%s/info' % (order.id)
        elif order.__tablename__ == 'searchAd_bra_client_order':
            url = mail.app.config[
                'DOMAIN'] + '/finance/searchAd_order/medium_rebate_invoice/%s/info' % (order.id)
        finance_users = [k for k in to_users if k.team.type in [13]]
        action_info = u'黄亮已同意客户发票申请，请' + \
            ', '.join(_get_active_user_name(finance_users)) + u'开具媒体返点发票'

    body = u"""
<h3 style="color:red;">流程状态: %s
<br/>%s<br/>订单链接地址: %s</h3>
<p><h4>状态信息:</h4>
发票信息:%s</p>
<p><h4>订单信息:</h4>
%s</p>

<p><h4>留言如下:</h4>
    <br/>%s</p>

<p>by %s</p>
""" % (action_msg, action_info, url, invoice_info, order.email_info, info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users) + to_other, body=body.replace('\n', '<br/>'))


def framework_douban_contract_apply(sender, apply_context):
    """框架订单豆瓣合同号申请"""
    order = apply_context['order']
    url = mail.app.config['DOMAIN'] + order.info_path()
    douban_users = User.douban_contracts()
    body = u"""
Dear %s:

请帮忙递交法务审核合同 + 分配合同号, 谢谢~

项目: 框架
代理集团: %s
直客销售: %s
渠道销售: %s
时间: %s : %s
金额: %s

附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (','.join([x.name for x in douban_users]), order.group.name,
       order.direct_sales_names, order.agent_sales_names,
       order.start_date_cn, order.end_date_cn,
       order.money, url, g.user.name)
    file_paths = []
    # if order.get_last_contract():
    #    file_paths.append(order.get_last_contract().real_path)
    if order.get_last_schedule():
        file_paths.append(order.get_last_schedule().real_path)
    send_attach_mail(u'【合同流程】%s-%s' % (order.name, u'豆瓣合同号申请'),
                     recipients=apply_context['to'],
                     body=body,
                     file_paths=file_paths)


def douban_contract_apply(sender, apply_context):
    """豆瓣合同号申请"""
    order = apply_context['order']
    url = mail.app.config['DOMAIN'] + order.info_path()
    douban_users = User.douban_contracts()
    body = u"""
Dear %s:

请帮忙递交法务审核合同 + 分配合同号, 谢谢~

项目: %s
客户: %s
代理: %s
直客销售: %s
渠道销售: %s
时间: %s : %s
金额: %s

附注:
    致趣订单管理系统链接地址: %s

by %s\n
""" % (','.join([x.name for x in douban_users]), order.campaign,
       order.client.name, order.jiafang_name,
       order.direct_sales_names, order.agent_sales_names,
       order.start_date_cn, order.end_date_cn,
       order.money, url, g.user.name)
    file_paths = []
    if order.get_last_contract():
        file_paths.append(order.get_last_contract().real_path)
    if order.get_last_schedule():
        file_paths.append(order.get_last_schedule().real_path)
    send_attach_mail(u'【合同流程】%s-%s' % (order.name, u'豆瓣合同号申请'),
                     recipients=apply_context['to'],
                     body=body,
                     file_paths=file_paths)


def outsource_distribute(sender, context):
    order = context['order']
    action_msg = context['action_msg']
    info = context['info']
    operater_users = context['operater_users']
    to_users = context['to_users']
    title = u'【费用报备】%s-%s-订单分配提醒' % (order.contract or u'无合同号',
                                     order.jiafang_name)
    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
        url = mail.app.config[
            'DOMAIN'] + url_for("outsource.client_outsources", order_id=order.id)
    elif order.__tablename__ == 'bra_douban_order':
        title = u"【直签豆瓣订单-合同流程】- %s" % (order.name)
        url = mail.app.config[
            'DOMAIN'] + url_for("outsource.douban_outsources", order_id=order.id)
    else:
        title = u"【合同流程】- %s" % (order.name)
        url = ''
    action_info = u'订单已分配给' + \
        ','.join(_get_active_user_name(operater_users)) + u'执行'

    body = u"""
<h3 style="color:red;">流程状态: %s
<br/>外包链接地址: %s</h3>
<p><h4>状态信息:</h4>
%s</p>
<p><h4>订单信息:</h4>
%s</p>

<p><h4>留言如下:</h4>
    <br/>%s</p>

<p>by %s</p>
""" % (action_msg, url, action_info, order.email_info, info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users), body=body.replace('\n', '<br/>'))


def outsource_apply(sender, context):
    """外包服务流程 发送邮件"""
    to_users = context['to_users']
    outsource_apply_user = context['outsource_apply_user']
    order = context['order']
    outsources = context['outsources']
    action_msg = context['action_msg']
    info = context['info']
    action = context['action']
    outsources_info = "\n".join([o.outsource_info for o in outsources])
    url = mail.app.config['DOMAIN'] + order.outsource_path()
    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_douban_order':
        title = u"【直签豆瓣订单-合同流程】- %s" % (order.name)
    if action in [0, 100]:
        if context['outsource_percent'] >= 0.02:
            if 3 in order.locations:
                action_check_info = u'请黄亮进行审批'
            else:
                action_check_info = u'请盖新进行审批'
        else:
            leader = [k for k in outsource_apply_user if k.team.type == 9]
            action_check_info = u'请' + \
                ','.join(_get_active_user_name(leader)) + u'进行审批'
    elif action == 1:
        action_check_info = ','.join(_get_active_user_name(
            order.operater_users)) + u'的外包费用通过申请'
    elif action == 2:
        action_check_info = ','.join(_get_active_user_name(
            order.operater_users)) + u'的外包费用没有通过申请，请核实后重新申请'
    else:
        action_check_info = ''
    action_info = outsources_info
    body = u"""
<h3 style="color:red;">流程状态: %s
<br/>%s<br/>外包链接地址: %s</h3>
<p><h4>状态信息:</h4>
%s</p>
<p><h4>订单信息:</h4>
%s</p>

<p><h4>留言如下:</h4>
    <br/>%s</p>

<p>by %s</p>
""" % (action_msg, action_check_info, url, action_info, order.email_info, info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users), body=body.replace('\n', '<br/>'))


def merger_outsource_apply(sender, apply_context):
    merger_outsource = apply_context['merger_outsource']
    outsources = merger_outsource.outsources
    outsources_info = "\n".join([o.outsource_info for o in outsources])
    pay_nums = merger_outsource.pay_num
    action = apply_context['action']
    if apply_context.has_key('url'):
        url = apply_context['url']
    else:
        url = mail.app.config['DOMAIN'] + outsources[0].finance_pay_path()
    if merger_outsource.invoice:
        invoice_type = u'有'
    else:
        invoice_type = u'无'
    to_user = apply_context['to']
    to_user_name = ''

    if action == 1:
        to_user_name = u'黄亮请审批外包合并付款信息'
        to_user += [k for k in User.all() if k.email.find('huangliang')
                    >= 0 or k.email.find('fenghaiyan') >= 0] + [k for k in User.finances()]
        if merger_outsource.__tablename__ == 'merger_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_client_target_info', target_id=merger_outsource.target.id)
        elif merger_outsource.__tablename__ == 'merger_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_client_target_personal_info')
        elif merger_outsource.__tablename__ == 'merger_douban_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_douban_target_personal_info')
        else:
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_douban_target_info', target_id=merger_outsource.target.id)
    elif action == -1:
        to_user_name = u'丰海艳您的外包合并付款信息被拒绝，请核查后重新申请'
        to_user += [k for k in User.all() if k.email.find('huangliang')
                    >= 0 or k.email.find('fenghaiyan') >= 0] + [k for k in User.finances()]
        if merger_outsource.__tablename__ == 'merger_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_client_target_info', target_id=merger_outsource.target.id)
        elif merger_outsource.__tablename__ == 'merger_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_client_target_personal_info')
        elif merger_outsource.__tablename__ == 'merger_douban_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_douban_target_personal_info')
        else:
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_douban_target_info', target_id=merger_outsource.target.id)
    elif action == 2:
        to_user_name = u'外包合并付款信息已同意付款，请' + \
            ','.join([k.name for k in User.finances()]) + u'付款'
        to_user += [k for k in User.all() if k.email.find('huangliang')
                    >= 0 or k.email.find('fenghaiyan') >= 0] + [k for k in User.finances()]
        if merger_outsource.__tablename__ == 'merger_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('finance_outsource_pay.info', target_id=merger_outsource.target.id)
        elif merger_outsource.__tablename__ == 'merger_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('finance_outsource_pay.info', target_id=0)
        elif merger_outsource.__tablename__ == 'merger_douban_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('finance_outsource_pay.douban_info', target_id=0)
        else:
            url = mail.app.config[
                'DOMAIN'] + url_for('finance_outsource_pay.douban_info', target_id=merger_outsource.target.id)
    elif action == 0:
        to_user_name = u'丰海艳您的外包合并付款信息已打款'
        to_user += [k for k in User.all() if k.email.find('huangliang')
                    >= 0 or k.email.find('fenghaiyan') >= 0] + [k for k in User.finances()]
        if merger_outsource.__tablename__ == 'merger_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_client_target_info', target_id=merger_outsource.target.id)
        elif merger_outsource.__tablename__ == 'merger_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_client_target_personal_info')
        elif merger_outsource.__tablename__ == 'merger_douban_personal_out_source':
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_douban_target_personal_info')
        else:
            url = mail.app.config[
                'DOMAIN'] + url_for('outsource.merget_douban_target_info', target_id=merger_outsource.target.id)
    body = u"""<h3 style="color:red;">
%s

%s
外包链接地址:%s</h3>
【外包组成】
%s
申请付款总金额: %s
是否有发票:%s
发票信息:%s
留言:
%s
by %s\n
""" % (apply_context['title'], to_user_name, url, outsources_info, pay_nums, invoice_type, merger_outsource.remark, apply_context['msg'], g.user.name)
    _insert_person_notcie(to_user, apply_context['title'], body)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_user))), 'info')
    send_html_mail(apply_context['title'], recipients=_get_active_user_email(to_user),
                   body=body.replace('\n', '<br/>'))


def account_leave_apply(sender, leave):
    status = leave.status
    if status in [0, 2]:
        if leave.is_long_leave():
            if status == 0:
                to_name = u''
            else:
                to_name = u'黄亮请审批您下属的请假申请'
        else:
            if status == 0:
                to_name = u''
            else:
                to_name = ','.join(
                    [k.name for k in leave.creator.team_leaders]) + u'请审批您下属的请假申请'
        url = mail.app.config['DOMAIN'] + \
            url_for('account_leave.info', lid=leave.id)
    elif status in [3, 4]:
        if status == 3:
            to_name = leave.creator.name + u'您的请假申请已批准'
        else:
            to_name = leave.creator.name + u'您的请假申请被拒绝'
        url = mail.app.config['DOMAIN'] + \
            url_for('account_leave.index', user_id=leave.creator.id)
    to_users = leave.senders + leave.creator.team_leaders + \
        [leave.creator] + [g.user]
    to_emails = list(set([k.email for k in to_users])) + ['admin@inad.com']
    if leave.is_long_leave():
        to_emails += ['huangliang@inad.com']
    body = u"""
<h3 style="color:red;">%s

申请状态: %s
请假申请链接地址: %s</h3>
<h3>请假信息:</h3>
请假人: %s
请假日期: %s - %s，共%s
请假类型: %s
请假原因: 
%s

请批准，谢谢

by %s
""" % (to_name, leave.status_cn, url, leave.creator.name, leave.start_time_cn, leave.end_time_cn,
       leave.rate_day_cn, leave.type_cn, leave.reason, g.user.name)
    title = u'【请假申请】- %s' % (leave.creator.name)
    _insert_person_notcie(to_users, title, body)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    send_html_mail(title, recipients=to_emails,
                   body=body.replace('\n', '<br/>'))


def account_out_apply(sender, out, status):
    if status == 1:
        msg = u'外出报备申请'
        to_name = ','.join(
            [k.name for k in out.creator.team_leaders]) + u'请审批您下属的外出报备'
    elif status == 10:
        msg = u'外出报备撤销'
        to_name = ','.join(
            [k.name for k in out.creator.team_leaders]) + u'，下属的外出报备已撤销'
    elif status == 11:
        msg = u'外出报备被驳回'
        to_name = out.creator.name + u'您的外出报备已被驳回'
    elif status == 2:
        msg = u'外出报备申请通过'
        to_name = out.creator.name + u'您的外出报备申请通过'
    elif status in [3, 4]:
        msg = u'会议纪要填写完成'
        to_name = ','.join(
            [k.name for k in out.creator.team_leaders]) + u'您下属的外出报备的会议纪要已填写完成'
    elif status == 13:
        msg = u'外出报备未审批-会议纪要填写完成'
        to_name = ','.join(
            [k.name for k in out.creator.team_leaders]) + u'您下属的外出报备的会议纪要已填写完成'
    elif status == 14:
        msg = u'外出报备申请通过-并完成会议纪要'
        to_name = out.creator.name + u'您的外出报备申请通过'
    title = u'【外出报备】' + '-' + out.m_persion_cn + '-' + out.creator.name
    url = mail.app.config['DOMAIN'] + url_for('account_out.info', oid=out.id)
    body = u"""
<h3 style="color:red;">%s

申请状态: %s
外出报备链接地址: %s</h3>
<h3>外出报备信息：</h3>
报备人：%s
开始时间：%s
结束时间：%s
公司名称：%s
会见人：  %s
地址：   %s
参会人（公司内部）：%s
外出原因：
%s
会议纪要：
%s

by:
%s
    """ % (msg, to_name, url, out.creator.name, out.start_time_cn, out.end_time_cn, out.m_persion_cn,
           out.persions, out.address, ','.join([k.name for k in out.joiners]),
           out.reason, out.meeting_s, g.user.name)
    to_users = out.creator.team_leaders + [g.user] + out.joiners
    joiners_leaders = []
    for k in out.joiners:
        joiners_leaders += k.team_leaders
    to_users += joiners_leaders
    if out.creator_type == 1:
        to_user_emails = [k.email for k in to_users] + ['admin@inad.com']
        if out.status in [3, 4]:
            title = u'会议纪要'
            to_user_emails = [k.email for k in to_users] + ['sales@inad.com']
    else:
        to_user_emails = [k.email for k in to_users] + ['admin@inad.com']
        if out.status == 3:
            to_user_emails = [k.email for k in to_users]
    if out.creator.team.location == 2:
        to_user_emails += ['salessh@inad.com']
    if out.creator.team.location == 1 and out.creator.team.type in [3, 4, 9]:
        to_user_emails += ['huawei@inad.com']

    # 会议纪要申请通过只抄送相关人+admin,不抄送leader
    if out.status == 2:
        to_users = [g.user] + out.joiners
        to_user_emails = [k.email for k in to_users] + ['admin@inad.com']
    # 会议纪要发送邮件标题改为"【外出报备】-会议纪要"
    if out.status in [3, 4]:
        title = u'会议纪要' + '-' + out.m_persion_cn + '-' + out.creator.name
    _insert_person_notcie(to_users, title, body)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    send_html_mail(title, list(set(to_user_emails)),
                   body=body.replace('\n', '<br/>'))


def planning_bref(sender, apply_context):
    bref = apply_context['bref']
    action = apply_context['status']
    # 获取某区域策划负责人
    c_loction = bref.creator.location
    planning_team_admins = [k for k in User.all_active(
    ) if k.location == c_loction and k.team.type == 6][0].team.admins
    # 获取某区域销售负责人
    sale_admins = bref.creator.team.admins + bref.creator.team_leaders
    # 获取某区域执行负责人
    operater_admins = [k for k in User.all_active(
    ) if k.location == c_loction and k.team.type == 15]
    if action == 2:
        title = u'【策划单】-%s' % (bref.title)
        to_name = ','.join([k.name for k in planning_team_admins])
        status_cn = u'下单申请'
    elif action == 10:
        title = u'【策划单】-%s' % (bref.title)
        status_cn = u'已取消'
        to_name = bref.creator.name
    elif action == 1:
        title = u'【策划单】-%s' % (bref.title)
        status_cn = u'已打回'
        to_name = bref.creator.name
    elif action == 3:
        title = u'【策划单】-%s' % (bref.title)
        status_cn = u'已分配'
        to_name = bref.creator.name + ',' + bref.toer.name
    elif action == 0:
        title = u'【策划单】-%s' % (bref.title)
        status_cn = u'已完成'
        to_name = bref.creator.name
    url = mail.app.config['DOMAIN'] + \
        url_for('planning_bref.info', bid=bref.id)
    # 邮件发送人
    to_emails = apply_context['to_other']
    to_users = operater_admins + planning_team_admins + [bref.creator] + sale_admins
    if bref.toer:
        to_users += [bref.toer]
    if bref.follower:
        to_users += [bref.follower]
    if action in [0, 3]:
        finish_text = u"""<h3>完成情况:</h3>
分配给: %s
分配人: %s
网盘地址:   %s
        """ % (bref.toer.name, bref.follower.name, bref.url)
    else:
        finish_text = ''

    body = u"""
<h3 style="color:red;">Dear %s:

%s-%s
策划单链接地址: %s</h3>
留言信息:
%s
%s
<h3>基本信息:</h3>
名称:  %s
代理/直客:   %s
品牌:  %s
产品:  %s
目标受众:    %s
背景:  %s
推广目的:    %s
推广主题:    %s
推广周期:    %s
推广预算:    %s
是否有模板   %s
<h3>项目说明:</h3>
下单需求方:   %s
应用场景:    %s
应用等级:    %s
完成时间:    %s
<h3>补充说明:</h3>
品牌意向媒体:  %s
建议:  %s
备注:  
%s

by:
%s
    """ % (to_name, title, status_cn, url, apply_context['msg'], finish_text, bref.title, bref.agent, bref.brand, bref.product, bref.target, bref.background,
           bref.push_target, bref.push_theme, bref.push_time, bref.budget_cn, bref.is_temp_cn, bref.agent_type_cn,
           bref.use_type_cn, bref.level_cn, bref.get_time_cn, bref.intent_medium, bref.suggest, bref.desc,
        g.user.name)
    _insert_person_notcie(to_users, title, body)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    send_html_mail(title, _get_active_user_email(to_users) +
                   to_emails+['planning@inad.com'], body=body.replace('\n', '<br/>'))


def account_kpi_apply(sender, apply_context):
    report = apply_context['report']
    if report.status == 2:
        if report.version == 1:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.check_apply', r_id=report.id)
        else:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.check_apply_v2', r_id=report.id)
        to_names = ','.join([k.name for k in report.creator.team_leaders])
        user_name = report.creator.name
        to_users = [k.email for k in report.creator.team_leaders] + \
            [report.creator.email]
        title = u'绩效考核-申请审批'
        body = u"""
Dear %s:

请您为 %s 的绩效考核打分。

附注: 
    KPI链接地址: %s

    """ % (to_names, user_name, url)
    elif report.status == 1:
        if report.version == 1:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.update', r_id=report.id)
        elif report.version == 2:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.update_v2', r_id=report.id)
        to_names = report.creator.name
        user_name = report.creator.name
        to_users = [k.email for k in report.creator.team_leaders] + \
            [report.creator.email]
        title = u'绩效考核-被打回'
        body = u"""
Dear %s:

您的绩效考核被打回请重新修改后提交领导审批。

附注: 
    KPI链接地址: %s

    """ % (to_names, url)
    elif report.status == 4:
        if report.version == 1:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.info', r_id=report.id)
        else:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.info_v2', r_id=report.id)
        to_names = ','.join([k.name for k in User.HR_leaders()])
        user_name = report.creator.name
        to_users = [k.email for k in User.HR_leaders(
        )] + [report.creator.email] + [k.email for k in report.creator.team_leaders]
        title = u'绩效考核-申请归档'
        body = u"""
Dear %s:

%s 的绩效已提交给您，请查看并归档。

附注: 
    KPI链接地址: %s

    """ % (to_names, user_name, url)
    elif report.status == 5:
        if report.version == 1:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.info', r_id=report.id)
        else:
            url = mail.app.config['DOMAIN'] + \
                url_for('account_kpi.info_v2', r_id=report.id)
        to_names = report.creator.name
        user_name = report.creator.name
        to_users = [k.email for k in User.HR_leaders(
        )] + [report.creator.email] + [k.email for k in report.creator.team_leaders]
        title = u'绩效考核-已归档'
        body = u"""
Dear %s:

您的绩效已归档，请通过下边链接查看评分。

附注: 
    KPI链接地址: %s

    """ % (to_names, url)
    elif report.status == 6:
        url = mail.app.config['DOMAIN'] + \
            url_for('account_kpi.personnal')
        to_names = apply_context['user'].name
        to_users = [apply_context['user'].email, g.user.email]
        title = u'绩效考核-请您为同事打分'
        body = u"""
Dear %s:

请您为同事的绩效考核打分，请通过下边链接进行打分。

附注: 
    KPI链接地址: %s

    """ % (to_names, url)
    send_simple_mail(title, list(set(to_users)), body=body)


def medium_back_money_apply(sender, apply_context):
    order = apply_context['order']
    num = apply_context['num']
    title = u"【新媒体订单-合同流程】- %s" % (order.name)
    s_title = u'项目回款信息-媒体返点回款信息'
    url = mail.app.config['DOMAIN'] + order.info_path()
    to_users = User.contracts() + [g.user] + User.medias()
    body = u"""
<h3 style="color:red;">流程状态: %s
回款详情:
本次回款金额: %s
订单链接地址: %s</h3>
<p><h4>订单信息:</h4>
%s</p>
<p>by %s</p>
""" % (s_title, str(num), url, order.email_info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users)+['guoyu@inad.com'], body=body.replace('\n', '<br/>'))


def back_money_apply(sender, apply_context):
    order = apply_context['order']
    num = apply_context['num']
    type = apply_context['type']
    if type == 'invoice':
        s_title = u'项目回款信息-返点发票信息'
    elif type == 'end':
        s_title = u'项目回款完成'
    elif type == 'no_end':
        s_title = u'回款状态变为未完成'
    else:
        s_title = u'项目回款信息'
    if num == -1:
        s_title = u'坏账项目'
    if order.__tablename__ in ['searchAd_bra_client_order', 'searchAd_bra_rebate_order']:
        to_users = order.direct_sales + order.agent_sales +\
            [order.creator, g.user] + order.leaders
    else:
        to_users = order.direct_sales + order.agent_sales + User.contracts() +\
            [order.creator, g.user] + order.leaders + User.medias()
        if 3 in order.locations:
            to_users += [k for k in User.all()
                         if k.email.find('chenjingjing') >= 0]
        if 1 in order.locations:
            to_users += [k for k in User.all()
                         if k.email.find('weizhaoting') >= 0]

    if order.__tablename__ == 'bra_client_order':
        title = u"【新媒体订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_framework_order':
        title = u"【框架订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_douban_order':
        title = u"【直签豆瓣订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchAd_bra_client_order':
        title = u"【搜索业务普通订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'bra_searchAd_framework_order':
        title = u"【搜索业务框架订单-合同流程】- %s" % (order.name)
    elif order.__tablename__ == 'searchad_bra_rebate_order':
        title = u"【搜索业务返点订单-合同流程】- %s" % (order.name)
    else:
        title = u"【合同流程】- %s" % (order.name)

    url = mail.app.config['DOMAIN'] + order.info_path()
    body = u"""
<h3 style="color:red;">流程状态: %s

回款详情:
本次回款金额: %s
已回款完成比例: %s %%
订单链接地址: %s</h3>
<p><h4>订单信息:</h4>
%s</p>
<p>by %s</p>
""" % (s_title, str(num), order.back_money_percent, url, order.email_info, g.user.name)
    flash(u'已发送邮件给%s' % (','.join(_get_active_user_name(to_users))), 'info')
    _insert_person_notcie(to_users, title, body)
    send_html_mail(title, recipients=_get_active_user_email(
        to_users), body=body.replace('\n', '<br/>'))


def email_init_signal(app):
    """注册信号的接收器"""
    password_changed_signal.connect_via(app)(password_changed)
    add_comment_signal.connect_via(app)(add_comment)
    zhiqu_contract_apply_signal.connect_via(app)(zhiqu_contract_apply)
    medium_invoice_apply_signal.connect_via(app)(medium_invoice_apply)
    agent_invoice_apply_signal.connect_via(app)(agent_invoice_apply)
    invoice_apply_signal.connect_via(app)(invoice_apply)
    medium_rebate_invoice_apply_signal.connect_via(
        app)(medium_rebate_invoice_apply)
    framework_douban_contract_apply_signal.connect_via(
        app)(framework_douban_contract_apply)
    douban_contract_apply_signal.connect_via(app)(douban_contract_apply)
    outsource_distribute_signal.connect_via(app)(outsource_distribute)
    outsource_apply_signal.connect_via(app)(outsource_apply)
    merger_outsource_apply_signal.connect_via(app)(merger_outsource_apply)
    account_leave_apply_signal.connect_via(app)(account_leave_apply)
    account_out_apply_signal.connect_via(app)(account_out_apply)
    planning_bref_signal.connect_via(app)(planning_bref)
    account_kpi_apply_signal.connect_via(app)(account_kpi_apply)
    back_money_apply_signal.connect_via(app)(back_money_apply)
    medium_back_money_apply_signal.connect_via(app)(medium_back_money_apply)
