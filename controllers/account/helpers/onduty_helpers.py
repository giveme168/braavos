# -*- coding: UTF-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_ondutys_excel(ondutys, start_date, end_date):
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    red_align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1, 'color': 'red'})
    url_format = workbook.add_format({
        'font_color': 'blue',
        'underline': 1,
        'valign': 'vcenter',
        'border': 1
    })
    keys = [u'员工姓名', u'异常次数', u'操作']
    worksheet.set_column(0, len(keys), 25)
    for k in range(len(keys)):
        worksheet.write(0, k, keys[k], align_center)
    th = 1
    for k in range(len(ondutys)):
        worksheet.write(th, 0, ondutys[k]['user'].name, align_center)
        if ondutys[k]['count'] > 0:
            worksheet.write(th, 1, ondutys[k]['count'], red_align_center)
        else:
            worksheet.write(th, 1, ondutys[k]['count'], align_center)
        worksheet.write_url(th, 2,
                            'http://z.inad.com/account/onduty/%s/info?start_time=%s&end_time=%s' % (
                                ondutys[k]['user'].id, start_date, end_date),
                            url_format, u'查看')
        th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s %s-%s.xls" %
                ("考勤表",
                 start_date,
                 end_date))
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
