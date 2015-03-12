# -*- coding: UTF-8 -*-
import datetime
import StringIO
import mimetypes
from werkzeug.datastructures import Headers
from flask import Blueprint, request, Response
from flask import render_template as tpl

from models.order import Order
from models.client_order import ClientOrder
from controllers.data_query.helpers.order_helpers import get_monthes_pre_days, write_excel

ORDER_PAGE_NUM = 50
data_query_order_bp = Blueprint('data_query_order', __name__, template_folder='../../templates/data_query/order')


@data_query_order_bp.route('/', methods=['GET'])
def index():
    query_type = int(request.args.get('query_type',1))
    query_month = request.args.get('query_month','')
    page = int(request.args.get('page',1))
    page = int(request.args.get('page', 1))

    if query_month:
        query_month = datetime.datetime.strptime(query_month,'%Y-%m')
    else:
        query_month = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m'),'%Y-%m')
    
    if query_type == 1:   
        orders = [{'agent_name':o.agent.name,'client_name':o.client.name,'campaign':o.campaign,'start':o.client_start,'end':o.client_end,'money':o.money} for o in ClientOrder.all() if o.client_start.strftime('%Y-%m') \
         <= query_month.strftime('%Y-%m') and o.client_end.strftime('%Y-%m') >= query_month.strftime('%Y-%m')]
    else:
        orders = [{'medium_name':o.medium.name,'campaign':o.campaign,'start':o.medium_start,'end':o.medium_end,'money':o.medium_money} for o in Order.all() if o.medium_start.strftime('%Y-%m') \
        <= query_month.strftime('%Y-%m') and o.medium_end.strftime('%Y-%m') >= query_month.strftime('%Y-%m')]
    
    th_count = 0
    th_obj = []
    for order in orders:
        pre_money = float(order['money'])/((order['end']-order['start']).days+1)
        monthes_pre_days = get_monthes_pre_days(query_month,datetime.datetime.fromordinal(order['start'].toordinal()),datetime.datetime.fromordinal(order['end'].toordinal()))    
        order['order_pre_money'] = [{'month':k['month'].strftime('%Y-%m'),'money':'%.2f'%(pre_money*k['days'])}for k in monthes_pre_days]
        if len(monthes_pre_days) > th_count:
            th_obj = [{'month':k['month'].strftime('%Y-%m')}for k in monthes_pre_days]
            th_count =len(monthes_pre_days)

    if 'excel' == request.args.get('extype', ''):
        filename = ("%s-%s.xls" % (u"查询", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
        xls = write_excel(orders,query_type,th_obj)
        response = get_download_response(xls, filename)
        return response

    return tpl('index.html', orders=orders, 
        page=page, query_type=query_type,
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
