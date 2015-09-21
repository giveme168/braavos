# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_order_excel(orders, t_type):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'代理/直客', u'客户', u'Campaign', u'直客销售', u'渠道销售', u'区域', u'合同号',
            u'媒体名称', u'执行开始时间', u'执行结束时间', u'客户合同金额']
    if t_type == 'agent_invoice':
        keys += [u'开票金额', u'开票时间']
    elif t_type == 'back_money':
        keys += [u'回款金额', u'回款时间']
    elif t_type == 'back_invoice':
        keys += [u'返点发票金额', u'返点发票时间']
    elif t_type == 'rebate_agent_invoice':
        keys += [u'返点发票金额', u'返点发票时间']
    elif t_type == 'pay_rebate_agent_invoice':
        keys += [u'打款金额', u'打款时间']
    elif t_type == 'medium_invoice':
        keys += [u'发票金额', u'开票时间']
    elif t_type == 'pay_medium_invoice':
        keys += [u'打款金额', u'打款时间']
    elif t_type == 'medium_rebate_invoice':
        keys += [u'开票金额', u'开票时间']

    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
    # 设置宽度为30
    worksheet.set_column(len(keys), 0, 20)
    # 设置高度
    for k in range(len(orders) + 1):
        worksheet.set_row(k, 30)
    th = 1
    for k in range(len(orders)):
        worksheet.write(th, 0, orders[k].client_order.agent.name, align_left)
        worksheet.write(th, 1, orders[k].client_order.client.name, align_left)
        worksheet.write(th, 2, orders[k].client_order.campaign, align_left)
        worksheet.write(th, 3, orders[k].client_order.direct_sales_names, align_left)
        worksheet.write(th, 4, orders[k].client_order.agent_sales_names, align_left)
        worksheet.write(th, 5, orders[k].client_order.locations_cn, align_left)
        worksheet.write(th, 6, orders[k].client_order.contract, align_left)
        worksheet.write(
            th, 7, ','.join([m.name for m in orders[k].client_order.medium_orders]), align_left)
        worksheet.write(th, 8, orders[k].client_order.start_date_cn, align_left)
        worksheet.write(th, 9, orders[k].client_order.end_date_cn, align_left)
        worksheet.write(th, 10, orders[k].client_order.money, align_left)
        if t_type == 'agent_invoice':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].create_time_cn, align_left)
        elif t_type == 'back_money':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].back_time_cn, align_left)
        elif t_type == 'back_invoice':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].back_time_cn, align_left)
        elif t_type == 'rebate_agent_invoice':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].add_time_cn, align_left)
        elif t_type == 'pay_rebate_agent_invoice':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].pay_time_cn, align_left)
        elif t_type == 'medium_invoice':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].add_time_cn, align_left)
        elif t_type == 'pay_medium_invoice':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].pay_time_cn, align_left)
        elif t_type == 'medium_rebate_invoice':
            worksheet.write(th, 11, orders[k].money, align_left)
            worksheet.write(th, 12, orders[k].create_time_cn, align_left)
        th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (t_type, datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
