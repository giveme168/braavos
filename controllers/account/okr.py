# -*- coding: utf-8 -*-
import datetime
# from flask.ext.mysqldb import MySQL
from flask import request, redirect, url_for, Blueprint, flash, json, g, current_app
from flask import render_template as tpl

from models.user import User, Okr, OKR_STATUS_APPLY
from libs.email_signals import account_okr_apply_signal

account_okr_bp = Blueprint('account_okr', __name__, template_folder='../../templates/account/okr/')


# 显示用户名下所有的okr记录,列表信息形式.点击季度season显示详情
@account_okr_bp.route('/')
def index():
    okrs = [k for k in Okr.all() if k.creator == g.user]
    # 后面接一个排序按照日期早晚
    return tpl('/account/okr/index.html', okrs=okrs)


# 填写okr表格
@account_okr_bp.route('/create', methods=['GET', 'POST'])
def create():
    # o_kr又变为了数组
    if request.method == 'POST':
        okr_json = request.values.get('OKR')
        # o_kr = json.loads(okr_json)
        status = request.values.get('status')
        # 判断是否填写过,下拉框 id=season
        if Okr.query.filter_by(season=request.values.get('season'), year=datetime.datetime.now().year,
                               creator=g.user).count() > 0:
            flash(u'您已经填写过该季度的OKR表了!', 'danger')
            return redirect(url_for("account_okr.create"))
        season = request.values.get('season')
        year = datetime.datetime.now().year
        Okr.add(
            year=year,
            season=season,
            status=status,
            o_kr=okr_json,
            creator=g.user,
        )
        return redirect(url_for('account_okr.index'))
    return tpl('/account/okr/create.html')


@account_okr_bp.route('/<season>', methods=['GET'])
def season_index():
    if not (g.user.is_HR_leader() or g.user.is_OPS() or g.user.is_super_leader()
            or g.user.email in ['huhui@inad.com']):
        flash(u'对不起您没有权限', 'danger')
    return redirect(url_for('okr_leave.index', user_id=g.user.id))
    # user_id = int(request.values.get('user_id', 0))
    season = int(request.values.get('type', 0))
    # status = int(request.values.get('status', 100))
    okr = Okr.query.filter_by(creator=g.user, season=season)
    return tpl('/account/kpi/index.html', okr=okr)


@account_okr_bp.route('/<user_id>/<lid>/update', methods=['GET', 'POST'])
def update(user_id, lid):
    okr = Okr.get(lid)
    okr_json = request.values.get('OKR')
    o_kr = json.loads(okr_json)
    if request.method == 'POST':
        status = request.values.get('status')
        okr.season = request.values.get('season')
        okr.o_kr = o_kr
        okr.status = status
        # okr.senders = User.gets(form.senders.data)
        okr.save()
        if int(status) == OKR_STATUS_APPLY:
            flash(u'已发送申请', 'success')
            account_okr_apply_signal.send(
                current_app._get_current_object(), okr=okr)
        else:
            flash(u'修改成功', 'success')
        return redirect(url_for('account_okr.index', user_id=user_id))
    return tpl('/account/okr/create.html', okr=okr)


@account_okr_bp.route('/<user_id>/<lid>/delete')
def delete(user_id, lid):
    Okr.get(lid).delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('account_okr.index', user_id=user_id))


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


'''
@account_okr_bp.route('/underling', methods=['GET'])
def underling():
    user_id = int(request.values.get('user_id', 0))
    season = int(request.values.get('season', 0))
    status = int(request.values.get('status', 100))

    if g.user.is_super_leader():
        okr = [k for k in Okr.all() if k.status in [
            OKR_STATUS_APPLY, OKR_STATUS_PASS]]
        under_users = [{'uid': k.id, 'name': k.name} for k in User.all()]
    else:
        under_users = _get_all_under_users(g.user.id)
        if user_id:
            underling_user_ids = [user_id]
        else:
            underling_user_ids = list(set([k['uid'] for k in under_users]))
        leaves = [k for k in Okr.all() if k.creator.id in underling_user_ids and k.status in [
            OKR_STATUS_APPLY, OKR_STATUS_PASS]]

    if season:
        okr = [k for k in okr if k.type == int(type)]
    if status != 100:
        okr = [k for k in okr if k.status == status]
    okr = sorted(okr, key=lambda x: x.start_time, reverse=True)
    return tpl('/account/leave/leaves.html', leaves=leaves, user_id=user_id, type=type, start=start,
               title=u'下属的请假申请列表', under_users=under_users, status=status,
               params="&user_id=%s&type=%s&start=%s&end=%s&status=%s" % (
                   user_id, type, start, end, str(status)),
               )
'''
