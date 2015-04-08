# -*- coding: utf-8 -*-
import datetime

import xlrd
from xpinyin import Pinyin
from flask import Blueprint, request, g
from flask import render_template as tpl

from models.user import User, Team
from models.client_order import ClientOrder
from models.order import Order
from models.client import Client, Group, Agent
from models.medium import Medium

util_upload_orders_bp = Blueprint(
    'util_upload_orders', __name__, template_folder='../../templates/util')
p = Pinyin()


@util_upload_orders_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['upload_file']
        xls_orders = '/tmp/uploads/' + f.filename.encode('utf8')
        f.save(xls_orders)
        if xls_orders:
            _fix_orders(xlrd.open_workbook(xls_orders))
            # try:
            #    _fix_orders(xlrd.open_workbook(xls_orders))
            # except Exception, e:
            #    print str(e)
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
            order_param = {}
            order_param['agent_name'] = table.col(0)[i].value
            order_param['client_name'] = table.col(1)[i].value
            order_param['campaign'] = table.col(2)[i].value
            order_param['contract'] = table.col(3)[i].value
            order_param['money'] = int(table.col(4)[i].value)
            order_param['medium_start'] = datetime.datetime(
                *xlrd.xldate_as_tuple(table.col(5)[i].value, excel_data.datemode)).date()
            order_param['medium_end'] = datetime.datetime(
                *xlrd.xldate_as_tuple(table.col(6)[i].value, excel_data.datemode)).date()
            order_param['reminde_date'] = datetime.datetime(
                *xlrd.xldate_as_tuple(table.col(7)[i].value, excel_data.datemode)).date()
            order_param['agent_sale_name'] = table.col(8)[i].value
            # 合同模板类型
            order_param['contract_type'] = table.col(9)[i].value
            # 合同资源形式
            order_param['resource_type'] = table.col(10)[i].value
            order_param['sale_type'] = table.col(11)[i].value
            order_param['medium_name'] = table.col(12)[i].value
            order_param['medium_contract'] = table.col(13)[i].value
            order_param['medium_money'] = table.col(14)[i].value
            _into_order(order_param)
    return


def _into_order(param):
    group = Group.query.filter_by(name=u'默认集团').first()
    if not group:
        group = Group.add(name=u'默认集团')
        group.save()

    agent = Agent.query.filter_by(name=param['agent_name']).first()
    if not agent:
        agent = Agent.add(name=param['agent_name'],
                          group=group,
                          tax_num='',
                          address='',
                          phone_num='',
                          bank='',
                          bank_num='',
                          )

    client = Client.query.filter_by(name=param['client_name']).first()
    if not client:
        client = Client.add(name=param['client_name'], industry=1)
        # client.save()

    medium = Medium.query.filter_by(name=param['medium_name']).first()
    if not medium:
        medium = Medium.add(name=param['medium_name'],
                            abbreviation=param['medium_name'],
                            tax_num='',
                            address='',
                            phone_num='',
                            bank='',
                            bank_num='',
                            owner=Team.query.filter_by(type=8).first()
                            )

    team = Team.query.filter_by(name=u'导入渠道销售团队').first()
    if not team:
        team = Team.add(
            name=u'导入渠道销售团队',
            type=4,
            location=0,
            admins=[],
        )
        # team.save()

    if not param['agent_sale_name']:
        agents = []
    else:
        agent_names = param['agent_sale_name'].split(' ')
        agents = []
        for k in agent_names:
            name = k.strip()
            p_name = p.get_pinyin(name, '').lower()
            email = p_name + '@inad.com'
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User.add(name, email, 'pwd@inad', team, 1)
            agents.append(user.id)

    if param['contract_type'].find(u'非标') >= 0:
        contract_type = 1
    else:
        contract_type = 0

    if param['resource_type'].find(u'硬广') >= 0:
        resource_type = 0
    elif param['resource_type'].find(u'互动') >= 0:
        resource_type = 1
    else:
        resource_type = 4

    if param['sale_type'] == u'代理':
        sale_type = 0
    else:
        sale_type = 1

    order = ClientOrder.add(
        agent=agent,
        client=client,
        campaign=param['campaign'],
        money=param['money'],
        client_start=param['medium_start'],
        client_end=param['medium_end'],
        reminde_date=param['reminde_date'],
        direct_sales=[],
        agent_sales=User.gets(agents),
        contract_type=contract_type,
        resource_type=resource_type,
        sale_type=sale_type,
        creator=g.user,
        create_time=datetime.datetime.now(),
    )
    order.add_comment(g.user,
                      u"新建了客户订单:%s - %s - %s" % (
                          order.agent.name,
                          order.client.name,
                          order.campaign
                      ))
    mo = Order.add(campaign=order.campaign,
                   medium=medium,
                   sale_money=param['money'],
                   medium_money=0,
                   medium_money2=0,
                   medium_start=param['medium_start'],
                   medium_end=param['medium_end'],
                   creator=g.user)
    order.add_comment(g.user, u"新建了媒体订单: %s %s元" %
                      (medium.name, mo.sale_money))
    order.medium_orders = [mo]
    order.save()
    return
