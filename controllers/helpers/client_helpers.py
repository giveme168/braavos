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
        th += 1
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
        th += 1
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


def write_medium_group_excel(medium_groups):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u"媒体供应商", u"级别", u"2014年返点", u"2015年返点", u"2016年返点", u"媒体名称", u"2014年返点", u"2015年返点", u"2016年返点"]
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
        worksheet.set_column(0, 0 + k, 20)
    th = 1
    for mg in medium_groups:
        mediums = mg['mediums']
        if len(mediums) > 1:
            worksheet.merge_range(th, 0, th + len(mediums) - 1, 0, mg['name'], align_left)
            worksheet.merge_range(th, 1, th + len(mediums) - 1, 1, mg['level_cn'], align_left)
            worksheet.merge_range(th, 2, th + len(mediums) - 1, 2, mg['rebate_2014'], align_left)
            worksheet.merge_range(th, 3, th + len(mediums) - 1, 3, mg['rebate_2015'], align_left)
            worksheet.merge_range(th, 4, th + len(mediums) - 1, 4, mg['rebate_2016'], align_left)
            for m in mediums:
                worksheet.write(th, 5, m['name'], align_left)
                worksheet.write(th, 6, m['rebate_2014'], align_left)
                worksheet.write(th, 7, m['rebate_2015'], align_left)
                worksheet.write(th, 8, m['rebate_2016'], align_left)
                th += 1
        elif len(mediums) == 1:
            worksheet.write(th, 0, mg['name'], align_left)
            worksheet.write(th, 1, mg['level_cn'], align_left)
            worksheet.write(th, 2, mg['rebate_2014'], align_left)
            worksheet.write(th, 3, mg['rebate_2015'], align_left)
            worksheet.write(th, 4, mg['rebate_2016'], align_left)
            worksheet.write(th, 5, mediums[0]['name'], align_left)
            worksheet.write(th, 6, mediums[0]['rebate_2014'], align_left)
            worksheet.write(th, 7, mediums[0]['rebate_2015'], align_left)
            worksheet.write(th, 8, mediums[0]['rebate_2016'], align_left)
            th += 1
        else:
            worksheet.write(th, 0, mg['name'], align_left)
            worksheet.write(th, 1, mg['level_cn'], align_left)
            worksheet.write(th, 2, mg['rebate_2014'], align_left)
            worksheet.write(th, 3, mg['rebate_2015'], align_left)
            worksheet.write(th, 4, mg['rebate_2016'], align_left)
            worksheet.write(th, 5, '', align_left)
            worksheet.write(th, 6, '', align_left)
            worksheet.write(th, 7, '', align_left)
            worksheet.write(th, 8, '', align_left)
            th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("媒体供应商详情.xls")
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
