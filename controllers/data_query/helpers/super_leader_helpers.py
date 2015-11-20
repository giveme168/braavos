# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def _write_money_in_excel(worksheet, align_center, pre_monthes, th, money):
    start = 2
    for k in range(len(money)):
        worksheet.write(th, start + k, float(money[k]), align_center)
    worksheet.write(
        th, len(pre_monthes) * 3 + 2, float(sum(money)), align_center)
    th += 1
    return th


def write_medium_money_excel(pre_monthes, douban_money,
                             youli_money, wuxian_money,
                             momo_money, zhihu_money,
                             xiachufang_money, xueqiu_money,
                             huxiu_money, kecheng_money,
                             midi_money, other_money,
                             searchAD_money, rebate_order_money,
                             total):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    # 设置宽度为30
    for k in range(0, len(pre_monthes) * 3 + 1):
        worksheet.set_column(k + 2, 2, 10)
    worksheet.set_column(1, 1, 30)
    # 设置高度
    for k in range(0, 74):
        worksheet.set_row(k, 30)

    worksheet.merge_range(0, 0, 0, 1, u'时间', align_center)
    worksheet.merge_range(1, 0, 1, 1, u'媒体项目', align_center)
    worksheet.merge_range(2, 0, 73, 0, u'致趣收入', align_center)

    locations = [u'华北', u'华东', u'华南']
    month_start, month_end = 2, 4
    location_end = 2
    for k in range(len(pre_monthes)):
        worksheet.merge_range(0, month_start, 0, month_end, str(
            pre_monthes[k]['month'].month) + u'月', align_center)
        for i in range(len(locations)):
            worksheet.write(1, location_end, locations[i], align_center)
            location_end += 1
        month_start, month_end = month_end + 1, month_end + 3
    worksheet.write(0, len(pre_monthes) * 3 + 2, u'合计', align_center)
    worksheet.write(1, len(pre_monthes) * 3 + 2, '', align_center)

    keys = [{'CCFF99': [u'豆瓣执行收入', u'豆瓣服务费收入计提', u'豆瓣返点成本', u'豆瓣毛利', '',
                        u'豆瓣收入(优力互动)', u'豆瓣媒体合同金额(优力互动)', u'豆瓣媒体净成本(优力互动)', u'豆瓣代理成本(优力互动)', u'致趣豆瓣毛利(优力互动)', '',
                        u'豆瓣收入(无线互联)', u'豆瓣媒体合同金额(无线互联)', u'豆瓣媒体净成本(无线互联)', u'豆瓣代理成本(无线互联)', u'致趣豆瓣毛利(无线互联)', '']},
            {'33CCFF': [
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
            {'AAAAAA': [
                u'其他收入', u'其他媒体执行金额', u'其他媒体净成本', u'其他代理成本', u'其他毛利', '']},
            {'FF0088': [
                u'搜索部门收入', u'搜索部门返点收入', u'搜索部门执行金额', u'搜索部门净成本', u'搜索部门代理成本', u'搜索部门毛利']}]
    th = 2
    for k in keys:
        for i in k[k.keys()[0]]:
            align_center_color = workbook.add_format(
                {'align': 'center', 'valign': 'vcenter', 'border': 1, 'fg_color': '#' + k.keys()[0]})
            if i:
                worksheet.write(th, 1, i, align_center_color)
            else:
                worksheet.merge_range(
                    th, 1, th, 2 + len(pre_monthes) * 3, '', align_center)
            th += 1

    # 重置th
    th = 2
    # 直签豆瓣
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, douban_money['ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, douban_money['in_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, douban_money['rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, douban_money['profit'])
    th += 1
    # 优利互助
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, youli_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, youli_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, youli_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, youli_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, youli_money['profit'])
    th += 1
    # 无线互联
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, wuxian_money['sale_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, wuxian_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, wuxian_money['m_ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, wuxian_money['a_rebate'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, wuxian_money['profit'])
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
        worksheet, align_center, pre_monthes, th, rebate_order_money['ex_money'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, searchAD_money['money2'])
    th = _write_money_in_excel(
        worksheet, align_center, pre_monthes, th, searchAD_money['m_ex_money'])
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
