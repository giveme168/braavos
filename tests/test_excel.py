# -*- coding: UTF-8 -*-
from xlwt import Alignment, Borders

from models.excel import (
    StyleFactory, FONT_SIZE_UNIT, COLOUR_RED, COLOUR_LIGHT_GRAY, COLOUR_BLACK)
from models.order import StyleTypes
from helper import add_schedule


def test_factory():
    factory = StyleFactory()
    base_style = factory.style
    base_assert(base_style)
    bold_style = factory.bold().style
    bold_assert(bold_style)
    bg_colour_style = factory.bg_colour(COLOUR_BLACK).style
    bg_colour_assert(bg_colour_style, COLOUR_BLACK)
    font_colour_style = factory.font_colour(COLOUR_BLACK).style
    font_colour_assert(font_colour_style, COLOUR_BLACK)


def test_types():
    styleTypes = StyleTypes()
    base_assert(styleTypes.base)

    base_assert(styleTypes.header)
    bold_assert(styleTypes.header)

    base_assert(styleTypes.gift)
    font_colour_assert(styleTypes.gift, COLOUR_RED)

    bg_colour_assert(styleTypes.base_weekend, COLOUR_LIGHT_GRAY)

    bg_colour_assert(styleTypes.gift_weekend, COLOUR_LIGHT_GRAY)
    font_colour_assert(styleTypes.gift_weekend, COLOUR_RED)


def base_assert(style):
    assert style.font.height == FONT_SIZE_UNIT * 12
    # 中间对齐
    assert style.alignment.horz == Alignment.HORZ_CENTER
    assert style.alignment.vert == Alignment.VERT_CENTER
    # 黑色边框
    assert style.borders.left == Borders.THIN
    assert style.borders.right == Borders.THIN
    assert style.borders.top == Borders.THIN
    assert style.borders.bottom == Borders.THIN
    assert style.borders.left_colour == COLOUR_BLACK
    assert style.borders.right_colour == COLOUR_BLACK
    assert style.borders.top_colour == COLOUR_BLACK
    assert style.borders.bottom_colour == COLOUR_BLACK
    assert style.num_format_str == '#,##0'  # 数字千位符


def bold_assert(style):
    assert style.font.bold is True


def bg_colour_assert(style, colour):
    assert style.pattern.pattern_fore_colour == colour


def font_colour_assert(style, colour):
    assert style.font.colour_index == colour


def test_excel_data(session):
    schedule = add_schedule()
    order = schedule.item.order
    excel_table = order.get_excel_table_by_status(0)
    assert len(excel_table) == 4
    assert len(excel_table[0]) == 9
    assert excel_table[2][4].data == 300
