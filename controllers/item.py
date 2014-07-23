#-*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for, g
from flask import render_template as tpl

from models.item import AdItem
from forms.item import ItemForm
from models.order import Order

item_bp = Blueprint('item', __name__, template_folder='../templates/item')


@item_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('item.create_item'))


@item_bp.route('/new_item', methods=['GET', 'POST'])
def new_item():
    order = Order.get(request.values.get("order"))
    if not order:
        abort(404)
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        pass
    form.order.data = order.name
    form.order.readonly = True
    return tpl('new_item.html', form=form, order=order)
