# -*- coding: UTF-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_order_excel(orders, year, total_money_data, location, type):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    money_align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'区域', u'代理/直客', u'客户合同号', u'客户', u'Campaign', u'客户合同金额', u'执行开始',
            u'执行结束', u'回款日期', u'回款总金额', u'欠款总金额', u'售卖类型', u'代理/直客']
    y, x = 0, 0
    for k in range(len(keys)):
        worksheet.merge_range(y, x, y + 1, x, keys[k], align_center)
        x += 1
    worksheet.merge_range(0, 13, 0, 25, u'客户执行金额', align_center)
    for k in range(12):
        worksheet.write(1, 13 + k, str(k + 1) + u'月', align_center)
    worksheet.write(1, 25, u'总计', align_center)
    # 设置宽度为30
    for k in range(51):
        worksheet.set_column(k, 0, 15)
    th = 2
    for k in range(len(orders)):
        worksheet.write(th, 0, orders[k]['locations_cn'], align_left)
        worksheet.write(th, 1, orders[k]['agent_name'], align_left)
        worksheet.write(th, 2, orders[k]['contract'], align_left)
        worksheet.write(th, 3, orders[k]['client_name'], align_left)
        worksheet.write(th, 4, orders[k]['campaign'], align_left)
        worksheet.write(th, 5, orders[k]['money'], money_align_left)
        worksheet.write(th, 6, orders[k]['start_date_cn'], align_left)
        worksheet.write(th, 7, orders[k]['end_date_cn'], align_left)
        worksheet.write(th, 8, orders[k]['reminde_date_cn'], align_left)
        worksheet.write(th, 9, orders[k]['back_moneys'], money_align_left)
        worksheet.write(th, 10, orders[k][
                        'money'] - orders[k]['back_moneys'], money_align_left)
        worksheet.write(th, 11, orders[k]['resource_type_cn'], align_left)
        worksheet.write(th, 12, orders[k]['sale_type'], align_left)
        money_data = orders[k]['money_data']
        for i in range(len(money_data)):
            worksheet.write(th, 13 + i, money_data[i], money_align_left)
        worksheet.write(th, 25, sum(money_data), money_align_left)
        worksheet.set_row(th, 20)
        th += 1
    # 总计
    worksheet.merge_range(th, 0, th, 4, u'总计', align_center)
    worksheet.write(th, 5, sum([k['money'] for k in orders]), money_align_left)
    worksheet.merge_range(th, 6, th, 8, '', align_center)
    worksheet.write(th, 9, sum([k['back_moneys']
                                for k in orders]), money_align_left)
    worksheet.write(th, 10, sum([k['money'] - k['back_moneys']
                                for k in orders]), money_align_left)
    worksheet.merge_range(th, 11, th, 12, '', align_center)
    for k in range(len(total_money_data)):
        worksheet.write(th, 13 + k, total_money_data[k], money_align_left)
    worksheet.write(th, 25, sum(total_money_data), money_align_left)
    workbook.close()
    response.data = output.getvalue()
    if type == 'client_order':
        type_cn = '新媒体订单'
    else:
        type_cn = '豆瓣订单'
    if location == 0:
        location_cn = '全部区域'
    elif location == 1:
        location_cn = '华北'
    elif location == 2:
        location_cn = '华东'
    elif location == 3:
        location_cn = '华南'
    filename = ("%s收入计提-%s-%s.xls" % (type_cn, str(year), location_cn))
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
