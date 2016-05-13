# -*- coding: utf-8 -*-
from flask import request, redirect, url_for, Blueprint, flash, json, g, current_app
from flask import render_template as tpl

from models.user import User, Okr, OKR_STATUS_APPLY, OKR_STATUS_PASS, OKR_STATUS_BACK, OKR_STATUS_NORMAL, OKR_QUARTER_CN
from libs.email_signals import account_okr_apply_signal

account_okr_bp = Blueprint('account_okr', __name__, template_folder='../../templates/account/okr/')

YEAR_LIST = ['2016', '2017', '2018', '2019', '2020']
PRIORITY_LIST = ['P0', 'P1', 'P2', 'P3']


# 显示用户名下所有的okr记录,列表信息形式.点击季度quarter显示详情
@account_okr_bp.route('/')
def index():
    okrs = [k for k in Okr.all() if k.creator == g.user]
    # 后面接一个排序按照日期早晚
    return tpl('/account/okr/index.html', okrs=okrs)


"""
@account_okr_bp.route('/create_json', methods=['POST'])
def create_json():
    okr = request.values.get('okr')
    print okr
    return jsonify({'ret': False})
"""


# 填写okr表格
@account_okr_bp.route('/create', methods=['GET', 'POST'])
def create():
    # o_kr又变为了数组
    if request.method == 'POST':
        okr_json = request.values.get('okr_json')
        o_kr = json.loads(okr_json)
        status = int(o_kr['status'])
        year = int(o_kr['year'])
        quarter = int(o_kr['quarter'])
        okrtext = json.dumps(o_kr['okrs'])
        # 判断是否填写过,下拉框 id=quarter
        if Okr.query.filter_by(quarter=quarter, year=year,
                               creator=g.user).first():
            flash(u'您已经填写过该季度的OKR表了!', 'danger')
            return tpl('/account/okr/update_new.html',
                       okrlist=o_kr['okrs'],
                       year=year,
                       quarter=quarter,
                       year_list=YEAR_LIST,
                       quarters=OKR_QUARTER_CN,
                       priority_list=PRIORITY_LIST)
        newokr = Okr.add(
            year=year,
            quarter=quarter,
            status=status,
            o_kr=okrtext,
            creator=g.user,
        )
        if int(status) == OKR_STATUS_NORMAL:
            flash(u'添加成功', 'success')
        else:
            flash(u'已发送申请', 'success')
            account_okr_apply_signal.send(
                current_app._get_current_object(), okr=newokr)
        return redirect(url_for('account_okr.index'))
    return tpl('/account/okr/create.html',
               year_list=YEAR_LIST,
               quarters=OKR_QUARTER_CN,
               priority_list=PRIORITY_LIST)


"""
# display the detail content of the current user by choosing year and quarter
@account_okr_bp.route('/<user_id>/<year>/<quarter>', methods=['GET'])
def quarter_detail(user_id, year, quarter):
    year = 0
    quarter = 0
    okrs = []
    okr = Okr.query.filter_by(creator_id=user_id, year=year, quarter=quarter).first()
    if okr:
        year = okr.year
        quarter = okr.quarter
        okrs = json.loads(okr.o_kr)
    return tpl('/account/okr/details.html', year=year, quarter=quarter, okrs=okrs)
"""


# update the OKR by changing the content in database without creating new log
@account_okr_bp.route('/<user_id>/<lid>/update', methods=['GET', 'POST'])
def update(user_id, lid):
    okr_old = Okr.query.get(lid)

    if request.method == 'POST':
        okr_json = request.values.get('okr_json')
        o_kr = json.loads(okr_json)
        quarter = int(o_kr['quarter'])
        status = int(o_kr['status'])
        year = int(o_kr['year'])
        okrtext = json.dumps(o_kr['okrs'])
        if quarter == okr_old.quarter and year == okr_old.year:
            okr_update = Okr.query.get(lid)
            okr_update.year = year
            okr_update.quarter = quarter
            okr_update.status = status
            okr_update.o_kr = okrtext
            okr_update.creator_id = user_id
            okr_update.save()
            if int(status) == OKR_STATUS_APPLY:
                flash(u'已发送申请', 'success')
                account_okr_apply_signal.send(
                    current_app._get_current_object(), okr=okr_update)
            else:
                flash(u'修改成功', 'success')
            return redirect(url_for('account_okr.index'))
        elif Okr.query.filter_by(quarter=quarter, year=year, creator=g.user).first():
            flash(u'您已经填写过该季度的OKR表了!', 'danger')
            return tpl('/account/okr/update_new.html',
                       okrlist=o_kr['okrs'],
                       year=year,
                       quarter=quarter,
                       year_list=YEAR_LIST,
                       quarters=OKR_QUARTER_CN,
                       priority_list=PRIORITY_LIST)
        okr_update = Okr.query.get(lid)
        okr_update.year = year
        okr_update.quarter = quarter
        okr_update.status = status
        okr_update.o_kr = okrtext
        okr_update.creator_id = user_id
        okr_update.save()
        if int(status) == OKR_STATUS_APPLY:
            flash(u'已发送申请', 'success')
            account_okr_apply_signal.send(
                current_app._get_current_object(), okr=okr_update)
        else:
            flash(u'修改成功', 'success')
        return redirect(url_for('account_okr.index'))
    okr = Okr.get(lid)
    okrlist = json.loads(okr.o_kr)
    return tpl('/account/okr/update_new.html',
               okrlist=okrlist,
               year=str(okr.year),
               quarter=okr.quarter,
               year_list=YEAR_LIST,
               quarters=OKR_QUARTER_CN,
               priority_list=PRIORITY_LIST)


# delete the log in database
@account_okr_bp.route('/<user_id>/<lid>/delete')
def delete(user_id, lid):
    Okr.get(lid).delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('account_okr.index', user_id=user_id))


# find the logs for subordinates
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


@account_okr_bp.route('/subordinates', methods=['GET'])
def subordinates():
    user_id = int(request.values.get('user_id', 0))
    quarter = int(request.values.get('quarter', 0))
    status = int(request.values.get('status', 100))
    year = int(request.values.get('year', 0))
    if g.user.is_super_leader():
        okr = [k for k in Okr.all() if k.status in [
            OKR_STATUS_APPLY, OKR_STATUS_PASS]]
        under_users = [{'uid': k.id, 'name': k.name} for k in User.all()]
    else:
        under_users = _get_all_under_users(g.user.id)
        okr = [k for k in Okr.all() if k.status in [OKR_STATUS_APPLY, OKR_STATUS_PASS]]

    if user_id:
        okr = [k for k in okr if k.creator.id == int(user_id)]
    if status != 100:
        okr = [k for k in okr if k.status == status]
    okrs = sorted(okr, key=lambda x: x.year, reverse=True)
    return tpl('/account/okr/subordinates.html', okrs=okrs, user_id=user_id,
               quarter=quarter, year=year,
               title=u'下属的OKR申请审核列表', under_users=under_users, status=status,
               params="&user_id=%s&status=%s" % (
                   user_id, str(status)),
               )


# display the detail okr content of the subordinates
@account_okr_bp.route('/<lid>/info', methods=['GET', 'POST'])
def info(lid):
    okr = Okr.get(lid)
    okrlist = json.loads(okr.o_kr)
    return tpl('/account/okr/info.html', okrlist=okrlist, okr=okr)


@account_okr_bp.route('/<user_id>/<lid>/status')
def status(user_id, lid):
    status = int(request.values.get('status', 1))
    okr = Okr.query.get(lid)
    okr.status = status
    okr.save()
    flash(okr.status_cn, 'success')
    account_okr_apply_signal.send(
        current_app._get_current_object(), okr=okr)
    if status in [OKR_STATUS_APPLY, OKR_STATUS_BACK]:
        return redirect(url_for('account_okr.index', user_id=user_id))
    else:
        return redirect(url_for('account_okr.subordinates'))
