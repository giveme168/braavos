# -*- coding: utf-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response, g, abort
from werkzeug.datastructures import Headers
import xlsxwriter
from flask import Blueprint, request, jsonify
from flask import render_template as tpl
from models.other import NianHui

from models.client_order import ClientOrder
from models.douban_order import DoubanOrder

other_bp = Blueprint('other', __name__, template_folder='../templates/other')


JM = {1: u'《try everthing》',
      2: u'《歌曲串烧》',
      3: u'《致趣联播》',
      4: u'《我也是歌手》',
      5: u'《脱口秀》',
      6: u'《蒙面歌王》',
      7: u'《INAD加油》',
      8: u'《uptown funk》',
      9: u'《极限挑战》',
      10: u'《台前幕后》',
      11: u'《狐狸说嘛呢》'}


@other_bp.route('/nianhui', methods=['GET', 'POST'])
def nianhui():
    if request.method == 'POST':
        ids = request.values.get('ids', '')
        if NianHui.query.filter_by(user=g.user).count() > 0:
            return jsonify({'status': -1, 'msg': u'您已经投过票了'})
        NianHui.add(user=g.user,
                    create_time=datetime.datetime.now(),
                    ids=ids)
        return jsonify({'status': 0, 'msg': '1123'})
    ids = '|'.join([k.ids for k in NianHui.all()])
    jm_count = {}
    total_count = 0
    for k, v in JM.items():
        jm_count[k] = 0
    for k in ids.split('|'):
        total_count += 1
        if int(k) in jm_count:
            jm_count[int(k)] += 1
    jm_count = sorted(jm_count.iteritems(), key=lambda x: x[1])
    jm_count.reverse()
    res = []
    for k in jm_count:
        res.append({'name': JM[k[0]], 'count': k[1],
                    'percent': float(k[1]) / total_count * 100})
    return tpl('/other/nhs.html', res=res, total_count=total_count)


def write_fix_date(orders, otype=None):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1})
    if otype == 'douban_order':
        keys = [u"项目名称", u"代理/直客", u"合同号", u"行业", u"直客销售", u"渠道销售",
                u"合同金额", u'客户返点金额', u'类型', u'执行开始时间', u'执行结束时间']
    else:
        keys = [u"项目名称", u"代理/直客", u"合同号", u"行业", u"直客销售", u"渠道销售",
                u"合同金额", u"已开发票总金额", u"媒体总金额", u"媒体名称", u"媒体售卖金额",
                u"媒体金额", u"媒体返点金额", u'客户返点金额', u'类型', u'执行开始时间', u'执行结束时间']
    for k in range(len(keys)):
        worksheet.write(0, 0 + k, keys[k], align_left)
    # 设置宽度
    for k in range(len(keys) + 1):
        worksheet.set_column(k, 0, 20)
    th = 1
    if otype == 'douban_order':
        for k in range(len(orders)):
            worksheet.write(th, 0, orders[k].campaign, align_left)
            worksheet.write(th, 1, orders[k].agent.name, align_left)
            worksheet.write(th, 2, orders[k].contract, align_left)
            worksheet.write(th, 3, orders[k].client.industry_cn, align_left)
            worksheet.write(th, 4, orders[k].direct_sales_names, align_left)
            worksheet.write(th, 5, orders[k].agent_sales_names, align_left)
            worksheet.write(th, 6, orders[k].money, align_left)
            worksheet.write(th, 7, orders[k].agent_rebate_value, align_left)
            worksheet.write(th, 8, orders[k].resource_type_cn, align_left)
            worksheet.write(th, 9, orders[k].start_date_cn, align_left)
            worksheet.write(th, 10, orders[k].end_date_cn, align_left)
            th += 1
    else:
        for k in range(len(orders)):
            mediums = orders[k].medium_orders
            if len(mediums) > 1:
                worksheet.merge_range(
                    th, 0, th + len(orders[k].medium_orders) - 1, 0, orders[k].campaign, align_left)
                worksheet.merge_range(
                    th, 1, th + len(orders[k].medium_orders) - 1, 1, orders[k].agent.name, align_left)
                worksheet.merge_range(
                    th, 2, th + len(orders[k].medium_orders) - 1, 2, orders[k].contract, align_left)
                worksheet.merge_range(
                    th, 3, th + len(orders[k].medium_orders) - 1, 3, orders[k].client.industry_cn, align_left)
                worksheet.merge_range(
                    th, 4, th + len(orders[k].medium_orders) - 1, 4, orders[k].direct_sales_names, align_left)
                worksheet.merge_range(
                    th, 5, th + len(orders[k].medium_orders) - 1, 5, orders[k].agent_sales_names, align_left)
                worksheet.merge_range(
                    th, 6, th + len(orders[k].medium_orders) - 1, 6, orders[k].money, align_left)
                worksheet.merge_range(
                    th, 7, th + len(orders[k].medium_orders) - 1, 7, orders[k].invoice_pass_sum, align_left)
                worksheet.merge_range(
                    th, 8, th + len(orders[k].medium_orders) - 1, 8, orders[k].mediums_money2, align_left)
                worksheet.merge_range(
                    th, 13, th + len(orders[k].medium_orders) - 1, 13, orders[k].agent_rebate_value, align_left)
                worksheet.merge_range(
                    th, 14, th + len(orders[k].medium_orders) - 1, 14, orders[k].resource_type_cn, align_left)
                worksheet.merge_range(
                    th, 15, th + len(orders[k].medium_orders) - 1, 15, orders[k].start_date_cn, align_left)
                worksheet.merge_range(
                    th, 16, th + len(orders[k].medium_orders) - 1, 16, orders[k].end_date_cn, align_left)
                for i in range(len(mediums)):
                    worksheet.write(th, 9, mediums[i].medium.name, align_left)
                    worksheet.write(th, 10, mediums[i].sale_money, align_left)
                    worksheet.write(
                        th, 11, mediums[i].medium_money2, align_left)
                    worksheet.write(
                        th, 12, mediums[i].medium_rebate_value, align_left)
                    th += 1
            else:
                worksheet.write(th, 0, orders[k].campaign, align_left)
                worksheet.write(th, 1, orders[k].agent.name, align_left)
                worksheet.write(th, 2, orders[k].contract, align_left)
                worksheet.write(
                    th, 3, orders[k].client.industry_cn, align_left)
                worksheet.write(
                    th, 4, orders[k].direct_sales_names, align_left)
                worksheet.write(th, 5, orders[k].agent_sales_names, align_left)
                worksheet.write(th, 6, orders[k].money, align_left)
                worksheet.write(th, 7, orders[k].invoice_pass_sum, align_left)
                worksheet.write(th, 8, orders[k].mediums_money2, align_left)
                worksheet.write(
                    th, 13, orders[k].agent_rebate_value, align_left)
                worksheet.write(th, 14, orders[k].resource_type_cn, align_left)
                worksheet.write(th, 15, orders[k].start_date_cn, align_left)
                worksheet.write(th, 16, orders[k].end_date_cn, align_left)
                try:
                    worksheet.write(th, 9, mediums[0].medium.name, align_left)
                    worksheet.write(th, 10, mediums[0].sale_money, align_left)
                    worksheet.write(th, 11, mediums[0].medium_money2, align_left)
                    worksheet.write(
                        th, 12, mediums[0].medium_rebate_value, align_left)
                except:
                    pass
                th += 1
    workbook.close()
    response.data = output.getvalue()
    if otype == 'douban_order':
        filename = ("%s-%s.xls" %
                    (u"fix_date_douban", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    else:
        filename = ("%s-%s.xls" %
                    (u"fix_date", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
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


@other_bp.route('/fix_data', methods=['GET'])
def fix_data():
    if not g.user.is_super_leader():
        abort(403)
    year = int(request.values.get('year', 2015))
    year_date = datetime.datetime.strptime(str(year), '%Y')
    orders = [k for k in ClientOrder.all() if k.client_start.year ==
              year and k.contract_status not in [0, 7, 8, 9] and k.status == 1 and k.contract]
    for k in orders:
        for i in k.medium_orders:
            if int(k.self_agent_rebate.split('-')[0]) == 1:
                agent_rebate_value = float(k.self_agent_rebate.split('-')[1])
                if k.money:
                    i.medium_rebate_value = agent_rebate_value * i.sale_money / k.money
                else:
                    i.medium_rebate_value = 0
            else:
                medium_rebate = i.medium_rebate_by_year(year_date)
                i.medium_rebate_value = i.medium_money2 * medium_rebate / 100
        if int(k.self_agent_rebate.split('-')[0]) == 1:
            k.agent_rebate_value = float(k.self_agent_rebate.split('-')[1])
        else:
            agent_rebate = k.agent_rebate
            k.agent_rebate_value = k.money * agent_rebate / 100
    if request.values.get('action') == 'download':
        return write_fix_date(orders)
    return tpl('/fix_data.html', orders=orders, year=year)


@other_bp.route('/fix_data_douban', methods=['GET'])
def fix_data_douban():
    if not g.user.is_super_leader():
        abort(403)
    year = int(request.values.get('year', 2015))
    orders = [k for k in DoubanOrder.all() if k.client_start.year ==
              year and k.contract_status not in [0, 7, 8, 9] and k.status == 1 and k.contract]
    for k in orders:
        if int(k.self_agent_rebate.split('-')[0]) == 1:
            k.agent_rebate_value = float(k.self_agent_rebate.split('-')[1])
        else:
            agent_rebate = k.agent_rebate
            k.agent_rebate_value = k.money * agent_rebate / 100
    if request.values.get('action') == 'download':
        return write_fix_date(orders, 'douban_order')
    return tpl('/fix_data_douban.html', orders=orders, year=year)
