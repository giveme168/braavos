# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, jsonify, g
from flask import render_template as tpl
from models.other import NianHui
other_bp = Blueprint('other', __name__, template_folder='../templates/other')


JM = {1: u'《try everthing》',
      2: u'《歌曲串烧》',
      3: u'《致趣联播》',
      4: u'《我也是歌手》',
      5: u'《脱口秀》',
      6: u'《蒙面歌王》',
      7: u'《INAD加油》',
      8: u'《uptown funk》',
      9: u'《极限挑战》',
      10: u'《台前幕后》',
      11: u'《狐狸说嘛呢》'}


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
    ids = '|'.join([k.ids for k in NianHui.all()])
    jm_count = {}
    total_count = 0
    for k, v in JM.items():
        jm_count[k] = 0
    for k in ids.split('|'):
        total_count += 1
        if int(k) in jm_count:
            jm_count[int(k)] += 1
    jm_count = sorted(jm_count.iteritems(), key=lambda x: x[1])
    jm_count.reverse()
    res = []
    for k in jm_count:
        res.append({'name': JM[k[0]], 'count': k[1], 'percent': float(k[1])/total_count*100})
    return tpl('/other/nhs.html', res=res, total_count=total_count)
