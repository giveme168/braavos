# -*- coding: UTF-8 -*-
import xlwt


def write_client_excel(huabei_agent_salers_orders,
                       huabei_direct_salers_orders,
                       huanan_agent_salers_orders,
                       huanan_direct_salers_orders,
                       huadong_agent_salers_orders,
                       huadong_direct_salers_orders,
                       now_year, Q, Q_monthes):
    xls = xlwt.Workbook(encoding='utf-8')
    sheet = xls.add_sheet("Sheet")
    sheet.write_merge(0, 1, 0, 32, Q)
    sheet.write_merge(2, 2, 0, 32, '华北区')

    keys = [u"渠道销售", u"状态", u"客户名称", u"合同号（代理下单号）", u"代理简称", u"项目名称", u"行业",
            u"直客销售", u"渠道销售", u"合同金额", u"媒体总金额", u"投放媒体", u"媒体金额"] + \
        [u"媒体%s月售卖金额" % (str(k)) for k in Q_monthes] + \
        [u"媒体%s月媒体金额" % (str(k)) for k in Q_monthes] + \
        [u"媒体%s金额差" % (str(k)) for k in Q_monthes] + \
        [u"本季度确认额", u"本季度执行额", u"上季度执行额", u"下季度执行额"] + \
        [u"%s月执行额" % (str(k)) for k in Q_monthes] + \
        [u"类型", u"AE", u"合同开始", u"合同结束"]
    for k in range(len(keys)):
        sheet.write(3, k, keys[k])
    th = 4
    for k in huabei_agent_salers_orders:
        medium_col = 0
        for i in k['orders']:
            medium_orders = i['order'].medium_orders
            for j in range(len(medium_orders)):
                sheet.write(th, 11, medium_orders[j].name)
                sheet.write(th, 12, medium_orders[j].medium_money2)
                for m in range(len(Q_monthes)):
                    sheet.write(th, 13 + m, medium_orders[j].get_executive_report_medium_money_by_month(
                        now_year, Q_monthes[m])['sale_money'])
                for m in range(len(Q_monthes)):
                    sheet.write(th, 16 + m, medium_orders[j].get_executive_report_medium_money_by_month(
                        now_year, Q_monthes[m])['medium_money2'])
                for m in range(len(Q_monthes)):
                    rate = medium_orders[j].get_executive_report_medium_money_by_month(now_year, Q_monthes[m])['sale_money'] - \
                        medium_orders[j].get_executive_report_medium_money_by_month(
                            now_year, Q_monthes[m])['medium_money2']
                    sheet.write(th, 19 + m, rate)
                th += 1
            medium_col += len(medium_orders)
            '''
            sheet.write_merge(th-medium_col, th-1, th, th, u'确认')
            sheet.write_merge(th-medium_col, th-1, 2, 2, i['order'].client.name)
            sheet.write_merge(th-medium_col, th-1, 3, 3, i['order'].contract)
            sheet.write_merge(th-medium_col, th-1, 4, 4, i['order'].agent.name)
            sheet.write_merge(th-medium_col, th-1, 5, 5, i['order'].campaign)
            sheet.write_merge(th-medium_col, th-1, 6, 6, i['order'].client.industry_cn)
            sheet.write_merge(th-medium_col, th-1, 7, 7, ','.join([u.name for u in i['order'].direct_sales]))
            sheet.write_merge(th-medium_col, th-1, 8, 8, ','.join([u.name for u in i['order'].agent_sales]))
            sheet.write_merge(th-medium_col, th-1, 9, 9, i['order'].money)
            sheet.write_merge(th-medium_col, th-1, 10, 10, i['order'].mediums_money2)
            sheet.write_merge(th-medium_col, th-1, 22, 22, '')
            sheet.write_merge(th-medium_col, th-1, 23, 23, i['now_Q_money'])
            sheet.write_merge(th-medium_col, th-1, 24, 24, i['last_Q_money'])
            sheet.write_merge(th-medium_col, th-1, 25, 25, i['after_Q_money'])
            for m in range(len(i['moneys'])):
                sheet.write_merge(th-medium_col, th-1, 26+m, 26+m, i['moneys'][m])
            sheet.write_merge(th-medium_col, th-1, 29, 29, i['order'].resource_type_cn)
            sheet.write_merge(th-medium_col, th-1, 30, 30, ",".join([u.name for u in i['order'].operater_users]))
            sheet.write_merge(th-medium_col, th-1, 31, 31, i['order'].client_start)
            sheet.write_merge(th-medium_col, th-1, 32, 32, i['order'].client_end)
            th += 1
        order_col = medium_col
        sheet.write_merge(th-order_col-1, th, 0, 0, k['user'].name)
        '''

    return xls
