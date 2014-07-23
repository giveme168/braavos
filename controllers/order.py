#-*- coding: UTF-8 -*-
import datetime

from flask import Blueprint, request, redirect, abort, url_for, g
from flask import render_template as tpl

from models.order import Order
from forms.order import OrderForm
from models.client import Client, Agent
from models.medium import Medium
from models.user import User

order_bp = Blueprint('order', __name__, template_folder='../templates/order')


@order_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('order.orders'))


@order_bp.route('/new_order', methods=['GET', 'POST'])
def new_order():
    form = OrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = Order(client=Client.get(form.client.data), campaign=form.campaign.data,
                      medium=Medium.get(form.medium.data), order_type=form.order_type.data,
                      contract=form.contract.data, money=form.money.data,
                      agent=Agent.get(form.agent.data), direct_sales=User.gets(form.direct_sales.data),
                      agent_sales=User.gets(form.agent_sales.data), operaters=User.gets(form.operaters.data),
                      planers=User.gets(form.planers.data), designers=User.gets(form.designers.data), creator=g.user,
                      create_time=datetime.datetime.now())
        order.add()
        return redirect(url_for("order.orders"))
    else:
        form.creator.data = g.user.name
    return tpl('new_order.html', form=form)


@order_bp.route('/order_detail/<order_id>', methods=['GET', 'POST'])
def order_detail(order_id):
    order = Order.get(order_id)
    if not order:
        abort(404)
    form = OrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order.client = Client.get(form.client.data)
        order.campaign = form.campaign.data
        order.medium = Medium.get(form.medium.data)
        order.order_type = form.order_type.data
        order.contract = form.contract.data
        order.money = form.money.data
        order.agent = Agent.get(form.agent.data)
        order.direct_sales = User.gets(form.direct_sales.data)
        order.agent_sales = User.gets(form.agent_sales.data)
        order.operaters = User.gets(form.operaters.data)
        order.designers = User.gets(form.designers.data)
        order.planers = User.gets(form.planers.data)
        order.save()
        return redirect(url_for("order.orders"))
    else:
        form.client.data = order.client.id
        form.campaign.data = order.campaign
        form.medium.choices = [(order.medium.id, order.medium.name)]
        form.medium.data = order.medium.id
        form.order_type.data = order.order_type
        form.contract.data = order.contract
        form.money.data = order.money
        form.agent.data = order.agent.id
        form.direct_sales.data = [u.id for u in order.direct_sales]
        form.agent_sales.data = [u.id for u in order.agent_sales]
        form.operaters.data = [u.id for u in order.operaters]
        form.designers.data = [u.id for u in order.designers]
        form.planers.data = [u.id for u in order.planers]
        form.creator.data = order.creator.name
    return tpl('order.html', form=form, order=order)


@order_bp.route('/orders', methods=['GET'])
def orders():
    orders = Order.all()
    return tpl('orders.html', orders=orders)
