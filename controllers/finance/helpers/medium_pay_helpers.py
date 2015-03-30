# -*- coding: UTF-8 -*-
import xlwt

from models.invoice import MediumInvoice, INVOICE_TYPE_CN, MEDIUM_INVOICE_STATUS_PASS


def medium_write_excel(orders):
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
    keys = [u'客户名称', u'媒体总金额', '已打款发票金额', u'开票时间', u'客户名称', u'媒体名称',
            u'公司名称', u'税号', u'公司地址', u'联系电话', u'银行账号', u'开户行', u'发票内容',
            u'发票金额', u'打款金额', u'发票类型', u'发票号', u'是否开票', u'申请人', u'是否打款']
    for k in range(len(keys)):
        sheet.write(0, k, keys[k])

    h, j = 1, 1
    for k in range(len(orders)):
        invoice_passes = [x for x in MediumInvoice.query.filter_by(
            client_order=orders[k]) if x.invoice_status == MEDIUM_INVOICE_STATUS_PASS]
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 0, 0, orders[k].name, style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 1, 1, str(orders[k].mediums_money2), style)
        sheet.write_merge(
            h, h + len(invoice_passes) - 1, 2, 2, str(orders[k].mediums_invoice_pass_sum), style)

        h = h + len(invoice_passes)
        for i in range(len(invoice_passes)):
            sheet.write(
                j, 3, invoice_passes[i].add_time_cn)
            sheet.write(j, 4, invoice_passes[i].client_order.name)
            sheet.write(j, 5, invoice_passes[i].medium.name)
            sheet.write(j, 6, invoice_passes[i].company)
            sheet.write(j, 7, invoice_passes[i].tax_id)
            sheet.write(j, 8, invoice_passes[i].address)
            sheet.write(j, 9, invoice_passes[i].phone)
            sheet.write(j, 10, invoice_passes[i].bank_id)
            sheet.write(j, 11, invoice_passes[i].bank)
            sheet.write(j, 12, invoice_passes[i].detail)
            sheet.write(j, 13, str(invoice_passes[i].money))
            sheet.write(j, 14, str(invoice_passes[i].pay_money))
            sheet.write(j, 15, INVOICE_TYPE_CN[invoice_passes[i].invoice_type])
            sheet.write(j, 16, invoice_passes[i].tax_id)
            if invoice_passes[i].bool_invoice:
                sheet.write(j, 17, u'发票已开')
            else:
                sheet.write(j, 17, u'没有发票')
            sheet.write(j, 18, invoice_passes[i].creator.name)
            if invoice_passes[i].bool_pay:
                sheet.write(j, 19, u'已打款')
            else:
                sheet.write(j, 19, u'未打款')
            j += 1
    return xls
