# -*- coding: UTF-8 -*-
# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime
import xlwt
import xlsxwriter

from flask import Response, g
from werkzeug.datastructures import Headers


############################################
# 根据开始时间、结束时间，返回相应的月份及天数
############################################
def get_monthes_pre_days(pre_month, start, end):
    pre_month_days_list = []
    count = 0
    while True:
        targetmonth = count + pre_month.month
        try:
            p_month_date = pre_month.replace(
                year=pre_month.year + int(targetmonth / 12), month=(targetmonth % 12))
        except:
            p_month_date = pre_month.replace(year=pre_month.year + int((targetmonth + 1) / 12),
                                             month=((targetmonth + 1) % 12), day=1)
            p_month_date += datetime.timedelta(days=-1)
        if start.replace(day=1) <= p_month_date:
            month_last_day = get_month_last_date(p_month_date)
            if start.replace(day=1) == end.replace(day=1):
                days = (end - start).days + 1
            else:
                if start.replace(day=1) == p_month_date:
                    days = (month_last_day - start).days + 1
                elif end <= month_last_day:
                    days = end.day
                elif start.replace(day=1) < p_month_date:
                    days = month_last_day.day
            pre_month_days_list.append({'month': p_month_date, 'days': days})
        if end.strftime('%Y-%m') == p_month_date.strftime('%Y-%m'):
            break
        count += 1
    return pre_month_days_list


######################
# 获取本月的最后一天
######################
def get_month_last_date(date_time):
    y = date_time.year
    m = date_time.month
    if m == 12:
        month_end_dt = datetime.date(y + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        month_end_dt = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
    return datetime.datetime.strptime(month_end_dt.isoformat(), '%Y-%m-%d')


def write_excel(orders, type, th_obj):
    xls = xlwt.Workbook(encoding='utf-8')
    sheet = xls.add_sheet("Sheet")
    if type == 1:  # 客户订单
        keys = [u'代理/直客', u'客户', 'Campaign', u'总金额', u'开始', u'结束']
    elif type == 2:  # 媒体订单
        keys = [u'投放媒体', 'Campaign', u'总金额', u'开始', u'结束']
    elif type == 3:  # 关联豆瓣订单
        keys = [u'甲方', u'客户', 'Campaign', u'总金额', u'开始', u'结束']
    else:  # 直签豆瓣订单
        keys = [u'代理/直客', u'客户', 'Campaign', u'总金额', u'开始', u'结束']
    keys += [k['month'] for k in th_obj]
    for k in range(len(keys)):
        sheet.write(0, k, keys[k])
    for k in range(len(orders)):
        order_pre_money = orders[k]['order_pre_money']
        if type == 1:  # 客户订单
            sheet.write(k + 1, 0, orders[k]['agent_name'])
            sheet.write(k + 1, 1, orders[k]['client_name'])
            sheet.write(k + 1, 2, orders[k]['campaign'])
            sheet.write(k + 1, 3, orders[k]['money'])
            sheet.write(k + 1, 4, str(orders[k]['start']))
            sheet.write(k + 1, 5, str(orders[k]['end']))
            for m in range(len(order_pre_money)):
                sheet.write(k + 1, 5 + m + 1, order_pre_money[m]['money'])
        elif type == 2:  # 媒体订单
            sheet.write(k + 1, 0, orders[k]['medium_name'])
            sheet.write(k + 1, 1, orders[k]['campaign'])
            sheet.write(k + 1, 2, orders[k]['money'])
            sheet.write(k + 1, 3, str(orders[k]['start']))
            sheet.write(k + 1, 4, str(orders[k]['end']))
            for m in range(len(order_pre_money)):
                sheet.write(k + 1, 4 + m + 1, order_pre_money[m]['money'])
        elif type == 3:  # 关联豆瓣订单
            sheet.write(k + 1, 0, orders[k]['jiafang_name'])
            sheet.write(k + 1, 1, orders[k]['client_name'])
            sheet.write(k + 1, 2, orders[k]['campaign'])
            sheet.write(k + 1, 3, orders[k]['money'])
            sheet.write(k + 1, 4, str(orders[k]['start']))
            sheet.write(k + 1, 5, str(orders[k]['end']))
            for m in range(len(order_pre_money)):
                sheet.write(k + 1, 5 + m + 1, order_pre_money[m]['money'])
        else:  # 直签豆瓣订单
            sheet.write(k + 1, 0, orders[k]['agent_name'])
            sheet.write(k + 1, 1, orders[k]['client_name'])
            sheet.write(k + 1, 2, orders[k]['campaign'])
            sheet.write(k + 1, 3, orders[k]['money'])
            sheet.write(k + 1, 4, str(orders[k]['start']))
            sheet.write(k + 1, 5, str(orders[k]['end']))
            for m in range(len(order_pre_money)):
                sheet.write(k + 1, 5 + m + 1, order_pre_money[m]['money'])
    return xls


def write_order_excel(orders):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'代理/直客', u'客户', u'Campaign', u'直客销售', u'渠道销售', u'区域', u'合同号',
            u'执行开始时间', u'执行结束时间', u'客户合同金额', u'已开客户发票金额',
            u'客户回款金额', u'客户付返点发票金额', u'已开客户返点发票金额', u'已打款客户返点金额',
            u'媒体名称', u'媒体合同金额', u'已收媒体发票金额', u'付款给媒体金额', u'已开媒体返点发票金额']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_center)
    # 设置宽度为30
    worksheet.set_column(len(keys), 0, 20)

    th = 1
    for k in range(len(orders)):
        mediums = orders[k].medium_orders
        medium_count = len(mediums)
        # 媒介导出报表时要拆分(多媒体合同时要拆分成一条一条，不需要合并)
        if g.user.is_media_leader():
            for i in range(len(mediums)):
                worksheet.set_row(th, 30)    # 设置高度
                worksheet.write(th, 0, orders[k].agent.name, align_left)
                worksheet.write(th, 1, orders[k].client.name, align_left)
                worksheet.write(th, 2, orders[k].campaign, align_left)
                worksheet.write(
                    th, 3, orders[k].direct_sales_names, align_left)
                worksheet.write(th, 4, orders[k].agent_sales_names, align_left)
                worksheet.write(th, 5, orders[k].locations_cn, align_left)
                worksheet.write(th, 6, orders[k].contract, align_left)
                worksheet.write(th, 7, orders[k].start_date_cn, align_left)
                worksheet.write(th, 8, orders[k].end_date_cn, align_left)
                worksheet.write(th, 9, orders[k].money, align_left)
                worksheet.write(th, 10, orders[k].pass_invoice_sum, align_left)
                worksheet.write(th, 11, orders[k].back_money_sum, align_left)
                worksheet.write(
                    th, 12, orders[k].back_money_rebate_sum, align_left)
                worksheet.write(
                    th, 13, orders[k].agent_invoice_sum, align_left)
                worksheet.write(
                    th, 14, orders[k].agent_invoice_pay_sum, align_left)
                worksheet.write(th, 15, mediums[i].medium.name, align_left)
                worksheet.write(th, 16, mediums[i].medium_money2, align_left)
                worksheet.write(
                    th, 17, mediums[i].medium_invoice_sum, align_left)
                worksheet.write(
                    th, 18, mediums[i].medium_invoice_pay_sum, align_left)
                worksheet.write(
                    th, 19, mediums[i].medium_invoice_rebate_invoice_sum, align_left)
                th += 1
        else:
            if medium_count == 1:
                worksheet.set_row(th, 30)    # 设置高度
                worksheet.write(th, 0, orders[k].agent.name, align_left)
                worksheet.write(th, 1, orders[k].client.name, align_left)
                worksheet.write(th, 2, orders[k].campaign, align_left)
                worksheet.write(
                    th, 3, orders[k].direct_sales_names, align_left)
                worksheet.write(th, 4, orders[k].agent_sales_names, align_left)
                worksheet.write(th, 5, orders[k].locations_cn, align_left)
                worksheet.write(th, 6, orders[k].contract, align_left)
                worksheet.write(th, 7, orders[k].start_date_cn, align_left)
                worksheet.write(th, 8, orders[k].end_date_cn, align_left)
                worksheet.write(th, 9, orders[k].money, align_left)
                worksheet.write(th, 10, orders[k].pass_invoice_sum, align_left)
                worksheet.write(th, 11, orders[k].back_money_sum, align_left)
                worksheet.write(
                    th, 12, orders[k].back_money_rebate_sum, align_left)
                worksheet.write(
                    th, 13, orders[k].agent_invoice_sum, align_left)
                worksheet.write(
                    th, 14, orders[k].agent_invoice_pay_sum, align_left)
                worksheet.write(th, 15, mediums[0].medium.name, align_left)
                worksheet.write(th, 16, mediums[0].medium_money2, align_left)
                worksheet.write(
                    th, 17, mediums[0].medium_invoice_sum, align_left)
                worksheet.write(
                    th, 18, mediums[0].medium_invoice_pay_sum, align_left)
                worksheet.write(
                    th, 19, mediums[0].medium_invoice_rebate_invoice_sum, align_left)
                th += 1
            else:
                worksheet.set_row(th, 30)    # 设置高度
                worksheet.merge_range(
                    th, 0, th + medium_count - 1, 0, orders[k].agent.name, align_left)
                worksheet.merge_range(
                    th, 1, th + medium_count - 1, 1, orders[k].client.name, align_left)
                worksheet.merge_range(
                    th, 2, th + medium_count - 1, 2, orders[k].campaign, align_left)
                worksheet.merge_range(
                    th, 3, th + medium_count - 1, 3, orders[k].direct_sales_names, align_left)
                worksheet.merge_range(
                    th, 4, th + medium_count - 1, 4, orders[k].agent_sales_names, align_left)
                worksheet.merge_range(
                    th, 5, th + medium_count - 1, 5, orders[k].locations_cn, align_left)
                worksheet.merge_range(
                    th, 6, th + medium_count - 1, 6, orders[k].contract, align_left)
                worksheet.merge_range(
                    th, 7, th + medium_count - 1, 7, orders[k].start_date_cn, align_left)
                worksheet.merge_range(
                    th, 8, th + medium_count - 1, 8, orders[k].end_date_cn, align_left)
                worksheet.merge_range(
                    th, 9, th + medium_count - 1, 9, orders[k].money, align_left)
                worksheet.merge_range(
                    th, 10, th + medium_count - 1, 10, orders[k].pass_invoice_sum, align_left)
                worksheet.merge_range(
                    th, 11, th + medium_count - 1, 11, orders[k].back_money_sum, align_left)
                worksheet.merge_range(
                    th, 12, th + medium_count - 1, 12, orders[k].back_money_rebate_sum, align_left)
                worksheet.merge_range(
                    th, 13, th + medium_count - 1, 13, orders[k].agent_invoice_sum, align_left)
                worksheet.merge_range(
                    th, 14, th + medium_count - 1, 14, orders[k].agent_invoice_pay_sum, align_left)
                for i in range(len(mediums)):
                    worksheet.set_row(th, 30)    # 设置高度
                    worksheet.write(
                        th, 15, mediums[i].name, align_left)
                    worksheet.write(
                        th, 16, mediums[i].medium_money2, align_left)
                    worksheet.write(
                        th, 17, mediums[i].medium_invoice_sum, align_left)
                    worksheet.write(
                        th, 18, mediums[i].medium_invoice_pay_sum, align_left)
                    worksheet.write(
                        th, 19, mediums[i].medium_invoice_rebate_invoice_sum, align_left)
                    th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (u"Cost", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
