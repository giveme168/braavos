# -*- coding: utf-8 -*-
import datetime
import json
from flask import Blueprint, request, g, abort
from flask import render_template as tpl
from models.user import User
from models.client_order import EditClientOrder, SUBJECT_CN
from controllers.finance.helpers.edit_order_helpers import write_edit_order_excel

from libs.paginator import Paginator

finance_client_order_edit_order_bp = Blueprint('finance_client_order_edit_order', __name__,
                                               template_folder='../../templates/finance/client_order/')


@finance_client_order_edit_order_bp.route('/', methods=['GET'])
def index():
    if not g.user.is_finance():
        abort(404)
    page = int(request.values.get('p', 1))
    now_date = datetime.datetime.now()
    year = int(request.values.get('year', now_date.year))
    month = int(request.values.get('month', now_date.month))
    search_info = request.values.get('search_info', '')
    orders = [order for order in EditClientOrder.query.filter_by(contract_status=10)
              if order.create_time.year == year and order.create_time.month == month]
    for order in orders:
        edit_objs = []
        prim_client_order_data = json.loads(order.prim_client_order_data)
        if order.agent.name != prim_client_order_data['agent_name']:
            last = u'代理/直客：' + prim_client_order_data['agent_name']
            now = u'代理/直客：' + order.agent.name
            edit_objs.append([last, now])
        if order.client.name != prim_client_order_data['client_name']:
            last = u'客户：' + prim_client_order_data['client_name']
            now = u'客户：' + order.client.name
            edit_objs.append([last, now])
        if 'subject' in prim_client_order_data:
            if order.subject != prim_client_order_data['subject']:
                last = u'签约主体：' + SUBJECT_CN[prim_client_order_data['subject']]
                now = u'签约主体：' + order.subject_cn
                edit_objs.append([last, now])
        if order.campaign != prim_client_order_data['campaign']:
            last = u'campaign：' + prim_client_order_data['campaign']
            now = u'campaign：' + order.campaign
            edit_objs.append([last, now])
        if order.money != prim_client_order_data['money']:
            last = u'客户金额：' + str(prim_client_order_data['money'])
            now = u'客户金额：' + str(order.money)
            edit_objs.append([last, now])
        if order.start_date_cn != prim_client_order_data['client_start']:
            last = u'执行开始：' + prim_client_order_data['client_start']
            now = u'执行开始：' + order.start_date_cn
            edit_objs.append([last, now])
        if order.end_date_cn != prim_client_order_data['client_end']:
            last = u'执行结束：' + prim_client_order_data['client_end']
            now = u'执行结束：' + order.end_date_cn
            edit_objs.append([last, now])
        if order.reminde_date_cn != prim_client_order_data['reminde_date']:
            last = u'回款时间：' + prim_client_order_data['reminde_date']
            now = u'回款时间：' + order.reminde_date_cn
            edit_objs.append([last, now])
        if set(order.direct_sales_ids) != set(prim_client_order_data['direct_sales']):
            last = u'直客销售：' + ','.join([u.name for u in User.gets(prim_client_order_data['direct_sales'])])
            now = u'直客销售：' + order.direct_sales_names
            edit_objs.append([last, now])
        if set(order.agent_sales_ids) != set(prim_client_order_data['agent_sales']):
            last = u'渠道销售：' + ','.join([u.name for u in User.gets(prim_client_order_data['agent_sales'])])
            now = u'渠道销售：' + order.agent_sales_names
            edit_objs.append([last, now])
        if set(order.assistant_sales_ids) != set(prim_client_order_data['assistant_sales']):
            last = u'销售助理：' + ','.join([u.name for u in User.gets(prim_client_order_data['assistant_sales'])])
            now = u'销售助理：' + order.assistant_sales_names
            edit_objs.append([last, now])
        if order.contract_type != prim_client_order_data['contract_type']:
            last = u'合同模板：' + prim_client_order_data['contract_type_cn']
            now = u'合同模板：' + order.contract_type_cn
            edit_objs.append([last, now])
        if order.resource_type != prim_client_order_data['resource_type']:
            last = u'售卖类型：' + prim_client_order_data['resource_type_cn']
            now = u'售卖类型：' + order.resource_type_cn
            edit_objs.append([last, now])
        if order.sale_type != prim_client_order_data['sale_type']:
            last = u'代理 or 直客：' + prim_client_order_data['sale_type_cn']
            now = u'代理 or 直客：' + order.sale_type_cn
            edit_objs.append([last, now])
        if order.self_agent_rebate != prim_client_order_data['self_agent_rebate']:
            if prim_client_order_data['self_agent_rebate']:
                p_self_agent_rebate = prim_client_order_data['self_agent_rebate'].split('-')
            else:
                p_self_agent_rebate = ['0', '0.0']
            status = p_self_agent_rebate[0]
            value = str(p_self_agent_rebate[1])
            if int(status):
                last = u'客户单笔返点：' + str(value)
            else:
                last = u'无客户单笔返点'
            if int(order.self_agent_rebate_value['status']):
                now = u'客户单笔返点：' + str(order.self_agent_rebate_value['value'])
            else:
                now = u'无客户单笔返点'
            edit_objs.append([last, now])
        for m in order.medium_orders:
            prim_order_data = json.loads(m.prim_order_data)
            edit_objs.append(['%s-%s媒体合同修改项:' % (m.medium_group.name, m.media.name), '', 'col'])
            if m.medium_group.id != prim_order_data['medium_group_id']:
                last = u'媒体供应商：' + prim_order_data['medium_group_cn']
                now = u'媒体供应商：' + m.medium_group.name
                edit_objs.append([last, now])
            if m.media.id != prim_order_data['media_id']:
                last = u'媒体：' + prim_order_data['media_name']
                now = u'媒体：' + m.media.name
                edit_objs.append([last, now])
            if m.sale_money != prim_order_data['sale_money']:
                last = u'售卖金额：' + str(prim_order_data['sale_money'])
                now = u'售卖金额：' + str(m.sale_money)
                edit_objs.append([last, now])
            if m.medium_money2 != prim_order_data['medium_money2']:
                last = u'媒体金额：' + str(prim_order_data['medium_money2'])
                now = u'媒体金额：' + str(m.medium_money2)
                edit_objs.append([last, now])
            if m.sale_CPM != prim_order_data['sale_CPM']:
                last = u'预估量CPM：' + str(prim_order_data['sale_CPM'])
                now = u'预估量CPM' + str(m.sale_CPM)
                edit_objs.append([last, now])
            if m.medium_CPM != prim_order_data['medium_CPM']:
                last = u'实际CPM：' + str(prim_order_data['medium_CPM'])
                now = u'实际CPM' + str(m.medium_CPM)
                edit_objs.append([last, now])
            if m.start_date_cn != prim_order_data['medium_start']:
                last = u'执行开始：' + str(prim_order_data['medium_start'])
                now = u'执行开始：' + m.start_date_cn
                edit_objs.append([last, now])
            if m.end_date_cn != prim_order_data['medium_end']:
                last = u'执行结束：' + str(prim_order_data['medium_end'])
                now = u'执行结束：' + m.end_date_cn
                edit_objs.append([last, now])
            if m.operaters_ids != prim_order_data['operaters']:
                last = u'执行人员：' + ','.join([u.name for u in User.gets(prim_order_data['operaters'])])
                now = u'执行人员：' + m.operater_names
                edit_objs.append([last, now])
            if m.designers_ids != prim_order_data['designers']:
                last = u'设计人员：' + ','.join([u.name for u in User.gets(prim_order_data['designers'])])
                now = u'设计人员：' + m.designer_names
                edit_objs.append([last, now])
            if m.planers_ids != prim_order_data['planers']:
                last = u'策划人员：' + ','.join([u.name for u in User.gets(prim_order_data['planers'])])
                now = u'策划人员：' + m.planers_names
                edit_objs.append([last, now])
            if m.self_medium_rebate != prim_order_data['self_medium_rebate']:
                if prim_order_data['self_medium_rebate']:
                    p_self_medium_rebate = prim_order_data['self_medium_rebate'].split('-')
                else:
                    p_self_medium_rebate = ['0', '0.0']
                status = p_self_medium_rebate[0]
                value = str(p_self_medium_rebate[1])
                if int(status):
                    last = u'媒体单笔返点：' + str(value)
                else:
                    last = u'无媒体单笔返点'
                if int(m.self_medium_rebate_value['status']):
                    now = u'媒体单笔返点：' + str(m.self_medium_rebate_value['value'])
                else:
                    now = u'无媒体单笔返点'
                edit_objs.append([last, now])
        order.edit_objs = edit_objs
    if request.values.get('action') == 'excel':
        return write_edit_order_excel(orders, year, month)
    paginator = Paginator(orders, 50)
    try:
        orders = paginator.page(page)
    except:
        orders = paginator.page(paginator.num_pages)
    return tpl('/finance/client_order/edit_order/index.html', orders=orders, year=year, month=month,
               search_info=search_info, params='&search_info=%s&year=%s&month=%s' % (search_info, year, month))
