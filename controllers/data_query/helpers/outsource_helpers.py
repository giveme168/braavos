# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_outsource_excel(monthes, data):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    worksheet.merge_range(0, 0, 1, 1, u'收支项目', align_left)

    for k in range(len(monthes)):
        if k == 0:
            start_td, end_td = 2, 4
        worksheet.merge_range(
            0, start_td, 0, end_td, monthes[k] + u'月', align_left)
        start_td += 3
        end_td += 3
    locations = [u'华东', u'华北', u'华南'] * 3
    for k in range(len(locations)):
        worksheet.write(1, 2 + k, locations[k], align_left)
    worksheet.merge_range(2, 0, 10, 0, u'外包项目', align_left)
    keys = [u'奖品', u'Flash', u'劳务(KOL、线下活动等)', u'效果优化',
            u'其他(视频等)', u'flash&H5开发', u'H5开发', u'区域总计', u'总计']
    for k in range(len(keys)):
        worksheet.write(2 + k, 1, keys[k], align_left)
    for k in range(len(data['1'])):
        worksheet.write(2, 2 + k * 3, data['1'][k]['huadong'], align_left)
        worksheet.write(2, 3 + k * 3, data['1'][k]['huabei'], align_left)
        worksheet.write(2, 4 + k * 3, data['1'][k]['huanan'], align_left)
    for k in range(len(data['2'])):
        worksheet.write(3, 2 + k * 3, data['2'][k]['huadong'], align_left)
        worksheet.write(3, 3 + k * 3, data['2'][k]['huabei'], align_left)
        worksheet.write(3, 4 + k * 3, data['2'][k]['huanan'], align_left)
    for k in range(len(data['3'])):
        worksheet.write(4, 2 + k * 3, data['3'][k]['huadong'], align_left)
        worksheet.write(4, 3 + k * 3, data['3'][k]['huabei'], align_left)
        worksheet.write(4, 4 + k * 3, data['3'][k]['huanan'], align_left)
    for k in range(len(data['4'])):
        worksheet.write(5, 2 + k * 3, data['4'][k]['huadong'], align_left)
        worksheet.write(5, 3 + k * 3, data['4'][k]['huabei'], align_left)
        worksheet.write(5, 4 + k * 3, data['4'][k]['huanan'], align_left)
    for k in range(len(data['5'])):
        worksheet.write(6, 2 + k * 3, data['5'][k]['huadong'], align_left)
        worksheet.write(6, 3 + k * 3, data['5'][k]['huabei'], align_left)
        worksheet.write(6, 4 + k * 3, data['5'][k]['huanan'], align_left)
    for k in range(len(data['6'])):
        worksheet.write(7, 2 + k * 3, data['6'][k]['huadong'], align_left)
        worksheet.write(7, 3 + k * 3, data['6'][k]['huabei'], align_left)
        worksheet.write(7, 4 + k * 3, data['6'][k]['huanan'], align_left)
    for k in range(len(data['7'])):
        worksheet.write(8, 2 + k * 3, data['7'][k]['huadong'], align_left)
        worksheet.write(8, 3 + k * 3, data['7'][k]['huabei'], align_left)
        worksheet.write(8, 4 + k * 3, data['7'][k]['huanan'], align_left)
    for k in range(len(data['t_locataion'])):
        worksheet.write(
            9, 2 + k * 3, data['t_locataion'][k]['huadong'], align_left)
        worksheet.write(
            9, 3 + k * 3, data['t_locataion'][k]['huabei'], align_left)
        worksheet.write(
            9, 4 + k * 3, data['t_locataion'][k]['huanan'], align_left)
    # for k in range(len(data['t_month'])):
    worksheet.merge_range(10, 2, 10, 4, data['t_month'][0], align_left)
    worksheet.merge_range(10, 5, 10, 7, data['t_month'][1], align_left)
    worksheet.merge_range(10, 8, 10, 10, data['t_month'][2], align_left)

    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"OutsourceWeekly", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


def write_client_excel(orders):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})

    keys = [u'代理/直客(甲方全称)', u'客户合同号', u'客户名称', u'Campaign名称', u'合同金额(元)',
            u'执行开始', u'执行结束', u'回款日期', u'直客销售', u'渠道销售', u'区域', u'合同模板类型',
            u'售卖类型', u'代理/直客', u'投放媒体', u'媒体合同号', u'售卖金额(元)', u'媒体金额(元)', u'分成金额(元)',
            u'预估量(CPM)', u'实际量(CPM)', u'执行开始', u'执行结束', u'执行人员']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
    th = 1
    for k in range(len(orders)):
        mediums = orders[k].medium_orders
        if len(mediums) > 1:
            worksheet.merge_range(
                th, 0, th + len(orders[k].medium_orders) - 1, 0, orders[k].agent.name, align_left)
            worksheet.merge_range(
                th, 1, th + len(orders[k].medium_orders) - 1, 1, orders[k].contract, align_left)
            worksheet.merge_range(
                th, 2, th + len(orders[k].medium_orders) - 1, 2, orders[k].client.name, align_left)
            worksheet.merge_range(
                th, 3, th + len(orders[k].medium_orders) - 1, 3, orders[k].campaign, align_left)
            worksheet.merge_range(
                th, 4, th + len(orders[k].medium_orders) - 1, 4, orders[k].money, align_left)
            worksheet.merge_range(
                th, 5, th + len(orders[k].medium_orders) - 1, 5, orders[k].start_date_cn, align_left)
            worksheet.merge_range(
                th, 6, th + len(orders[k].medium_orders) - 1, 6, orders[k].end_date_cn, align_left)
            worksheet.merge_range(
                th, 7, th + len(orders[k].medium_orders) - 1, 7, orders[k].reminde_date_cn, align_left)
            worksheet.merge_range(
                th, 8, th + len(orders[k].medium_orders) - 1, 8, orders[k].direct_sales_names, align_left)
            worksheet.merge_range(
                th, 9, th + len(orders[k].medium_orders) - 1, 9, orders[k].agent_sales_names, align_left)
            worksheet.merge_range(
                th, 10, th + len(orders[k].medium_orders) - 1, 10, orders[k].locations_cn, align_left)
            worksheet.merge_range(
                th, 11, th + len(orders[k].medium_orders) - 1, 11, orders[k].contract_type_cn, align_left)
            worksheet.merge_range(
                th, 12, th + len(orders[k].medium_orders) - 1, 12, orders[k].resource_type_cn, align_left)
            worksheet.merge_range(
                th, 13, th + len(orders[k].medium_orders) - 1, 13, orders[k].sale_type_cn, align_left)
            for i in range(len(mediums)):
                worksheet.write(th, 14, mediums[i].medium.name, align_left)
                worksheet.write(th, 15, mediums[i].medium_contract, align_left)
                worksheet.write(th, 16, mediums[i].sale_money, align_left)
                worksheet.write(th, 17, mediums[i].medium_money2, align_left)
                worksheet.write(th, 18, mediums[i].medium_money, align_left)
                worksheet.write(th, 19, mediums[i].sale_CPM, align_left)
                worksheet.write(th, 20, mediums[i].medium_CPM, align_left)
                worksheet.write(th, 21, mediums[i].start_date_cn, align_left)
                worksheet.write(th, 22, mediums[i].end_date_cn, align_left)
                worksheet.write(th, 23, mediums[i].operater_names, align_left)
                th += 1
        else:
            worksheet.write(th, 0, orders[k].agent.name, align_left)
            worksheet.write(th, 1, orders[k].contract, align_left)
            worksheet.write(th, 2, orders[k].client.name, align_left)
            worksheet.write(th, 3, orders[k].campaign, align_left)
            worksheet.write(th, 4, orders[k].money, align_left)
            worksheet.write(th, 5, orders[k].start_date_cn, align_left)
            worksheet.write(th, 6, orders[k].end_date_cn, align_left)
            worksheet.write(th, 7, orders[k].reminde_date_cn, align_left)
            worksheet.write(th, 8, orders[k].direct_sales_names, align_left)
            worksheet.write(th, 9, orders[k].agent_sales_names, align_left)
            worksheet.write(th, 10, orders[k].locations_cn, align_left)
            worksheet.write(th, 11, orders[k].contract_type_cn, align_left)
            worksheet.write(th, 12, orders[k].resource_type_cn, align_left)
            worksheet.write(th, 13, orders[k].sale_type_cn, align_left)
            worksheet.write(
                th, 14, orders[k].medium_orders[0].medium.name, align_left)
            worksheet.write(
                th, 15, orders[k].medium_orders[0].medium_contract, align_left)
            worksheet.write(
                th, 16, orders[k].medium_orders[0].sale_money, align_left)
            worksheet.write(
                th, 17, orders[k].medium_orders[0].medium_money2, align_left)
            worksheet.write(
                th, 18, orders[k].medium_orders[0].medium_money, align_left)
            worksheet.write(
                th, 19, orders[k].medium_orders[0].sale_CPM, align_left)
            worksheet.write(
                th, 20, orders[k].medium_orders[0].medium_CPM, align_left)
            worksheet.write(
                th, 21, orders[k].medium_orders[0].start_date_cn, align_left)
            worksheet.write(
                th, 22, orders[k].medium_orders[0].end_date_cn, align_left)
            worksheet.write(
                th, 23, orders[k].medium_orders[0].operater_names, align_left)
            th += 1

    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"ClientOrders", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
