# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, redirect, url_for, g, abort, jsonify
from flask import render_template as tpl, flash

from models.user import User, UserOnDuty, Out, Leave


account_onduty_bp = Blueprint(
    'account_onduty', __name__, template_folder='../../templates/account/onduty/')


@account_onduty_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        onduty_file = request.files['file']
        data = onduty_file.readlines()
        for k in data:
            p = k.strip().split()
            if len(p) == 7:
                sn = p[0]
                check_time = datetime.datetime.strptime(
                    p[1] + ' ' + p[2], '%Y-%m-%d %H:%M:%S')
                user = User.query.filter_by(sn=sn).first()
                if user:
                    if not UserOnDuty.query.filter_by(sn=sn, check_time=check_time).first():
                        UserOnDuty.add(
                            user=user,
                            sn=sn,
                            check_time=check_time,
                            create_time=datetime.datetime.now()
                        )
        return redirect(url_for('account_onduty.index'))
    users = User.all_active()
    name = request.values.get('name', '')
    location = int(request.values.get('location', 0))
    if name:
        users = [k for k in users if k.name == name]
    if location:
        users = [k for k in users if k.location == location]
    return tpl('/account/onduty/index.html', users=users, name=name, location=location)


@account_onduty_bp.route('/<uid>/info', methods=['GET'])
def info(uid):
    user = User.get(uid)
    outs = [k for k in Out.all() if k.creator == user or user in k.joiners]
    leaves = list(Leave.query.filter_by(creator=user))
    start_time = request.values.get('start_time', '')
    end_time = request.values.get('end_time', '')
    if not start_time and not end_time:
        end_time = datetime.datetime.strptime(
            datetime.datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
        start_time = end_time - datetime.timedelta(days=30)
    else:
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    dutys = []
    s = start_time
    for k in range(1, (end_time - start_time).days + 2):
        d = s + datetime.timedelta(days=1)
        dus = UserOnDuty.query.filter_by(user=user).filter(
            UserOnDuty.check_time >= s, UserOnDuty.check_time < d)
        if dus.count() >= 2:
            on_time = dus[0].check_time.strftime('%Y-%m-%d %H:%M:%S')
            off_time = dus[-1].check_time.strftime('%Y-%m-%d %H:%M:%S')
        elif dus.count() < 2 and dus.count() > 0:
            on_time = dus[0].check_time.strftime('%Y-%m-%d %H:%M:%S')
            off_time = u'无'
        else:
            on_time = u'无'
            off_time = u'无'

        out_info = ""
        leave_info = ""
        for k in outs:
            if k.start_time_date <= s.date() and k.end_time_date >= s.date():
                out_info += u'外出时间：%s 至 %s<br/>'%(k.start_time_cn, k.end_time_cn)

        for k in leaves:
            if k.start_time_date <= s.date() and k.end_time_date >= s.date():
                leave_info += u'请假时间：%s点 至 %s点<br/>'%(k.start_time_cn, k.end_time_cn)

        dutys.append({'date_cn': s.strftime('%Y-%m-%d'),
                      'on_time': on_time,
                      'off_time': off_time,
                      'out_info': out_info,
                      'leave_info': leave_info})
        s = d

    return tpl('/account/onduty/info.html', user=user,
               start_time=start_time.strftime('%Y-%m-%d'),
               end_time=end_time.strftime('%Y-%m-%d'),
               dutys=dutys)
