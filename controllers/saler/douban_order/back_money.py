# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, abort, url_for, current_app
from flask import redirect, flash, g, request, render_template as tpl

from models.douban_order import DoubanOrder, BackMoney, BackInvoiceRebate
from libs.signals import back_money_apply_signal

saler_douban_order_back_money_bp = Blueprint(
    'saler_douban_order_back_money', __name__, template_folder='../../templates/saler/douban_order')


@saler_douban_order_back_money_bp.route('/<order_id>', methods=['GET'])
def index(order_id):
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    return tpl('/saler/douban_order/back_money/index.html', order=order)


@saler_douban_order_back_money_bp.route('/order/<order_id>/back_money', methods=['GET', 'POST'])
def back_money(order_id):
    if not (g.user.is_contract() or g.user.is_finance()):
        abort(404)
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    if request.method == 'POST':
        money = float(request.values.get('money', 0))
        back_time = request.values.get(
            'back_time', datetime.date.today().strftime('%Y-%m-%d'))
        back_money_status = request.values.get('back_money_status', '')
        if back_money_status != '':
            if int(back_money_status) == 0:
                order.back_money_status = int(back_money_status)
                order.save()
                flash(u'完成所有回款!', 'success')
                order.add_comment(g.user, u"完成所有回款", msg_channel=4)
                apply_context = {
                    'order': order,
                    'num': 0,
                    'type': 'end',
                }
                back_money_apply_signal.send(
                    current_app._get_current_object(), apply_context=apply_context)
        else:
            bm = BackMoney.add(
                douban_order=order,
                money=money,
                back_time=back_time,
                create_time=datetime.date.today().strftime('%Y-%m-%d'))
            bm.save()
            apply_context = {
                'order': order,
                'num': money,
                'type': 'money',
            }
            back_money_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
            flash(u'回款信息保存成功!', 'success')
            order.add_comment(
                g.user, u"更新了回款信息，回款金额: %s; 回款时间: %s;" % (money, back_time), msg_channel=4)
        return redirect(url_for("saler_douban_order_back_money.back_money", order_id=order.id))
    return tpl('/saler/douban_order/back_money/index.html', order=order)


@saler_douban_order_back_money_bp.route('/order/<order_id>/back_invoice', methods=['GET', 'POST'])
def back_invoice(order_id):
    if not (g.user.is_contract() or g.user.is_finance()):
        abort(404)
    order = DoubanOrder.get(order_id)
    if not order:
        abort(404)
    if request.method == 'POST':
        money = float(request.values.get('money', 0))
        back_time = request.values.get(
            'back_time', datetime.date.today().strftime('%Y-%m-%d'))
        num = request.values.get('num', '')
        bm = BackInvoiceRebate.add(
            douban_order=order,
            money=money,
            back_time=back_time,
            num=num,
            create_time=datetime.date.today().strftime('%Y-%m-%d'))
        bm.save()
        apply_context = {
            'order': order,
            'num': money,
            'type': 'invoice',
        }
        back_money_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        flash(u'返点发票信息保存成功!', 'success')
        order.add_comment(
            g.user, u"更新了返点发票信息，发票金额: %s; 发票时间: %s; 发票号: %s;" % (money, back_time, num), msg_channel=4)
        return redirect(url_for("saler_douban_order_back_money.back_money", order_id=order.id))
    return tpl('/saler/douban_order/back_money/index.html', order=order)


@saler_douban_order_back_money_bp.route('/order/<order_id>/back_money/<bid>/delete', methods=['GET'])
def delete(order_id, bid):
    order = DoubanOrder.get(order_id)
    bm = BackMoney.get(bid)
    order.add_comment(g.user, u"删除了回款信息，回款金额: %s; 回款时间: %s;" %
                      (bm.money, bm.back_time_cn), msg_channel=4)
    bm.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("saler_douban_order_back_money.back_money", order_id=order.id))


@saler_douban_order_back_money_bp.route('/order/<order_id>/back_money/<bid>/delete_invoice', methods=['GET'])
def delete_invoice(order_id, bid):
    order = DoubanOrder.get(order_id)
    bm = BackInvoiceRebate.get(bid)
    order.add_comment(g.user, u"删除了返点发票信息，发票金额: %s; 开票时间: %s; 发票号: %s;" % (
        bm.money, bm.back_time_cn, bm.num), msg_channel=4)
    bm.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("saler_douban_order_back_money.back_money", order_id=order.id))
