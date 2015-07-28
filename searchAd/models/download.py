# -*- coding: UTF-8 -*-
from .excel import (ExcelCellItem, StyleFactory, EXCEL_DATA_TYPE_STR,
                          EXCEL_DATA_TYPE_NUM, COLOUR_RED, COLOUR_LIGHT_GRAY)


def download_excel_table_by_clientorders(orders):
    excel_table = []
    temp_row = []
    for header_cn in [u"CLientOrder ID", u"代理/直客", u"客户", u"Campaign",
                      u"合同金额", u"合同号", u"开始日期", u"结束日期",
                      u"回款日期", u"直客销售", u"渠道销售",
                      u"区域", u"直签/代理", u"状态"]:
        header_type = StyleTypes.header
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, header_cn, header_type))
    excel_table.append(temp_row)  # 表头
    base_type = StyleTypes.base
    for order in orders:
        temp_row = []
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, order.id, base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.agent.name or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.client.name or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.campaign or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, order.money or 0, base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.contract or u"无合同号", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.start_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.end_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.reminde_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.direct_sales_names or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.agent_sales_names or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.locations_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.sale_type_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.contract_status_cn or " ", base_type))
        excel_table.append(temp_row)
    return excel_table


def download_excel_table_by_doubanorders(orders):
    excel_table = []
    temp_row = []
    for header_cn in [u"DoubanOrder ID", u"代理/直客", u"客户", u"Campaign",
                      u"合同金额", u"合同号", u"开始日期", u"结束日期",
                      u"回款日期", u"直客销售", u"渠道销售",
                      u"区域", u"直签/代理", u"状态"]:
        header_type = StyleTypes.header
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, header_cn, header_type))
    excel_table.append(temp_row)  # 表头
    base_type = StyleTypes.base
    for order in orders:
        temp_row = []
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, order.id, base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.agent.name or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.client.name or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.campaign or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, order.money or 0, base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.contract or u"无合同号", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.start_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.end_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.reminde_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.direct_sales_names or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.agent_sales_names or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.locations_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.sale_type_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.contract_status_cn or " ", base_type))
        excel_table.append(temp_row)
    return excel_table


def download_excel_table_by_frameworkorders(orders):
    excel_table = []
    temp_row = []
    for header_cn in [u"FrameworkOrder ID", u"代理集团", u"备注",
                      u"合同金额", u"合同号", u"开始日期", u"结束日期",
                      u"回款日期", u"直客销售", u"渠道销售",
                      u"状态"]:
        header_type = StyleTypes.header
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, header_cn, header_type))
    excel_table.append(temp_row)  # 表头
    base_type = StyleTypes.base
    for order in orders:
        temp_row = []
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, order.id, base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.group.name or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.description or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_NUM, order.money or 0, base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.contract or u"无合同号", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.start_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.end_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.reminde_date_cn or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.direct_sales_names or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.agent_sales_names or " ", base_type))
        temp_row.append(ExcelCellItem(EXCEL_DATA_TYPE_STR, order.contract_status_cn or " ", base_type))
        excel_table.append(temp_row)
    return excel_table


class StyleTypes(object):
    """The Style of the Excel's unit"""
    base = StyleFactory().style
    header = StyleFactory().bold().style
    gift = StyleFactory().font_colour(COLOUR_RED).style
    base_weekend = StyleFactory().bg_colour(COLOUR_LIGHT_GRAY).style
    gift_weekend = StyleFactory().font_colour(COLOUR_RED).bg_colour(COLOUR_LIGHT_GRAY).style
    discount = StyleFactory().font_num('0%').style
    gift_discount = StyleFactory().font_colour(COLOUR_RED).font_num('0%').style
