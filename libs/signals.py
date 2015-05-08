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
outsource_distribute_signal = braavos_signals.signal('outsource_distribute')
merger_outsource_apply_signal = braavos_signals.signal('merger_outsource_apply')
apply_leave_signal = braavos_signals.signal('apply_leave')


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
    send_simple_mail(apply_context['title'], recipients=apply_context['to'], body=text)


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
    send_simple_mail(apply_context['title'], recipients=apply_context['to'], body=text)


'''
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
    send_simple_mail(apply_context['title'], recipients=apply_context['to'], body=text)
'''


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


def outsource_distribute(sender, apply_context):
    order = apply_context['order']
    title = u'【费用报备】%s-%s-订单分配提醒' % (order.contract or u'无合同号', order.jiafang_name)
    send_simple_mail(title, recipients=apply_context[
                     'to'], body=order.outsource_distribute_email_info(title))

def outsource_apply(sender, apply_context):
    """外包服务流程 发送邮件"""
    order = apply_context['order']
    outsources = apply_context['outsources']
    outsources_info = "\n".join([o.outsource_info for o in outsources])
    
    url = mail.app.config['DOMAIN'] + order.outsource_path()
    send_simple_mail(apply_context['title'], recipients=apply_context['to'],
                     body=order.outsource_email_info(apply_context['to_users'],
                                                     apply_context['title'], outsources_info,
                                                     url, apply_context['msg']))

def merger_outsource_apply(sender, apply_context):
    outsources = apply_context['outsources']
    outsources_info = "\n".join([o.outsource_info for o in outsources])
    pay_nums = sum([k.pay_num for k in outsources])
    if apply_context.has_key('url'):
        url = apply_context['url']
    else:
        url = mail.app.config['DOMAIN'] + outsources[0].finance_pay_path()
    if apply_context['invoice'] == 'True':
        invoice_type = u'有'
    else:
        invoice_type = u'无'
    body = u"""
Dear %s:

%s

【外包组成】
%s

申请付款总金额: %s
是否有发票:%s
发票信息:%s

留言:
%s


附注:
    致趣订单管理系统链接地址: %s

by %s\n
"""% (apply_context['to_users'], apply_context['title'], outsources_info, pay_nums, invoice_type, apply_context['remark'], apply_context['msg'], url, g.user.name)
    send_simple_mail(apply_context['title'], recipients=apply_context['to'],
                     body=body)


def apply_leave(sender, leave):
    status = leave.status
    if status in [0, 2]:
        to_name = ','.join([k.name for k in leave.creator.team_leaders])
        url = mail.app.config['DOMAIN'] + url_for('user.leaves')
    elif status in [3, 4]:
        to_name = leave.creator.name
        url = mail.app.config['DOMAIN'] + url_for('user.leave', user_id=leave.creator.id)
    to_users = leave.senders + leave.creator.team_leaders + [leave.creator]+ [g.user]
    to_emails = list(set([k.email for k in to_users])) + ['admin@inad.com']

    body = u"""
Dear %s:

申请状态: %s

请假人: %s
请假日期: %s - %s，共%s
请假类型: %s
请假原因: %s

请批准，谢谢


附注: 
    致趣订单管理系统链接地址: %s

"""% (to_name, leave.status_cn, leave.creator.name, leave.start_time_cn, leave.end_time_cn, leave.rate_day_cn, leave.type_cn, leave.reason, url)
    
    send_simple_mail(u'【请假申请】- %s'% (leave.creator.name), recipients=to_emails, body=body)


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
    outsource_distribute_signal.connect_via(app)(outsource_distribute)
    merger_outsource_apply_signal.connect_via(app)(merger_outsource_apply)
    apply_leave_signal.connect_via(app)(apply_leave)
