# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def _insert_medium_data(workbook, worksheet, data, th):
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    worksheet.merge_range(th, 0, th + 3, 0, data['name'], align_center)
    worksheet.write(th, 1, u'售卖金额', align_center)
    worksheet.write(th + 1, 1, u'媒体金额', align_center)
    worksheet.write(th + 2, 1, u'媒体返点', align_center)
    worksheet.write(th + 3, 1, u'代理返点', align_center)
    for k in range(12):
        worksheet.write(th, 2 + k, data['sale_money_data'][k], align_left)
        worksheet.write(
            th + 1, 2 + k, data['medium_money2_data'][k], align_left)
        worksheet.write(
            th + 2, 2 + k, data['medium_rebate_data'][k], align_left)
        worksheet.write(
            th + 3, 2 + k, data['agent_rebate_data'][k], align_left)
    worksheet.write(th, 14, sum(data['sale_money_data']), align_center)
    worksheet.write(th + 1, 14, sum(data['medium_money2_data']), align_center)
    worksheet.write(th + 2, 14, sum(data['medium_rebate_data']), align_center)
    worksheet.write(th + 3, 14, sum(data['agent_rebate_data']), align_center)
    return th + 4


def write_client_excel(medium_data, year):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u"媒体名称", u"类别"] + [u"%s-%s-01" % (year, str(k)) for k in range(1, 13)] + [u'总计']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
        worksheet.set_column(0, k, 15)
    th = 1
    for k in medium_data:
        th = _insert_medium_data(workbook, worksheet, k, th)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"MediumsWeekly", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
