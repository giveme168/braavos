# -*- coding: UTF-8 -*-
import datetime
import StringIO
import mimetypes
from werkzeug.datastructures import Headers
from flask import Blueprint, request, Response
from flask import render_template as tpl

from models.order import Order
from models.client_order import ClientOrder, ECPM_CONTRACT_STATUS_LIST
from models.associated_douban_order import AssociatedDoubanOrder
from models.douban_order import DoubanOrder
from controllers.data_query.helpers.order_helpers import get_monthes_pre_days, write_excel

ORDER_PAGE_NUM = 50
data_query_order_bp = Blueprint('data_query_order', __name__, template_folder='../../templates/data_query/order')


@data_query_order_bp.route('/', methods=['GET'])
def index():
    query_type = int(request.args.get('query_type', 4))
    query_month = request.args.get('query_month', '')
    page = int(request.args.get('page', 1))
    if query_month:
        query_month = datetime.datetime.strptime(query_month, '%Y-%m')
    else:
        query_month = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m'), '%Y-%m')
    # 全部客户订单
    if query_type == 1:
        query_orders = [o for o in ClientOrder.all() if o.client_start.strftime('%Y-%m') <=
                        query_month.strftime('%Y-%m') and o.client_end.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'agent_name': o.agent.name, 'client_name': o.client.name, 'campaign': o.campaign,
                   'start': o.client_start, 'end': o.client_end, 'money': o.money} for o in query_orders]
    # 全部媒体订单
    elif query_type == 2:
        query_orders = [o for o in Order.all() if o.medium_start.strftime('%Y-%m') <=
                        query_month.strftime('%Y-%m') and o.medium_end.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'medium_name': o.medium.name, 'campaign': o.campaign, 'start': o.medium_start,
                   'end': o.medium_end, 'money': o.medium_money} for o in query_orders]
    # 全部关联豆瓣订单
    elif query_type == 3:
        query_orders = [o for o in AssociatedDoubanOrder.all() if o.start_date.strftime('%Y-%m') <=
                        query_month.strftime('%Y-%m') and o.end_date.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'jiafang_name': o.jiafang_name, 'client_name': o.client.name, 'campaign': o.campaign, 'start': o.start_date,
                   'end': o.end_date, 'money': o.money} for o in query_orders]
    # 全部直签豆瓣订单
    else:
        query_orders = [o for o in DoubanOrder.all() if o.client_start.strftime('%Y-%m') <=
                        query_month.strftime('%Y-%m') and o.client_end.strftime('%Y-%m') >=
                        query_month.strftime('%Y-%m') and o.contract_status in ECPM_CONTRACT_STATUS_LIST]
        orders = [{'agent_name': o.agent.name, 'client_name': o.client.name, 'campaign': o.campaign,
                   'start': o.client_start, 'end': o.client_end, 'money': o.money} for o in query_orders]
    th_count = 0
    th_obj = []
    for order in orders:
        pre_money = float(order['money']) / ((order['end'] - order['start']).days + 1)
        monthes_pre_days = get_monthes_pre_days(query_month, datetime.datetime.fromordinal(order['start'].toordinal()),
                                                datetime.datetime.fromordinal(order['end'].toordinal()))
        order['order_pre_money'] = [{'month': k['month'].strftime('%Y-%m'),
                                     'money': '%.2f' % (pre_money * k['days'])}
                                    for k in monthes_pre_days]
        if len(monthes_pre_days) > th_count:
            th_obj = [{'month': k['month'].strftime('%Y-%m')}for k in monthes_pre_days]
            th_count = len(monthes_pre_days)
    if 'excel' == request.args.get('extype', ''):
        if query_type == 1:
            filename = ("%s-%s.xls" % (u"月度客户订单金额", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        elif query_type == 2:
            filename = ("%s-%s.xls" % (u"月度媒体订单金额", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        elif query_type == 3:
            filename = ("%s-%s.xls" % (u"月度关联豆瓣订单金额", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        else:
            filename = ("%s-%s.xls" % (u"月度直签豆瓣订单金额", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = write_excel(orders, query_type, th_obj)
        response = get_download_response(xls, filename)
        return response
    return tpl('index.html',
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
