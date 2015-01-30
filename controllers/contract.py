# -*- coding: UTF-8 -*-
from flask import Blueprint, redirect, abort
from flask import g, flash, current_app

from models.douban_order import DoubanOrder
from models.associated_douban_order import AssociatedDoubanOrder
from models.user import User

from libs.signals import douban_contract_apply_signal

contract_bp = Blueprint('contract', __name__, template_folder='../templates/contract')


def contract_apply(order):
    if not order:
        abort(404)
    to_users = User.douban_contracts_by_order(order) + [order.creator, g.user]
    to_emails = [x.email for x in set(to_users)]
    douban_contract_apply_context = {"to": to_emails, "order": order}
    douban_contract_apply_signal.send(current_app._get_current_object(), apply_context=douban_contract_apply_context)
    flash(u'[%s] 已向豆瓣发送合同号申请邮件 ' % (order.name), 'success')
    flash(u'[%s] 已发送邮件给 %s ' % (order.name, ', '.join(to_emails)), 'info')
    return redirect(order.info_path())


@contract_bp.route('/douban/<order_id>', methods=['GET'])
def douban_apply(order_id):
    order = DoubanOrder.get(order_id)
    return contract_apply(order)


@contract_bp.route('/associated_douban/<order_id>', methods=['GET'])
def associated_douban_apply(order_id):
    order = AssociatedDoubanOrder.get(order_id)
    return contract_apply(order)
