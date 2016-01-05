# -*- coding: utf-8 -*-
from flask import Blueprint, request, flash
from flask import render_template as tpl
from models.user import User
from models.client_order import ClientOrder
from models.douban_order import DoubanOrder

account_turnover_bp = Blueprint(
    'account_turnover', __name__, template_folder='../../templates/account/turnover/')


@account_turnover_bp.route('/index', methods=['GET', 'POST'])
def index():
    salers = User.sales()
    if request.method == 'POST':
        f_saler = int(request.values.get('f_saler', 0))
        t_saler = int(request.values.get('t_saler', 0))
        if not f_saler or not t_saler:
            flash(u'请选择正确的员工', 'danger')
            return tpl('/account/turnover/index.html', salers=salers)
        f_user = User.get(f_saler)
        t_user = User.get(t_saler)
        client_orders = ClientOrder.all()
        douban_orders = DoubanOrder.all()
        for k in client_orders:
            if f_user in k.salers and t_user not in k.replace_sales:
                k.replace_sales = k.replace_sales+[t_user]
                k.save()
        for k in douban_orders:
            if f_user in k.salers and t_user not in k.replace_sales:
                k.replace_sales = k.replace_sales+[t_user]
                k.save()
        flash(u'成功', 'success')
    return tpl('/account/turnover/index.html', salers=salers)
