# -*- coding: utf-8 -*-
import datetime

from flask import request, Blueprint, abort, flash, g, redirect, url_for
from flask import render_template as tpl

from models.user import TEAM_LOCATION_CN
from libs.paginator import Paginator
from searchAd.models.rebate_order import searchAdRebateOrder, searchAdBackMoney, searchAdBackInvoiceRebate, CONTRACT_STATUS_CN

searchAd_finance_rebate_order_back_money_bp = Blueprint(
    'searchAd_finance_rebate_order_back_money', __name__, template_folder='../../../../templates/finance/rebate_order')


ORDER_PAGE_NUM = 50


@searchAd_finance_rebate_order_back_money_bp.route('/orders', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = list(searchAdRebateOrder.all())
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1

    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '')
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    year = int(request.values.get('year', datetime.datetime.now().year))
    # page = max(1, page)
    # start = (page - 1) * ORDER_PAGE_NUM
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    orders = [k for k in orders if k.client_start.year == year or k.client_end.year == year]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower() in o.search_info.lower()]
    if orderby and len(orders):
        orders = sorted(
            orders, key=lambda x: getattr(x, orderby), reverse=True)
    select_locations = TEAM_LOCATION_CN.items()
    select_locations.insert(0, (-1, u'全部区域'))
    select_statuses = CONTRACT_STATUS_CN.items()
    select_statuses.insert(0, (-1, u'全部合同状态'))
    paginator = Paginator(orders, ORDER_PAGE_NUM)
    try:
        orders = paginator.page(page)
    except:
        orders = paginator.page(paginator.num_pages)

    return tpl('/finance/searchAd_rebate_order/back_money/index.html', orders=orders,
               locations=select_locations, location_id=location_id,
               statuses=select_statuses, status_id=status_id,
               orderby=orderby, now_date=datetime.date.today(),
               search_info=search_info, page=page, year=year,
               params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s&year=%s' %
                      (orderby, search_info, location_id, status_id, str(year)))


@searchAd_finance_rebate_order_back_money_bp.route('/order/<order_id>/back_money', methods=['GET', 'POST'])
def back_money(order_id):
    if not g.user.is_finance():
        abort(404)
    order = searchAdRebateOrder.get(order_id)
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
        else:
            bm = searchAdBackMoney.add(
                rebate_order=order,
                money=money,
                back_time=back_time,
                create_time=datetime.date.today().strftime('%Y-%m-%d'))
            bm.save()
            flash(u'回款信息保存成功!', 'success')
            order.add_comment(
                g.user, u"更新了回款信息，回款金额: %s; 回款时间: %s;" % (money, back_time), msg_channel=4)
        return redirect(url_for("searchAd_finance_rebate_order_back_money.back_money", order_id=order.id))
    return tpl('/finance/searchAd_rebate_order/back_money/info.html', order=order)


@searchAd_finance_rebate_order_back_money_bp.route('/order/<order_id>/back_invoice', methods=['GET', 'POST'])
def back_invoice(order_id):
    if not g.user.is_finance():
        abort(404)
    order = searchAdRebateOrder.get(order_id)
    if not order:
        abort(404)
    if request.method == 'POST':
        money = float(request.values.get('money', 0))
        back_time = request.values.get(
            'back_time', datetime.date.today().strftime('%Y-%m-%d'))
        num = request.values.get('num', '')
        bm = searchAdBackInvoiceRebate.add(
            rebate_order=order,
            money=money,
            back_time=back_time,
            num=num,
            create_time=datetime.date.today().strftime('%Y-%m-%d'))
        bm.save()
        flash(u'返点发票信息保存成功!', 'success')
        order.add_comment(
            g.user, u"更新了返点发票信息，发票金额: %s; 发票时间: %s; 发票号: %s;" % (money, back_time, num), msg_channel=4)
        return redirect(url_for("searchAd_finance_rebate_order_back_money.back_money", order_id=order.id))
    return tpl('/finance/searchAd_rebate_order/back_money/info.html', order=order)


@searchAd_finance_rebate_order_back_money_bp.route('/order/<order_id>/back_money/<bid>/delete', methods=['GET'])
def delete(order_id, bid):
    order = searchAdRebateOrder.get(order_id)
    bm = searchAdBackMoney.get(bid)
    order.add_comment(g.user, u"删除了回款信息，回款金额: %s; 回款时间: %s;" %
                      (bm.money, bm.back_time_cn), msg_channel=4)
    bm.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("searchAd_finance_rebate_order_back_money.back_money", order_id=order.id))


@searchAd_finance_rebate_order_back_money_bp.route('/order/<order_id>/back_money/<bid>/delete_invoice', methods=['GET'])
def delete_invoice(order_id, bid):
    order = searchAdRebateOrder.get(order_id)
    bm = searchAdBackInvoiceRebate.get(bid)
    order.add_comment(g.user, u"删除了返点发票信息，发票金额: %s; 开票时间: %s; 发票号: %s;" % (
        bm.money, bm.back_time_cn, bm.num), msg_channel=4)
    bm.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("searchAd_finance_rebate_order_back_money.back_money", order_id=order.id))
