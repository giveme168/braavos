# -*- coding: UTF-8 -*-
import xlwt

from models.outsource import OUTSOURCE_STATUS_APPLY_MONEY, OUTSOURCE_STATUS_PAIED


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

    keys = [u'合同名称', u'合同总金额', '外包应付总金额', u'外包占比', u'投放媒体', u'请款中', u'已打款',
            u'投放媒体', u'收款方', u'外包类别', u'是否开发票', u'Flash功能分类', u'金额', u'打款金额', u'开户行', u'卡号', u'支付宝', u'联系方式', u'备注']
    for k in range(len(keys)):
        sheet.write(0, k, keys[k])

    h, j = 1, 1
    for k in range(len(orders)):
        outsource_passes = orders[k].get_outsources_by_status(
            OUTSOURCE_STATUS_PAIED)
        outsource_apply = orders[k].get_outsources_by_status(
            OUTSOURCE_STATUS_APPLY_MONEY)
        sheet.write_merge(
            h, h + len(outsource_passes) - 1, 0, 0, orders[k].name, style)
        sheet.write_merge(
            h, h + len(outsource_passes) - 1, 1, 1, str(orders[k].money), style)
        sheet.write_merge(
            h, h + len(outsource_passes) - 1, 2, 2, str(orders[k].outsources_sum), style)
        sheet.write_merge(h, h + len(outsource_passes) - 1, 3,
                          3, str(orders[k].outsources_percent) + '%', style)
        sheet.write_merge(h, h + len(outsource_passes) - 1, 4, 4,
                          u','.join([k.name for k in orders[k].mediums]), style)
        sheet.write_merge(
            h, h + len(outsource_passes) - 1, 5, 5, str(len(outsource_apply)), style)
        sheet.write_merge(
            h, h + len(outsource_passes) - 1, 6, 6, str(len(outsource_passes)), style)

        h = h + len(outsource_passes)

        for i in range(len(outsource_passes)):
            sheet.write(j, 7, outsource_passes[i].medium_order.medium.name)
            sheet.write(j, 8, outsource_passes[i].target.name)
            sheet.write(j, 9, outsource_passes[i].type_cn)
            sheet.write(j, 10, outsource_passes[i].invoice_cn)
            sheet.write(j, 11, outsource_passes[i].subtype_cn)
            sheet.write(j, 12, outsource_passes[i].num or 0)
            sheet.write(j, 13, outsource_passes[i].pay_num or 0)
            sheet.write(j, 14, outsource_passes[i].target.bank)
            sheet.write(j, 15, outsource_passes[i].target.card)
            sheet.write(j, 16, outsource_passes[i].target.alipay)
            sheet.write(j, 17, outsource_passes[i].target.contract)
            sheet.write(j, 18, outsource_passes[i].remark)
            j += 1
    return xls
