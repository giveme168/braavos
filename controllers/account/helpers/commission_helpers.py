# -*- coding: UTF-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_report_excel(Q, now_year, orders):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    text_format = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    text_format.set_text_wrap()
    keys = [u'代理公司', u'项目名称', u'类型', u'大区', u'合同编号', u'合同金额', u'执行开始',
            u'执行结束', u'发票时间', u'发票金额', u'回款时间', u'回款金额', u'区域', u'类型',
            u'销售', u'计算公式（说明：完成率* 提成比例 * 回款金额 * 项目账期系数 = 提成）', u'提成金额']
    worksheet.set_column(0, len(keys), 20)
    worksheet.set_column(15, 15, 80)
    for k in range(len(keys)):
        worksheet.write(0, k, keys[k], align_center)
    th = 1
    for k in range(len(orders)):
        salers_count = orders[k]['salers_count']
        sale_data = orders[k]['direct_sales'] + orders[k]['agent_sales']
        if salers_count > 1:
            worksheet.merge_range(
                th, 0, th + salers_count - 1, 0, orders[k]['agent_name'], align_left)
            worksheet.merge_range(
                th, 1, th + salers_count - 1, 1, orders[k]['campaign'], align_left)
            worksheet.merge_range(
                th, 2, th + salers_count - 1, 2, orders[k]['industry_cn'], align_left)
            worksheet.merge_range(
                th, 3, th + salers_count - 1, 3, orders[k]['locations_cn'], align_left)
            worksheet.merge_range(
                th, 4, th + salers_count - 1, 4, orders[k]['contract'], align_left)
            worksheet.merge_range(
                th, 5, th + salers_count - 1, 5, orders[k]['money'], align_left)
            worksheet.merge_range(
                th, 6, th + salers_count - 1, 6, orders[k]['client_start'], align_left)
            worksheet.merge_range(
                th, 7, th + salers_count - 1, 7, orders[k]['client_end'], align_left)
            worksheet.merge_range(
                th, 8, th + salers_count - 1, 8, orders[k]['invoice_time'] or u'无', align_left)
            worksheet.merge_range(
                th, 9, th + salers_count - 1, 9, orders[k]['invoice_sum'], align_left)
            worksheet.merge_range(
                th, 10, th + salers_count - 1, 10, orders[k]['money_time'] or u'无', align_left)
            worksheet.merge_range(
                th, 11, th + salers_count - 1, 11, orders[k]['money_sum'], align_left)
            for i in range(salers_count):
                worksheet.write(th, 12, sale_data[i][
                                'location_cn'], align_left)
                worksheet.write(th, 13, sale_data[i]['type'], align_left)
                worksheet.write(th, 14, sale_data[i]['name'], align_left)
                str_formula = sale_data[i]['str_formula'].replace(
                    '<br/>', '\n').replace('&nbsp;', ' ')
                worksheet.write(th, 15, str_formula, text_format)
                worksheet.write(th, 16, sale_data[i][
                                'commission_money'], align_center)
                worksheet.set_row(th, 15 * len(str_formula.split('\n')))
                th += 1
        else:
            worksheet.write(th, 0, orders[k]['agent_name'], align_left)
            worksheet.write(th, 1, orders[k]['campaign'], align_left)
            worksheet.write(th, 2, orders[k]['industry_cn'], align_left)
            worksheet.write(th, 3, orders[k]['locations_cn'], align_left)
            worksheet.write(th, 4, orders[k]['contract'], align_left)
            worksheet.write(th, 5, orders[k]['money'], align_left)
            worksheet.write(th, 6, orders[k]['client_start'].strftime(
                '%Y-%m-%d'), align_left)
            worksheet.write(th, 7, orders[k]['client_end'].strftime(
                '%Y-%m-%d'), align_left)
            worksheet.write(th, 8, orders[k][
                            'invoice_time'] or u'无', align_left)
            worksheet.write(th, 9, orders[k]['invoice_sum'], align_left)
            worksheet.write(th, 10, orders[k][
                            'money_time'] or u'无', align_left)
            worksheet.write(th, 11, orders[k]['money_sum'], align_left)
            worksheet.write(th, 12, sale_data[0]['location_cn'], align_left)
            worksheet.write(th, 13, sale_data[0]['type'], align_left)
            worksheet.write(th, 14, sale_data[0]['name'], align_left)
            str_formula = sale_data[0]['str_formula'].replace(
                '<br/>', '\n').replace('&nbsp;', ' ')
            worksheet.write(th, 15, str_formula, text_format)
            worksheet.write(th, 16, sale_data[0][
                            'commission_money'], align_center)
            worksheet.set_row(th, 15 * len(str_formula.split('\n')))
            th += 1
    worksheet.merge_range(th, 0, th, 4, u'总计', align_center)
    worksheet.write(th, 5, sum([k['money'] for k in orders]), align_left)
    worksheet.merge_range(th, 6, th, 8, '', align_center)
    worksheet.write(th, 9, sum([k['invoice_sum'] for k in orders]), align_left)
    worksheet.write(th, 10, '', align_left)
    worksheet.write(th, 11, sum([k['money_sum'] for k in orders]), align_left)
    worksheet.merge_range(th, 12, th, 15, '', align_center)
    worksheet.write(th, 16, sum(
        [k['total_commission_money'] for k in orders]), align_center)
    worksheet.set_row(th, 20)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" % ("销售提成表", str(now_year) + str(Q)))
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
