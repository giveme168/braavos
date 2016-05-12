# -*- coding: UTF-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_client_excel(agents):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u"名称", u"所属集团", u"2014年返点", u"2015年返点", u"2016年返点"]
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
        worksheet.set_column(0, 0 + k, 20)
    th = 1
    for k in range(len(agents)):
        worksheet.write(th, 0, agents[k]['name'], align_left)
        worksheet.write(th, 1, agents[k]['group_name'], align_left)
        worksheet.write(th, 2, agents[k]['rebate_2014'], align_left)
        worksheet.write(th, 3, agents[k]['rebate_2015'], align_left)
        worksheet.write(th, 4, agents[k]['rebate_2016'], align_left)
    workbook.close()
    response.data = output.getvalue()
    filename = ("代理详情.xls")
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


def write_medium_excel(mediums):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u"名称", u"级别", u"2014年返点", u"2015年返点", u"2016年返点"]
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
        worksheet.set_column(0, 0 + k, 20)
    th = 1
    for k in range(len(mediums)):
        worksheet.write(th, 0, mediums[k]['name'], align_left)
        worksheet.write(th, 1, mediums[k]['level_cn'], align_left)
        worksheet.write(th, 2, mediums[k]['rebate_2014'], align_left)
        worksheet.write(th, 3, mediums[k]['rebate_2015'], align_left)
        worksheet.write(th, 4, mediums[k]['rebate_2016'], align_left)
    workbook.close()
    response.data = output.getvalue()
    filename = ("媒体详情.xls")
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
