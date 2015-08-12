# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, redirect, url_for, g
from flask import render_template as tpl, flash, current_app

from models.user import User, Leave, LEAVE_STATUS_NORMAL, LEAVE_STATUS_APPLY, LEAVE_STATUS_PASS, LEAVE_STATUS_BACK
from forms.user import UserLeaveForm

from libs.signals import apply_leave_signal
from libs.paginator import Paginator

account_leave_bp = Blueprint(
    'account_leave', __name__, template_folder='../../templates/account/leave/')


@account_leave_bp.route('/leaves')
def leaves():
    if not (g.user.is_HR_leader() or g.user.is_OPS() or g.user.is_super_leader()):
        flash(u'对不起您没有权限', 'danger')
        return redirect(url_for('account_leave.index', user_id=g.user.id))
    user_id = int(request.values.get('user_id', 0))
    page = int(request.values.get('p', 1))
    type = int(request.values.get('type', 0))
    status = int(request.values.get('status', 100))
    start = request.values.get('start', '')
    end = request.values.get('end', '')

    leaves = [
        k for k in Leave.all() if k.status in [LEAVE_STATUS_APPLY, LEAVE_STATUS_PASS]]

    if start and end:
        start_time = datetime.datetime.strptime(start, "%Y-%m-%d")
        end_time = datetime.datetime.strptime(end, "%Y-%m-%d")
        leaves = [k for k in leaves if k.start_time >=
                  start_time and k.start_time < end_time]
    if type:
        leaves = [k for k in leaves if k.type == int(type)]
    if user_id:
        leaves = [k for k in leaves if k.creator.id == user_id]
    if status != 100:
        leaves = [k for k in leaves if k.status == status]

    paginator = Paginator(leaves, 50)
    try:
        leaves = paginator.page(page)
    except:
        leaves = paginator.page(paginator.num_pages)
    return tpl('/account/leave/leaves.html', leaves=leaves, user_id=user_id, type=type, start=start,
               title=u'所有请假申请列表', under_users=[{'uid': k.id, 'name': k.name} for k in User.all()],
               params="&user_id=%s&type=%s&start=%s&end=%s&status=%s" % (
                   user_id, type, start, end, str(status)),
               status=status, end=end, page=page)


def _get_all_under_users(self_user_id):
    under_users = []
    all_user = [{'uid': user.id, 'name': user.name, 'is_kpi_leader': user.is_kpi_leader, 'leaders': [
        k.id for k in user.team_leaders]} for user in User.all() if user.is_active()]

    def get_under(under_users, all_user, self_user_id):
        d_user = [user for user in all_user if self_user_id in user['leaders']]
        for k in d_user:
            under_users.append(k)
            if k['is_kpi_leader'] and self_user_id != k['uid']:
                under_users += get_under(under_users, all_user, k['uid'])
        return under_users
    return get_under(under_users, all_user, self_user_id)


@account_leave_bp.route('/underling', methods=['GET'])
def underling():
    user_id = int(request.values.get('user_id', 0))
    page = int(request.values.get('p', 1))
    type = int(request.values.get('type', 0))
    status = int(request.values.get('status', 100))
    start = request.values.get('start', '')
    end = request.values.get('end', '')

    if g.user.is_super_leader():
        leaves = [k for k in Leave.all() if k.status in [
            LEAVE_STATUS_APPLY, LEAVE_STATUS_PASS]]
        under_users = [{'uid': k.id, 'name': k.name}for k in User.all()]
    else:
        under_users = _get_all_under_users(g.user.id)
        if user_id:
            underling_user_ids = [user_id]
        else:
            underling_user_ids = list(set([k['uid'] for k in under_users]))
        leaves = [k for k in Leave.all() if k.creator.id in underling_user_ids and k.status in [
            LEAVE_STATUS_APPLY, LEAVE_STATUS_PASS]]

    if start and end:
        start_time = datetime.datetime.strptime(start, "%Y-%m-%d")
        end_time = datetime.datetime.strptime(end, "%Y-%m-%d")
        leaves = [k for k in leaves if k.start_time >=
                  start_time and k.start_time < end_time]
    if type:
        leaves = [k for k in leaves if k.type == int(type)]
    if status != 100:
        leaves = [k for k in leaves if k.status == status]

    paginator = Paginator(leaves, 50)
    try:
        leaves = paginator.page(page)
    except:
        leaves = paginator.page(paginator.num_pages)
    return tpl('/account/leave/leaves.html', leaves=leaves, user_id=user_id, type=type, start=start,
               title=u'下属的请假申请列表', under_users=under_users, status=status,
               params="&user_id=%s&type=%s&start=%s&end=%s&status=%s" % (
                   user_id, type, start, end, str(status)),
               end=end, page=page)


@account_leave_bp.route('/<user_id>')
def index(user_id):
    if g.user.id != int(user_id):
        flash(u'对不起您不能查看别人的请假申请表', 'danger')
        return redirect(url_for('account_leave.index', user_id=g.user.id))
    page = int(request.values.get('p', 1))
    leaves = [k for k in Leave.all() if k.creator.id == int(user_id)]
    paginator = Paginator(leaves, 50)
    try:
        leaves = paginator.page(page)
    except:
        leaves = paginator.page(paginator.num_pages)
    return tpl('/account/leave/index.html', leaves=leaves, page=page)


@account_leave_bp.route('/<user_id>/create', methods=['GET', 'POST'])
def create(user_id):
    form = UserLeaveForm(request.form)
    if request.method == 'POST':
        status = request.values.get('status')
        leave = Leave.add(type=form.type.data,
                          start_time=datetime.datetime.strptime(
                              request.values.get('start'), '%Y-%m-%d %H'),
                          end_time=datetime.datetime.strptime(
                              request.values.get('end'), '%Y-%m-%d %H'),
                          rate_day=request.values.get(
                              'day', '0') + '-' + request.values.get('half', '1'),
                          reason=form.reason.data,
                          status=status,
                          senders=User.gets(form.senders.data),
                          creator=g.user,
                          create_time=datetime.date.today())
        if int(status) == LEAVE_STATUS_NORMAL:
            flash(u'添加成功', 'success')
        else:
            flash(u'已发送申请', 'success')
            apply_leave_signal.send(
                current_app._get_current_object(), leave=leave)
        return redirect(url_for('account_leave.index', user_id=user_id))
    days = [{'key': k, 'value': k} for k in range(0, 21)]
    days += [{'key': k, 'value': k} for k in [30, 98, 113, 128]]
    return tpl('/account/leave/create.html', form=form, leave=None, days=days)


@account_leave_bp.route('/<user_id>/<lid>/delete')
def delete(user_id, lid):
    Leave.get(lid).delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('account_leave.index', user_id=user_id))


@account_leave_bp.route('/<user_id>/<lid>/status')
def status(user_id, lid):
    status = int(request.values.get('status', 1))
    leave = Leave.get(lid)
    leave.status = status
    leave.save()
    flash(leave.status_cn, 'success')
    apply_leave_signal.send(current_app._get_current_object(), leave=leave)
    if status in [LEAVE_STATUS_APPLY, LEAVE_STATUS_BACK]:
        return redirect(url_for('account_leave.index', user_id=user_id))
    else:
        return redirect(url_for('account_leave.underling'))


@account_leave_bp.route('/<user_id>/<lid>/update', methods=['GET', 'POST'])
def update(user_id, lid):
    leave = Leave.get(lid)
    form = UserLeaveForm(request.form)
    if request.method == 'POST':
        status = request.values.get('status')
        leave.type = form.type.data
        leave.start_time = datetime.datetime.strptime(
            request.values.get('start'), '%Y-%m-%d %H'),
        leave.end_time = datetime.datetime.strptime(
            request.values.get('end'), '%Y-%m-%d %H'),
        leave.rate_day = request.values.get(
            'day', '0') + '-' + request.values.get('half', '1'),
        leave.reason = form.reason.data
        leave.status = status
        leave.senders = User.gets(form.senders.data)
        leave.create_time = datetime.date.today()
        leave.save()
        if int(status) == LEAVE_STATUS_APPLY:
            flash(u'已发送申请', 'success')
            apply_leave_signal.send(
                current_app._get_current_object(), leave=leave)
        else:
            flash(u'修改成功', 'success')
        return redirect(url_for('account_leave.index', user_id=user_id))
    form.type.data = leave.type
    form.reason.data = leave.reason
    form.senders.data = [u.id for u in leave.senders]
    days = [{'key': k, 'value': k} for k in range(0, 21)]
    days += [{'key': k, 'value': k} for k in [30, 98, 113, 128]]
    return tpl('/account/leave/create.html', form=form, leave=leave, days=days)


@account_leave_bp.route('/<lid>/info', methods=['GET', 'POST'])
def info(lid):
    leave = Leave.get(lid)
    return tpl('/account/leave/info.html', leave=leave)
