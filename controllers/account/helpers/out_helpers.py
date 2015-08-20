# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_outs_excel(outs):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'外出申请人', u'参会人', u'开始时间', u'结束时间', u'状态']
    worksheet.set_column(0, len(keys), 25)
    for k in range(len(keys)):
        worksheet.write(0, k, keys[k], align_center)
    th = 1
    for k in range(len(outs)):
        if len(outs[k].joiners) > 1:
            worksheet.merge_range(
                th, 0, th + len(outs[k].joiners) - 1, 0, outs[k].creator.name, align_center)
            worksheet.merge_range(
                th, 2, th + len(outs[k].joiners) - 1, 2, outs[k].start_time_cn, align_center)
            worksheet.merge_range(
                th, 3, th + len(outs[k].joiners) - 1, 3, outs[k].end_time_cn, align_center)
            worksheet.merge_range(
                th, 4, th + len(outs[k].joiners) - 1, 4, outs[k].status_cn, align_center)
            joiners = outs[k].joiners
            for i in range(len(joiners)):
                worksheet.write(th + i, 1, joiners[i].name, align_center)
            th += len(outs[k].joiners)
        else:
            worksheet.write(th, 0, outs[k].creator.name, align_center)
            if outs[k].joiners:
                worksheet.write(th, 1, outs[k].joiners[0].name, align_center)
            else:
                worksheet.write(th, 1, '', align_center)
            worksheet.write(th, 2, outs[k].start_time_cn, align_center)
            worksheet.write(th, 3, outs[k].end_time_cn, align_center)
            worksheet.write(th, 4, outs[k].status_cn, align_center)
            th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                ("外出报备", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
