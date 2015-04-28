# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, request, g, flash, redirect, abort
from flask import render_template as tpl


from models.user import User
from models.framework_order import FrameworkOrder
from forms.order import FrameworkOrderForm
from models.client import Agent, Group

util_insert_framework_orders_bp = Blueprint(
    'util_insert_framework_orders', __name__, template_folder='../../templates/util')


@util_insert_framework_orders_bp.route('/', methods=['GET', 'POST'])
def index():
    if not g.user.is_super_admin():
        abort(402)
    form = FrameworkOrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = FrameworkOrder.add(group=Group.get(form.group.data),
                                   agents=Agent.gets(form.agents.data),
                                   description=form.description.data,
                                   money=int(
                                       round(float(form.money.data or 0))),
                                   client_start=form.client_start.data,
                                   client_end=form.client_end.data,
                                   reminde_date=form.reminde_date.data,
                                   direct_sales=User.gets(
                                       form.direct_sales.data),
                                   agent_sales=User.gets(form.agent_sales.data),
                                   contract_type=form.contract_type.data,
                                   creator=g.user,
                                   contract_status=2,
                                   contract=request.values.get('contract'),
                                   create_time=datetime.now())
        order.add_comment(g.user, u"导入了框架订单")
        flash(u'导入框架订单成功', 'success')
        return redirect(order.info_path())
    else:
        form.client_start.data = datetime.now().date()
        form.client_end.data = datetime.now().date()
        form.reminde_date.data = datetime.now().date()
    return tpl('insert_framework_order.html', form=form)
