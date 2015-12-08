#-*- coding: UTF-8 -*-
import datetime

from flask import url_for, g, flash
from libs.mail import send_simple_mail, send_attach_mail, send_html_mail, mail
from blinker import Namespace

from models.user import User
from models.account.data import PersonNotice

braavos_signals = Namespace()

zhiqu_contract_apply_signal = braavos_signals.signal('zhiqu_contract_apply')


def _get_active_user(send_users):
    active_users = User.all_active()
    send_users = [k for k in send_users if k in active_users]
    return list(set(send_users))


def _get_active_user_email(send_users):
    send_users = _get_active_user(send_users)
    return [k.email for k in send_users] + ['guoyu@inad.com']


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


def zhiqu_contract_apply(sender, context):
    order = context['order']
    to_users = context['to_users']
    action_msg = context['action_msg']
    info = context['info']
    if context.has_key('action'):
        action = context['action']
    else:
        action = None
    if action and int(action) == 1:
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
        action_info = u'请' + ','.join(_get_active_user_name(contract_users)) +\
            u'进行合同打印'
    elif action and int(action) == 5:
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
        salers = order.direct_sales + order.agent_sales + [order.creator]
        action_info = ','.join(_get_active_user_name(salers)) + u'您的合同已撤单'
    elif action and int(action) == 19:
        contract_users = [k for k in to_users if k.team.type in [10]]
        action_info = u'请' + ','.join(_get_active_user_name(contract_users)) +\
            u'进行合同确认归档'
    elif action and int(action) == 20:
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
        to_users), body=body.replace('\n', '<br/>'))


def email_init_signal(app):
    """注册信号的接收器"""
    zhiqu_contract_apply_signal.connect_via(app)(zhiqu_contract_apply)
