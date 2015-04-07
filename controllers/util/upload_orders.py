# -*- coding: utf-8 -*-
import xlrd

from flask import Blueprint, request
from flask import render_template as tpl


util_upload_orders_bp = Blueprint(
    'util_upload_orders', __name__, template_folder='../../templates/util')


@util_upload_orders_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['upload_file']
        xls_orders = '/tmp/uploads/' + f.filename.encode('utf8')
        f.save(xls_orders)
        if xls_orders:
            try:
                _fix_orders(xlrd.open_workbook(xls_orders))
            except Exception, e:
                print str(e)
    return tpl('upload_orders.html')


def _fix_orders(excel_data):
    table = excel_data.sheet_by_index(0)
    # 行数
    nrows = table.nrows
    # 列数
    ncols = table.ncols
    if ncols != 15:
        return

    for i in range(nrows):
        if i > 0:
            print '11', table.col(0)[i].value
    return
