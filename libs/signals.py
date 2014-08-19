#-*- coding: UTF-8 -*-
from libs.mail import send_simple_mail
from blinker import Namespace

braavos_signals = Namespace()
password_changed_signal = braavos_signals.signal('password-changed')


@password_changed_signal.connect
def password_changed(user):
    send_simple_mail(u'InAd帐号密码重设通知',
                     recipients=[user.email],
                     body=u'您的InAd帐号密码已经被重新设置, 如果不是您的操作, 请联系广告平台管理员')
