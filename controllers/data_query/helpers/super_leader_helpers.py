# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response, g
from werkzeug.datastructures import Headers
import xlsxwriter


def _write_money_in_excel(worksheet, align_center, pre_monthes, th, money):
    start = 2
    for k in range(len(money)):
        worksheet.write(th, start + k, float(money[k]), align_center)
    worksheet.write(
        th, len(pre_monthes) * 4 + 2, float(sum(money)), align_center)
    th += 1
    return th


# 导出媒体清单
def write_medium_money_excel(pre_monthes, douban_money,
                             youli_money, wuxian_money,
                             momo_money, zhihu_money,
                             xiachufang_money, xueqiu_money,
                             huxiu_money, kecheng_money,
                             weipiao_money, one_money,
                             midi_money, other_money,
                             searchAD_money, rebate_order_money,
                             total, up_money, year):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    # 设置宽度为30
    for k in range(0, len(pre_monthes) * 4 + 1):
        worksheet.set_column(k + 2, 2, 10)
    worksheet.set_column(1, 1, 30)
    # 设置高度
    for k in range(0, 76 + len(up_money) * 6):
        worksheet.set_row(k, 30)

    worksheet.merge_range(0, 0, 0, 1, u'时间', align_center)
    worksheet.merge_range(1, 0, 1, 1, u'媒体项目', align_center)
    worksheet.merge_range(2, 0, 76 + len(up_money) *
                          6, 0, u'致趣收入', align_center)

    locations = [u'媒介', u'华北', u'华东', u'华南']
    month_start, month_end = 2, 5
    location_end = 2
    for k in range(len(pre_monthes)):
        worksheet.merge_range(0, month_start, 0, month_end, str(
            pre_monthes[k]['month'].month) + u'月', align_center)
        for i in range(len(locations)):
            worksheet.write(1, location_end, locations[i], align_center)
            location_end += 1
        month_start, month_end = month_end + 1, month_end + 4
    worksheet.write(0, len(pre_monthes) * 4 + 2, u'合计', align_center)
    worksheet.write(1, len(pre_monthes) * 4 + 2, '', align_center)
    if g.user.is_aduit() and str(year) == '2014':
        keys = []
    else:
        keys = [{'CCFF99': [u'豆瓣执行收入', u'豆瓣服务费收入计提', u'豆瓣返点成本', u'豆瓣毛利', '']}]
    keys += [{'33CCFF': [
        u'陌陌收入', u'陌陌媒体执行金额', u'陌陌媒体净成本', u'陌陌代理成本', u'陌陌毛利', '']},
        {'0066FF': [
            u'知乎收入', u'知乎媒体执行金额', u'知乎媒体净成本', u'知乎代理成本', u'知乎毛利', '']},
        {'AA7700': [
            u'下厨房收入', u'下厨房媒体执行金额', u'下厨房媒体净成本', u'下厨房代理成本', u'下厨房毛利', '']},
        {'007799': [
            u'雪球收入', u'雪球媒体执行金额', u'雪球媒体净成本', u'雪球代理成本', u'雪球毛利', '']},
        {'9F88FF': [
            u'虎嗅收入', u'虎嗅媒体执行金额', u'虎嗅媒体净成本', u'虎嗅代理成本', u'虎嗅毛利', '']},
        {'FF8888': [
            u'课程格子收入', u'课程格子媒体执行金额', u'课程格子媒体净成本', u'课程格子代理成本', u'课程格子毛利', '']},
        {'FFBB00': [
            u'迷笛收入', u'迷笛媒体执行金额', u'迷笛媒体净成本', u'迷笛代理成本', u'迷笛毛利', '']},
        {'FF3333': [
            u'微票收入', u'微票媒体执行金额', u'微票媒体净成本', u'微票代理成本', u'微票毛利', '']},
        {'E93EFF': [
            u'ONE收入', u'One媒体执行金额', u'One媒体净成本', u'One代理成本', u'One毛利', '']}]
    for k, v in up_money.items():
        keys.append({'FF7F50': [k + u'收入', k + u'媒体执行金额',
                                k + u'媒体净成本', k + u'代理成本', k + u'毛利', '']})
    keys += [{'AAAAAA': [u'其他收入', u'其他媒体执行金额', u'其他媒体净成本', u'其他代理成本', u'其他毛利', '']},
             {'FF0088': [u'效果业务收入', u'效果业务返点收入', u'效果业务执行金额', u'效果业务代理成本', u'效果业务毛利']}]
    th = 2
    for k in keys:
        for i in k[k.keys()[0]]:
            align_center_color = workbook.add_format(
                {'align': 'center', 'valign': 'vcenter', 'border': 1, 'fg_color': '#' + k.keys()[0]})
            if i:
                worksheet.write(th, 1, i, align_center_color)
            else:
                worksheet.merge_range(
                    th, 1, th, 2 + len(pre_monthes) * 4, '', align_center)
            th += 1

    # 重置th
    th = 2
    if g.user.is_aduit() and str(year) == '2014':
        pass
    else:
        # 直签豆瓣
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, douban_money['sale_money'])
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, douban_money['money2'])
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, douban_money['a_rebate'])
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, douban_money['profit'])
        th += 1
    # 陌陌
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, momo_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, momo_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, momo_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, momo_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, momo_money['profit'])
    th += 1
    # 知乎
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, zhihu_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, zhihu_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, zhihu_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, zhihu_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, zhihu_money['profit'])
    th += 1
    # 下厨房
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xiachufang_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xiachufang_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xiachufang_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xiachufang_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xiachufang_money['profit'])
    th += 1
    # 雪球
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xueqiu_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xueqiu_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xueqiu_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xueqiu_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, xueqiu_money['profit'])
    th += 1
    # 虎嗅
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, huxiu_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, huxiu_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, huxiu_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, huxiu_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, huxiu_money['profit'])
    th += 1
    # 课程格子
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, kecheng_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, kecheng_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, kecheng_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, kecheng_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, kecheng_money['profit'])
    th += 1
    # 迷笛
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, midi_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, midi_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, midi_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, midi_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, midi_money['profit'])
    th += 1
    # 微票
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, weipiao_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, weipiao_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, weipiao_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, weipiao_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, weipiao_money['profit'])
    th += 1
    # One
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, one_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, one_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, one_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, one_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, one_money['profit'])
    th += 1

    # 大于100W的媒体
    for k, v in up_money.items():
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, v['sale_money'])
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, v['money2'])
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, v['m_ex_money'])
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, v['a_rebate'])
        th = _write_money_in_excel(
            worksheet, align_center, pre_monthes, th, v['profit'])
        th += 1

    # 其他
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, other_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, other_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, other_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, other_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, other_money['profit'])
    th += 1
    # 搜索部门
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, searchAD_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, rebate_order_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, searchAD_money['money2'])
    # th = _write_money_in_excel(
    # worksheet, align_center, pre_monthes, th, searchAD_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, searchAD_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, searchAD_money['profit'])
    # 合计
    worksheet.write(th, 1, u'合计', align_center)
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, total)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                ("媒体清单", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


COLUMN_LIST = ['A', 'B', 'C', 'D', 'E']


# 导出可视化报表折线图
def write_line_excel(obj):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': 1})

    # Add the worksheet data that the charts will refer to.
    headings = obj['headings']
    data = obj['data']

    worksheet.write_row('A1', headings, bold)
    '''
    worksheet.write_column('A2', data[0])
    worksheet.write_column('B2', data[1])
    worksheet.write_column('C2', data[2])
    worksheet.write_column('D2', data[3])
    '''
    # Create a new chart object. In this case an embedded chart.
    chart = workbook.add_chart({'type': 'line'})

    # 循环插入每条线，并减去第一组数据（第一组数据为月份的显示）
    for k in range(len(obj['data'])):
        worksheet.write_column(COLUMN_LIST[k] + '2', data[k])
        if k >= 1:
            worksheet.set_column(k, k, 25)
            chart.add_series({
                'name': ['Sheet1', 0, k],
                'categories': ['Sheet1', 1, 0, len(data[0]), 0],
                'values': ['Sheet1', 1, k, len(data[k]), k],
            })
    # Add a chart title and some axis labels.
    chart.set_title({'name': obj['title']})
    # chart.set_x_axis({'name': 'Test number'})
    # chart.set_y_axis({'name': 'Sample length (mm)'})

    # Set an Excel chart style. Colors with white outline and shadow.
    chart.set_style(10)

    # Insert the chart into the worksheet (with an offset).
    chart.set_size({'width': 600, 'height': 400})
    worksheet.insert_chart('E2', chart, {'x_offset': 40, 'y_offset': 10})

    workbook.close()

    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (str(obj['title']), datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


# 导出可视化报表饼图
def write_pie_excel(obj):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    worksheet.set_column(1, 1, 30)
    worksheet.set_column(2, 2, 15)
    worksheet.set_column(3, 3, 10)
    bold = workbook.add_format({'bold': 1})

    # Add the worksheet data that the charts will refer to.
    headings = obj['headings']
    data = obj['data']

    worksheet.write_row('A1', headings, bold)
    worksheet.write_column('A2', data[0])
    worksheet.write_column('B2', data[1])
    worksheet.write_column('C2', data[2])
    worksheet.write_column('D2', data[3])

    #######################################################################
    #
    # Create a new chart object.
    #
    chart = workbook.add_chart({'type': 'pie'})

    # Configure the series. Note the use of the list syntax to define ranges:
    chart.add_series({
        'name': u'占比',
        'categories': ['Sheet1', 1, 1, len(data[1]), 1],
        'values': ['Sheet1', 1, 2, len(data[3]), 2],
    })

    # Add a title.
    chart.set_title({'name': obj['title']})

    # Set an Excel chart style. Colors with white outline and shadow.
    chart.set_style(10)

    # Insert the chart into the worksheet (with an offset).
    chart.set_size({'width': 700, 'height': 500})
    worksheet.insert_chart('E2', chart, {'x_offset': 25, 'y_offset': 10})
    workbook.close()

    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (str(obj['title']), datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


# 导出代理总表
def write_agent_total_excel(year, agent_obj, total_is_sale_money, total_is_medium_money):
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
    keys = [u'代理集团', u'代理', u'合同号', 'campaign', u'销售金额', u'媒介金额']
    for k in range(len(keys)):
        worksheet.set_column(k, 0, 30)
        worksheet.write(0, k, keys[k], align_center)
    th = 1
    for k in agent_obj:
        agents = k['agents']
        if k['excel_order_count'] == 1:
            worksheet.write(th, 0, k['name'], align_left)
        else:
            worksheet.merge_range(th, 0, th + k['excel_order_count'] - 1, 0, k['name'], align_left)
        for a in agents:
            if a['orders']:
                if len(a['orders']) == 1:
                    worksheet.write(th, 1, a['name'], align_left)
                else:
                    worksheet.merge_range(th, 1, th + a['html_order_count'] - 1, 1, a['name'], align_left)
                for o in a['orders']:
                    worksheet.write(th, 2, o['contract'] or u'无合同号', align_left)
                    worksheet.write(th, 3, o['campaign'], align_left)
                    worksheet.write(th, 4, o['is_sale_money'], money_align_left)
                    worksheet.write(th, 5, o['is_medium_money'], money_align_left)
                    th += 1
    worksheet.merge_range(th, 0, th, 3, u'总计', align_center)
    worksheet.write(th, 4, total_is_sale_money, money_align_left)
    worksheet.write(th, 5, total_is_medium_money, money_align_left)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" % ('代理总表', str(year)))
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


# 导出客户总表
def write_client_total_excel(year, HB_data, HD_data, HN_data, type):
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
    keys = [u'区域', u'行业', u'客户', '代理', u'Q1', u'Q2', u'Q3', u'Q4']
    for k in range(len(keys)):
        worksheet.set_column(k, 0, 30)
        worksheet.write(0, k, keys[k], align_center)
    th = 1
    count = sum([k['excel_order_count'] for k in HB_data['location_data']])
    if count > 1:
        worksheet.merge_range(th, 0, th + count - 1, 0, u'华北', align_left)
    else:
        worksheet.write(th, 0, u'华北', align_left)
        th += 1
    for k in HB_data['location_data']:
        agents = k['clients']
        if k['excel_order_count'] == 1:
            worksheet.write(th, 1, k['name'], align_left)
        else:
            worksheet.merge_range(th, 1, th + k['excel_order_count'] - 1, 1, k['name'], align_left)
        for a in agents:
            if a['orders']:
                if len(a['orders']) == 1:
                    worksheet.write(th, 2, a['name'], align_left)
                else:
                    worksheet.merge_range(th, 2, th + a['html_order_count'] - 1, 2, a['name'], align_left)
                for o in a['orders']:
                    worksheet.write(th, 3, o['agent_name'], align_left)
                    worksheet.write(th, 4, o['Q1_money'], money_align_left)
                    worksheet.write(th, 5, o['Q2_money'], money_align_left)
                    worksheet.write(th, 6, o['Q3_money'], money_align_left)
                    worksheet.write(th, 7, o['Q4_money'], money_align_left)
                    th += 1
    # 总计
    worksheet.merge_range(th, 0, th, 3, '总计', align_center)
    worksheet.write(th, 4, HB_data['total_Q1_money'], money_align_left)
    worksheet.write(th, 5, HB_data['total_Q2_money'], money_align_left)
    worksheet.write(th, 6, HB_data['total_Q3_money'], money_align_left)
    worksheet.write(th, 7, HB_data['total_Q4_money'], money_align_left)
    th += 1
    count = sum([k['excel_order_count'] for k in HD_data['location_data']])
    if count > 1:
        worksheet.merge_range(th, 0, th + count - 1, 0, u'华东', align_left)
    else:
        worksheet.write(th, 0, u'华东', align_left)
        th += 1
    for k in HD_data['location_data']:
        agents = k['clients']
        if k['excel_order_count'] == 1:
            worksheet.write(th, 1, k['name'], align_left)
        else:
            worksheet.merge_range(th, 1, th + k['excel_order_count'] - 1, 1, k['name'], align_left)
        for a in agents:
            if a['orders']:
                if len(a['orders']) == 1:
                    worksheet.write(th, 2, a['name'], align_left)
                else:
                    worksheet.merge_range(th, 2, th + a['html_order_count'] - 1, 2, a['name'], align_left)
                for o in a['orders']:
                    worksheet.write(th, 3, o['agent_name'], align_left)
                    worksheet.write(th, 4, o['Q1_money'], money_align_left)
                    worksheet.write(th, 5, o['Q2_money'], money_align_left)
                    worksheet.write(th, 6, o['Q3_money'], money_align_left)
                    worksheet.write(th, 7, o['Q4_money'], money_align_left)
                    th += 1
    # 总计
    worksheet.merge_range(th, 0, th, 3, '总计', align_center)
    worksheet.write(th, 4, HD_data['total_Q1_money'], money_align_left)
    worksheet.write(th, 5, HD_data['total_Q2_money'], money_align_left)
    worksheet.write(th, 6, HD_data['total_Q3_money'], money_align_left)
    worksheet.write(th, 7, HD_data['total_Q4_money'], money_align_left)
    th += 1
    count = sum([k['excel_order_count'] for k in HN_data['location_data']])
    if count > 1:
        worksheet.merge_range(th, 0, th + count - 1, 0, u'华南', align_left)
    else:
        worksheet.write(th, 0, u'华南', align_left)
        th += 1
    for k in HN_data['location_data']:
        agents = k['clients']
        if k['excel_order_count'] == 1:
            worksheet.write(th, 1, k['name'], align_left)
        else:
            worksheet.merge_range(th, 1, th + k['excel_order_count'] - 1, 1, k['name'], align_left)
        for a in agents:
            if a['orders']:
                if len(a['orders']) == 1:
                    worksheet.write(th, 2, a['name'], align_left)
                else:
                    worksheet.merge_range(th, 2, th + a['html_order_count'] - 1, 2, a['name'], align_left)
                for o in a['orders']:
                    worksheet.write(th, 3, o['agent_name'], align_left)
                    worksheet.write(th, 4, o['Q1_money'], money_align_left)
                    worksheet.write(th, 5, o['Q2_money'], money_align_left)
                    worksheet.write(th, 6, o['Q3_money'], money_align_left)
                    worksheet.write(th, 7, o['Q4_money'], money_align_left)
                    th += 1
    # 总计
    worksheet.merge_range(th, 0, th, 3, '总计', align_center)
    worksheet.write(th, 4, HN_data['total_Q1_money'], money_align_left)
    worksheet.write(th, 5, HN_data['total_Q2_money'], money_align_left)
    worksheet.write(th, 6, HN_data['total_Q3_money'], money_align_left)
    worksheet.write(th, 7, HN_data['total_Q4_money'], money_align_left)
    th += 1
    # 总计
    worksheet.merge_range(th, 0, th, 3, '三区总计', align_center)
    worksheet.write(th, 4, HB_data['total_Q1_money'] + HD_data['total_Q1_money'] +
                    HN_data['total_Q1_money'], money_align_left)
    worksheet.write(th, 5, HB_data['total_Q2_money'] + HD_data['total_Q2_money'] +
                    HN_data['total_Q2_money'], money_align_left)
    worksheet.write(th, 6, HB_data['total_Q3_money'] + HD_data['total_Q3_money'] +
                    HN_data['total_Q3_money'], money_align_left)
    worksheet.write(th, 7, HB_data['total_Q4_money'] + HD_data['total_Q4_money'] +
                    HN_data['total_Q4_money'], money_align_left)
    workbook.close()
    response.data = output.getvalue()
    if type == "douban":
        filename = ("%s-%s.xls" % ('豆瓣客户总表', str(year)))
    else:
        filename = ("%s-%s.xls" % ('新媒体客户总表', str(year)))
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
