# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response, g
from werkzeug.datastructures import Headers
import xlsxwriter


def write_client_medium_excel(orders):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})

    keys = [u'区域', u'媒体供应商', u'所属媒体', u'代理/直客', u'客户', u'Campaign', u'合同金额', u'合同号', u'合同状态',
            u'执行开始', u'执行结束', u'回款日期', u'直客销售', u'渠道销售', u'直签/代理', u'媒体服务费']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
        worksheet.set_column(0, 0 + k, 15)
    th = 1
    for k in range(len(orders)):
        worksheet.write(th, 0, orders[k].locations_cn, align_left)
        worksheet.write(th, 1, orders[k].medium_group.name, align_left)
        worksheet.write(th, 2, orders[k].media.name, align_left)
        worksheet.write(th, 3, orders[k].agent.name, align_left)
        worksheet.write(th, 4, orders[k].client.name, align_left)
        worksheet.write(th, 5, orders[k].campaign, align_left)
        worksheet.write(th, 6, orders[k].money, align_left)
        worksheet.write(th, 7, orders[k].contract, align_left)
        worksheet.write(th, 8, orders[k].contract_status_cn, align_left)
        worksheet.write(th, 9, orders[k].start_date_cn, align_left)
        worksheet.write(th, 10, orders[k].end_date_cn, align_left)
        worksheet.write(th, 11, orders[k].reminde_date_cn, align_left)
        worksheet.write(th, 12, orders[k].direct_sales_names, align_left)
        worksheet.write(th, 13, orders[k].agent_sales_names, align_left)
        worksheet.write(th, 14, orders[k].sale_type_cn, align_left)
        worksheet.write(th, 15, orders[k].medium_money, align_left)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"ClienMediumtOrders", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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

    keys = [u'代理/直客(甲方全称)', u'客户合同号', u'客户名称', u'Campaign名称', u'客户合同金额(元)',
            u'执行开始', u'执行结束', u'回款日期', u'账期', u'回款比例', u'回款总金额', u'欠款金额', u'客户发票总金额',
            u'直客销售', u'渠道销售', u'区域', u'合同模板类型', u'售卖类型', u'代理/直客', u'媒体供应商', u'投放媒体',
            u'媒体订单状态', u'媒体合同号', u'售卖金额(元)', u'媒体金额(元)',
            u'是否给媒体打款', u'是否收到媒体发票',
            u'预估量(CPM)', u'实际量(CPM)', u'执行开始', u'执行结束', u'执行人员', u'豆瓣关联媒体订单',
            u'豆瓣合同号', u'Campaign名称', u'豆瓣合同金额']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
        worksheet.set_column(0, 0 + k, 15)
    th = 1
    now_date = datetime.datetime.now().date()
    for k in range(len(orders)):
        if orders[k].contract_status not in [7, 8, 9]:  # and orders[k].back_money_status != -1:
            if now_date > orders[k].reminde_date and orders[k].back_money_percent != 100:
                align_left = workbook.add_format(
                    {'align': 'left', 'valign': 'vcenter', 'border': 1, 'fg_color': 'FF8888'})
            else:
                align_left = workbook.add_format(
                    {'align': 'left', 'valign': 'vcenter', 'border': 1})
            mediums = orders[k].medium_orders
            ex_order_ids = []
            if len(mediums) > 1:
                if g.user.is_media_leader():
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
                        th, 8, th + len(orders[k].medium_orders) - 1, 8, orders[k].payable_time, align_left)

                    worksheet.merge_range(th, 9, th + len(orders[k].medium_orders) - 1, 9, str(
                        orders[k].back_money_percent) + "%", align_left)
                    worksheet.merge_range(
                        th, 10, th + len(orders[k].medium_orders) - 1, 10, orders[k].back_moneys, align_left)
                    worksheet.merge_range(th, 11, th + len(orders[k].medium_orders) - 1, 11, orders[
                                          k].money - orders[k].back_moneys, align_left)
                    worksheet.merge_range(
                        th, 12, th + len(orders[k].medium_orders) - 1, 12, orders[k].invoice_pass_sum, align_left)

                    worksheet.merge_range(
                        th, 13, th + len(orders[k].medium_orders) - 1, 13, orders[k].direct_sales_names, align_left)
                    worksheet.merge_range(
                        th, 14, th + len(orders[k].medium_orders) - 1, 14, orders[k].agent_sales_names, align_left)
                    worksheet.merge_range(
                        th, 15, th + len(orders[k].medium_orders) - 1, 15, orders[k].locations_cn, align_left)
                    worksheet.merge_range(
                        th, 16, th + len(orders[k].medium_orders) - 1, 16, orders[k].contract_type_cn, align_left)
                    worksheet.merge_range(
                        th, 17, th + len(orders[k].medium_orders) - 1, 17, orders[k].resource_type_cn, align_left)
                    worksheet.merge_range(
                        th, 18, th + len(orders[k].medium_orders) - 1, 18, orders[k].sale_type_cn, align_left)
                    for i in range(len(mediums)):
                        worksheet.write(
                            th, 19, mediums[i].medium_group.name, align_left)
                        worksheet.write(
                            th, 20, mediums[i].media.name, align_left)
                        worksheet.write(
                            th, 21, mediums[i].finish_status_cn, align_left)
                        worksheet.write(
                            th, 22, mediums[i].medium_contract, align_left)
                        worksheet.write(
                            th, 23, mediums[i].sale_money, align_left)
                        worksheet.write(
                            th, 24, mediums[i].medium_money2, align_left)
                        worksheet.write(th, 25, '', align_left)
                        worksheet.write(th, 26, '', align_left)
                        worksheet.write(
                            th, 27, mediums[i].sale_CPM, align_left)
                        worksheet.write(
                            th, 28, mediums[i].medium_CPM, align_left)
                        worksheet.write(
                            th, 29, mediums[i].start_date_cn, align_left)
                        worksheet.write(
                            th, 30, mediums[i].end_date_cn, align_left)
                        worksheet.write(
                            th, 31, mediums[i].operater_names, align_left)
                        if mediums[i].associated_douban_order:
                            worksheet.write(
                                th, 32, mediums[i].associated_douban_order.name, align_left)
                            worksheet.write(
                                th, 33, mediums[i].associated_douban_order.contract, align_left)
                            worksheet.write(
                                th, 34, mediums[i].associated_douban_order.campaign, align_left)
                            worksheet.write(
                                th, 35, mediums[i].associated_douban_order.money, align_left)
                        else:
                            worksheet.write(th, 32, '', align_left)
                            worksheet.write(th, 33, '', align_left)
                            worksheet.write(th, 34, '', align_left)
                            worksheet.write(th, 35, '', align_left)
                        th += 1
                else:
                    order_id = orders[k].id
                    for i in range(len(mediums)):
                        worksheet.write(
                            th, 0, orders[k].agent.name, align_left)
                        worksheet.write(th, 1, orders[k].contract, align_left)
                        worksheet.write(
                            th, 2, orders[k].client.name, align_left)
                        worksheet.write(th, 3, orders[k].campaign, align_left)
                        if order_id in ex_order_ids:
                            worksheet.write(th, 4, '', align_left)
                        else:
                            worksheet.write(th, 4, orders[k].money, align_left)
                        worksheet.write(
                            th, 5, orders[k].start_date_cn, align_left)
                        worksheet.write(
                            th, 6, orders[k].end_date_cn, align_left)
                        worksheet.write(
                            th, 7, orders[k].reminde_date_cn, align_left)
                        worksheet.write(
                            th, 8, orders[k].payable_time, align_left)
                        if order_id in ex_order_ids:
                            worksheet.write(th, 9, "", align_left)
                        else:
                            worksheet.write(th, 9, str(
                                orders[k].back_money_percent) + "%", align_left)
                        if order_id in ex_order_ids:
                            worksheet.write(th, 10, '', align_left)
                            worksheet.write(th, 11, '', align_left)
                            worksheet.write(th, 12, '', align_left)
                        else:
                            worksheet.write(
                                th, 10, orders[k].back_moneys, align_left)
                            worksheet.write(
                                th, 11, orders[k].money - orders[k].back_moneys, align_left)
                            worksheet.write(
                                th, 12, orders[k].invoice_pass_sum, align_left)

                        worksheet.write(
                            th, 13, orders[k].direct_sales_names, align_left)
                        worksheet.write(
                            th, 14, orders[k].agent_sales_names, align_left)
                        worksheet.write(
                            th, 15, orders[k].locations_cn, align_left)
                        worksheet.write(
                            th, 16, orders[k].contract_type_cn, align_left)
                        worksheet.write(
                            th, 17, orders[k].resource_type_cn, align_left)
                        worksheet.write(
                            th, 18, orders[k].sale_type_cn, align_left)
                        worksheet.write(
                            th, 19, mediums[i].medium_group.name, align_left)
                        worksheet.write(
                            th, 20, mediums[i].media.name, align_left)
                        worksheet.write(
                            th, 21, mediums[i].finish_status_cn, align_left)
                        worksheet.write(
                            th, 22, mediums[i].medium_contract, align_left)
                        worksheet.write(
                            th, 23, mediums[i].sale_money, align_left)
                        worksheet.write(
                            th, 24, mediums[i].medium_money2, align_left)
                        worksheet.write(th, 25, '', align_left)
                        worksheet.write(th, 26, '', align_left)
                        worksheet.write(
                            th, 27, mediums[i].sale_CPM, align_left)
                        worksheet.write(
                            th, 28, mediums[i].medium_CPM, align_left)
                        worksheet.write(
                            th, 29, mediums[i].start_date_cn, align_left)
                        worksheet.write(
                            th, 30, mediums[i].end_date_cn, align_left)
                        worksheet.write(
                            th, 31, mediums[i].operater_names, align_left)
                        if mediums[i].associated_douban_order:
                            worksheet.write(
                                th, 32, mediums[i].associated_douban_order.name, align_left)
                            worksheet.write(
                                th, 33, mediums[i].associated_douban_order.contract, align_left)
                            worksheet.write(
                                th, 34, mediums[i].associated_douban_order.campaign, align_left)
                            worksheet.write(
                                th, 35, mediums[i].associated_douban_order.money, align_left)
                        else:
                            worksheet.write(th, 32, '', align_left)
                            worksheet.write(th, 33, '', align_left)
                            worksheet.write(th, 34, '', align_left)
                            worksheet.write(th, 35, '', align_left)
                        if order_id not in ex_order_ids:
                            ex_order_ids.append(order_id)
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
                worksheet.write(th, 8, orders[k].payable_time, align_left)
                worksheet.write(th, 9, str(
                    orders[k].back_money_percent) + "%", align_left)
                worksheet.write(th, 10, orders[k].back_moneys, align_left)
                worksheet.write(
                    th, 11, orders[k].money - orders[k].back_moneys, align_left)
                worksheet.write(th, 12, orders[k].invoice_pass_sum, align_left)
                worksheet.write(
                    th, 13, orders[k].direct_sales_names, align_left)
                worksheet.write(
                    th, 14, orders[k].agent_sales_names, align_left)
                worksheet.write(th, 15, orders[k].locations_cn, align_left)
                worksheet.write(th, 16, orders[k].contract_type_cn, align_left)
                worksheet.write(th, 17, orders[k].resource_type_cn, align_left)
                worksheet.write(th, 18, orders[k].sale_type_cn, align_left)
                if orders[k].medium_orders:
                    worksheet.write(
                        th, 19, orders[k].medium_orders[0].medium_group.name, align_left)
                    worksheet.write(
                        th, 20, orders[k].medium_orders[0].media.name, align_left)
                    worksheet.write(
                        th, 21, orders[k].medium_orders[0].finish_status_cn, align_left)
                    worksheet.write(
                        th, 22, orders[k].medium_orders[0].medium_contract, align_left)
                    worksheet.write(
                        th, 23, orders[k].medium_orders[0].sale_money, align_left)
                    worksheet.write(
                        th, 24, orders[k].medium_orders[0].medium_money2, align_left)
                    worksheet.write(
                        th, 25, '', align_left)
                    worksheet.write(
                        th, 26, '', align_left)
                    worksheet.write(
                        th, 27, orders[k].medium_orders[0].sale_CPM, align_left)
                    worksheet.write(
                        th, 28, orders[k].medium_orders[0].medium_CPM, align_left)
                    worksheet.write(
                        th, 29, orders[k].medium_orders[0].start_date_cn, align_left)
                    worksheet.write(
                        th, 30, orders[k].medium_orders[0].end_date_cn, align_left)
                    worksheet.write(
                        th, 31, orders[k].medium_orders[0].operater_names, align_left)
                if orders[k].associated_douban_orders:
                    worksheet.write(
                        th, 32, orders[k].associated_douban_orders[0].name, align_left)
                    worksheet.write(
                        th, 33, orders[k].associated_douban_orders[0].contract, align_left)
                    worksheet.write(
                        th, 34, orders[k].associated_douban_orders[0].campaign, align_left)
                    worksheet.write(
                        th, 35, orders[k].associated_douban_orders[0].money, align_left)
                else:
                    worksheet.write(th, 32, '', align_left)
                    worksheet.write(th, 33, '', align_left)
                    worksheet.write(th, 34, '', align_left)
                    worksheet.write(th, 35, '', align_left)
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


def write_frameworkorder_excel(orders):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})

    keys = [u"FrameworkOrder ID", u"代理集团", u"备注",
            u"合同金额", u"合同号", u"开始日期", u"结束日期",
            u"回款日期", u"直客销售", u"渠道销售",
            u"状态"]
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
        worksheet.set_column(0, 0 + k, 15)
    th = 1
    for order in orders:
        worksheet.write(th, 0, order.id, align_left)
        worksheet.write(th, 1, order.group.name or " ", align_left)
        worksheet.write(th, 2, order.description or " ", align_left)
        worksheet.write(th, 3, order.money or 0, align_left)
        worksheet.write(th, 4, order.contract or u"无合同号", align_left)
        worksheet.write(th, 5, order.start_date_cn or " ", align_left)
        worksheet.write(th, 6, order.end_date_cn or " ", align_left)
        worksheet.write(th, 7, order.reminde_date_cn or " ", align_left)
        worksheet.write(th, 8, order.direct_sales_names or " ", align_left)
        worksheet.write(th, 9, order.agent_sales_names or " ", align_left)
        worksheet.write(th, 10, order.contract_status_cn or " ", align_left)
        th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"FOrders", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


def write_searchAd_client_excel(orders):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})

    keys = [u'代理/直客(甲方全称)', u'客户合同号', u'客户名称', u'Campaign名称', u'合同金额(元)',
            u'执行开始', u'执行结束', u'回款日期', u'回款金额', u'销售', u'区域', u'合同模板类型',
            u'推广类型', u'代理/直客', u'投放媒体', u'媒体合同号', u'客户下单金额(元)', u'给媒体/供应商下单金额(元)',
            u'是否给媒体打款', u'是否收到媒体发票',
            u'预估量(CPM)', u'实际量(CPM)', u'执行开始', u'执行结束', u'执行人员']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
        worksheet.set_column(0, 0 + k, 15)
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
                th, 8, th + len(orders[k].medium_orders) - 1, 8, orders[k].client_back_moneys, align_left)
            worksheet.merge_range(
                th, 9, th + len(orders[k].medium_orders) - 1, 9, orders[k].direct_sales_names, align_left)
            worksheet.merge_range(
                th, 10, th + len(orders[k].medium_orders) - 1, 10, orders[k].locations_cn, align_left)
            worksheet.merge_range(
                th, 11, th + len(orders[k].medium_orders) - 1, 11, orders[k].contract_type_cn, align_left)
            worksheet.merge_range(
                th, 12, th + len(orders[k].medium_orders) - 1, 12, orders[k].resource_type_cn, align_left)
            worksheet.merge_range(
                th, 13, th + len(orders[k].medium_orders) - 1, 13, orders[k].sale_type_cn, align_left)
            for i in range(len(mediums)):
                worksheet.write(th, 14, mediums[i].media.name, align_left)
                worksheet.write(th, 15, mediums[i].medium_contract, align_left)
                worksheet.write(th, 16, mediums[i].sale_money, align_left)
                worksheet.write(th, 17, mediums[i].medium_money2, align_left)
                worksheet.write(th, 18, '', align_left)
                worksheet.write(th, 19, '', align_left)
                worksheet.write(th, 20, mediums[i].sale_CPM, align_left)
                worksheet.write(th, 21, mediums[i].medium_CPM, align_left)
                worksheet.write(th, 22, mediums[i].start_date_cn, align_left)
                worksheet.write(th, 23, mediums[i].end_date_cn, align_left)
                worksheet.write(th, 24, mediums[i].operater_names, align_left)
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
            worksheet.write(th, 8, orders[k].client_back_moneys, align_left)
            worksheet.write(th, 9, orders[k].direct_sales_names, align_left)
            worksheet.write(th, 10, orders[k].locations_cn, align_left)
            worksheet.write(th, 11, orders[k].contract_type_cn, align_left)
            worksheet.write(th, 12, orders[k].resource_type_cn, align_left)
            worksheet.write(th, 13, orders[k].sale_type_cn, align_left)
            if orders[k].medium_orders:
                worksheet.write(
                    th, 14, orders[k].medium_orders[0].media.name, align_left)
                worksheet.write(
                    th, 15, orders[k].medium_orders[0].medium_contract, align_left)
                worksheet.write(
                    th, 16, orders[k].medium_orders[0].sale_money, align_left)
                worksheet.write(
                    th, 17, orders[k].medium_orders[0].medium_money2, align_left)
                worksheet.write(
                    th, 18, '', align_left)
                worksheet.write(
                    th, 19, '', align_left)
                worksheet.write(
                    th, 20, orders[k].medium_orders[0].sale_CPM, align_left)
                worksheet.write(
                    th, 21, orders[k].medium_orders[0].medium_CPM, align_left)
                worksheet.write(
                    th, 22, orders[k].medium_orders[0].start_date_cn, align_left)
                worksheet.write(
                    th, 23, orders[k].medium_orders[0].end_date_cn, align_left)
                worksheet.write(
                    th, 24, orders[k].medium_orders[0].operater_names, align_left)
            th += 1

    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"searchAdClientOrders", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
