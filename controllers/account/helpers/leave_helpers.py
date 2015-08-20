# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_outs_excel(leaves):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'请假人', u'请假类型', u'开始时间', u'结束时间', u'时长', u'状态']
    worksheet.set_column(0, len(keys), 25)
    for k in range(len(keys)):
        worksheet.write(0, k, keys[k], align_center)
    th = 1
    for k in range(len(leaves)):
        worksheet.write(th, 0, leaves[k].creator.name, align_center)
        worksheet.write(th, 1, leaves[k].type_cn, align_center)
        worksheet.write(th, 2, leaves[k].start_time_cn, align_center)
        worksheet.write(th, 3, leaves[k].end_time_cn, align_center)
        worksheet.write(th, 4, leaves[k].rate_day_cn, align_center)
        worksheet.write(th, 5, leaves[k].status_cn, align_center)
        th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                ("请假申请", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
