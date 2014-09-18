#-*- coding: UTF-8 -*-
from flask import url_for, g
from libs.mail import send_simple_mail, mail
from blinker import Namespace

braavos_signals = Namespace()
password_changed_signal = braavos_signals.signal('password-changed')
add_comment_signal = braavos_signals.signal('add-comment')
change_state_apply_signal = braavos_signals.signal('change_state_apply')


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


@change_state_apply_signal.connect
def change_state_apply(change_state_apply):
    url = mail.app.config['DOMAIN'] + url_for(
        'order.order_detail', order_id=change_state_apply.order.id, step=change_state_apply.type)
    send_simple_mail(u'Inad[%s]申请%s' % (g.user.name, change_state_apply.type_cn),
                     recipients=change_state_apply.leaders,
                     body=(
                         u'定单：%s\n[%s]申请%s，请求审批\n%s'
                         % (change_state_apply.order.name, g.user.name, change_state_apply.type_cn, url)))
