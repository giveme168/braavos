# -*- coding: utf-8 -*-
import datetime
from flask import request, g, Blueprint, redirect, abort, url_for
from flask import render_template as tpl

from models.douban_order import DoubanOrder, OtherCost

saler_douban_order_other_cost_bp = Blueprint(
    'saler_douban_order_other_cost', __name__, template_folder='../../templates/saler/douban_order')


@saler_douban_order_other_cost_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    if not (g.user.is_super_leader() or g.user.is_finance() or g.user.is_aduit()):
        abort(403)
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    return tpl('/saler/douban_order/other_cost/index.html', order=order)


@saler_douban_order_other_cost_bp.route('/<order_id>/create', methods=['POST'])
def create(order_id):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        abort(403)
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    money = request.values.get('money', 0)
    invoice = request.values.get('invoice', '')
    type = int(request.values.get('type', 1))
    on_time = request.values.get('on_time', datetime.datetime.today())
    other_cost = OtherCost.add(
        douban_order=order,
        money=money,
        invoice=invoice,
        type=type,
        on_time=on_time
    )
    order.add_comment(g.user, u"添加了尚典外包，金额：%s ; 发票：%s ; 类型：%s ; 发生时间：%s" % (
        str(other_cost.money),
        other_cost.invoice,
        other_cost.type_cn,
        other_cost.on_time_cn), msg_channel=10)

    return redirect(url_for('saler_douban_order_other_cost.index', order_id=order_id))


@saler_douban_order_other_cost_bp.route('/<order_id>/<oid>/delete', methods=['GET'])
def delete(order_id, oid):
    if not (g.user.is_super_leader() or g.user.is_finance()):
        abort(403)
    other_cost = OtherCost.get(oid)
    other_cost.douban_order.add_comment(g.user, u"删除了尚典外包，金额：%s ; 发票：%s ; 类型：%s ; 发生时间：%s" % (
        str(other_cost.money),
        other_cost.invoice,
        other_cost.type_cn,
        other_cost.on_time_cn), msg_channel=10)
    other_cost.delete()
    return redirect(url_for('saler_douban_order_other_cost.index', order_id=order_id))