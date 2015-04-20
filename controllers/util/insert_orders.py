# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, request, g, flash, redirect, abort
from flask import render_template as tpl

from forms.order import ClientOrderForm

from models.user import User
from models.client_order import ClientOrder
from models.order import Order
from models.client import Client, Agent
from models.medium import Medium

util_insert_orders_bp = Blueprint(
    'util_insert_orders', __name__, template_folder='../../templates/util')


######################
# client order
######################
@util_insert_orders_bp.route('/', methods=['GET', 'POST'])
def index():
    if not g.user.is_super_admin():
        abort(402)
    form = ClientOrderForm(request.form)
    mediums = [(m.id, m.name) for m in Medium.all()]
    if request.method == 'POST' and form.validate():
        order = ClientOrder.add(agent=Agent.get(form.agent.data),
                                client=Client.get(form.client.data),
                                campaign=form.campaign.data,
                                money=int(round(float(form.money.data or 0))),
                                client_start=form.client_start.data,
                                client_end=form.client_end.data,
                                reminde_date=form.reminde_date.data,
                                direct_sales=User.gets(form.direct_sales.data),
                                agent_sales=User.gets(form.agent_sales.data),
                                contract_type=form.contract_type.data,
                                resource_type=form.resource_type.data,
                                sale_type=form.sale_type.data,
                                contract=request.values.get('contract', ''),
                                creator=g.user,
                                contract_status=2,
                                create_time=datetime.now())
        order.add_comment(g.user,
                          u"导入了客户订单:%s - %s - %s" % (
                              order.agent.name,
                              order.client.name,
                              order.campaign
                          ))
        medium_ids = request.values.getlist('medium')
        medium_moneys = request.values.getlist('medium_money')
        medium_moneys2 = request.values.getlist('medium_money2')
        medium_contracts = request.values.getlist('medium_contract')
        if medium_ids and medium_moneys and len(medium_ids) == len(medium_moneys):
            for x in range(len(medium_ids)):
                medium = Medium.get(medium_ids[x])
                mo = Order.add(campaign=order.campaign,
                               medium=medium,
                               sale_money=0,
                               medium_money=int(
                                   round(float(medium_moneys[x] or 0))),
                               medium_money2=int(
                                   round(float(medium_moneys2[x] or 0))),
                               medium_contract=medium_contracts[x],
                               medium_start=order.client_start,
                               medium_end=order.client_end,
                               creator=g.user)
                order.medium_orders = order.medium_orders + [mo]
                order.add_comment(g.user, u"导入了媒体订单: %s %s元" %
                                  (medium.name, mo.sale_money))
            order.save()
        flash(u'导入客户订单成功!', 'success')
        return redirect(order.info_path())
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('insert_order.html', form=form, mediums=mediums)
