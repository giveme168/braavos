# -*- coding: UTF-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_edit_order_excel(orders, year, month):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'代理/直客', u'客户名称', u'Campaign', u'合同号', u'合同金额', u'开始时间', u'结束时间', u'改单人', u'改单时间']
    for k in range(len(keys)):
        worksheet.merge_range(0, k, 1, k, keys[k], align_center)
    worksheet.merge_range(0, 9, 0, 10, u'更改内容', align_center)
    worksheet.write(1, 9, u'更前内容', align_center)
    worksheet.write(1, 10, u'更后内容', align_center)
    # 设置宽度
    worksheet.set_column(8, 0, 20)
    worksheet.set_column(9, 10, 40)
    th = 2
    for k in range(len(orders)):
        edit_msg_len = len(orders[k].edit_objs)
        worksheet.merge_range(th, 0, th + edit_msg_len - 1, 0, orders[k].agent.name, align_left)
        worksheet.merge_range(th, 1, th + edit_msg_len - 1, 1, orders[k].client.name, align_left)
        worksheet.merge_range(th, 2, th + edit_msg_len - 1, 2, orders[k].campaign, align_left)
        worksheet.merge_range(th, 3, th + edit_msg_len - 1, 3, orders[k].contract or u'无', align_left)
        worksheet.merge_range(th, 4, th + edit_msg_len - 1, 4, orders[k].money, align_left)
        worksheet.merge_range(th, 5, th + edit_msg_len - 1, 5, orders[k].start_date_cn, align_left)
        worksheet.merge_range(th, 6, th + edit_msg_len - 1, 6, orders[k].end_date_cn, align_left)
        worksheet.merge_range(th, 7, th + edit_msg_len - 1, 7, orders[k].creator.name, align_left)
        worksheet.merge_range(th, 8, th + edit_msg_len - 1, 8, orders[k].create_time_cn, align_left)
        edit_objs = orders[k].edit_objs
        for e in range(edit_msg_len):
            if len(edit_objs[e]) == 3:
                worksheet.merge_range(th, 9, th, 10, edit_objs[e][0], align_left)
            else:
                worksheet.write(th, 9, edit_objs[e][0], align_left)
                worksheet.write(th, 10, edit_objs[e][1], align_left)
            th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s的改单申请.xls" % (str(year), str(month)))
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
