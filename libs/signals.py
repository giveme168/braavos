#-*- coding: UTF-8 -*-
from flask import url_for, g
from libs.mail import send_simple_mail, mail
from blinker import Namespace

braavos_signals = Namespace()
password_changed_signal = braavos_signals.signal('password-changed')
add_comment_signal = braavos_signals.signal('add-comment')
order_apply_signal = braavos_signals.signal('order_apply')
reply_apply_signal = braavos_signals.signal('reply_apply')
contract_apply_signal = braavos_signals.signal('contract_apply')


@password_changed_signal.connect
def password_changed(user):
    send_simple_mail(u'InAd帐号密码重设通知',
                     recipients=[user.email],
                     body=u'您的InAd帐号密码已经被重新设置, 如果不是您的操作, 请联系广告平台管理员')


@add_comment_signal.connect
def add_comment(comment):
    send_simple_mail(u'InAd留言提醒[%s]' % comment.target.name,
                     recipients=[u.email for u in comment.target.get_mention_users(except_user=comment.creator)],
                     body=(u'%s的新留言:\n\n %s' % (comment.creator.name, comment.msg)))


@order_apply_signal.connect
def order_apply(change_state_apply):
    url = mail.app.config['DOMAIN'] + url_for(
        'order.order_detail', order_id=change_state_apply.order.id, step=change_state_apply.next_step)
    send_simple_mail(u'【%s审批申请】%s-%s' % (change_state_apply.type_cn, change_state_apply.order.name, g.user.name),
                     recipients=[g.user.email],
                     body=(
                         u"""定单-%s\n
                         预订链接：%s\n
                         申请理由请查看排期下方留言\n
                         请于2个工作日内与申请审批的Leader联系，及时通过审核，超过时间没有审核的，系统会自动释放资源为未下单。\n
                         如不通过系统将自动将资源释放为申请前状态并提示理由。"""
                         % (change_state_apply.order.name, url)))
    send_simple_mail(u'【%s审批申请】%s-%s' % (change_state_apply.type_cn, change_state_apply.order.name, g.user.name),
                     recipients=change_state_apply.receiver,
                     body=(
                         u"""定单-%s\n
                         预订链接：%s\n
                         %s 申请下单，请求审批\n
                         申请理由请查看排期下方留言\n
                         请于2个工作日内核实通过审核，超过时间没有审核的，系统会自动释放资源为申请前状态。\n
                         如不通过请在留言框内注明理由，系统将自动将资源释放为申请前状态。"""
                         % (change_state_apply.order.name, url, g.user.name)))


@reply_apply_signal.connect
def reply_apply(change_state_apply):
    url = mail.app.config['DOMAIN'] + url_for(
        'order.order_detail', order_id=change_state_apply.order.id, step=change_state_apply.next_step)
    if change_state_apply.agree:
        send_simple_mail(u'【%s】%s-%s' % (change_state_apply.type_cn, change_state_apply.order.name, g.user.name),
                         recipients=change_state_apply.receiver,
                         body=(
                             u"""定单-%s\n
                             预订链接：%s\n
                             审核已通过。"""
                             % (change_state_apply.order.name, url)))
    else:
        send_simple_mail(u'【%s】%s-%s' % (change_state_apply.type_cn, change_state_apply.order.name, g.user.name),
                         recipients=change_state_apply.receiver,
                         body=(
                             u"""定单-%s\n
                             预订链接：%s\n
                             审核未通过，系统已将资源释放为申请前状态，请及时注意预订资源情况。
                             未通过理由请查看排期下方留言"""
                             % (change_state_apply.order.name, url)))


@contract_apply_signal.connect
def contract_apply(apply_context):
    order = apply_context['order']
    url = mail.app.config['DOMAIN'] + order.info_path()
    send_simple_mail(u'【合同流程】%s-%s' % (order.name, apply_context['action_msg']),
                     recipients=apply_context['to'],
                     body=(u"""
订单:%s 【%s】\n
链接地址： %s\n
留言如下: \n
%s\n
\n
by %s\n
""" % (order.name, apply_context['action_msg'], url, apply_context['msg'], g.user.name)))
