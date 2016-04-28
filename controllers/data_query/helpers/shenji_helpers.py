# -*- coding: UTF-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_client_order_excel(orders, year):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    money_align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'代理/直客', u'客户合同号', u'客户', u'Campaign', u'客户合同金额', u'执行开始',
            u'执行结束', u'回款日期', u'回款总金额', u'欠款总金额', u'售卖类型', u'代理/直客']
    y, x = 0, 0
    for k in range(len(keys)):
        worksheet.merge_range(y, x, y + 1, x, keys[k], align_center)
        x += 1
    worksheet.merge_range(0, 12, 0, 24, u'客户执行金额', align_center)
    for k in range(12):
        worksheet.write(1, 12 + k, str(k + 1) + u'月', align_center)
    worksheet.write(1, 24, u'总计', align_center)
    worksheet.merge_range(0, 25, 0, 37, u'客户返点', align_center)
    for k in range(12):
        worksheet.write(1, 25 + k, str(k + 1) + u'月', align_center)
    worksheet.write(1, 37, u'总计', align_center)
    worksheet.merge_range(0, 38, 1, 38, u'投放媒体', align_center)
    worksheet.merge_range(0, 39, 1, 39, u'媒体合同号', align_center)
    worksheet.merge_range(0, 40, 1, 40, u'媒体售卖金额', align_center)
    worksheet.merge_range(0, 41, 1, 41, u'媒体金额', align_center)
    worksheet.merge_range(0, 42, 0, 54, u'媒体执行金额', align_center)
    for k in range(12):
        worksheet.write(1, 42 + k, str(k + 1) + u'月', align_center)
    worksheet.write(1, 54, u'总计', align_center)
    worksheet.merge_range(0, 55, 0, 67, u'媒体返点', align_center)
    for k in range(12):
        worksheet.write(1, 55 + k, str(k + 1) + u'月', align_center)
    worksheet.write(1, 67, u'总计', align_center)

    # 设置宽度为30
    for k in range(67):
        worksheet.set_column(k, 0, 15)
    th = 2
    for k in range(len(orders)):
        medium_data = orders[k]['medium_data']
        if len(medium_data) > 1:
            worksheet.merge_range(
                th, 0, th + len(medium_data) - 1, 0, orders[k]['agent_name'], align_left)
            worksheet.merge_range(
                th, 1, th + len(medium_data) - 1, 1, orders[k]['contract'], align_left)
            worksheet.merge_range(
                th, 2, th + len(medium_data) - 1, 2, orders[k]['client_name'], align_left)
            worksheet.merge_range(
                th, 3, th + len(medium_data) - 1, 3, orders[k]['campaign'], align_left)
            worksheet.merge_range(
                th, 4, th + len(medium_data) - 1, 4, orders[k]['money'], money_align_left)
            worksheet.merge_range(
                th, 5, th + len(medium_data) - 1, 5, orders[k]['start_date_cn'], align_left)
            worksheet.merge_range(
                th, 6, th + len(medium_data) - 1, 6, orders[k]['end_date_cn'], align_left)
            worksheet.merge_range(
                th, 7, th + len(medium_data) - 1, 7, orders[k]['reminde_date_cn'], align_left)
            worksheet.merge_range(
                th, 8, th + len(medium_data) - 1, 8, orders[k]['back_moneys'], money_align_left)
            worksheet.merge_range(th, 9, th + len(medium_data) - 1, 9,
                                  orders[k]['money'] - orders[k]['back_moneys'], money_align_left)
            worksheet.merge_range(
                th, 10, th + len(medium_data) - 1, 10, orders[k]['resource_type_cn'], align_left)
            worksheet.merge_range(
                th, 11, th + len(medium_data) - 1, 11, orders[k]['sale_type'], align_left)
            money_data = orders[k]['money_data']
            for i in range(len(money_data)):
                worksheet.merge_range(
                    th, 12 + i, th + len(medium_data) - 1, 12 + i, money_data[i], money_align_left)
            worksheet.merge_range(
                th, 24, th + len(medium_data) - 1, 24, sum(money_data), money_align_left)
            money_rebate_data = orders[k]['money_rebate_data']
            for i in range(len(money_rebate_data)):
                worksheet.merge_range(
                    th, 25 + i, th + len(medium_data) - 1, 25 + i, money_rebate_data[i], money_align_left)
            worksheet.merge_range(
                th, 37, th + len(medium_data) - 1, 37, sum(money_rebate_data), money_align_left)
            for m in medium_data:
                worksheet.write(th, 38, m['name'], align_left)
                worksheet.write(th, 39, m['medium_contract'], align_left)
                worksheet.write(th, 40, m['sale_money'], money_align_left)
                worksheet.write(th, 41, m['medium_money2'], money_align_left)
                medium_money2_data = m['medium_money2_data']
                for i in range(len(medium_money2_data)):
                    worksheet.write(
                        th, 42 + i, medium_money2_data[i], money_align_left)
                worksheet.write(th, 54, sum(
                    medium_money2_data), money_align_left)
                medium_money2_rebate_data = m['medium_money2_rebate_data']
                for i in range(len(medium_money2_rebate_data)):
                    worksheet.write(
                        th, 55 + i, medium_money2_rebate_data[i], money_align_left)
                worksheet.write(th, 67, sum(
                    medium_money2_rebate_data), money_align_left)
                worksheet.set_row(th, 20)
                th += 1
        else:
            worksheet.write(th, 0, orders[k]['agent_name'], align_left)
            worksheet.write(th, 1, orders[k]['contract'], align_left)
            worksheet.write(th, 2, orders[k]['client_name'], align_left)
            worksheet.write(th, 3, orders[k]['campaign'], align_left)
            worksheet.write(th, 4, orders[k]['money'], money_align_left)
            worksheet.write(th, 5, orders[k]['start_date_cn'], align_left)
            worksheet.write(th, 6, orders[k]['end_date_cn'], align_left)
            worksheet.write(th, 7, orders[k]['reminde_date_cn'], align_left)
            worksheet.write(th, 8, orders[k]['back_moneys'], money_align_left)
            worksheet.write(th, 9, orders[k][
                            'money'] - orders[k]['back_moneys'], money_align_left)
            worksheet.write(th, 10, orders[k]['resource_type_cn'], align_left)
            worksheet.write(th, 11, orders[k]['sale_type'], align_left)
            money_data = orders[k]['money_data']
            for i in range(len(money_data)):
                worksheet.write(th, 12 + i, money_data[i], money_align_left)
            worksheet.write(th, 24, sum(money_data), money_align_left)
            money_rebate_data = orders[k]['money_rebate_data']
            for i in range(len(money_rebate_data)):
                worksheet.write(
                    th, 25 + i, money_rebate_data[i], money_align_left)
            worksheet.write(th, 37, sum(money_rebate_data), money_align_left)
            if medium_data:
                worksheet.write(th, 38, medium_data[0]['name'], align_left)
                worksheet.write(th, 39, medium_data[0][
                                'medium_contract'], align_left)
                worksheet.write(th, 40, medium_data[0][
                                'sale_money'], money_align_left)
                worksheet.write(th, 41, medium_data[0][
                                'medium_money2'], money_align_left)
                medium_money2_data = medium_data[0]['medium_money2_data']
                for i in range(len(medium_money2_data)):
                    worksheet.write(
                        th, 42 + i, medium_money2_data[i], money_align_left)
                worksheet.write(th, 54, sum(
                    medium_money2_data), money_align_left)
                medium_money2_rebate_data = medium_data[
                    0]['medium_money2_rebate_data']
                for i in range(len(medium_money2_rebate_data)):
                    worksheet.write(
                        th, 55 + i, medium_money2_rebate_data[i], money_align_left)
                worksheet.write(th, 67, sum(
                    medium_money2_rebate_data), money_align_left)
            worksheet.set_row(th, 20)
            th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("cost_income_client_order-%s.xls" % (str(year)))
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
