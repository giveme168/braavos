# -*- coding: UTF-8 -*-
import datetime
import StringIO
import mimetypes
from werkzeug.datastructures import Headers
from flask import Blueprint, request, Response
from flask import render_template as tpl

from models.order import Order
from models.client_order import (ClientOrder, ClientOrderExecutiveReport, ECPM_CONTRACT_STATUS_LIST,
                                 BackMoney, BackInvoiceRebate)
from models.associated_douban_order import AssociatedDoubanOrder
from models.douban_order import DoubanOrder
from models.invoice import Invoice, MediumInvoice, MediumInvoicePay, AgentInvoice, AgentInvoicePay, MediumRebateInvoice
from controllers.data_query.helpers.order_helpers import get_monthes_pre_days, write_excel, write_order_excel

ORDER_PAGE_NUM = 50
data_query_order_bp = Blueprint(
    'data_query_order', __name__, template_folder='../../templates/data_query/order')

'''
Invoice        # 客户发票
MediumInvoice  # 媒体发票
MediumInvoicePay  # 媒体发票打款
AgentInvoice    # 甲方返点发票
AgentInvoicePay # 甲方返点发票打款
BackMoney       # 回款回款
BackInvoiceRebate   #  返点发票
MediumRebateInvoice   # 媒体返点发票
'''


@data_query_order_bp.route('/cost', methods=['GET'])
def cost():
    client_invoices = list(Invoice.all())
    medium_invoices = list(MediumInvoice.all())
    medium_invoice_pays = list(MediumInvoicePay.all())
    medium_invoice_rebate_invoice = list(MediumRebateInvoice.all())
    agent_invoices = list(AgentInvoice.all())
    agent_invoice_pays = list(AgentInvoicePay.all())
    back_moneys = list(BackMoney.all())
    back_money_rebates = list(BackInvoiceRebate.all())

    now_date = datetime.datetime.now()
    info = request.values.get('info', '').strip()
    location = int(request.values.get('location', 0))
    year = request.values.get('year', now_date.strftime('%Y'))
    month = request.values.get('month', now_date.strftime('%m'))

    if month != '00':
        search_date = datetime.datetime.strptime(
            str(year) + '-' + str(month), '%Y-%m')
        orders = set([k.client_order for k in ClientOrderExecutiveReport.query.filter_by(
            month_day=search_date) if k.client_order.status == 1])
    else:
        orders = [k for k in ClientOrder.all() if k.client_start.year == int(
            year) or k.client_end.year == int(year)]
    if location != 0:
        orders = [k for k in orders if location in k.locations]
    if info:
        orders = [k for k in orders if info in k.search_info]

    orders = sorted(list(orders), key=lambda x: x.client_start, reverse=False)
    for order in orders:
        order.pass_invoice_sum = sum(
            [k.money for k in client_invoices if k.invoice_status == 0 and k.client_order == order])
        order.back_money_sum = sum(
            [k.money for k in back_moneys if k.client_order == order])
        order.back_money_rebate_sum = sum(
            [k.money for k in back_money_rebates if k.client_order == order])
        order.agent_invoice_sum = sum(
            [k.money for k in agent_invoices if k.client_order == order])

        agent_invoice_pay_sum = 0.0
        invoices = [k for k in agent_invoices if k.client_order == order]
        for invoice in invoices:
            agent_invoice_pay_sum += sum(
                [k.money for k in agent_invoice_pays if k.pay_status == 0 and k.agent_invoice == invoice])
        order.agent_invoice_pay_sum = agent_invoice_pay_sum

        order.medium_invoice_sum = sum(
            [k.money for k in medium_invoices if k.client_order == order])
        invoices = [k for k in medium_invoices if k.client_order == order]
        order.medium_invoice_pay_sum = sum(
            [k.money for k in medium_invoice_pays if k.pay_status == 0 and k.medium_invoice in invoices])
        order.medium_invoice_rebate_invoice_sum = sum(
            [k.money for k in medium_invoice_rebate_invoice if k.client_order == order and k.invoice_status == 0])
        for m in order.medium_orders:
            m.medium_invoice_sum = sum(
                [k.money for k in medium_invoices if k.client_order == order and k.medium == m.medium])
            m_invoices = [
                k for k in medium_invoices if k.client_order == order and k.medium == m.medium]
            m.medium_invoice_pay_sum = sum(
                [k.money for k in medium_invoice_pays if k.pay_status == 0 and k.medium_invoice in m_invoices])
            m.medium_invoice_rebate_invoice_sum = sum(
                [k.money for k in medium_invoice_rebate_invoice if k.client_order == order and
                 k.invoice_status == 0 and k.medium == m.medium])
    if request.values.get('action', '') == 'download':
        response = write_order_excel(list(orders))
        return response
    return tpl('cost.html', orders=orders, location=location,
               year=year, month=month, info=info)


@data_query_order_bp.route('/', methods=['GET'])
def index():
    query_type = int(request.args.get('query_type', 4))
    query_month = request.args.get('query_month', '')
    page = int(request.args.get('page', 1))
    if query_month:
        query_month = datetime.datetime.strptime(query_month, '%Y-%m')
    else:
        query_month = datetime.datetime.strptime(
            datetime.datetime.now().strftime('%Y-%m'), '%Y-%m')
    # 全部客户订单
    if query_type == 1:
        query_orders = [o for o in ClientOrder.all() if o.client_end.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'agent_name': o.agent.name, 'client_name': o.client.name, 'campaign': o.campaign,
                   'start': o.client_start, 'end': o.client_end, 'money': o.money} for o in query_orders]
    # 全部媒体订单
    elif query_type == 2:
        query_orders = [o for o in Order.all() if o.medium_end.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'medium_name': o.medium.name, 'campaign': o.campaign, 'start': o.medium_start,
                   'end': o.medium_end, 'money': o.medium_money} for o in query_orders]
    # 全部关联豆瓣订单
    elif query_type == 3:
        query_orders = [o for o in AssociatedDoubanOrder.all() if o.end_date.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'jiafang_name': o.jiafang_name, 'client_name': o.client.name, 'campaign': o.campaign,
                   'start': o.start_date, 'end': o.end_date, 'money': o.money} for o in query_orders]
    # 全部直签豆瓣订单
    else:
        query_orders = [o for o in DoubanOrder.all() if o.client_end.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'agent_name': o.agent.name, 'client_name': o.client.name, 'campaign': o.campaign,
                   'start': o.client_start, 'end': o.client_end, 'money': o.money} for o in query_orders]
    th_count = 0
    th_obj = []
    for order in orders:
        if order['money']:
            pre_money = float(order['money']) / \
                ((order['end'] - order['start']).days + 1)
        else:
            pre_money = 0
        monthes_pre_days = get_monthes_pre_days(query_month, datetime.datetime.fromordinal(order['start'].toordinal()),
                                                datetime.datetime.fromordinal(order['end'].toordinal()))
        order['order_pre_money'] = [{'month': k['month'].strftime('%Y-%m'),
                                     'money': '%.2f' % (pre_money * k['days'])}
                                    for k in monthes_pre_days]
        if len(monthes_pre_days) > th_count:
            th_obj = [
                {'month': k['month'].strftime('%Y-%m')}for k in monthes_pre_days]
            th_count = len(monthes_pre_days)
    if 'excel' == request.args.get('extype', ''):
        if query_type == 1:
            filename = (
                "%s-%s.xls" % (u"月度客户订单金额", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        elif query_type == 2:
            filename = (
                "%s-%s.xls" % (u"月度媒体订单金额", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        elif query_type == 3:
            filename = ("%s-%s.xls" % (u"月度关联豆瓣订单金额",
                                       datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        else:
            filename = ("%s-%s.xls" % (u"月度直签豆瓣订单金额",
                                       datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = write_excel(orders, query_type, th_obj)
        response = get_download_response(xls, filename)
        return response
    return tpl('/data_query/order/index.html',
               orders=orders,
               page=page,
               query_type=query_type,
               query_month=query_month.strftime('%Y-%m'),
               th_obj=th_obj)


def get_download_response(xls, filename):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    xls.save(output)
    response.data = output.getvalue()
    mimetype_tuple = mimetypes.guess_type(filename)
    response_headers = Headers({
        'Pragma': "public",
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Cache-Control': 'private',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
    response.headers = response_headers
    response.set_cookie('fileDownload', 'true', path='/')
    return response
