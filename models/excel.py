#-*- coding: UTF-8 -*-
from xlwt import (XFStyle, Font, Alignment,
    Borders, Pattern, Workbook, Utils, Formula)

COLOUR_RED = 2
COLOUR_LIGHT_GRAY = 22
COLOUR_BLACK = 0
FONT_SIZE_UNIT = 20

EXCEL_DATE_TYPE_MERGE = 0
EXCEL_DATE_TYPE_STR = 1
EXCEL_DATE_TYPE_NUM = 2
EXCEL_DATE_TYPE_FORMULA = 3


class StyleFactory(object):
    def __init__(self):
        self.style = XFStyle()
        base_font = Font()  # 设置基本字体
        base_font.height = FONT_SIZE_UNIT * 12
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
        borders.left_colour = COLOUR_BLACK
        borders.right_colour = COLOUR_BLACK
        borders.top_colour = COLOUR_BLACK
        borders.bottom_colour = COLOUR_BLACK
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


class ExcelCellItem(object):
    """docstring for ExcelCellItem"""
    def __init__(self, type, date=" ", style=StyleFactory().style, merge_row=0, merge_col=0):
        self.type = type
        self.date = date
        self.style = style
        self.merge_col = merge_col
        self.merge_row = merge_row


class Excel(object):
    def __init__(self, row_height=500, col_width=3333):
        self.row_height = row_height  # 单元格的单位高度
        self.col_width = col_width  # 单元格的单位宽度

    def write_excle(self, excel_table):
        self.xls = Workbook(encoding='utf-8')
        self.sheet = self.xls.add_sheet("Sheet")
        self.excel_table = excel_table

        for row in range(0, len(excel_table)):
            self.sheet.row(row).height = self.row_height
            for col in range(0, len(excel_table[row])):
                cell = excel_table[row][col]
                if cell.type == EXCEL_DATE_TYPE_STR:
                    self.sheet.write_merge(
                        row, row + cell.merge_row, col, col + cell.merge_col, cell.date, cell.style)
                    if str_len(cell.date) > 11:
                        min_width = self.col_width * (str_len(cell.date) / 12 + 1)
                        self.sheet.col(col).width = (
                            self.sheet.col(col).width if self.sheet.col(col).width > min_width
                            else min_width)
                if cell.type == EXCEL_DATE_TYPE_NUM:
                    self.sheet.write_merge(
                        row, row + cell.merge_row, col, col + cell.merge_col, cell.date, cell.style)
                if cell.type == EXCEL_DATE_TYPE_FORMULA:
                    self.sheet.write_merge(
                        row, row + cell.merge_row, col, col + cell.merge_col, Formula(cell.date), cell.style)
        return self.xls


def str_len(str):
    len = 0
    for char in str:
        if ord(char) > 127:
            len += 2
        else:
            len += 1
    return len
