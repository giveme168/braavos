# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, redirect, url_for, flash, abort, g
from flask import render_template as tpl

from models.user import User, UserOnDuty, Leave, OutReport
from controllers.account.helpers.onduty_helpers import write_ondutys_excel

account_onduty_bp = Blueprint(
    'account_onduty', __name__, template_folder='../../templates/account/onduty/')

# 特殊日期
EXIT_DAYS = ['2016-01-01', '2016-02-06', '2016-02-07', '2016-02-08', '2016-02-09', '2016-02-10',
             '2016-02-11', '2016-02-12', '2016-02-13', '2016-02-14', '2016-04-04', '2016-05-02',
             '2016-06-09', '2016-06-10', '2016-09-15', '2016-09-16', '2016-10-03', '2016-10-04',
             '2016-10-05', '2016-10-06', '2016-10-07']
EXIT_DATE_TIMES = [datetime.datetime.strptime(
    k, '%Y-%m-%d') for k in EXIT_DAYS]


# 格式化外出报备
def _format_out():
    outs = list(OutReport.all())
    fout = []
    for k in outs:
        fout.append({'start_time': k.start_time,
                     'end_time': k.end_time,
                     'create_time': k.create_time,
                     'status': k.status,
                     'start_time_date': k.start_time.date(),
                     'end_time_date': k.end_time.date(),
                     'start_time_cn': k.start_time.strftime('%Y-%m-%d %H:%M'),
                     'end_time_cn': k.end_time.strftime('%Y-%m-%d %H:%M'),
                     'creator': k.creator,
                     'creator_id': int(k.creator.id)})
        '''
        for i in k.joiners:
            fout.append({'start_time': k.start_time,
                         'end_time': k.end_time,
                         'create_time': k.create_time,
                         'status': k.status,
                         'start_time_date': k.start_time_date,
                         'end_time_date': k.end_time_date,
                         'start_time_cn': k.start_time.strftime('%Y-%m-%d %H:%M'),
                         'end_time_cn': k.end_time.strftime('%Y-%m-%d %H:%M'),
                         'creator': i,
                         'creator_id': int(i.id)})
        '''
    return fout


# 格式化请假申请
def _format_leave():
    leaves = list(Leave.all())
    fleaves = []
    for k in leaves:
        fleaves.append({'start_time': k.start_time,
                        'end_time': k.end_time,
                        'create_time': k.create_time,
                        'start_time_date': k.start_time.date(),
                        'end_time_date': k.end_time.date(),
                        'start_time_cn': k.start_time.strftime('%Y-%m-%d %H'),
                        'end_time_cn': k.end_time.strftime('%Y-%m-%d %H'),
                        'status': k.status,
                        'creator': k.creator,
                        'creator_id': int(k.creator.id)})
    return fleaves


# 格式化考勤
def _format_onduty(start_time, end_time):
    onduty = UserOnDuty.query.filter(UserOnDuty.check_time >= start_time,
                                     UserOnDuty.check_time < end_time)
    fonduty = []
    for k in onduty:
        fonduty.append({'check_time': k.check_time,
                        'check_time_cn': k.check_time.strftime('%Y-%m-%d %H:%M:%S'),
                        # 'user': k.user,
                        'user_id': k.user.id,
                        'id': k.id})
    return fonduty


# 获取华北区某个销售违纪次数
def _get_unusual_by_user(all_dus, outs, leaves, user, start_date, end_date):
    default_recruited = datetime.datetime.strptime(
        '1970-01-01', '%Y-%m-%d')
    user_recruited = user.recruited_date
    # date to datetime
    start_date_time = datetime.datetime(*(start_date.timetuple()[:6]))
    end_date_time = datetime.datetime(*(end_date.timetuple()[:6]))
    # 所有请假
    user_leaves = [k for k in leaves if k['creator_id']
                   == int(user.id)]
    # 所有外出
    user_outs = [k for k in outs if k['creator_id'] == int(user.id)]

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
                dus = [k for k in all_dus if k['check_time'] >= s and k[
                    'check_time'] < d and k['user_id'] == int(user.id)]
                day_leave = [k for k in user_leaves if k['start_time_date'] <= s.date(
                ) and k['end_time_date'] >= s.date()]
                day_out = [k for k in user_outs if k['start_time_date'] <= s.date() and
                           k['end_time_date'] >= s.date() and k['status'] in [3, 4]]
                if len(dus) == 0:
                    if not day_leave and not day_out:
                        unusual_count += 1
                elif len(dus) == 1:
                    if not day_leave and not day_out:
                        unusual_count += 1
                else:
                    on_time = dus[0]['check_time']
                    off_time = dus[-1]['check_time']
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
    offset_day = int(now_date.strftime('%w'))
    if offset_day == 0:
        start_date = (now_date - datetime.timedelta(7 + 6))
        end_date = (now_date - datetime.timedelta(7 + 2))
    else:
        start_date = (now_date - datetime.timedelta(offset_day + 6))
        end_date = (now_date - datetime.timedelta(offset_day + 2))
    return start_date, end_date


# 获取最后一个打卡记录的日期
def _get_last_onduty_date():
    ondutys = UserOnDuty.query.all()
    try:
        return ondutys[-1].check_time.date()
    except:
        return ondutys[-1].check_time.date()


# 获取区间时间内的考勤
def _get_onduty(all_dus, outs, leaves, user, start_time, end_time, last_onduty_date):
    dutys = []
    s = start_time
    for d in range(1, (end_time - start_time).days + 2):
        d = s + datetime.timedelta(days=1)
        dus = [k for k in all_dus if k['check_time'] >= s and k[
            'check_time'] < d and k['user_id'] == int(user.id)]
        if len(dus) >= 2:
            on_time_str = dus[0]['check_time'].strftime('%Y-%m-%d %H:%M:%S')
            off_time_str = dus[-1]['check_time'].strftime('%Y-%m-%d %H:%M:%S')
        elif len(dus) < 2 and len(dus) > 0:
            on_time_str = dus[0]['check_time'].strftime('%Y-%m-%d %H:%M:%S')
            off_time_str = u'无'
        else:
            on_time_str = u'无'
            off_time_str = u'无'

        out_info = ""
        leave_info = ""
        warning_info = ""
        for k in outs:
            if k['start_time_date'] <= s.date() and k['end_time_date'] >= s.date():
                out_info += u'外出时间：%s 至 %s<br/>' % (
                    k['start_time_cn'], k['end_time_cn'])
        for k in leaves:
            if k['start_time_date'] <= s.date() and k['end_time_date'] >= s.date():
                leave_info += u'请假时间：%s点 至 %s点<br/>' % (
                    k['start_time_cn'], k['end_time_cn'])
        # 入职时间
        try:
            recruited_date = user.recruited_date.date()
        except:
            recruited_date = datetime.datetime.now().date()
        warning_count = 0
        if not (leave_info + out_info) and d.date() <= last_onduty_date and recruited_date <= d.date():
            if user.sn and s not in EXIT_DATE_TIMES and int(s.strftime('%w')) not in [0, 6]:
                if len(dus) >= 2:
                    on_time = dus[0]['check_time']
                    off_time = dus[-1]['check_time']
                    on_time_str = on_time.strftime('%Y-%m-%d %H:%M:%S')
                    off_time_str = off_time.strftime('%Y-%m-%d %H:%M:%S')
                    offset_hour = (
                        off_time - on_time).total_seconds() / 60 / 60
                    if offset_hour < 9:
                        warning_info += u'工时未满8小时'
                        warning_count += 1
                else:
                    warning_info += u'工时未满8小时'
                    warning_count += 1
        dutys.append({'date_cn': s.strftime('%Y-%m-%d'),
                      'on_time': on_time_str,
                      'off_time': off_time_str,
                      'out_info': out_info,
                      'warning_info': warning_info,
                      'leave_info': leave_info,
                      'warning_count': warning_count,
                      'dus': dus})
        s = d
    return dutys


@account_onduty_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.values.get('action', '') == 'excel':
            start_date = request.values.get('start_date')
            end_date = request.values.get('end_date')
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            outs = _format_out()
            leaves = _format_leave()
            all_dus = _format_onduty(start_date, end_date)
            # 打卡最后一次时间
            last_onduty_date = _get_last_onduty_date()
            duty_obj = []
            for user in User.all_active():
                u_outs = [k for k in outs if k['creator_id'] == int(user.id)]
                u_leaves = [k for k in leaves if k[
                    'creator_id'] == int(user.id)]
                dutys = _get_onduty(all_dus, u_outs, u_leaves,
                                    user, start_date, end_date, last_onduty_date)
                duty_obj.append({'count': sum(item['warning_count'] for item in dutys),
                                 'user': user})
            return write_ondutys_excel(duty_obj, start_date, end_date)
        else:
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
                                create_time=datetime.datetime.now(),
                                type=0
                            )
            return redirect(url_for('account_onduty.index'))
    now_date = datetime.datetime.now()
    now_month_first_day = now_date.replace(day=1)
    end_date = (now_month_first_day - datetime.timedelta(days=1)).date()
    start_date = end_date.replace(day=1)

    users = User.all_active()
    name = request.values.get('name', '')
    location = int(request.values.get('location', 0))
    if name:
        users = [k for k in users if k.name == name]
    if location:
        users = [k for k in users if k.location == location]
    return tpl('/account/onduty/index.html', users=users, name=name, location=location,
               start_date=start_date, end_date=end_date)


@account_onduty_bp.route('/unusual', methods=['GET'])
def unusual():
    start_date = request.values.get('start_date', '')
    end_date = request.values.get('end_date', '')
    if not start_date and not end_date:
        start_date, end_date = _get_last_week_date()
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    all_active_user = User.all_active()
    salers = [u for u in all_active_user if u.location == 1 and u.is_out_saler]
    outs = _format_out()
    leaves = _format_leave()
    all_dus = _format_onduty(start_date, end_date)
    # 打卡最后一次时间
    last_onduty_date = _get_last_onduty_date()
    users = []
    for user in salers:
        u_outs = [k for k in outs if k['creator_id'] == int(user.id)]
        u_leaves = [k for k in leaves if k['creator_id'] == int(user.id)]
        dutys = _get_onduty(all_dus, u_outs, u_leaves, user,
                            start_date, end_date, last_onduty_date)
        users.append({'count': sum(item['warning_count'] for item in dutys),
                      'user': user})
    return tpl('/account/onduty/unusual_index.html', users=users, location=1,
               start_date=start_date.date(), end_date=end_date.date())


@account_onduty_bp.route('/<uid>/info', methods=['GET', 'POST'])
def info(uid):
    user = User.get(uid)
    if request.method == 'POST':
        if not (g.user.is_HR_leader() or g.user.is_HR() or g.user.is_OPS() or g.user.is_super_leader()):
            abort(403)
        check_time = request.values.get('check_time', '')
        if not check_time:
            flash(u'请选择打卡时间', 'danger')
            return redirect(url_for('account_onduty.info', uid=uid))
        UserOnDuty.add(user=user,
                       sn=user.sn,
                       check_time=check_time,
                       type=0,
                       create_time=datetime.datetime.now())
        flash(u'添加成功', 'success')
        return redirect(url_for('account_onduty.info', uid=uid))

    start_time = request.values.get('start_time', '')
    end_time = request.values.get('end_time', '')
    if not start_time and not end_time:
        end_time = datetime.datetime.strptime(
            datetime.datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
        end_time = end_time + datetime.timedelta(days=1)
        start_time = end_time - datetime.timedelta(days=30)
    else:
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    now_date_a = datetime.datetime.now()
    outs = [k for k in _format_out() if k['creator_id'] == int(uid)]
    print u'获取所有外出', (datetime.datetime.now() - now_date_a).total_seconds()
    leaves = [k for k in _format_leave() if k['creator_id'] == int(uid)]
    print u'获取所有请假', (datetime.datetime.now() - now_date_a).total_seconds()
    # 打卡最后一次时间
    last_onduty_date = _get_last_onduty_date()
    print u'获取上一次打卡时间', (datetime.datetime.now() - now_date_a).total_seconds()
    all_dus = _format_onduty(start_time, end_time)
    print u'获取所有凯芹', (datetime.datetime.now() - now_date_a).total_seconds()
    dutys = _get_onduty(all_dus, outs, leaves, user,
                        start_time, end_time, last_onduty_date)
    print u'结果', (datetime.datetime.now() - now_date_a).total_seconds()
    return tpl('/account/onduty/info.html', user=user,
               start_time=start_time.strftime('%Y-%m-%d'),
               end_time=end_time.strftime('%Y-%m-%d'),
               dutys=dutys)


@account_onduty_bp.route('/<uid>/onduty/<did>/delete')
def onduty_delete(uid, did):
    UserOnDuty.get(did).delete()
    return redirect(url_for('account_onduty.info', uid=uid))
