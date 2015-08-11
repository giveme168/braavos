# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, request, redirect, url_for, g
from flask import render_template as tpl, flash, current_app
from wtforms import SelectMultipleField

from models.user import User, Out, OUT_STATUS_APPLY, OUT_STATUS_MEETED, OUT_STATUS_PASS, OUT_STATUS_MEETED_NOT_PASS
from models.client import Client, Agent
from models.medium import Medium
from libs.signals import apply_out_signal
from libs.paginator import Paginator

from libs.wtf import Form

account_out_bp = Blueprint(
    'account_out', __name__, template_folder='../../templates/account/out/')


class JoinersForm(Form):
    joiners = SelectMultipleField(u'参会人（公司内部）', coerce=int)

    def __init__(self, *args, **kwargs):
        super(JoinersForm, self).__init__(*args, **kwargs)
        self.joiners.choices = [(m.id, m.name) for m in User.all_active()]


@account_out_bp.route('/')
def index():
    page = int(request.values.get('p', 1))
    outs = list(Out.query.filter_by(creator=g.user))
    paginator = Paginator(outs, 50)
    try:
        outs = paginator.page(page)
    except:
        outs = paginator.page(paginator.num_pages)
    return tpl('/account/out/index.html', outs=outs, page=page)


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


@account_out_bp.route('/underling')
def underling():
    user_id = int(request.values.get('user_id', 0))
    page = int(request.values.get('p', 1))
    status = int(request.values.get('status', 0))
    start = request.values.get('start', '')
    end = request.values.get('end', '')

    under_users = _get_all_under_users(g.user.id)
    if user_id:
        underling_user_ids = [user_id]
    else:
        underling_user_ids = list(set([k['uid'] for k in under_users]))
    outs = [k for k in Out.all() if k.creator.id in underling_user_ids and k.status in [
        OUT_STATUS_APPLY, OUT_STATUS_PASS, OUT_STATUS_MEETED, OUT_STATUS_MEETED_NOT_PASS]]

    if start and end:
        start_time = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_time = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M")
        outs = [k for k in outs if k.start_time >=
                start_time and k.start_time < end_time]
    if status:
        outs = [k for k in outs if k.status == status]
    paginator = Paginator(outs, 50)
    try:
        outs = paginator.page(page)
    except:
        outs = paginator.page(paginator.num_pages)
    return tpl('/account/out/outs.html', outs=outs, user_id=user_id, start=start,
               title=u'下属的外出报备列表', under_users=under_users, status=status,
               params="&user_id=%s&start=%s&end=%s&status=%s" % (
                   user_id, start, end, status),
               end=end, page=page)


@account_out_bp.route('/outs')
def outs():
    user_id = int(request.values.get('user_id', 0))
    page = int(request.values.get('p', 1))
    status = int(request.values.get('status', 0))
    start = request.values.get('start', '')
    end = request.values.get('end', '')
    outs = [
        k for k in Out.all() if k.status > 0]

    if start and end:
        start_time = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_time = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M")
        outs = [k for k in outs if k.start_time >=
                start_time and k.start_time < end_time]
    if status:
        outs = [k for k in outs if k.status == status]
    if user_id:
        outs = [k for k in outs if k.creator.id == user_id]
    paginator = Paginator(outs, 50)
    try:
        outs = paginator.page(page)
    except:
        outs = paginator.page(paginator.num_pages)
    return tpl('/account/out/outs.html', outs=outs, user_id=user_id, start=start,
               title=u'所有外出报备列表', status=status,
               params="&user_id=%s&start=%s&end=%s&status=%s" % (
                   user_id, start, end, status), end=end, page=page,
               under_users=[{'uid': k.id, 'name': k.name} for k in User.all()])


@account_out_bp.route('/create', methods=['GET', 'POST'])
def create():
    m_persions = []
    if g.user.is_out_saler:
        m_persions += [{'key': '1' + '-' +
                        str(k.id) + '-' + k.name, 'name': k.name} for k in Client.all()]
        m_persions += [{'key': '2' + '-' +
                        str(k.id) + '-' + k.name, 'name': k.name} for k in Agent.all()]
        m_persions += [{'key': '3' + '-' +
                        str(k.id) + '-' + k.name, 'name': k.name} for k in Medium.all()]
        m_persions.append({'key': 100, 'name': u'其他'})
    joiners_form = JoinersForm(request.form)
    if request.method == 'POST':
        if g.user.is_out_saler:
            creator_type = 1
        else:
            creator_type = 2
        start_time = request.values.get('start_time', '')
        end_time = request.values.get('end_time', '')
        # m_person有两种类型，一种是其他所以填写，一种是代理+客户+媒体组合而成，例如：1-1，2-1，3-1（具体请查看m_persions）
        m_persion = request.values.get('m_persion', '')
        m_persion_type = int(request.values.get('m_persion_type', 1))
        reason = request.values.get('reason', '')
        persions = request.values.get('persions', '')
        address = request.values.get('address', '')
        out = Out.add(
            start_time=datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M'),
            end_time=datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M'),
            reason=reason,
            joiners=User.gets(request.values.getlist('joiners')),
            meeting_s='',
            persions=persions,
            address=address,
            m_persion=m_persion,
            m_persion_type=m_persion_type,
            creator_type=creator_type,
            status=int(request.values.get('action', 0)),
            creator=g.user,
            create_time=datetime.datetime.now()
        )
        if int(request.values.get('action', 0)) == OUT_STATUS_APPLY:
            flash(u'已发送申请', 'success')
            apply_out_signal.send(
                current_app._get_current_object(), out=out, status=1)
        else:
            flash(u'添加成功，请及时申请外出报备', 'success')
        return redirect(url_for('account_out.index'))
    return tpl('/account/out/create.html', m_persions=m_persions, joiners_form=joiners_form)


@account_out_bp.route('/<oid>/status')
def status(oid):
    status = int(request.values.get('status', 1))
    out = Out.get(oid)
    if status == 10:
        out.status = 0
        msg = u'外出报备撤回'
    elif status == 11:
        out.status = 0
        msg = u'外出报备被驳回'
    elif status == 1:
        out.status = 1
        msg = u'外出报备，邮件已发出'
    elif status == 2:
        out.status = 2
        msg = u'外出报备通过'
    elif status == 14:
        out.status = 3
        msg = u'外出报备通过-会议纪要填写完毕'
    out.save()
    flash(msg, 'success')
    apply_out_signal.send(
        current_app._get_current_object(), out=out, status=status)
    if g.user == out.creator:
        return redirect(url_for('account_out.index'))
    else:
        return redirect(url_for('account_out.underling'))


@account_out_bp.route('/<oid>/delete')
def delete(oid):
    Out.get(oid).delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('account_out.index'))


@account_out_bp.route('/<oid>/info')
def info(oid):
    out = Out.get(oid)
    return tpl('/account/out/info.html', out=out)


@account_out_bp.route('/<oid>/meeting_s', methods=['POST', 'GET'])
def meeting_s(oid):
    out = Out.get(oid)
    if request.method == 'POST':
        meeting_s = request.values.get('meeting_s', '')
        out.meeting_s = meeting_s
        if out.status == 1:
            out.status = 4
        elif out.status == 2:
            out.status = 3
        out.save()
        flash(u'会议纪要填写完毕', 'success')
        apply_out_signal.send(
            current_app._get_current_object(), out=out, status=3)
        return redirect(url_for('account_out.index'))
    return tpl('/account/out/meeting_s.html', out=out)


@account_out_bp.route('/<oid>/update', methods=['POST', 'GET'])
def update(oid):
    out = Out.get(oid)
    joiners_form = JoinersForm(request.form)
    joiners_form.joiners.data = [u.id for u in out.joiners]
    m_persions = []
    if g.user.is_out_saler:
        m_persions += [{'key': '1' + '-' +
                        str(k.id) + '-' + k.name, 'name': k.name} for k in Client.all()]
        m_persions += [{'key': '2' + '-' +
                        str(k.id) + '-' + k.name, 'name': k.name} for k in Agent.all()]
        m_persions += [{'key': '3' + '-' +
                        str(k.id) + '-' + k.name, 'name': k.name} for k in Medium.all()]
        m_persions.append({'key': 100, 'name': u'其他'})
    if request.method == 'POST':
        if g.user.is_out_saler:
            creator_type = 1
        else:
            creator_type = 2
        start_time = request.values.get('start_time', '')
        end_time = request.values.get('end_time', '')
        # m_person有两种类型，一种是其他所以填写，一种是代理+客户+媒体组合而成，例如：1-1，2-1，3-1（具体请查看m_persions）
        m_persion = request.values.get('m_persion', '')
        m_persion_type = int(request.values.get('m_persion_type', 1))
        reason = request.values.get('reason', '')
        persions = request.values.get('persions', '')
        address = request.values.get('address', '')
        out.start_time = datetime.datetime.strptime(
            start_time, '%Y-%m-%d %H:%M')
        out.end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M')
        out.reason = reason

        out.joiners = User.gets(request.values.getlist('joiners'))
        out.persions = persions
        out.address = address
        out.m_persion = m_persion
        out.m_persion_type = m_persion_type
        out.creator_type = creator_type
        out.status = int(request.values.get('action', 0))
        out.create_time = datetime.datetime.now()
        out.save()
        if int(int(request.values.get('action', 0))) == OUT_STATUS_APPLY:
            flash(u'已发送申请', 'success')
            apply_out_signal.send(
                current_app._get_current_object(), out=out, status=1)
        else:
            flash(u'添加成功，请及时申请外出报备', 'success')
        return redirect(url_for('account_out.index'))
    return tpl('/account/out/update.html', out=out, m_persions=m_persions, joiners_form=joiners_form)
