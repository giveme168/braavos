# -*- coding: UTF-8 -*-
import xlwt

import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter

from models.invoice import Invoice, MediumRebateInvoice, INVOICE_TYPE_CN, INVOICE_STATUS_PASS


def write_excel(orders):
    xls = xlwt.Workbook(encoding='utf-8')

    style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()  # 为样式创建字体
    font.name = 'Times New Roman'  # 选择字体
    font.bold = True  # 是否加粗
    style.font = font  # 为样式设置字体
    # font.height = 500 #设置高度
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_CENTER  # 设置水平居中
    al.vert = xlwt.Alignment.VERT_CENTER  # 设置垂直居中
    al.wrap = xlwt.Alignment.WRAP_AT_RIGHT  # 设置文字可以换行
    style.alignment = al

    sheet = xls.add_sheet("Sheet")
    keys = [u'合同名称', u'合同总金额', '已开发票金额', u'未开发票金额', u'申请通过个数', u'发票时间', u'公司名称',
            u'税号', u'公司地址', u'联系电话', u'银行账号', u'开户行', u'发票内容', u'发票金额', u'发票类型', u'发票号', u'回款时间']
    for k in range(len(keys)):
        sheet.write(0, k, keys[k])

    h, j = 1, 1
    for k in range(len(orders)):
        invoice_passes = [x for x in Invoice.query.filter_by(
            client_order=orders[k]) if x.invoice_status == INVOICE_STATUS_PASS]
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 0, 0, orders[k].name, style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 1, 1, str(orders[k].money), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 2, 2, str(orders[k].invoice_pass_sum), style)
        sheet.write_merge(h, h + len(invoice_passes) - 1, 3, 3,
                          str(orders[k].money - orders[k].invoice_pass_sum), style)
        sheet.write_merge(h, h + len(invoice_passes) - 1, 4, 4,
                          str(len(orders[k].get_invoice_by_status(0))), style)
        h = h + len(invoice_passes)
        for i in range(len(invoice_passes)):
            sheet.write(
                j, 5, invoice_passes[i].create_time.strftime('%Y-%m-%d'))
            sheet.write(j, 6, invoice_passes[i].company)
            sheet.write(j, 7, invoice_passes[i].tax_id)
            sheet.write(j, 8, invoice_passes[i].address)
            sheet.write(j, 9, invoice_passes[i].phone)
            sheet.write(j, 10, invoice_passes[i].bank_id)
            sheet.write(j, 11, invoice_passes[i].bank)
            sheet.write(j, 12, invoice_passes[i].detail)
            sheet.write(j, 13, invoice_passes[i].money)
            sheet.write(j, 14, INVOICE_TYPE_CN[invoice_passes[i].invoice_type])
            sheet.write(j, 15, invoice_passes[i].invoice_num)
            sheet.write(j, 16, str(invoice_passes[i].back_time_cn))
            j += 1
    return xls


def write_medium_rebate_invoice_excel(orders):
    xls = xlwt.Workbook(encoding='utf-8')

    style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()  # 为样式创建字体
    font.name = 'Times New Roman'  # 选择字体
    font.bold = True  # 是否加粗
    style.font = font  # 为样式设置字体
    # font.height = 500 #设置高度
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_CENTER  # 设置水平居中
    al.vert = xlwt.Alignment.VERT_CENTER  # 设置垂直居中
    al.wrap = xlwt.Alignment.WRAP_AT_RIGHT  # 设置文字可以换行
    style.alignment = al

    sheet = xls.add_sheet("Sheet")
    keys = [u'代理/直客', u'客户名称', u'Campaign', u'合同号', u'合同总金额', u'媒体总金额', u'媒体返点总金额',
            u'已开发票总金额', u'未开发票总金额', u'申请通过个数', u'投放媒体', u'发票时间', u'公司名称', u'税号',
            u'公司地址', u'联系电话', u'银行账号', u'开户行', u'发票内容', u'发票金额', u'发票类型', u'发票号',
            u'回款时间']
    h = 0
    for k in range(len(keys)):
        sheet.write(h, k, keys[k])

    h += 1
    for order in orders:
        invoice_passes = [x for x in MediumRebateInvoice.query.filter_by(
            client_order=order) if x.invoice_status == INVOICE_STATUS_PASS]
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 0, 0, order.agent.name, style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 1, 1, order.client.name, style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 2, 2, order.campaign, style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 3, 3, str(order.contract), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 4, 4, str(order.money), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 5, 5, str(order.mediums_money2), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 6, 6, str(order.mediums_rebate_money), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 7, 7, str(order.mediums_rebate_invoice_pass_sum), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 8, 8, str(order.mediums_rebate_money -
                                                      order.mediums_rebate_invoice_pass_sum), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 9, 9, str(len(order.get_medium_rebate_invoice_by_status(0))), style)
        for invoice in invoice_passes:
            sheet.write(h, 10, invoice.medium.name)
            sheet.write(h, 11, invoice.create_time.strftime('%Y-%m-%d'))
            sheet.write(h, 12, invoice.company)
            sheet.write(h, 13, invoice.tax_id)
            sheet.write(h, 14, invoice.address)
            sheet.write(h, 15, invoice.phone)
            sheet.write(h, 16, invoice.bank_id)
            sheet.write(h, 17, invoice.bank)
            sheet.write(h, 18, invoice.detail)
            sheet.write(h, 19, invoice.money)
            sheet.write(h, 20, INVOICE_TYPE_CN[invoice.invoice_type])
            sheet.write(h, 21, invoice.invoice_num)
            sheet.write(h, 22, str(invoice.back_time_cn))
            h += 1
    return xls


def write_apply_pass_invoice_excel(orders, type):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})

    keys = [u'代理/直客', u'客户名称', u'Campaign', u'合同号', u'开票时间', u'公司名称', u'税号',
            u'公司地址', u'联系电话', u'银行账号', u'开户行', u'发票内容', u'发票金额', u'发票类型',
            u'申请人']
    if type == 'medium_rebate_invoice':
        keys.insert(4, u'所属媒体')
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
    # 设置宽度为30
    worksheet.set_column(len(keys), 0, 20)
    # 设置高度
    for k in range(len(orders) + 2):
        worksheet.set_row(k, 30)
    th = 1
    if type == 'client_order_invoice':
        for k in range(len(orders)):
            worksheet.write(th, 0, orders[k].client_order.agent.name, align_left)
            worksheet.write(th, 1, orders[k].client_order.client.name, align_left)
            worksheet.write(th, 2, orders[k].client_order.campaign, align_left)
            worksheet.write(th, 3, orders[k].client_order.contract, align_left)
            worksheet.write(th, 4, orders[k].create_time_cn, align_left)
            worksheet.write(th, 5, orders[k].company, align_left)
            worksheet.write(th, 6, orders[k].tax_id, align_left)
            worksheet.write(th, 7, orders[k].address, align_left)
            worksheet.write(th, 8, orders[k].phone, align_left)
            worksheet.write(th, 9, orders[k].bank_id, align_left)
            worksheet.write(th, 10, orders[k].bank, align_left)
            worksheet.write(th, 11, orders[k].detail, align_left)
            worksheet.write(th, 12, orders[k].money, align_left)
            worksheet.write(th, 13, orders[k].invoice_type_cn, align_left)
            worksheet.write(th, 14, orders[k].creator.name, align_left)
            th += 1
        worksheet.merge_range(th, 0, th, 11, u'总计', align_center)
        worksheet.merge_range(th, 12, th, 14, sum(
            [k.money for k in orders]), align_left)
    elif type == 'medium_rebate_invoice':
        for k in range(len(orders)):
            worksheet.write(th, 0, orders[k].client_order.agent.name, align_left)
            worksheet.write(th, 1, orders[k].client_order.client.name, align_left)
            worksheet.write(th, 2, orders[k].client_order.campaign, align_left)
            worksheet.write(th, 3, orders[k].client_order.contract, align_left)
            worksheet.write(th, 4, orders[k].media.name, align_left)
            worksheet.write(th, 5, orders[k].create_time_cn, align_left)
            worksheet.write(th, 6, orders[k].company, align_left)
            worksheet.write(th, 7, orders[k].tax_id, align_left)
            worksheet.write(th, 8, orders[k].address, align_left)
            worksheet.write(th, 9, orders[k].phone, align_left)
            worksheet.write(th, 10, orders[k].bank_id, align_left)
            worksheet.write(th, 11, orders[k].bank, align_left)
            worksheet.write(th, 12, orders[k].detail, align_left)
            worksheet.write(th, 13, orders[k].money, align_left)
            worksheet.write(th, 14, orders[k].invoice_type_cn, align_left)
            worksheet.write(th, 15, orders[k].creator.name, align_left)
            th += 1
        worksheet.merge_range(th, 0, th, 12, u'总计', align_center)
        worksheet.merge_range(th, 13, th, 15, sum(
            [k.money for k in orders]), align_left)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (type, datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
