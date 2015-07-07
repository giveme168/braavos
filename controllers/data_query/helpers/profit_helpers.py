# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response, g
from werkzeug.datastructures import Headers
import xlsxwriter


def write_douban_order_excel(orders, year, month):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    keys = [u'区域', u'合同号', u'客户名称', u'代理/直客', u'项目名称', u'客户合同总金额', u'客户' +
            str(month) + u'月执行额', str(month) + u'月支付代理返点', str(month) + u'月合同利润', u'合同开始', u'合同结束']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
    th = 1
    for k in range(len(orders)):
        worksheet.write(th, 0, orders[k].locations_cn, align_left)
        worksheet.write(th, 1, orders[k].contract, align_left)
        worksheet.write(th, 2, orders[k].client.name, align_left)
        worksheet.write(th, 3, orders[k].agent.name, align_left)
        worksheet.write(th, 4, orders[k].campaign, align_left)
        worksheet.write(th, 5, orders[k].money, align_left)
        worksheet.write(th, 6, orders[k].executive_report(
            g.user, year, [month], 'normal')[0], align_left)
        worksheet.write(
            th, 7, orders[k].rebate_agent_by_month(year, month), align_left)
        worksheet.write(th, 8, orders[k].profit_money(year, month), align_left)
        worksheet.write(th, 9, orders[k].start_date_cn, align_left)
        worksheet.write(th, 10, orders[k].end_date_cn, align_left)
        th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"Execution-douban", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


def write_order_excel(orders, year, month):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    keys = [u'所属区域', u'合同号', u'客户名称', u'项目名称', u'合同总金额', u'客户',
            str(month) + u'月执行额', str(month) + u'月支付代理返点', u'投放媒体',
            str(month) + u'月客户金额', u'媒体合同号',
            u'媒体合同总金额', str(month) + u'月媒体执行金额', str(month) + u'月媒体返点',
            str(month) + u'月合同利润', u'合同开始', u'合同结束']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
    th = 1
    for k in range(len(orders)):
        mediums = orders[k].medium_orders
        if len(mediums) > 1:
            worksheet.merge_range(
                th, 0, th + len(mediums) - 1, 0, orders[k].locations_cn, align_left)
            worksheet.merge_range(
                th, 1, th + len(mediums) - 1, 1, orders[k].contract, align_left)
            worksheet.merge_range(
                th, 2, th + len(mediums) - 1, 2, orders[k].client.name, align_left)
            worksheet.merge_range(
                th, 3, th + len(mediums) - 1, 3, orders[k].agent.name, align_left)
            worksheet.merge_range(
                th, 4, th + len(mediums) - 1, 4, orders[k].campaign, align_left)
            worksheet.merge_range(
                th, 5, th + len(mediums) - 1, 5, orders[k].money, align_left)
            worksheet.merge_range(th, 6, th + len(mediums) - 1, 6,
                                  orders[k].executive_report(g.user, year, [month], 'normal')[0], align_left)
            worksheet.merge_range(th, 7, th + len(mediums) - 1, 7,
                                  orders[k].rebate_agent_by_month(year, month), align_left)
            worksheet.merge_range(
                th, 13, th + len(mediums) - 1, 14, orders[k].profit_money(year, month), align_left)
            worksheet.merge_range(
                th, 14, th + len(mediums) - 1, 15, orders[k].start_date_cn, align_left)
            worksheet.merge_range(
                th, 15, th + len(mediums) - 1, 16, orders[k].end_date_cn, align_left)
            for i in range(len(mediums)):
                worksheet.write(th, 8, mediums[i].medium.name, align_left)
                worksheet.write(th, 9, mediums[i].get_executive_report_medium_money_by_month(
                    year, month, 'normal')['sale_money'], align_left)
                worksheet.write(th, 10, mediums[i].medium_contract, align_left)
                worksheet.write(
                    th, 11, mediums[i].medium_money2 or '', align_left)
                worksheet.write(th, 12, mediums[i].get_executive_report_medium_money_by_month(
                    year, month, 'normal')['medium_money2'], align_left)
                worksheet.write(
                    th, 13, mediums[i].rebate_medium_by_month(year, month), align_left)
                th += 1

        else:
            worksheet.write(th, 0, orders[k].locations_cn, align_left)
            worksheet.write(th, 1, orders[k].contract, align_left)
            worksheet.write(th, 2, orders[k].client.name, align_left)
            worksheet.write(th, 3, orders[k].agent.name, align_left)
            worksheet.write(th, 4, orders[k].campaign, align_left)
            worksheet.write(th, 5, orders[k].money, align_left)
            worksheet.write(th, 6, orders[k].executive_report(
                g.user, year, [month], 'normal')[0], align_left)
            worksheet.write(
                th, 7, orders[k].rebate_agent_by_month(year, month), align_left)
            if orders[k].medium_orders:
                worksheet.write(
                    th, 8, orders[k].medium_orders[0].medium.name, align_left)
                medium_order = orders[k].medium_orders[0]
                s_money = medium_order.get_executive_report_medium_money_by_month(year,
                                                                                  month,
                                                                                  'normal')['sale_money']
                worksheet.write(th, 9, s_money, align_left)
                worksheet.write(
                    th, 10, orders[k].medium_orders[0].medium_contract, align_left)
                worksheet.write(
                    th, 11, orders[k].medium_orders[0].medium_money2 or '', align_left)
                medium_order = orders[k].medium_orders[0]
                money2 = medium_order.get_executive_report_medium_money_by_month(year,
                                                                                 month,
                                                                                 'normal')['medium_money2']
                worksheet.write(th, 12, money2, align_left)
                worksheet.write(
                    th, 13, orders[k].medium_orders[0].rebate_medium_by_month(year, month), align_left)
            worksheet.write(
                th, 14, orders[k].profit_money(year, month), align_left)
            worksheet.write(th, 15, orders[k].start_date_cn, align_left)
            worksheet.write(th, 16, orders[k].end_date_cn, align_left)
            th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"Execution", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
