# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, request, redirect, g
from flask import render_template as tpl

from models.user import UserHandBook

account_data_bp = Blueprint(
    'account_data', __name__, template_folder='../../templates/account/data/')


@account_data_bp.route('/handbook', methods=['GET', 'POST'])
def handbook():
    if request.method == 'POST':
        user_hand_book = UserHandBook.query.filter_by(user=g.user).first()
        if not user_hand_book:
            UserHandBook.add(user=g.user, create_time=datetime.datetime.now())
        return redirect('/')
    return tpl('/account/data/handbook.html')
