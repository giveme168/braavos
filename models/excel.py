#-*- coding: UTF-8 -*-
from xlwt import XFStyle, Font, Alignment, Borders, Pattern, Workbook, Utils, Formula

RED = 2
LIGHT_GRAY = 22
BLACK = 0
FONT_SIZE = 12 * 20
DATE_START_COL = 3
DATE_START_ROW = 2


class StyleFactory(object):
    def __init__(self):
        self.style = XFStyle()
        base_font = Font()  # 设置基本字体
        base_font.height = FONT_SIZE
        self.style.font = base_font
        alignment = Alignment()  # 设置对齐
        alignment.horz = Alignment.HORZ_CENTER
        alignment.vert = Alignment.VERT_CENTER
        self.style.alignment = alignment
        borders = Borders()  # 设置边框
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        borders.top = Borders.THIN
        borders.bottom = Borders.THIN
        borders.left_colour = BLACK
        borders.right_colour = BLACK
        borders.top_colour = BLACK
        borders.bottom_colour = BLACK
        self.style.borders = borders
        self.style.num_format_str = '#,##0'  # 设置数字格式

    def bold(self):
        bold_font = self.style.font
        bold_font.bold = True
        self.style.font = bold_font
        return self

    def bg_colour(self, colour):
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = colour
        self.style.pattern = pattern
        return self

    def font_colour(self, colour):
        font = self.style.font
        font.colour_index = colour
        self.style.font = font
        return self


class StyleTypes(object):
        """The Style of the Excel's unit"""
        def __init__(self):
            self.base = StyleFactory().style
            self.header = StyleFactory().bold().style
            self.gift = StyleFactory().font_colour(RED).style
            self.base_weekend = StyleFactory().bg_colour(LIGHT_GRAY).style
            self.gift_weekend = StyleFactory().font_colour(RED).bg_colour(LIGHT_GRAY).style


class Excel(object):
    row_height = 500  # 单元格的单位高度
    col_width = 3333  # 单元格的单位宽度
    style_type = StyleTypes()

    def __init__(self, items_info):
        self.xls = Workbook(encoding='utf-8')
        self.sheet = self.xls.add_sheet("Sheet")
        self.items_info = items_info
        self.write_header()
        row = DATE_START_ROW
        for v, sale_type_cn, sale_type_items in items_info['items']:
            if not len(sale_type_items):
                break
            if sale_type_cn == u"配送":
                item_type = self.style_type.gift
                item_weekend_type = self.style_type.gift_weekend
            else:
                item_type = self.style_type.base
                item_weekend_type = self.style_type.base_weekend
            self.sheet.write_merge(
                row, row + len(sale_type_items) - 1, 0, 0, sale_type_cn, item_type)
            row = self.write_items(sale_type_items, item_type, item_weekend_type, row)
        self.write_total(row)
        self.sheet.col(1).width = self.col_width * 3
        self.sheet.col(2).width = self.col_width * 3

    def write_header(self):
        self.sheet.write_merge(0, 1, 0, 0, u"售卖类型", self.style_type.header)
        self.sheet.write_merge(0, 1, 1, 1, u"展示位置", self.style_type.header)
        self.sheet.write_merge(0, 1, 2, 2, u"广告标准", self.style_type.header)
        column = DATE_START_COL
        for m, m_len in self.items_info['months'].items():
            self.sheet.write_merge(
                0, 0, column, column + m_len - 1, str(m) + u"月", self.style_type.header)
            column += m_len
        column = 3
        for d in self.items_info['dates']:
            if d.isoweekday() in [6, 7]:
                self.sheet.write(1, column, d.day, self.style_type.base_weekend)
            else:
                self.sheet.write(1, column, d.day, self.style_type.base)
            column += 1
        self.sheet.write_merge(0, 1, column, column, u"总预订量", self.style_type.header)
        column += 1
        self.sheet.write_merge(0, 1, column, column, u"刊例单价", self.style_type.header)
        column += 1
        self.sheet.write_merge(0, 1, column, column, u"刊例总价", self.style_type.header)
        column += 1
        self.sheet.write_merge(0, 1, column, column, u"折扣", self.style_type.header)
        column += 1
        self.sheet.write_merge(0, 1, column, column, u"净价", self.style_type.header)
        self.sheet.row(0).height = self.row_height
        self.sheet.row(1).height = self.row_height

    def write_items(self, sale_type_items, item_type, item_weekend_type, row):
        for item in sale_type_items:
            self.sheet.write(row, 1, item.position.name, item_type)
            self.sheet.write(row, 2, item.position.size.name, item_type)
            column = DATE_START_COL
            for i in range(0, len(self.items_info['dates'])):
                d = self.items_info['dates'][i]
                if d.isoweekday() in [6, 7]:
                    if item.schedule_by_date(d):
                        self.sheet.write(
                            row, column, item.schedule_by_date(d).num, item_weekend_type)
                    else:
                        self.sheet.write(row, column, " ", item_weekend_type)
                else:
                    if item.schedule_by_date(d):
                        self.sheet.write(row, column, item.schedule_by_date(d).num, item_type)
                    else:
                        self.sheet.write(row, column, " ", item_type)
                column += 1
            self.sheet.write(
                row, DATE_START_COL + len(self.items_info['dates']), item.schedule_sum, item_type)
            self.sheet.write(
                row, DATE_START_COL + len(self.items_info['dates']) + 1, item.position.price, item_type)
            self.sheet.write(
                row, DATE_START_COL + len(self.items_info['dates']) + 2,
                item.schedule_sum * item.position.price, item_type)
            self.sheet.row(row).height = self.row_height
            row += 1
        return row

    def write_total(self, row):
        self.sheet.row(row).height = self.row_height
        self.sheet.write_merge(row, row, 0, 2, "total", self.style_type.base)
        for i in range(0, len(self.items_info['dates']) + 1):
            formula = 'SUM(%s:%s)' % (
                Utils.rowcol_to_cell(DATE_START_ROW, DATE_START_COL + i),
                Utils.rowcol_to_cell(row - 1, DATE_START_COL + i))
            self.sheet.write(row, DATE_START_COL + i, Formula(formula), self.style_type.base)
        column = DATE_START_COL + len(self.items_info['dates']) + 1
        self.sheet.write(row, column, "/", self.style_type.base)
        column += 1
        formula = 'SUM(%s:%s)' % (
                Utils.rowcol_to_cell(DATE_START_ROW, column),
                Utils.rowcol_to_cell(row - 1, column))
        self.sheet.write(row, column, Formula(formula), self.style_type.base)
