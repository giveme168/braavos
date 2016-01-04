# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, redirect, url_for
from flask import render_template as tpl

from models.user import User, UserOnDuty, Out, Leave

account_onduty_bp = Blueprint(
    'account_onduty', __name__, template_folder='../../templates/account/onduty/')

# 特殊日期
EXIT_DAYS = ['2016-01-01', '2016-02-06', '2016-02-14', '2016-04-04', '2016-05-02', '2016-06-09',
             '2016-06-10', '2016-09-15', '2016-09-16', '2016-10-03', '2016-10-04', '2016-10-05',
             '2016-10-06', '2016-10-07']
EXIT_DATE_TIMES = [datetime.datetime.strptime(
    k, '%Y-%m-%d') for k in EXIT_DAYS]


# 获取华北区某个销售违纪次数
def _get_unusual_by_user(user, start_date, end_date):
    default_recruited = datetime.datetime.strptime(
        '1970-01-01', '%Y-%m-%d')
    user_recruited = user.recruited_date
    # date to datetime
    start_date_time = datetime.datetime(*(start_date.timetuple()[:6]))
    end_date_time = datetime.datetime(*(end_date.timetuple()[:6]))
    # 所有请假
    user_leaves = list(Leave.query.filter_by(creator=user))
    # 所有外出
    user_outs = [k for k in list(Out.all()) if k.creator ==
                 user or user in k.joiners]
    if not user.sn or user_recruited == default_recruited or not user_recruited:
        # 没有员工编号或者没有填写入职时间视为新员工
        user.unusual_count = 0
    else:
        pre_days = _get_pre_dates(start_date_time, end_date_time)
        unusual_count = 0
        s = start_date_time
        for day in pre_days:
            d = s + datetime.timedelta(days=1)
            if day > user_recruited and day not in EXIT_DATE_TIMES and int(day.strftime('%w')) not in [0, 6]:
                dus = UserOnDuty.query.filter_by(user=user).filter(
                    UserOnDuty.check_time >= s, UserOnDuty.check_time < d)

                day_leave = [k for k in user_leaves if k.start_time_date <= s.date(
                ) and k.end_time_date >= s.date()]
                day_out = [k for k in user_outs if k.start_time_date <= s.date() and
                           k.end_time_date >= s.date() and k.status in [3, 4]]
                if dus.count() == 0:
                    if not day_leave and not day_out:
                        unusual_count += 1
                elif dus.count() == 1:
                    if not day_leave and not day_out:
                        unusual_count += 1
                else:
                    on_time = dus[0].check_time
                    off_time = dus[-1].check_time
                    offset_hour = (
                        off_time - on_time).total_seconds() / 60 / 60
                    if offset_hour < 9:
                        if not day_leave and not day_out:
                            unusual_count += 1
            s = d
        user.unusual_count = unusual_count
    return user


# 获取华北区销售违纪人员及次数
def _get_unusual(start_date, end_date):
    all_active_user = User.all_active()
    salers = [u for u in all_active_user if u.location == 1 and u.is_out_saler]
    last_check_date = _get_last_onduty_date()
    if last_check_date < start_date:
        for saler in salers:
            saler.unusual_count = 0
    else:
        for saler in salers:
            saler = _get_unusual_by_user(saler, start_date, end_date)
    return salers


# 获取开始至结束的每一天
def _get_pre_dates(start_date, end_date):
    days = (end_date - start_date).days
    dates = []
    for k in range(days + 1):
        date = start_date + datetime.timedelta(k)
        dates.append(date)
    return dates


# 获取上周周一、周五的日期
def _get_last_week_date():
    now_date = datetime.datetime.now()
    now_date = datetime.datetime.strptime('2016-01-01', '%Y-%m-%d')
    offset_day = int(now_date.strftime('%w'))
    if offset_day == 0:
        start_date = (now_date - datetime.timedelta(7 + 6)).date()
        end_date = (now_date - datetime.timedelta(7 + 2)).date()
    else:
        start_date = (now_date - datetime.timedelta(offset_day + 6)).date()
        end_date = (now_date - datetime.timedelta(offset_day + 2)).date()
    return start_date, end_date


# 获取最后一个打卡记录的日期
def _get_last_onduty_date():
    ondutys = UserOnDuty.query.all()
    try:
        return ondutys[-1].check_time.date()
    except:
        return ondutys[-1].check_time.date()


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


@account_onduty_bp.route('/unusual', methods=['GET'])
def unusual():
    start_date = request.values.get('start_date', '')
    end_date = request.values.get('end_date', '')
    if not start_date and not end_date:
        start_date, end_date = _get_last_week_date()
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    users = _get_unusual(start_date, end_date)
    return tpl('/account/onduty/unusual_index.html', users=users, location=1,
               start_date=start_date, end_date=end_date)


@account_onduty_bp.route('/<uid>/info', methods=['GET'])
def info(uid):
    user = User.get(uid)
    outs = [k for k in list(Out.all()) if k.creator ==
            user or user in k.joiners]
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
        warning_info = ""
        for k in outs:
            if k.start_time_date <= s.date() and k.end_time_date >= s.date():
                out_info += u'外出时间：%s 至 %s<br/>' % (
                    k.start_time_cn, k.end_time_cn)

        for k in leaves:
            if k.start_time_date <= s.date() and k.end_time_date >= s.date():
                leave_info += u'请假时间：%s点 至 %s点<br/>' % (
                    k.start_time_cn, k.end_time_cn)

        if not out_info and not leave_info:
            if user.sn and s not in EXIT_DATE_TIMES and int(s.strftime('%w')) not in [0, 6]:
                if dus.count() >= 2:
                    on_time = dus[0].check_time
                    off_time = dus[-1].check_time
                    offset_hour = (
                        off_time - on_time).total_seconds() / 60 / 60
                    if offset_hour < 9:
                        warning_info += u'工时未满8小时'
                else:
                    warning_info += u'工时未满8小时'
        dutys.append({'date_cn': s.strftime('%Y-%m-%d'),
                      'on_time': on_time,
                      'off_time': off_time,
                      'out_info': out_info,
                      'warning_info': warning_info,
                      'leave_info': leave_info})
        s = d

    return tpl('/account/onduty/info.html', user=user,
               start_time=start_time.strftime('%Y-%m-%d'),
               end_time=end_time.strftime('%Y-%m-%d'),
               dutys=dutys)
