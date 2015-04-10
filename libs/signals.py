#-*- coding: UTF-8 -*-
from flask import url_for, g
from libs.mail import send_simple_mail, send_attach_mail, mail
from blinker import Namespace

from models.user import User

braavos_signals = Namespace()
password_changed_signal = braavos_signals.signal('password-changed')
add_comment_signal = braavos_signals.signal('add-comment')
order_apply_signal = braavos_signals.signal('order_apply')
reply_apply_signal = braavos_signals.signal('reply_apply')
contract_apply_signal = braavos_signals.signal('contract_apply')
douban_contract_apply_signal = braavos_signals.signal('douban_contract_apply')
outsource_apply_signal = braavos_signals.signal('outsource_apply')
invoice_apply_signal = braavos_signals.signal('invoice_apply')
medium_invoice_apply_signal = braavos_signals.signal('medium_invoice_apply')


def password_changed(sender, user):
    send_simple_mail(u'InAd帐号密码重设通知',
                     recipients=[user.email],
                     body=u'您的InAd帐号密码已经被重新设置, 如果不是您的操作, 请联系广告平台管理员')


def add_comment(sender, comment):
    send_simple_mail(u'InAd留言提醒[%s]' % comment.target.name,
                     recipients=[
                         u.email for u in comment.target.get_mention_users(except_user=comment.creator)],
                     body=(u'%s的新留言:\n\n %s' % (comment.creator.name, comment.msg)))


def order_apply(sender, change_state_apply):
    url = mail.app.config['DOMAIN'] + url_for(
        'schedule.order_detail', order_id=change_state_apply.order.id, step=change_state_apply.next_step)
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


def reply_apply(sender, change_state_apply):
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


def contract_apply_douban(sender, apply_context):
    """豆瓣直签豆瓣、关联豆瓣订单 发送豆瓣合同管理员"""
    order = apply_context['order']
    file_paths = []
    if order.get_last_contract():
        file_paths.append(order.get_last_contract().real_path)
    if order.get_last_schedule():
        file_paths.append(order.get_last_schedule().real_path)

    send_attach_mail(u'【合同流程】%s-%s' % (order.name, apply_context['action_msg']),
                     recipients=apply_context['to'],
                     body=order.douban_contract_email_info(
                         title=u"请帮忙打印合同, 谢谢~"),
                     file_paths=file_paths)


def contract_apply(sender, apply_context, action=None):
    """合同流程 发送邮件"""
    order = apply_context['order']
    if order.__tablename__ == 'bra_douban_order' and order.contract_status == 4 and action == 5:
        contract_apply_douban(sender, apply_context)
    elif order.__tablename__ == 'bra_client_order' and order.associated_douban_orders and order.contract_status == 4 and action == 5:
        apply_context['order'] = order.associated_douban_orders[0]
        contract_apply_douban(sender, apply_context)
    else:
        url = mail.app.config['DOMAIN'] + order.info_path()
        send_simple_mail(u'【合同流程】%s-%s' % (order.name, apply_context['action_msg']),
                         recipients=apply_context['to'],
                         body=(u"""%s

订单: %s
链接地址: %s
订单信息:
%s
留言如下:
    %s
\n
by %s
""" % (apply_context['action_msg'], order.name, url, order.email_info, apply_context['msg'], g.user.name)))


def medium_invoice_apply(sender, apply_context):
    order = apply_context['order']
    invoices = apply_context['invoices']
    invoice_info = "\n".join(
        [u'发票信息: ' + o.detail + u'; 发票金额: ' + str(o.money) + u'; 发票号: ' + o.invoice_num for o in invoices])
    if apply_context['send_type'] == "saler":
        url = mail.app.config['DOMAIN'] + order.saler_invoice_path()
    else:
        url = mail.app.config['DOMAIN'] + order.finance_invoice_path()
    text = u"""%s
订单: %s
链接地址: %s
发票信息:
%s
留言如下:
    %s
\n
by %s
""" % (apply_context['action_msg'], order.name, url, invoice_info, apply_context['msg'], g.user.name)


def invoice_apply(sender, apply_context):
    order = apply_context['order']
    invoices = apply_context['invoices']
    invoice_info = "\n".join(
        [u'发票信息: ' + o.detail + u'; 发票金额' + str(o.money) for o in invoices])
    if apply_context['send_type'] == "saler":
        url = mail.app.config['DOMAIN'] + order.saler_invoice_path()
    else:
        url = mail.app.config['DOMAIN'] + order.finance_invoice_path()
    text = u"""%s
订单: %s
链接地址: %s
发票信息:
%s
留言如下:
    %s
\n
by %s
""" % (apply_context['action_msg'], order.name, url, invoice_info, apply_context['msg'], g.user.name)


def medium_invoice_apply(sender, apply_context):
    order = apply_context['order']
    invoices = apply_context['invoices']
    invoice_info = "\n".join(
        [u'发票信息: ' + o.detail + u'; 发票金额' + str(o.money) for o in invoices])
    if apply_context['send_type'] == "saler":
        url = mail.app.config['DOMAIN'] + order.saler_invoice_path()
    else:
        url = mail.app.config['DOMAIN'] + order.finance_invoice_path()
    text = u"""%s
订单: %s
链接地址: %s
发票信息:
%s
留言如下:
    %s
\n
by %s
""" % (apply_context['action_msg'], order.name, url, invoice_info, apply_context['msg'], g.user.name)


def outsource_apply(sender, apply_context):
    """外包服务流程 发送邮件"""
    order = apply_context['order']
    outsources = apply_context['outsources']
    outsources_info = "\n".join([o.outsource_info for o in outsources])
    if outsources[0].status == 3:
        url = mail.app.config['DOMAIN'] + order.finance_outsource_path()
    else:
        url = mail.app.config['DOMAIN'] + order.outsource_path()
    send_simple_mail(u'【外包报备流程】%s-%s' % (order.name, apply_context['action_msg']),
                     recipients=apply_context['to'],
                     body=(u"""%s

订单: %s
链接地址: %s
订单信息:
%s
外包信息:
%s
留言如下:
    %s
\n
by %s
""" % (apply_context['action_msg'], order.name, url, order.outsource_info, outsources_info, apply_context['msg'], g.user.name)))


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
    send_attach_mail(u'【豆瓣合同号申请】%s' % order.name,
                     recipients=apply_context['to'],
                     body=body,
                     file_paths=file_paths)


def init_signal(app):
    """注册信号的接收器"""
    password_changed_signal.connect_via(app)(password_changed)
    add_comment_signal.connect_via(app)(add_comment)
    order_apply_signal.connect_via(app)(order_apply)
    reply_apply_signal.connect_via(app)(reply_apply_signal)
    contract_apply_signal.connect_via(app)(contract_apply)
    douban_contract_apply_signal.connect_via(app)(douban_contract_apply)
    outsource_apply_signal.connect_via(app)(outsource_apply)
    invoice_apply_signal.connect_via(app)(invoice_apply)
    medium_invoice_apply_signal.connect_via(app)(medium_invoice_apply)
