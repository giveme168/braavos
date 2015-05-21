# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, request, g, flash, redirect, abort
from flask import render_template as tpl


from models.user import User
from models.douban_order import DoubanOrder
from forms.order import DoubanOrderForm
from models.client import Client, Agent

util_insert_douban_orders_bp = Blueprint(
    'util_insert_douban_orders', __name__, template_folder='../../templates/util')


@util_insert_douban_orders_bp.route('/', methods=['GET', 'POST'])
def index():
    if not g.user.is_super_admin():
        abort(402)
    form = DoubanOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = DoubanOrder.add(client=Client.get(form.client.data),
                                agent=Agent.get(form.agent.data),
                                campaign=form.campaign.data,
                                money=int(round(float(form.money.data or 0))),
                                medium_CPM=form.medium_CPM.data,
                                sale_CPM=form.sale_CPM.data,
                                client_start=form.client_start.data,
                                client_end=form.client_end.data,
                                reminde_date=form.reminde_date.data,
                                direct_sales=User.gets(form.direct_sales.data),
                                agent_sales=User.gets(form.agent_sales.data),
                                operaters=User.gets(form.operaters.data),
                                designers=User.gets(form.designers.data),
                                planers=User.gets(form.planers.data),
                                contract_type=form.contract_type.data,
                                resource_type=form.resource_type.data,
                                sale_type=form.sale_type.data,
                                creator=g.user,
                                contract=request.values.get('contract'),
                                contract_status=2,
                                create_time=datetime.now())
        order.add_comment(g.user,
                          u"导入了直签豆瓣订单:%s - %s - %s" % (
                              order.agent.name,
                              order.client.name,
                              order.campaign
                          ))
        flash(u'导入订单成功', 'success')
        return redirect(order.info_path())
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('insert_douban_order.html', form=form)