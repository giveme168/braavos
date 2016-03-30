# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


TEAM_LOCATION_CN = {
    0: "ALL",
    1: "HuaBei",
    2: "HuaDong",
    3: "HuaNan",
}


def _insert_excel(workbook, worksheet, salers, stype, location, now_year, Q, Q_monthes, otype, th=0):
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    location_format = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'fg_color': '#FFFF77', 'border': 1})
    if not salers:
        return worksheet, th
    if stype != 'direct':
        if otype == 'douban':
            worksheet.merge_range(th, 0, th, 20, location, location_format)
        else:
            worksheet.merge_range(th, 0, th, 34, location, location_format)
    th += 1
    if stype == 'agent':
        keys = [u'渠道销售']
    else:
        keys = [u'直客销售']
    if otype == 'douban':
        keys += [u"状态", u"客户名称", u"合同号（代理下单号）", u"代理简称", u"项目名称", u"行业"] +\
            [u"直客销售", u"渠道销售", u"合同金额", u"本季度确认额", u"本季度执行额", u"上季度执行额", u"下季度执行额"] +\
            [u"%s月执行金额" % (str(k)) for k in Q_monthes] +\
            [u"类型", u"AE", u"合同开始", u"合同结束"]
        for k in range(len(keys)):
            worksheet.write(th, k, keys[k], align_left)
            worksheet.set_column(th, k, 15)
        th += 1
        for k in salers:
            medium_orders_count = 0
            for i in k['orders']:
                worksheet.write(th, 2, i['order']['client_name'], align_left)
                worksheet.write(th, 3, i['order']['contract'], align_left)
                worksheet.write(th, 4, i['order']['agent_name'], align_left)
                worksheet.write(th, 5, i['order']['campaign'], align_left)
                worksheet.write(
                    th, 6, i['order']['industry_cn'], align_left)
                worksheet.write(
                    th, 7, ','.join([u['name'] for u in i['order']['direct_sales']]), align_left)
                worksheet.write(
                    th, 8, ','.join([u['name'] for u in i['order']['agent_sales']]), align_left)
                if stype == 'agent':
                    worksheet.write(
                        th, 9, i['order']['zhixing_money'][0], align_left)
                else:
                    worksheet.write(
                        th, 9, i['order']['zhixing_money'][1], align_left)
                worksheet.write(th, 10, "", align_left)
                worksheet.write(th, 11, i['now_Q_money'], align_left)
                worksheet.write(th, 12, i['last_Q_money'], align_left)
                worksheet.write(th, 13, i['after_Q_money'], align_left)
                for m in range(len(i['moneys'])):
                    worksheet.write(th, 14 + m, i['moneys'][m], align_left)
                worksheet.write(
                    th, 17, i['order']['resource_type_cn'], align_left)
                worksheet.write(
                    th, 18, ",".join([u['name'] for u in i['order']['operater_users']]), align_left)
                worksheet.write(
                    th, 19, i['order']['client_start'].strftime('%Y/%m/%d'), align_left)
                worksheet.write(
                    th, 20, i['order']['client_end'].strftime('%Y/%m/%d'), align_left)
                th += 1
            orders_count = len(k['orders'])
            worksheet.merge_range(
                th - orders_count, 1, th - 1, 1, u'确认', align_left)
            worksheet.merge_range(
                th - orders_count, 0, th + 1, 0, k['user']['name'], align_left)
            worksheet.merge_range(th, 1, th, 8, 'Tatol', align_left)
            worksheet.write(th, 9, k['total_order_money'], align_left)
            worksheet.write(th, 10, '', align_left)
            worksheet.write(th, 11, k['total_now_Q_money'], align_left)
            worksheet.write(th, 12, k['total_last_Q_money'], align_left)
            worksheet.write(th, 13, k['total_after_Q_money'], align_left)
            worksheet.write(th, 14, k['total_frist_month_money'], align_left)
            worksheet.write(th, 15, k['total_second_month_money'], align_left)
            worksheet.write(th, 16, k['total_third_month_money'], align_left)
            worksheet.merge_range(th, 17, th, 20, '', align_left)
            th += 1
            worksheet.merge_range(th, 1, th, 2, Q + u'任务', align_left)
            worksheet.write(th, 3, '', align_left)
            worksheet.merge_range(th, 4, th, 5, u'预估完成率', align_left)
            worksheet.write(th, 6, '', align_left)
            worksheet.merge_range(th, 7, th, 20, '', align_left)
            th += 1
    else:
        keys += [u"状态", u"客户名称", u"合同号（代理下单号）", u"代理简称", u"项目名称", u"行业", u"直客销售",
                 u"渠道销售", u"合同金额", u'已开发票总金额', u"媒体总金额", u"投放媒体", u'媒体合同号', u"媒体金额"] +\
            [u"媒体%s月售卖金额" % (str(k)) for k in Q_monthes] +\
            [u"媒体%s月媒体金额" % (str(k)) for k in Q_monthes] +\
            [u"媒体%s月豆瓣金额" % (str(k)) for k in Q_monthes] +\
            [u"本季度确认额", u"本季度执行额", u"上季度执行额", u"下季度执行额"] +\
            [u"%s月执行额" % (str(k)) for k in Q_monthes] +\
            [u"类型", u"AE", u"合同开始", u"合同结束"]
        for k in range(len(keys)):
            worksheet.write(th, k, keys[k], align_left)
            worksheet.set_column(th, k, 15)
        th += 1
        for k in salers:
            medium_orders_count = 0
            for i in k['orders']:
                medium_orders = i['order']['medium_orders']
                medium_orders_count += len(medium_orders)
                if len(medium_orders) == 0:
                    medium_orders_count += 1
                medium_order_count = len(medium_orders)
                if medium_order_count == 0 or medium_order_count == 1:
                    worksheet.write(
                        th, 2, i['order']['client_name'], align_left)
                    worksheet.write(th, 3, i['order']['contract'], align_left)
                    worksheet.write(th, 4, i['order'][
                                    'agent_name'], align_left)
                    worksheet.write(th, 5, i['order']['campaign'], align_left)
                    worksheet.write(
                        th, 6, i['order']['industry_cn'], align_left)
                    worksheet.write(
                        th, 7, ','.join([u['name'] for u in i['order']['direct_sales']]), align_left)
                    worksheet.write(
                        th, 8, ','.join([u['name'] for u in i['order']['agent_sales']]), align_left)
                    if stype == 'agent':
                        worksheet.write(
                            th, 9, i['order']['zhixing_money'][0], align_left)
                        worksheet.write(
                            th, 11, i['order']['zhixing_medium_money2'][0], align_left)
                    else:
                        worksheet.write(
                            th, 9, i['order']['zhixing_money'][1], align_left)
                        worksheet.write(
                            th, 11, i['order']['zhixing_medium_money2'][1], align_left)
                    worksheet.write(
                        th, 10, i['order']['invoice_pass_sum'], align_left)
                    worksheet.write(th, 24, '', align_left)
                    worksheet.write(th, 25, i['now_Q_money'], align_left)
                    worksheet.write(th, 26, i['last_Q_money'], align_left)
                    worksheet.write(th, 27, i['after_Q_money'], align_left)
                    for m in range(len(i['moneys'])):
                        worksheet.write(th, 28 + m, i['moneys'][m], align_left)
                    worksheet.write(
                        th, 31, i['order']['resource_type_cn'], align_left)
                    worksheet.write(
                        th, 32, ",".join([u['name'] for u in i['order']['operater_users']]), align_left)
                    worksheet.write(
                        th, 33, i['order']['client_start'].strftime('%Y/%m/%d'), align_left)
                    worksheet.write(
                        th, 34, i['order']['client_end'].strftime('%Y/%m/%d'), align_left)
                else:
                    worksheet.merge_range(
                        th, 2, th + medium_order_count - 1, 2, i['order']['client_name'], align_left)
                    worksheet.merge_range(
                        th, 3, th + medium_order_count - 1, 3, i['order']['contract'], align_left)
                    worksheet.merge_range(
                        th, 4, th + medium_order_count - 1, 4, i['order']['agent_name'], align_left)
                    worksheet.merge_range(
                        th, 5, th + medium_order_count - 1, 5, i['order']['campaign'], align_left)
                    worksheet.merge_range(
                        th, 6, th + medium_order_count - 1, 6, i['order']['industry_cn'], align_left)
                    worksheet.merge_range(th, 7, th + medium_order_count - 1, 7,
                                          ','.join([u['name'] for u in i['order']['direct_sales']]), align_left)
                    worksheet.merge_range(th, 8, th + medium_order_count - 1, 8,
                                          ','.join([u['name'] for u in i['order']['agent_sales']]), align_left)
                    if stype == 'agent':
                        worksheet.merge_range(
                            th, 9, th + medium_order_count - 1, 9, i['order']['zhixing_money'][0], align_left)
                        worksheet.merge_range(
                            th, 11, th + medium_order_count - 1, 11, i['order']['zhixing_medium_money2'][0], align_left)
                    else:
                        worksheet.merge_range(
                            th, 9, th + medium_order_count - 1, 9, i['order']['zhixing_money'][1], align_left)
                        worksheet.merge_range(
                            th, 11, th + medium_order_count - 1, 11, i['order']['zhixing_medium_money2'][1], align_left)
                    worksheet.merge_range(
                        th, 10, th + medium_order_count - 1, 10, i['order']['invoice_pass_sum'], align_left)
                    worksheet.merge_range(
                        th, 24, th + medium_order_count - 1, 24, '', align_left)
                    worksheet.merge_range(
                        th, 25, th + medium_order_count - 1, 25, i['now_Q_money'], align_left)
                    worksheet.merge_range(
                        th, 26, th + medium_order_count - 1, 26, i['last_Q_money'], align_left)
                    worksheet.merge_range(
                        th, 27, th + medium_order_count - 1, 27, i['after_Q_money'], align_left)
                    for m in range(len(i['moneys'])):
                        worksheet.merge_range(
                            th, 28 + m, th + medium_order_count - 1, 28 + m, i['moneys'][m], align_left)
                    worksheet.merge_range(
                        th, 31, th + medium_order_count - 1, 31, i['order']['resource_type_cn'], align_left)
                    worksheet.merge_range(th, 32, th + medium_order_count - 1,
                                          32, ",".join([u['name'] for u in i['order']['operater_users']]), align_left)
                    worksheet.merge_range(th, 33, th + medium_order_count - 1, 33,
                                          i['order']['client_start'].strftime('%Y/%m/%d'), align_left)
                    worksheet.merge_range(th, 34, th + medium_order_count - 1, 34,
                                          i['order']['client_end'].strftime('%Y/%m/%d'), align_left)
                if medium_orders:
                    for j in range(len(medium_orders)):
                        worksheet.write(
                            th, 12, medium_orders[j]['name'], align_left)
                        worksheet.write(
                            th, 13, medium_orders[j]['contract'], align_left)
                        if stype == 'agent':
                            worksheet.write(
                                th, 14, medium_orders[j]['zhixing_medium_money2'][0], align_left)
                            for m in range(len(Q_monthes)):
                                worksheet.write(
                                    th,
                                    15 + m,
                                    medium_orders[j]['medium_money_by_month'][
                                        m][0]['sale_money'],
                                    align_left)
                            for m in range(len(Q_monthes)):
                                worksheet.write(
                                    th,
                                    18 + m,
                                    medium_orders[j]['medium_money_by_month'][
                                        m][0]['medium_money2'],
                                    align_left)
                            for m in range(len(Q_monthes)):
                                worksheet.write(
                                    th,
                                    21 + m,
                                    medium_orders[j][
                                        'associated_douban_pro_month_money'][m][0],
                                    align_left)
                        else:
                            worksheet.write(
                                th, 14, medium_orders[j]['zhixing_medium_money2'][1], align_left)
                            for m in range(len(Q_monthes)):
                                worksheet.write(
                                    th,
                                    15 + m,
                                    medium_orders[j]['medium_money_by_month'][
                                        m][1]['sale_money'],
                                    align_left)
                            for m in range(len(Q_monthes)):
                                worksheet.write(
                                    th,
                                    18 + m,
                                    medium_orders[j]['medium_money_by_month'][
                                        m][1]['medium_money2'],
                                    align_left)
                            for m in range(len(Q_monthes)):
                                worksheet.write(
                                    th,
                                    21 + m,
                                    medium_orders[j][
                                        'associated_douban_pro_month_money'][m][1],
                                    align_left)
                        th += 1
                else:
                    worksheet.write(th, 12, '', align_left)
                    worksheet.write(th, 13, '', align_left)
                    worksheet.write(
                        th, 14, '', align_left)
                    for m in range(len(Q_monthes)):
                        worksheet.write(th, 15 + m, '', align_left)
                    for m in range(len(Q_monthes)):
                        worksheet.write(th, 18 + m, '', align_left)
                    for m in range(len(Q_monthes)):
                        worksheet.write(th, 21 + m, '', align_left)
                    th += 1
            worksheet.merge_range(
                th - medium_orders_count, 1, th - 1, 1, u'确认', align_left)
            worksheet.merge_range(
                th - medium_orders_count, 0, th + 1, 0, k['user']['name'], align_left)
            worksheet.merge_range(th, 1, th, 8, 'Tatol', align_left)
            worksheet.write(th, 9, k['total_order_money'], align_left)
            worksheet.write(th, 10, k['total_order_invoice'], align_left)
            worksheet.write(
                th, 11, k['total_order_mediums_money2'], align_left)
            worksheet.write(th, 12, ' ', align_left)
            worksheet.write(th, 13, ' ', align_left)
            worksheet.write(
                th, 14, k['total_order_mediums_money2'], align_left)
            worksheet.write(
                th, 15, k['total_frist_saler_money_by_month'], align_left)
            worksheet.write(
                th, 16, k['total_second_saler_money_by_month'], align_left)
            worksheet.write(
                th, 17, k['total_third_saler_money_by_month'], align_left)
            worksheet.write(
                th, 18, k['total_frist_medium_money2_by_month'], align_left)
            worksheet.write(
                th, 19, k['total_second_medium_money2_by_month'], align_left)
            worksheet.write(
                th, 20, k['total_third_medium_money2_by_month'], align_left)
            worksheet.write(
                th, 21, k['total_frist_douban_money_by_month'], align_left)
            worksheet.write(
                th, 22, k['total_second_douban_money_by_month'], align_left)
            worksheet.write(
                th, 23, k['total_third_douban_money_by_month'], align_left)
            worksheet.write(th, 24, '', align_left)
            worksheet.write(th, 25, k['total_now_Q_money'], align_left)
            worksheet.write(th, 26, k['total_last_Q_money'], align_left)
            worksheet.write(th, 27, k['total_after_Q_money'], align_left)
            worksheet.write(th, 28, k['total_frist_month_money'], align_left)
            worksheet.write(th, 29, k['total_second_month_money'], align_left)
            worksheet.write(th, 30, k['total_third_month_money'], align_left)
            worksheet.merge_range(th, 31, th, 34, '', align_left)
            th += 1
            worksheet.merge_range(th, 1, th, 2, Q + u'任务', align_left)
            worksheet.write(th, 3, '', align_left)
            worksheet.merge_range(th, 4, th, 5, u'预估完成率', align_left)
            worksheet.write(th, 6, '', align_left)
            worksheet.merge_range(th, 7, th, 34, '', align_left)
            th += 1
    return worksheet, th


def _insert_excel_total(workbook, worksheet, orders, th, Q_monthes, otype):
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    if otype == 'douban':
        keys = [u"合同总金额", u"本季度确认金额", u"本季度执行金额", u"非本季度执行金额"] +\
            [u"%s月执行额" % (str(k)) for k in Q_monthes] + \
            [u"预估", u"类型", u"执行", u"合同开始", u"合同结束"]
        for k in range(len(keys)):
            worksheet.write(0, 9 + k, keys[k], align_left)
            worksheet.set_column(0, 9 + k, 20)
        worksheet.write(
            1, 9, sum([k['total_order_money'] for k in orders]), align_left)
        worksheet.write(1, 10, '', align_left)
        worksheet.write(
            1, 11, sum([k['total_now_Q_money'] for k in orders]), align_left)
        worksheet.write(1, 12, '', align_left)
        worksheet.write(
            1, 13, sum([k['total_frist_month_money'] for k in orders]), align_left)
        worksheet.write(
            1, 14, sum([k['total_second_month_money'] for k in orders]), align_left)
        worksheet.write(
            1, 15, sum([k['total_third_month_money'] for k in orders]), align_left)
        worksheet.write(1, 16, '', align_left)
        worksheet.write(1, 17, '', align_left)
        worksheet.write(1, 18, '', align_left)
        worksheet.write(1, 19, '', align_left)
        worksheet.write(1, 20, '', align_left)
    else:
        keys = [u"合同总金额", u"媒体金额", u"本季度确认金额", u"本季度执行金额", u"非本季度执行金额"] +\
            [u"%s月执行额" % (str(k)) for k in Q_monthes] + \
            [u"预估", u"类型", u"执行", u"合同开始", u"合同结束"]
        for k in range(len(keys)):
            worksheet.write(0, 9 + k, keys[k], align_left)
            worksheet.set_column(0, 9 + k, 20)
        worksheet.write(
            1, 9, sum([k['total_order_money'] for k in orders]), align_left)
        worksheet.write(
            1, 10, sum([k['total_order_mediums_money2'] for k in orders]), align_left)
        worksheet.write(1, 11, '', align_left)
        worksheet.write(
            1, 12, sum([k['total_now_Q_money'] for k in orders]), align_left)
        worksheet.write(1, 13, '', align_left)
        worksheet.write(
            1, 14, sum([k['total_frist_month_money'] for k in orders]), align_left)
        worksheet.write(
            1, 15, sum([k['total_second_month_money'] for k in orders]), align_left)
        worksheet.write(
            1, 16, sum([k['total_third_month_money'] for k in orders]), align_left)
        worksheet.write(1, 17, '', align_left)
        worksheet.write(1, 18, '', align_left)
        worksheet.write(1, 19, '', align_left)
        worksheet.write(1, 20, '', align_left)
        worksheet.write(1, 21, '', align_left)
    return worksheet, th


def _insert_excel_location_total(workbook, worksheet, orders, otype, th):
    if not orders:
        return worksheet, th
    red_align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1, 'bold': True, 'font_color': 'red'})
    th += 2
    if otype == 'douban':
        worksheet.write(th, 8, 'Tatol', red_align_left)
        worksheet.write(
            th, 9, sum([k['total_order_money'] for k in orders]), red_align_left)
        worksheet.write(th, 10, '', red_align_left)
        worksheet.write(
            th, 11, sum([k['total_now_Q_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 12, sum([k['total_last_Q_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 13, sum([k['total_after_Q_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 14, sum([k['total_frist_month_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 15, sum([k['total_second_month_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 16, sum([k['total_third_month_money'] for k in orders]), red_align_left)
    else:
        worksheet.write(th, 8, 'Tatol', red_align_left)
        worksheet.write(
            th, 9, sum([k['total_order_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 10, sum([k['total_order_invoice'] for k in orders]), red_align_left)
        worksheet.write(
            th, 11, sum([k['total_order_mediums_money2'] for k in orders]), red_align_left)
        worksheet.write(th, 12, '', red_align_left)
        worksheet.write(th, 13, '', red_align_left)
        worksheet.write(
            th, 14, sum([k['total_order_mediums_money2'] for k in orders]), red_align_left)
        worksheet.write(th, 15, sum(
            [k['total_frist_saler_money_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 16, sum(
            [k['total_second_saler_money_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 17, sum(
            [k['total_third_saler_money_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 18, sum(
            [k['total_frist_medium_money2_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 19, sum(
            [k['total_second_medium_money2_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 20, sum(
            [k['total_third_medium_money2_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 21, sum(
            [k['total_frist_douban_money_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 22, sum(
            [k['total_second_douban_money_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 23, sum(
            [k['total_third_douban_money_by_month'] for k in orders]), red_align_left)
        worksheet.write(th, 24, '', red_align_left)
        worksheet.write(
            th, 25, sum([k['total_now_Q_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 26, sum([k['total_last_Q_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 27, sum([k['total_after_Q_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 28, sum([k['total_frist_month_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 29, sum([k['total_second_month_money'] for k in orders]), red_align_left)
        worksheet.write(
            th, 30, sum([k['total_third_month_money'] for k in orders]), red_align_left)
    th += 2
    return worksheet, th


def write_client_excel(huabei_agent_salers_orders,
                       huabei_direct_salers_orders,
                       huanan_agent_salers_orders,
                       huanan_direct_salers_orders,
                       huadong_agent_salers_orders,
                       huadong_direct_salers_orders,
                       now_year, Q, Q_monthes, otype='client'):
    if otype == 'douban':
        filename = ("%s-%s.xls" %
                    (u"DoubanWeekly", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    else:
        filename = ("%s-%s.xls" %
                    (u"InadWeekly", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    Q_format = workbook.add_format({'align': 'left',
                                    'valign': 'vcenter',
                                    'fg_color': '#D7E4BC',
                                    'border': 1})
    worksheet.merge_range(0, 0, 1, 8, Q, Q_format)
    # 画出华北区渠道销售
    worksheet, th = _insert_excel(
        workbook, worksheet, huabei_agent_salers_orders, 'agent', u'华北区', now_year, Q, Q_monthes, otype, th=2)
    # 画出华北区直客销售
    worksheet, th = _insert_excel(
        workbook, worksheet, huabei_direct_salers_orders, 'direct', u'华北区', now_year, Q, Q_monthes, otype, th)
    huabei_orders = huabei_agent_salers_orders + huabei_direct_salers_orders
    # 画出华北区综合
    worksheet, th = _insert_excel_location_total(
        workbook, worksheet, huabei_orders, otype, th)

    # 画出华南区渠道销售
    worksheet, th = _insert_excel(
        workbook, worksheet, huanan_agent_salers_orders, 'agent', u'华南区', now_year, Q, Q_monthes, otype, th)
    # 画出华南区直客销售
    worksheet, th = _insert_excel(
        workbook, worksheet, huanan_direct_salers_orders, 'direct', u'华南区', now_year, Q, Q_monthes, otype, th)
    huanan_orders = huanan_agent_salers_orders + huanan_direct_salers_orders
    # 画出华南区综合
    worksheet, th = _insert_excel_location_total(
        workbook, worksheet, huanan_orders, otype, th)

    # 画出华东区渠道销售
    worksheet, th = _insert_excel(
        workbook, worksheet, huadong_agent_salers_orders, 'agent', u'华东区', now_year, Q, Q_monthes, otype, th)
    # 画出华南区直客销售
    worksheet, th = _insert_excel(
        workbook, worksheet, huadong_direct_salers_orders, 'direct', u'华东区', now_year, Q, Q_monthes, otype, th)
    huadong_orders = huadong_agent_salers_orders + huadong_direct_salers_orders
    # 画出华南区综合
    worksheet, th = _insert_excel_location_total(
        workbook, worksheet, huadong_orders, otype, th)

    # 画出所有合同总和
    total_orders = huabei_orders + huanan_orders + huadong_orders
    worksheet, th = _insert_excel_total(
        workbook, worksheet, total_orders, th, Q_monthes, otype)

    workbook.close()
    response.data = output.getvalue()
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


def new_insert_order_info(worksheet, align_center, order, th):
    if order:
        worksheet.write(th, 2, order['contract'], align_center)
        worksheet.write(th, 3, order['agent_name'], align_center)
        worksheet.write(th, 4, order['campaign'], align_center)
        worksheet.write(th, 5, order['industry_cn'], align_center)
        worksheet.write(th, 6, order['direct_sales_names'], align_center)
        worksheet.write(th, 7, order['agent_sales_names'], align_center)
        worksheet.write(th, 8, order['money'], align_center)
        worksheet.write(th, 9, order['medium_money2'], align_center)
        worksheet.write(th, 10, '', align_center)
        worksheet.write(th, 11, order['now_Q_money_zhixing'], align_center)
        worksheet.write(th, 12, order['last_Q_money'], align_center)
        worksheet.write(th, 13, order['after_Q_money'], align_center)
        worksheet.write(th, 14, order['first_month_money'], align_center)
        worksheet.write(th, 15, order['second_month_money'], align_center)
        worksheet.write(th, 16, order['third_month_money'], align_center)
        worksheet.write(th, 17, '', align_center)
        worksheet.write(th, 18, '', align_center)
        worksheet.write(th, 19, '', align_center)
        worksheet.write(th, 20, order['resource_type_cn'], align_center)
        worksheet.write(th, 21, order['operater_names'], align_center)
        worksheet.write(th, 22, str(order['client_start']), align_center)
        worksheet.write(th, 23, str(order['client_end']), align_center)
    else:
        worksheet.write(th, 2, '', align_center)
        worksheet.write(th, 3, '', align_center)
        worksheet.write(th, 4, '', align_center)
        worksheet.write(th, 5, '', align_center)
        worksheet.write(th, 6, '', align_center)
        worksheet.write(th, 7, '', align_center)
        worksheet.write(th, 8, '', align_center)
        worksheet.write(th, 9, '', align_center)
        worksheet.write(th, 10, '', align_center)
        worksheet.write(th, 11, '', align_center)
        worksheet.write(th, 12, '', align_center)
        worksheet.write(th, 13, '', align_center)
        worksheet.write(th, 14, '', align_center)
        worksheet.write(th, 15, '', align_center)
        worksheet.write(th, 16, '', align_center)
        worksheet.write(th, 17, '', align_center)
        worksheet.write(th, 18, '', align_center)
        worksheet.write(th, 19, '', align_center)
        worksheet.write(th, 20, '', align_center)
        worksheet.write(th, 21, '', align_center)
        worksheet.write(th, 22, '', align_center)
        worksheet.write(th, 23, '', align_center)
    return th


def new_insert_order_table(worksheet, align_center, order, th, title):
    delivered_merge_length = len(order['Delivered']) or 1
    confirmed_merge_length = len(order['Confirmed']) or 1
    merge_length = delivered_merge_length + confirmed_merge_length
    worksheet.merge_range(th, 0, th + merge_length - 1, 0, title, align_center)
    if len(order['Delivered']) > 1:
        worksheet.merge_range(th, 1,
                              th + len(order['Delivered']) - 1,
                              1, u'确认', align_center)
        for k in order['Delivered']:
            new_insert_order_info(worksheet, align_center, k, th)
            th += 1
    else:
        worksheet.write(th, 1, u'确认', align_center)
        if order['Delivered']:
            new_insert_order_info(worksheet, align_center,
                                  order['Delivered'][0], th)
        else:
            new_insert_order_info(worksheet, align_center, None, th)
        th += 1

    if len(order['Confirmed']) > 1:
        worksheet.merge_range(th + len(order['Delivered']) - 1,
                              1, th + len(order['Delivered']) +
                              len(order['Confirmed']) - 2,
                              1, u'流程中', align_center)
        for k in order['Confirmed']:
            new_insert_order_info(worksheet, align_center, k, th)
            th += 1
    else:
        worksheet.write(th, 1, u'流程中', align_center)
        if order['Confirmed']:
            new_insert_order_info(worksheet, align_center,
                                  order['Confirmed'][0], th)
        else:
            new_insert_order_info(worksheet, align_center, None, th)
        th += 1
    return th


def new_insert_total_table(worksheet, align_center, order, th, title):
    worksheet.write(th, 25, title, align_center)
    worksheet.write(th, 26, sum([k['money']
                                 for k in order['Delivered']]), align_center)
    worksheet.write(th, 27, sum([k['medium_money2']
                                 for k in order['Delivered']]), align_center)
    worksheet.write(th, 28, '', align_center)
    worksheet.write(th, 29, sum([k['now_Q_money_zhixing']
                                 for k in order['Delivered']]), align_center)
    worksheet.write(th, 30, sum([k['first_month_money']
                                 for k in order['Delivered']]), align_center)
    worksheet.write(th, 31, sum([k['second_month_money']
                                 for k in order['Delivered']]), align_center)
    worksheet.write(th, 32, sum([k['third_month_money']
                                 for k in order['Delivered']]), align_center)
    th += 1
    return th


def write_medium_index_excel(Q, now_year, Q_monthes, location_id, douban_data, youli_data,
                             wuxian_data, zhihu_data, weipiao_data, one_data, xueqiu_data,
                             huxiu_data, ledongli_data, kecheng_data, xiecheng_data, momo_data,
                             lama_data, nice_data, meijie_data, other_data, total_money,
                             total_medium_money2, total_now_Q_money_check, total_first_month_money,
                             total_second_month_money, total_third_month_money, total_now_Q_money_zhixing):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    title = [u'投放媒体', u'状态', u'合同号', u'代理名称', u'项目名称', u'行业', u'直客销售', u'渠道销售',
             u'合同金额', u'媒体金额', u'本季度确认额', u'本季度执行额', u'上季度执行额', u'下季度执行额']
    title += [str(k) + u'月执行额' for k in Q_monthes]
    title += [u'80%预估', u'50％以上预估', u'50％以下预估', u'类型', u'执行', u'开始时间', u'结束时间']
    for k in range(len(title)):
        worksheet.write(0, 0 + k, title[k], align_center)
    # 设置宽度
    for k in range(33):
        worksheet.set_column(k, 0, 20)
    # 根据媒体展示详情
    th = 1
    th = new_insert_order_table(
        worksheet, align_center, douban_data, th, u'豆瓣')
    th = new_insert_order_table(
        worksheet, align_center, youli_data, th, u'优力互动')
    th = new_insert_order_table(
        worksheet, align_center, wuxian_data, th, u'无线互联')
    th = new_insert_order_table(worksheet, align_center, zhihu_data, th, u'知乎')
    th = new_insert_order_table(
        worksheet, align_center, weipiao_data, th, u'微票儿')
    th = new_insert_order_table(worksheet, align_center, one_data, th, u'ONE')
    th = new_insert_order_table(
        worksheet, align_center, xueqiu_data, th, u'雪球')
    th = new_insert_order_table(worksheet, align_center, huxiu_data, th, u'虎嗅')
    th = new_insert_order_table(
        worksheet, align_center, ledongli_data, th, u'乐动力')
    th = new_insert_order_table(
        worksheet, align_center, kecheng_data, th, u'课程格子')
    th = new_insert_order_table(
        worksheet, align_center, xiecheng_data, th, u'携程')
    th = new_insert_order_table(worksheet, align_center, momo_data, th, u'陌陌')
    th = new_insert_order_table(worksheet, align_center, lama_data, th, u'辣妈帮')
    th = new_insert_order_table(
        worksheet, align_center, nice_data, th, u'nice')
    th = new_insert_order_table(
        worksheet, align_center, other_data, th, u'其他媒体')
    th = new_insert_order_table(
        worksheet, align_center, meijie_data, th, u'媒介下单')

    # 展示总计信息
    total_title = [u"投放媒体", u'合同金额', u"媒体金额", u"本季度确认额", u"本季度执行额"]
    total_title += [str(k) + u'月执行额' for k in Q_monthes]
    for k in range(len(total_title)):
        worksheet.write(0, 25 + k, total_title[k], align_center)
    th = 1
    th = new_insert_total_table(
        worksheet, align_center, douban_data, th, u'豆瓣')
    th = new_insert_total_table(
        worksheet, align_center, youli_data, th, u'优力互动')
    th = new_insert_total_table(
        worksheet, align_center, wuxian_data, th, u'无线互联')
    th = new_insert_total_table(worksheet, align_center, zhihu_data, th, u'知乎')
    th = new_insert_total_table(
        worksheet, align_center, weipiao_data, th, u'微票儿')
    th = new_insert_total_table(worksheet, align_center, one_data, th, u'ONE')
    th = new_insert_total_table(
        worksheet, align_center, xueqiu_data, th, u'雪球')
    th = new_insert_total_table(worksheet, align_center, huxiu_data, th, u'虎嗅')
    th = new_insert_total_table(
        worksheet, align_center, ledongli_data, th, u'乐动力')
    th = new_insert_total_table(
        worksheet, align_center, kecheng_data, th, u'课程格子')
    th = new_insert_total_table(
        worksheet, align_center, xiecheng_data, th, u'携程')
    th = new_insert_total_table(worksheet, align_center, momo_data, th, u'陌陌')
    th = new_insert_total_table(worksheet, align_center, lama_data, th, u'辣妈帮')
    th = new_insert_total_table(
        worksheet, align_center, nice_data, th, u'nice')
    th = new_insert_total_table(
        worksheet, align_center, other_data, th, u'其他媒体')
    th = new_insert_total_table(
        worksheet, align_center, meijie_data, th, u'媒介下单')

    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s-%s-%s.xls" % (u"MediumWeekly",
                                     str(now_year), str(Q),
                                     TEAM_LOCATION_CN[location_id]))
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
