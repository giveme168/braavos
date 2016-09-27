# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_order_excel(orders, t_type):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    if t_type in ['personal_outsource', 'outsource']:
        keys = [u'打款时间', u'是否有发票', u'发票信息', u'申请打款总金额', u'收款方', u'开户行',
                u'卡号', u'支付宝', u'订单名称', u'订单合同号', u'成本金额', u'打款金额', u'备注']
        for k in range(len(keys)):
            worksheet.write(0, 0 + k, keys[k], align_center)
        # 设置宽度为30
        worksheet.set_column(len(keys), 0, 20)
        th = 1
        for k in range(len(orders)):
            outsources_len = len(orders[k].outsources)
            if outsources_len == 1:
                worksheet.write(th, 0, orders[k].create_time_cn, align_left)
                if orders[k].invoice:
                    worksheet.write(th, 1, u'有', align_left)
                else:
                    worksheet.write(th, 1, u'无', align_left)
                worksheet.write(th, 2, orders[k].remark, align_left)
                worksheet.write(th, 3, orders[k].pay_num, align_left)
            else:
                worksheet.merge_range(
                    th, 0, th + outsources_len - 1, 0, orders[k].create_time_cn, align_left)
                if orders[k].invoice:
                    worksheet.merge_range(
                        th, 1, th + outsources_len - 1, 1, u'有', align_left)
                else:
                    worksheet.merge_range(
                        th, 1, th + outsources_len - 1, 1, u'无', align_left)
                worksheet.merge_range(
                    th, 2, th + outsources_len - 1, 2, orders[k].remark, align_left)
                worksheet.merge_range(
                    th, 3, th + outsources_len - 1, 3, orders[k].pay_num, align_left)
            for o in orders[k].outsources:
                worksheet.write(th, 4, o.target.name, align_left)
                worksheet.write(th, 5, o.target.bank, align_left)
                worksheet.write(th, 6, o.target.card, align_left)
                worksheet.write(th, 7, o.target.alipay, align_left)
                worksheet.write(th, 8, o.order.name, align_left)
                worksheet.write(th, 9, o.order.contract, align_left)
                worksheet.write(th, 10, o.pay_num, align_left)
                if orders[k].invoice:
                    worksheet.write(th, 11, o.pay_num, align_left)
                else:
                    worksheet.write(th, 11, o.pay_num * 0.95, align_left)
                worksheet.write(th, 12, o.remark, align_left)
                th += 1
        worksheet.merge_range(th, 0, th, 2, u'总计', align_center)
        worksheet.write(th, 3, sum([k.pay_num for k in orders]), align_center)
        worksheet.merge_range(th, 4, th, 9, '', align_center)
        worksheet.write(th, 10, sum(
            [k.re_pay_num for k in orders]), align_center)
        worksheet.write(th, 11, sum(
            [k.ex_pay_num for k in orders]), align_center)
        worksheet.write(th, 12, '', align_left)
        # 设置高度
        for k in range(th + 2):
            worksheet.set_row(k, 30)
    elif t_type in ['douban_back_money', 'douban_back_invoice']:
        keys = [u'代理/直客', u'客户', u'Campaign', u'直客销售', u'渠道销售', u'区域', u'合同号',
                u'执行开始时间', u'执行结束时间', u'合同回款时间', u'客户合同金额']
        if t_type == 'douban_back_money':
            keys += [u'回款金额', u'回款比例', u'回款时间', u'回款时间差']
        elif t_type == 'douban_back_invoice':
            keys += [u'返点发票金额', u'回款比例', u'返点发票时间']
        for k in range(len(keys)):
            worksheet.write(0, 0 + k, keys[k], align_center)
        # 设置宽度为30
        worksheet.set_column(len(keys), 0, 20)
        # 设置高度
        for k in range(len(orders) + 2):
            worksheet.set_row(k, 30)
        th = 1
        for k in range(len(orders)):
            worksheet.write(
                th, 0, orders[k].douban_order.agent.name, align_left)
            worksheet.write(
                th, 1, orders[k].douban_order.client.name, align_left)
            worksheet.write(th, 2, orders[k].douban_order.campaign, align_left)
            worksheet.write(
                th, 3, orders[k].douban_order.direct_sales_names, align_left)
            worksheet.write(
                th, 4, orders[k].douban_order.agent_sales_names, align_left)
            worksheet.write(
                th, 5, orders[k].douban_order.locations_cn, align_left)
            worksheet.write(th, 6, orders[k].douban_order.contract, align_left)
            worksheet.write(
                th, 7, orders[k].douban_order.start_date_cn, align_left)
            worksheet.write(
                th, 8, orders[k].douban_order.end_date_cn, align_left)
            worksheet.write(
                th, 9, orders[k].douban_order.reminde_date_cn, align_left)
            worksheet.write(th, 10, orders[k].douban_order.money, align_left)
            if t_type == 'douban_back_money':
                worksheet.write(th, 11, orders[k].money, align_left)
                worksheet.write(th, 12, str(
                    orders[k].douban_order.back_money_percent) + u'%', align_left)
                worksheet.write(th, 13, orders[k].back_time_cn, align_left)
                worksheet.write(th, 14, str(
                    orders[k].real_back_money_diff_time) + u'天', align_left)
            elif t_type == 'douban_back_invoice':
                worksheet.write(th, 11, orders[k].money, align_left)
                worksheet.write(th, 12, str(
                    orders[k].douban_order.back_money_percent) + u'%', align_left)
                worksheet.write(th, 13, orders[k].back_time_cn, align_left)
            th += 1
        worksheet.merge_range(th, 0, th, 10, u'总计', align_center)
        if t_type == 'douban_back_money':
            worksheet.merge_range(th, 11, th, 14, sum(
                [k.money for k in orders]), align_left)
        else:
            worksheet.merge_range(th, 11, th, 13, sum(
                [k.money for k in orders]), align_left)
    elif t_type == 'bill_rebate_invoice':
        keys = [u'媒体供应商', u'广告主', u'投放媒体', u'推广类型', u'结算开始时间', u'结算截止时间',
                u'实际消耗金额', u'对应返点金额', u'返点发票金额', u'返点发票时间']
        for k in range(len(keys)):
            worksheet.write(0, 0 + k, keys[k], align_center)
        # 设置宽度为30
        worksheet.set_column(len(keys), 0, 20)
        # 设置高度
        for k in range(len(orders) + 2):
            worksheet.set_row(k, 30)
        th = 1
        for k in range(len(orders)):
            worksheet.write(th, 0, orders[k].client_order_bill.company_cn, align_left)
            worksheet.write(th, 1, orders[k].client_order_bill.client.name, align_left)
            worksheet.write(th, 2, orders[k].client_order_bill.medium.name, align_left)
            worksheet.write(th, 3, orders[k].client_order_bill.resource_type_cn, align_left)
            worksheet.write(th, 4, orders[k].client_order_bill.start_cn, align_left)
            worksheet.write(th, 5, orders[k].client_order_bill.end_cn, align_left)
            worksheet.write(th, 6, orders[k].client_order_bill.money, align_left)
            worksheet.write(th, 7, orders[k].client_order_bill.rebate_money, align_left)
            worksheet.write(th, 8, orders[k].money, align_left)
            worksheet.write(th, 9, orders[k].create_time_cn, align_left)
            th += 1
        worksheet.merge_range(th, 0, th, 7, u'总计', align_center)
        worksheet.merge_range(th, 8, th, 9, sum(
            [k.money for k in orders]), align_left)
    else:
        keys = [u'代理/直客', u'客户', u'Campaign', u'直客销售', u'渠道销售', u'区域', u'合同号',
                u'媒体名称', u'执行开始时间', u'执行结束时间', u'合同回款时间', u'客户合同金额']
        if t_type == 'agent_invoice':
            keys += [u'开票金额', u'开票时间']
        elif t_type == 'back_money':
            keys += [u'回款金额', u'回款比例', u'回款时间', u'回款时间差']
        elif t_type == 'back_invoice':
            keys += [u'返点发票金额', u'回款比例', u'返点发票时间']
        elif t_type == 'rebate_agent_invoice':
            keys += [u'返点发票金额', u'返点发票时间']
        elif t_type == 'pay_rebate_agent_invoice':
            keys += [u'打款金额', u'打款时间']
        elif t_type == 'medium_invoice':
            keys += [u'发票金额', u'开票时间']
        elif t_type == 'pay_medium_invoice':
            keys += [u'打款金额', u'打款时间']
        elif t_type == 'medium_rebate_invoice':
            keys += [u'开票金额', u'开票时间']

        for k in range(len(keys)):
            worksheet.write(0, 0 + k, keys[k], align_center)
        # 设置宽度为30
        worksheet.set_column(len(keys), 0, 20)
        # 设置高度
        for k in range(len(orders) + 2):
            worksheet.set_row(k, 30)
        th = 1
        for k in range(len(orders)):
            worksheet.write(
                th, 0, orders[k].client_order.agent.name, align_left)
            worksheet.write(
                th, 1, orders[k].client_order.client.name, align_left)
            worksheet.write(th, 2, orders[k].client_order.campaign, align_left)
            worksheet.write(
                th, 3, orders[k].client_order.direct_sales_names, align_left)
            worksheet.write(
                th, 4, orders[k].client_order.agent_sales_names, align_left)
            worksheet.write(
                th, 5, orders[k].client_order.locations_cn, align_left)
            worksheet.write(th, 6, orders[k].client_order.contract, align_left)
            if t_type == 'pay_medium_invoice':
                worksheet.write(th, 7, orders[k].medium_invoice.company, align_left)
            elif t_type == 'medium_invoice':
                worksheet.write(th, 7, orders[k].company, align_left)
            elif t_type == 'medium_rebate_invoice':
                worksheet.write(th, 7, orders[k].company, align_left)
            else:
                worksheet.write(
                    th, 7, ','.join([m.name for m in orders[k].client_order.medium_orders]), align_left)
            worksheet.write(
                th, 8, orders[k].client_order.start_date_cn, align_left)
            worksheet.write(
                th, 9, orders[k].client_order.end_date_cn, align_left)
            worksheet.write(
                th, 10, orders[k].client_order.reminde_date_cn, align_left)
            worksheet.write(th, 11, orders[k].client_order.money, align_left)
            if t_type == 'agent_invoice':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, orders[k].create_time_cn, align_left)
            elif t_type == 'back_money':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, str(
                    orders[k].client_order.back_money_percent) + '%', align_left)
                worksheet.write(th, 14, orders[k].back_time_cn, align_left)
                worksheet.write(th, 15, str(
                    orders[k].real_back_money_diff_time) + u'天', align_left)
            elif t_type == 'back_invoice':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, str(
                    orders[k].client_order.back_money_percent) + '%', align_left)
                worksheet.write(th, 14, orders[k].back_time_cn, align_left)
            elif t_type == 'rebate_agent_invoice':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, orders[k].add_time_cn, align_left)
            elif t_type == 'pay_rebate_agent_invoice':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, orders[k].pay_time_cn, align_left)
            elif t_type == 'medium_invoice':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, orders[k].add_time_cn, align_left)
            elif t_type == 'pay_medium_invoice':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, orders[k].pay_time_cn, align_left)
            elif t_type == 'medium_rebate_invoice':
                worksheet.write(th, 12, orders[k].money, align_left)
                worksheet.write(th, 13, orders[k].create_time_cn, align_left)
            th += 1
        worksheet.merge_range(th, 0, th, 11, u'总计', align_center)
        if t_type == 'back_money':
            worksheet.merge_range(th, 12, th, 15, sum(
                [k.money for k in orders]), align_left)
        else:
            worksheet.merge_range(th, 12, th, 14, sum(
                [k.money for k in orders]), align_left)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (t_type, datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
