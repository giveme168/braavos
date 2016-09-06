# -*- coding: UTF-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_searchAd_client_bill_excel(data):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    money_align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'})
    keys = [u'媒体供应商', u'广告主', u'投放媒体', u'推广类型', u'结算开始时间', u'结算截止时间', u'实际消耗金额', u'对应返点金额']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
        worksheet.set_column(0, 0 + k, 20)
    th = 1
    for k in range(len(data)):
        worksheet.write(th, 0, data[k].company_cn, align_left)
        worksheet.write(th, 1, data[k].client.name, align_left)
        worksheet.write(th, 2, data[k].medium.name, align_left)
        worksheet.write(th, 3, data[k].resource_type_cn, align_left)
        worksheet.write(th, 4, data[k].start, align_left)
        worksheet.write(th, 5, data[k].end, align_left)
        worksheet.write(th, 6, data[k].money, money_align_left)
        worksheet.write(th, 7, data[k].rebate_money, money_align_left)
        th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("效果部门对账单.xls")
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
