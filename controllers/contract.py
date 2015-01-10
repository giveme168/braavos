# -*- coding: UTF-8 -*-
from flask import Blueprint, redirect, abort
from flask import g, flash

from models.douban_order import DoubanOrder
from models.user import User

from libs.signals import douban_contract_apply_signal

contract_bp = Blueprint('contract', __name__, template_folder='../templates/contract')


@contract_bp.route('/douban/<order_id>', methods=['GET'])
def douban_apply(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    to_users = User.douban_contracts() + order.direct_sales + order.agent_sales + [order.creator, g.user] + User.contracts() + User.douban_contracts()
    to_emails = [x.email for x in set(to_users)]
    douban_contract_apply_context = {"to": to_emails, "order": order}
    douban_contract_apply_signal.send(douban_contract_apply_context)
    flash(u'[%s] 已向豆瓣发送合同号申请邮件 ' % (order.name), 'success')
    flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')
    return redirect(order.info_path())
