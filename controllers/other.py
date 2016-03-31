# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, jsonify, g
from flask import render_template as tpl
from models.other import NianHui
other_bp = Blueprint('other', __name__, template_folder='../templates/other')


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
    return tpl('/other/nhs.html')
