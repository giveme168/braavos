# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_client_excel(mediums):
    now_date = datetime.datetime.now()
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_left_money = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.0'})
    keys = [u"媒体名称", u"类别"] + [u"%s-%s-01" % (now_date.year, str(k)) for k in range(1, 13)] + [u'总计']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
    th = 1
    for k in range(len(list(mediums))):
        worksheet.merge_range(th, 0, th + 2, 0, mediums[k].name, align_left)
        worksheet.write(th, 1, u'售卖金额', align_left)
        worksheet.write(th + 1, 1, u'媒体金额', align_left)
        worksheet.write(th + 2, 1, u'金额差', align_left)
        for i in range(1, 13):
            worksheet.write(
                th, 1 + i, mediums[k].sale_money_report_by_month(i), align_left_money)
            worksheet.write(
                th + 1, 1 + i, mediums[k].medium_money2_report_by_month(i), align_left_money)
            worksheet.write(th + 2, 1 + i, mediums[k].sale_money_report_by_month(
                i) - mediums[k].medium_money2_report_by_month(i), align_left_money)
        worksheet.write(
            th, 14, mediums[k].sale_money_report_by_year(), align_left_money)
        worksheet.write(
            th + 1, 14, mediums[k].medium_money2_report_by_year(), align_left_money)
        worksheet.write(th + 2, 14, mediums[k].sale_money_report_by_year() - mediums[
                        k].medium_money2_report_by_year(), align_left_money)
        th += 3
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
