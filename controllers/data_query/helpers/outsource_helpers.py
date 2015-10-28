# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_outsource_excel(monthes, data):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    worksheet.merge_range(0, 0, 1, 1, u'收支项目', align_left)

    for k in range(len(monthes)):
        if k == 0:
            start_td, end_td = 2, 4
        worksheet.merge_range(
            0, start_td, 0, end_td, monthes[k] + u'月', align_left)
        start_td += 3
        end_td += 3
    locations = [u'华东', u'华北', u'华南'] * 3
    for k in range(len(locations)):
        worksheet.write(1, 2 + k, locations[k], align_left)
    worksheet.merge_range(2, 0, 10, 0, u'外包项目', align_left)
    keys = [u'奖品', u'Flash', u'劳务(KOL、线下活动等)', u'效果优化',
            u'其他(视频等)', u'flash&H5开发', u'H5开发', u'区域总计', u'总计']
    for k in range(len(keys)):
        worksheet.write(2 + k, 1, keys[k], align_left)
    for k in range(len(data['1'])):
        worksheet.write(2, 2 + k * 3, data['1'][k]['huadong'], align_left)
        worksheet.write(2, 3 + k * 3, data['1'][k]['huabei'], align_left)
        worksheet.write(2, 4 + k * 3, data['1'][k]['huanan'], align_left)
    for k in range(len(data['2'])):
        worksheet.write(3, 2 + k * 3, data['2'][k]['huadong'], align_left)
        worksheet.write(3, 3 + k * 3, data['2'][k]['huabei'], align_left)
        worksheet.write(3, 4 + k * 3, data['2'][k]['huanan'], align_left)
    for k in range(len(data['3'])):
        worksheet.write(4, 2 + k * 3, data['3'][k]['huadong'], align_left)
        worksheet.write(4, 3 + k * 3, data['3'][k]['huabei'], align_left)
        worksheet.write(4, 4 + k * 3, data['3'][k]['huanan'], align_left)
    for k in range(len(data['4'])):
        worksheet.write(5, 2 + k * 3, data['4'][k]['huadong'], align_left)
        worksheet.write(5, 3 + k * 3, data['4'][k]['huabei'], align_left)
        worksheet.write(5, 4 + k * 3, data['4'][k]['huanan'], align_left)
    for k in range(len(data['5'])):
        worksheet.write(6, 2 + k * 3, data['5'][k]['huadong'], align_left)
        worksheet.write(6, 3 + k * 3, data['5'][k]['huabei'], align_left)
        worksheet.write(6, 4 + k * 3, data['5'][k]['huanan'], align_left)
    for k in range(len(data['6'])):
        worksheet.write(7, 2 + k * 3, data['6'][k]['huadong'], align_left)
        worksheet.write(7, 3 + k * 3, data['6'][k]['huabei'], align_left)
        worksheet.write(7, 4 + k * 3, data['6'][k]['huanan'], align_left)
    for k in range(len(data['7'])):
        worksheet.write(8, 2 + k * 3, data['7'][k]['huadong'], align_left)
        worksheet.write(8, 3 + k * 3, data['7'][k]['huabei'], align_left)
        worksheet.write(8, 4 + k * 3, data['7'][k]['huanan'], align_left)
    for k in range(len(data['t_locataion'])):
        worksheet.write(
            9, 2 + k * 3, data['t_locataion'][k]['huadong'], align_left)
        worksheet.write(
            9, 3 + k * 3, data['t_locataion'][k]['huabei'], align_left)
        worksheet.write(
            9, 4 + k * 3, data['t_locataion'][k]['huanan'], align_left)
    # for k in range(len(data['t_month'])):
    worksheet.merge_range(10, 2, 10, 4, data['t_month'][0], align_left)
    worksheet.merge_range(10, 5, 10, 7, data['t_month'][1], align_left)
    worksheet.merge_range(10, 8, 10, 10, data['t_month'][2], align_left)

    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                ("外包总计", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


def _insert_month_data(worksheet, align_center, data, now_year, month, th):
    if data:
        worksheet.merge_range(
            th, 1, th + len(data) - 1, 1, month + u'月', align_center)
        for k in data:
            worksheet.write(th, 2, k.contract or u'无合同号', align_center)
            worksheet.write(th, 3, k.campaign, align_center)
            worksheet.write(th, 4, k.money, align_center)
            worksheet.write(th, 5, k.locations_cn, align_center)
            worksheet.write(th, 6, float(k.outsources_sum), align_center)
            worksheet.write(
                th, 7, str(float(k.outsources_percent)) + '%', align_center)
            worksheet.write(th, 8, float(k.outsources_paied_sum), align_center)
            o_money = k.o_money
            for i in range(len(o_money)):
                worksheet.write(th, 9 + i, o_money[i], align_center)
            th += 1
    else:
        worksheet.write(th, 1, month + u'月', align_center)
        for k in range(35):
            worksheet.write(th, 1 + k + 1, '', align_center)
        th += 1
    return th


def _insert_Q(worksheet, align_center, Q, start, end):
    worksheet.merge_range(start, 0, end, 0, Q, align_center)
    return


def _insert_total_data(worksheet, align_center_color, data, th):
    worksheet.merge_range(th, 0, th, 8, u'合计', align_center_color)
    for k in range(len(data)):
        worksheet.write(th, k + 9, str(float(data[k])), align_center_color)
    th += 1
    return th


def write_outsource_info_excel(now_year, pre_month_orders, total_Q_data):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    align_center_color = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1, 'fg_color': '#228B22'})
    # 设置宽度为30
    for k in range(41):
        worksheet.set_column(k, 0, 15)
    # 设置高度
    for k in range(1000):
        worksheet.set_row(k, 25)
    worksheet.merge_range(0, 0, 2, 1, u'详情/月份', align_center_color)

    worksheet.merge_range(0, 2, 1, 8, u'合同信息', align_center_color)
    keys = [u'项目合同号', u'项目名称', u'项目金额', u'大区', u'应付小计', u'所占比重', u'实付金额']
    for k in range(len(keys)):
        worksheet.write(2, k + 2, keys[k], align_center_color)

    start, end = 9, 15
    for k in range(4):
        worksheet.merge_range(0, start, 0, end, u'项目成本', align_center_color)
        worksheet.merge_range(
            1, start, 1, end, 'Q' + str(k + 1), align_center_color)
        start, end = end + 1, end + 7

    keys = [u'奖品', u'Flash', u'劳务(KOL、线下活动等)', u'效果优化', u'其他(视频等)',
            u'flash&H5开发', u'H5开发']

    td = 9
    for i in range(4):
        for k in keys:
            worksheet.write(2, td, k, align_center_color)
            td += 1

    th = 3
    Q1_start = th
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['1'], now_year, '1', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['2'], now_year, '2', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['3'], now_year, '3', th)
    _insert_Q(worksheet, align_center, 'Q1', Q1_start, th - 1)
    Q2_start = th
    th = _insert_total_data(
        worksheet, align_center_color, total_Q_data['first'], th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['4'], now_year, '4', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['5'], now_year, '5', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['6'], now_year, '6', th)
    _insert_Q(worksheet, align_center, 'Q2', Q2_start + 1, th - 1)
    Q3_start = th
    th = _insert_total_data(
        worksheet, align_center_color, total_Q_data['second'], th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['7'], now_year, '7', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['8'], now_year, '8', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['9'], now_year, '9', th)
    _insert_Q(worksheet, align_center, 'Q3', Q3_start + 1, th - 1)
    Q4_start = th
    th = _insert_total_data(
        worksheet, align_center_color, total_Q_data['third'], th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['10'], now_year, '10', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['11'], now_year, '11', th)
    th = _insert_month_data(
        worksheet, align_center, pre_month_orders['12'], now_year, '12', th)
    _insert_Q(worksheet, align_center, 'Q4', Q4_start + 1, th - 1)
    th = _insert_total_data(
        worksheet, align_center_color, total_Q_data['forth'], th)
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                ('外包详情', datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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
            u'执行开始', u'执行结束', u'回款日期', u'回款金额', u'直客销售', u'渠道销售', u'区域', u'合同模板类型',
            u'售卖类型', u'代理/直客', u'投放媒体', u'媒体订单状态', u'媒体合同号', u'售卖金额(元)', u'媒体金额(元)', u'分成金额(元)',
            u'是否给媒体打款', u'是否收到媒体发票',
            u'预估量(CPM)', u'实际量(CPM)', u'执行开始', u'执行结束', u'执行人员', u'豆瓣关联媒体订单',
            u'豆瓣合同号', u'Campaign名称', u'豆瓣合同金额']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
        worksheet.set_column(0, 0 + k, 15)
    th = 1
    now_date = datetime.datetime.now().date()
    for k in range(len(orders)):
        if now_date > orders[k].reminde_date and orders[k].back_money_percent != 100:
            align_left = workbook.add_format(
                {'align': 'left', 'valign': 'vcenter', 'border': 1, 'fg_color': 'FF8888'})
        else:
            align_left = workbook.add_format(
                {'align': 'left', 'valign': 'vcenter', 'border': 1})
        mediums = orders[k].medium_orders
        if len(mediums) > 1:
            '''
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
                th, 10, th + len(orders[k].medium_orders) - 1, 10, orders[k].agent_sales_names, align_left)
            worksheet.merge_range(
                th, 11, th + len(orders[k].medium_orders) - 1, 11, orders[k].locations_cn, align_left)
            worksheet.merge_range(
                th, 12, th + len(orders[k].medium_orders) - 1, 12, orders[k].contract_type_cn, align_left)
            worksheet.merge_range(
                th, 13, th + len(orders[k].medium_orders) - 1, 13, orders[k].resource_type_cn, align_left)
            worksheet.merge_range(
                th, 14, th + len(orders[k].medium_orders) - 1, 14, orders[k].sale_type_cn, align_left)
            '''
            for i in range(len(mediums)):
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
                worksheet.write(th, 10, orders[k].agent_sales_names, align_left)
                worksheet.write(th, 11, orders[k].locations_cn, align_left)
                worksheet.write(th, 12, orders[k].contract_type_cn, align_left)
                worksheet.write(th, 13, orders[k].resource_type_cn, align_left)
                worksheet.write(th, 14, orders[k].sale_type_cn, align_left)
                worksheet.write(th, 15, mediums[i].medium.name, align_left)
                worksheet.write(
                    th, 16, mediums[i].finish_status_cn, align_left)
                worksheet.write(th, 17, mediums[i].medium_contract, align_left)
                worksheet.write(th, 18, mediums[i].sale_money, align_left)
                worksheet.write(th, 19, mediums[i].medium_money2, align_left)
                worksheet.write(th, 20, mediums[i].medium_money, align_left)
                worksheet.write(th, 21, '', align_left)
                worksheet.write(th, 22, '', align_left)
                worksheet.write(th, 23, mediums[i].sale_CPM, align_left)
                worksheet.write(th, 24, mediums[i].medium_CPM, align_left)
                worksheet.write(th, 25, mediums[i].start_date_cn, align_left)
                worksheet.write(th, 26, mediums[i].end_date_cn, align_left)
                worksheet.write(th, 27, mediums[i].operater_names, align_left)
                if mediums[i].associated_douban_order:
                    worksheet.write(
                        th, 28, mediums[i].associated_douban_order.name, align_left)
                    worksheet.write(
                        th, 29, mediums[i].associated_douban_order.contract, align_left)
                    worksheet.write(
                        th, 30, mediums[i].associated_douban_order.campaign, align_left)
                    worksheet.write(
                        th, 31, mediums[i].associated_douban_order.money, align_left)
                else:
                    worksheet.write(th, 28, '', align_left)
                    worksheet.write(th, 29, '', align_left)
                    worksheet.write(th, 30, '', align_left)
                    worksheet.write(th, 31, '', align_left)
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
            worksheet.write(th, 10, orders[k].agent_sales_names, align_left)
            worksheet.write(th, 11, orders[k].locations_cn, align_left)
            worksheet.write(th, 12, orders[k].contract_type_cn, align_left)
            worksheet.write(th, 13, orders[k].resource_type_cn, align_left)
            worksheet.write(th, 14, orders[k].sale_type_cn, align_left)
            if orders[k].medium_orders:
                worksheet.write(
                    th, 15, orders[k].medium_orders[0].medium.name, align_left)
                worksheet.write(
                    th, 16, orders[k].medium_orders[0].finish_status_cn, align_left)
                worksheet.write(
                    th, 17, orders[k].medium_orders[0].medium_contract, align_left)
                worksheet.write(
                    th, 18, orders[k].medium_orders[0].sale_money, align_left)
                worksheet.write(
                    th, 19, orders[k].medium_orders[0].medium_money2, align_left)
                worksheet.write(
                    th, 20, orders[k].medium_orders[0].medium_money, align_left)
                worksheet.write(
                    th, 21, '', align_left)
                worksheet.write(
                    th, 22, '', align_left)
                worksheet.write(
                    th, 23, orders[k].medium_orders[0].sale_CPM, align_left)
                worksheet.write(
                    th, 24, orders[k].medium_orders[0].medium_CPM, align_left)
                worksheet.write(
                    th, 25, orders[k].medium_orders[0].start_date_cn, align_left)
                worksheet.write(
                    th, 26, orders[k].medium_orders[0].end_date_cn, align_left)
                worksheet.write(
                    th, 27, orders[k].medium_orders[0].operater_names, align_left)
            if orders[k].associated_douban_orders:
                worksheet.write(
                    th, 28, orders[k].associated_douban_orders[0].name, align_left)
                worksheet.write(
                    th, 29, orders[k].associated_douban_orders[0].contract, align_left)
                worksheet.write(
                    th, 30, orders[k].associated_douban_orders[0].campaign, align_left)
                worksheet.write(
                    th, 31, orders[k].associated_douban_orders[0].money, align_left)
            else:
                worksheet.write(th, 28, '', align_left)
                worksheet.write(th, 29, '', align_left)
                worksheet.write(th, 30, '', align_left)
                worksheet.write(th, 31, '', align_left)
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
#            worksheet.merge_range(
# th, 10, th + len(orders[k].medium_orders) - 1, 10,
# orders[k].agent_sales_names, align_left)
            worksheet.merge_range(
                th, 10, th + len(orders[k].medium_orders) - 1, 10, orders[k].locations_cn, align_left)
            worksheet.merge_range(
                th, 11, th + len(orders[k].medium_orders) - 1, 11, orders[k].contract_type_cn, align_left)
            worksheet.merge_range(
                th, 12, th + len(orders[k].medium_orders) - 1, 12, orders[k].resource_type_cn, align_left)
            worksheet.merge_range(
                th, 13, th + len(orders[k].medium_orders) - 1, 13, orders[k].sale_type_cn, align_left)
            for i in range(len(mediums)):
                worksheet.write(th, 14, mediums[i].medium.name, align_left)
                worksheet.write(th, 15, mediums[i].medium_contract, align_left)
                worksheet.write(th, 16, mediums[i].sale_money, align_left)
                worksheet.write(th, 17, mediums[i].medium_money2, align_left)
#                worksheet.write(th, 18, mediums[i].medium_money, align_left)
                worksheet.write(th, 18, '', align_left)
                worksheet.write(th, 19, '', align_left)
                worksheet.write(th, 20, mediums[i].sale_CPM, align_left)
                worksheet.write(th, 21, mediums[i].medium_CPM, align_left)
                worksheet.write(th, 22, mediums[i].start_date_cn, align_left)
                worksheet.write(th, 23, mediums[i].end_date_cn, align_left)
                worksheet.write(th, 24, mediums[i].operater_names, align_left)
#                if mediums[i].associated_douban_order:
#                    worksheet.write(th, 27, mediums[i].associated_douban_order.name, align_left)
#                    worksheet.write(th, 28, mediums[i].associated_douban_order.contract, align_left)
#                    worksheet.write(th, 29, mediums[i].associated_douban_order.campaign, align_left)
#                    worksheet.write(th, 30, mediums[i].associated_douban_order.money, align_left)
#                else:
#                    worksheet.write(th, 27, '', align_left)
#                    worksheet.write(th, 28, '', align_left)
#                    worksheet.write(th, 29, '', align_left)
#                    worksheet.write(th, 30, '', align_left)
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
#            worksheet.write(th, 10, orders[k].agent_sales_names, align_left)
            worksheet.write(th, 10, orders[k].locations_cn, align_left)
            worksheet.write(th, 11, orders[k].contract_type_cn, align_left)
            worksheet.write(th, 12, orders[k].resource_type_cn, align_left)
            worksheet.write(th, 13, orders[k].sale_type_cn, align_left)
            if orders[k].medium_orders:
                worksheet.write(
                    th, 14, orders[k].medium_orders[0].medium.name, align_left)
                worksheet.write(
                    th, 15, orders[k].medium_orders[0].medium_contract, align_left)
                worksheet.write(
                    th, 16, orders[k].medium_orders[0].sale_money, align_left)
                worksheet.write(
                    th, 17, orders[k].medium_orders[0].medium_money2, align_left)
#                worksheet.write(
# th, 18, orders[k].medium_orders[0].medium_money, align_left)
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
#            if orders[k].associated_douban_orders:
#                worksheet.write(
#                    th, 27, orders[k].associated_douban_orders[0].name, align_left)
#                worksheet.write(
#                    th, 28, orders[k].associated_douban_orders[0].contract, align_left)
#                worksheet.write(
#                    th, 29, orders[k].associated_douban_orders[0].campaign, align_left)
#                worksheet.write(
#                    th, 30, orders[k].associated_douban_orders[0].money, align_left)
#            else:
#                worksheet.write(th, 27, '', align_left)
#                worksheet.write(th, 28, '', align_left)
#                worksheet.write(th, 29, '', align_left)
#                worksheet.write(th, 30, '', align_left)
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
