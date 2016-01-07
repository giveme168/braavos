# -*- coding: utf-8 -*-
import datetime

from flask import request, Blueprint, abort, flash, g, redirect, url_for
from flask import current_app, render_template as tpl

from models.user import TEAM_LOCATION_CN
from libs.paginator import Paginator
from models.client_order import ClientOrder, MediumBackMoney, CONTRACT_STATUS_CN
from models.order import Order
from libs.email_signals import medium_back_money_apply_signal

finance_client_order_medium_back_money_bp = Blueprint(
    'finance_client_order_medium_back_money', __name__, template_folder='../../templates/finance/client_order')


ORDER_PAGE_NUM = 50


@finance_client_order_medium_back_money_bp.route('/orders', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    orders = list(ClientOrder.all())
    if request.args.get('selected_status'):
        status_id = int(request.args.get('selected_status'))
    else:
        status_id = -1

    orderby = request.args.get('orderby', '')
    search_info = request.args.get('searchinfo', '').strip()
    location_id = int(request.args.get('selected_location', '-1'))
    page = int(request.args.get('p', 1))
    # page = max(1, page)
    # start = (page - 1) * ORDER_PAGE_NUM
    if location_id >= 0:
        orders = [o for o in orders if location_id in o.locations]
    if status_id >= 0:
        orders = [o for o in orders if o.contract_status == status_id]
    if search_info != '':
        orders = [
            o for o in orders if search_info.lower() in o.search_invoice_info.lower()]
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

    return tpl('/finance/client_order/medium_back_money/index.html', orders=orders,
               locations=select_locations, location_id=location_id,
               statuses=select_statuses, status_id=status_id,
               orderby=orderby, now_date=datetime.date.today(),
               search_info=search_info, page=page,
               params='&orderby=%s&searchinfo=%s&selected_location=%s&selected_status=%s' %
                      (orderby, search_info, location_id, status_id))


@finance_client_order_medium_back_money_bp.route('/order/<order_id>/info', methods=['GET', 'POST'])
def back_money(order_id):
    if not g.user.is_finance():
        abort(404)
    client_order = ClientOrder.get(order_id)
    back_moneys = MediumBackMoney.query.filter_by(client_order_id=order_id)
    if not client_order:
        abort(404)
    if request.method == 'POST':
        money = float(request.values.get('money', 0))
        back_time = request.values.get(
            'back_time', datetime.date.today().strftime('%Y-%m-%d'))
        medium_id = request.values.get('medium')
        order = Order.get(medium_id)
        MediumBackMoney.add(client_order_id=order_id,
                            order_id=medium_id,
                            money=money,
                            back_time=back_time)
        client_order.add_comment(g.user, u"更新了媒体返点回款信息，所属媒体:%s; 回款金额: %s; 回款时间: %s;" % (
            order.medium.name, money, back_time), msg_channel=8)
        apply_context = {
            'order': client_order,
            'num': money,
            'type': 'money',
        }
        medium_back_money_apply_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        flash(u'回款信息保存成功!', 'success')
    return tpl('/finance/client_order/medium_back_money/info.html', order=client_order, back_moneys=back_moneys)


@finance_client_order_medium_back_money_bp.route('/order/<order_id>/back_money/<bid>/delete', methods=['GET'])
def delete(order_id, bid):
    order = ClientOrder.get(order_id)
    bm = MediumBackMoney.get(bid)
    order.add_comment(g.user, u"删除了媒体返点回款信息，所属媒体: %s; 回款金额: %s; 回款时间: %s;" %
                      (bm.order.medium.name, bm.money, bm.back_time_cn), msg_channel=8)
    bm.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("finance_client_order_medium_back_money.back_money", order_id=order.id))
