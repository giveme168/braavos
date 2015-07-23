# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, url_for, Blueprint, flash, json, jsonify, g, current_app
from flask import render_template as tpl

from models.user import User, PerformanceEvaluation
from libs.paginator import Paginator
from libs.signals import kpi_apply_signal
from controllers.account.helpers.kpi_helpers import write_report_excel

account_kpi_bp = Blueprint(
    'account_kpi', __name__, template_folder='../../templates/account/kpi/')


@account_kpi_bp.route('/', methods=['GET'])
def index():
    page = int(request.values.get('page', 1))
    reports = PerformanceEvaluation.query.filter_by(creator=g.user)
    paginator = Paginator(list(reports), 20)
    try:
        reports = paginator.page(page)
    except:
        reports = paginator.page(paginator.num_pages)
    return tpl('/account/kpi/index.html', reports=reports)


@account_kpi_bp.route('/create', methods=['GET', 'POST'])
def create():
    if g.user.is_kpi_leader:
        type = 2
    else:
        type = 1
    if request.method == 'POST':
        if PerformanceEvaluation.query.filter_by(version=1, creator=g.user).count() > 0:
            flash(u'您已经填写过绩效考核表了!', 'danger')
            return redirect(url_for("account_kpi.index"))
        now_report = {}
        future_report = {}
        for k in range(1, 4):
            # KR指标数据
            now_report[
                'kr_' + str(k) + '_key'] = request.values.get('kr_' + str(k) + '_key', '')
            now_report[
                'kr_' + str(k) + '_value'] = request.values.get('kr_' + str(k) + '_value', '')
            now_report[
                'kr_' + str(k) + '_res'] = request.values.get('kr_' + str(k) + '_res', '')
            now_report[
                'kr_' + str(k) + '_w'] = int(request.values.get('kr_' + str(k) + '_w', 0))
            now_report[
                'kr_' + str(k) + '_s'] = float(request.values.get('kr_' + str(k) + '_s', 0.00))

            # 改进提升指标数据
            now_report[
                'up_' + str(k) + '_key'] = request.values.get('up_' + str(k) + '_key', '')
            now_report[
                'up_' + str(k) + '_value'] = request.values.get('up_' + str(k) + '_value', '')
            now_report[
                'up_' + str(k) + '_res'] = request.values.get('up_' + str(k) + '_res', '')
            now_report[
                'up_' + str(k) + '_w'] = int(request.values.get('up_' + str(k) + '_w', 0))
            now_report[
                'up_' + str(k) + '_s'] = float(request.values.get('up_' + str(k) + '_s', 0.00))

            if type == 2:
                # 管理指标数据
                now_report[
                    'manage_' + str(k) + '_key'] = request.values.get('manage_' + str(k) + '_key', '')
                now_report[
                    'manage_' + str(k) + '_value'] = request.values.get('manage_' + str(k) + '_value', '')
                now_report[
                    'manage_' + str(k) + '_res'] = request.values.get('manage_' + str(k) + '_res', '')
                now_report[
                    'manage_' + str(k) + '_w'] = int(request.values.get('manage_' + str(k) + '_w', 0))
                now_report[
                    'manage_' + str(k) + '_s'] = float(request.values.get('manage_' + str(k) + '_s', 0.00))

                # 管理指标数据
                future_report[
                    'next_manage_' + str(k) + '_key'] = request.values.get('next_manage_' + str(k) + '_key', '')
                future_report[
                    'next_manage_' + str(k) + '_value'] = request.values.get('next_manage_' + str(k) + '_value', '')
                future_report[
                    'next_manage_' + str(k) + '_w'] = int(request.values.get('next_manage_' + str(k) + '_w', 0))

            # KR指标数据
            future_report[
                'next_kr_' + str(k) + '_key'] = request.values.get('next_kr_' + str(k) + '_key', '')
            future_report[
                'next_kr_' + str(k) + '_value'] = request.values.get('next_kr_' + str(k) + '_value', '')
            future_report[
                'next_kr_' + str(k) + '_w'] = int(request.values.get('next_kr_' + str(k) + '_w', 0))

            # 改进提升指标数据
            future_report[
                'next_up_' + str(k) + '_key'] = request.values.get('next_up_' + str(k) + '_key', '')
            future_report[
                'next_up_' + str(k) + '_value'] = request.values.get('next_up_' + str(k) + '_value', '')
            future_report[
                'next_up_' + str(k) + '_w'] = int(request.values.get('next_up_' + str(k) + '_w', 0))
        # 胜任能力情况
        now_report['knowledge_res'] = request.values.get('knowledge_res', '')
        now_report['positive_res'] = request.values.get('positive_res', '')
        now_report['team_res'] = request.values.get('team_res', '')
        now_report['teach_res'] = request.values.get('teach_res', '')
        now_report['abide_res'] = request.values.get('abide_res', '')
        now_report['knowledge_s'] = float(
            request.values.get('knowledge_s', 0.00))
        now_report['positive_s'] = float(request.values.get('positive_s', 0.00))
        now_report['team_s'] = float(request.values.get('team_s', 0.00))
        now_report['teach_s'] = float(request.values.get('teach_s', 0.00))
        now_report['abide_s'] = float(request.values.get('abide_s', 0.00))

        # 自我总结
        now_report['self_summary'] = request.values.get('self_summary', '')

        # 各项得分
        KR_score = 0
        upper_score = 0
        manage_score = 0
        ability_score = now_report['knowledge_s'] * 0.04 + now_report['positive_s'] * 0.04 + now_report[
            'team_s'] * 0.04 + now_report['teach_s'] * 0.04 + now_report['abide_s'] * 0.04
        for k in range(1, 4):
            KR_score += now_report['kr_' +
                                   str(k) + '_w'] * now_report['kr_' + str(k) + '_s'] / 100
            upper_score += now_report['up_' +
                                      str(k) + '_w'] * now_report['up_' + str(k) + '_s'] / 100
            if type == 2:
                manage_score += now_report[
                    'manage_' + str(k) + '_w'] * now_report['manage_' + str(k) + '_s'] / 100
        total_score = KR_score + upper_score + manage_score + ability_score

        PerformanceEvaluation.add(
            type=type,
            self_upper_score=upper_score,
            self_KR_score=KR_score,
            self_manage_score=manage_score,
            self_ability_score=ability_score,
            self_total_score=total_score,
            now_report=json.dumps(now_report),
            future_report=json.dumps(future_report),
            creator=g.user,
            create_time=datetime.datetime.now(),
        )
        flash(u'绩效考核表添加成功，如果填写无误请申请Leader评分!', 'success')
        return redirect(url_for("account_kpi.index"))
    scores = [float(k) / 10 for k in range(1, 51)]
    scores.append(0.00)
    scores.reverse()
    weights = [k for k in range(1, 41)]
    weights.append(0)
    weights.reverse()
    return tpl('/account/kpi/create.html', type=type, scores=scores, weights=weights)


@account_kpi_bp.route('/<r_id>/update', methods=['GET', 'POST'])
def update(r_id):
    report = PerformanceEvaluation.get(r_id)
    if report.creator != g.user:
        flash(u'对不起，该绩效考核不是您的!', 'danger')
        return redirect(url_for("account_kpi.index"))
    if request.method == 'POST':
        now_report = {}
        future_report = {}
        for k in range(1, 4):
            # KR指标数据
            now_report[
                'kr_' + str(k) + '_key'] = request.values.get('kr_' + str(k) + '_key', '')
            now_report[
                'kr_' + str(k) + '_value'] = request.values.get('kr_' + str(k) + '_value', '')
            now_report[
                'kr_' + str(k) + '_res'] = request.values.get('kr_' + str(k) + '_res', '')
            now_report[
                'kr_' + str(k) + '_w'] = int(request.values.get('kr_' + str(k) + '_w', 0))
            now_report[
                'kr_' + str(k) + '_s'] = float(request.values.get('kr_' + str(k) + '_s', 0.00))

            # 改进提升指标数据
            now_report[
                'up_' + str(k) + '_key'] = request.values.get('up_' + str(k) + '_key', '')
            now_report[
                'up_' + str(k) + '_value'] = request.values.get('up_' + str(k) + '_value', '')
            now_report[
                'up_' + str(k) + '_res'] = request.values.get('up_' + str(k) + '_res', '')
            now_report[
                'up_' + str(k) + '_w'] = int(request.values.get('up_' + str(k) + '_w', 0))
            now_report[
                'up_' + str(k) + '_s'] = float(request.values.get('up_' + str(k) + '_s', 0.00))

            if report.type == 2:
                # 管理指标数据
                now_report[
                    'manage_' + str(k) + '_key'] = request.values.get('manage_' + str(k) + '_key', '')
                now_report[
                    'manage_' + str(k) + '_value'] = request.values.get('manage_' + str(k) + '_value', '')
                now_report[
                    'manage_' + str(k) + '_res'] = request.values.get('manage_' + str(k) + '_res', '')
                now_report[
                    'manage_' + str(k) + '_w'] = int(request.values.get('manage_' + str(k) + '_w', 0))
                now_report[
                    'manage_' + str(k) + '_s'] = float(request.values.get('manage_' + str(k) + '_s', 0.00))

                # 管理指标数据
                future_report[
                    'next_manage_' + str(k) + '_key'] = request.values.get('next_manage_' + str(k) + '_key', '')
                future_report[
                    'next_manage_' + str(k) + '_value'] = request.values.get('next_manage_' + str(k) + '_value', '')
                future_report[
                    'next_manage_' + str(k) + '_w'] = int(request.values.get('next_manage_' + str(k) + '_w', 0))

            # KR指标数据
            future_report[
                'next_kr_' + str(k) + '_key'] = request.values.get('next_kr_' + str(k) + '_key', '')
            future_report[
                'next_kr_' + str(k) + '_value'] = request.values.get('next_kr_' + str(k) + '_value', '')
            future_report[
                'next_kr_' + str(k) + '_w'] = int(request.values.get('next_kr_' + str(k) + '_w', 0))

            # 改进提升指标数据
            future_report[
                'next_up_' + str(k) + '_key'] = request.values.get('next_up_' + str(k) + '_key', '')
            future_report[
                'next_up_' + str(k) + '_value'] = request.values.get('next_up_' + str(k) + '_value', '')
            future_report[
                'next_up_' + str(k) + '_w'] = int(request.values.get('next_up_' + str(k) + '_w', 0))
        # 胜任能力情况
        now_report['knowledge_res'] = request.values.get('knowledge_res', '')
        now_report['positive_res'] = request.values.get('positive_res', '')
        now_report['team_res'] = request.values.get('team_res', '')
        now_report['teach_res'] = request.values.get('teach_res', '')
        now_report['abide_res'] = request.values.get('abide_res', '')
        now_report['knowledge_s'] = float(
            request.values.get('knowledge_s', 0.00))
        now_report['positive_s'] = float(request.values.get('positive_s', 0.00))
        now_report['team_s'] = float(request.values.get('team_s', 0.00))
        now_report['teach_s'] = float(request.values.get('teach_s', 0.00))
        now_report['abide_s'] = float(request.values.get('abide_s', 0.00))

        # 自我总结
        now_report['self_summary'] = request.values.get('self_summary', '')

        # 各项得分
        KR_score = 0
        upper_score = 0
        manage_score = 0
        ability_score = now_report['knowledge_s'] * 0.04 + now_report['positive_s'] * 0.04 + now_report[
            'team_s'] * 0.04 + now_report['teach_s'] * 0.04 + now_report['abide_s'] * 0.04
        for k in range(1, 4):
            KR_score += now_report['kr_' +
                                   str(k) + '_w'] * now_report['kr_' + str(k) + '_s'] / 100
            upper_score += now_report['up_' +
                                      str(k) + '_w'] * now_report['up_' + str(k) + '_s'] / 100
            if report.type == 2:
                manage_score += now_report[
                    'manage_' + str(k) + '_w'] * now_report['manage_' + str(k) + '_s'] / 100
        total_score = KR_score + upper_score + manage_score + ability_score

        report.self_upper_score = upper_score
        report.self_KR_score = KR_score
        report.self_manage_score = manage_score
        report.self_ability_score = ability_score
        report.self_total_score = total_score
        report.now_report = json.dumps(now_report)
        report.future_report = json.dumps(future_report)
        report.creator = g.user
        report.create_time = datetime.datetime.now()
        report.save()
        flash(u'绩效考核表修改成功，如果填写无误请申请Leader评分!', 'success')
        return redirect(url_for("account_kpi.index"))
    report.now_report_obj = json.loads(report.now_report)
    report.future_report_obj = json.loads(report.future_report)
    scores = [float(k) / 10 for k in range(1, 51)]
    scores.append(0.00)
    scores.reverse()
    weights = [k for k in range(1, 41)]
    weights.append(0)
    weights.reverse()
    return tpl('/account/kpi/update.html', type=report.type, scores=scores, weights=weights, report=report)


@account_kpi_bp.route('/<r_id>/apply/<status>', methods=['GET', 'POST'])
def apply(r_id, status):
    report = PerformanceEvaluation.get(r_id)
    report.status = status
    report.save()
    apply_context = {}
    apply_context['report'] = report
    kpi_apply_signal.send(
        current_app._get_current_object(), apply_context=apply_context)
    if int(status) == 1:
        flash(u'绩效考核已被打回!', 'success')
        return redirect(url_for("account_kpi.underling"))
    elif int(status) == 2:
        flash(u'申请评分成功，请等待Leader回复!', 'success')
        if g.user.is_HR_leader():
            return redirect(url_for("account_kpi.underling"))
        else:
            return redirect(url_for("account_kpi.index"))
    elif int(status) == 3:
        flash(u'提交给HR成功', 'success')
        return redirect(url_for("account_kpi.underling"))
    elif int(status) == 4:
        flash(u'归档成功', 'success')
        return redirect(url_for("account_kpi.underling"))


@account_kpi_bp.route('/<r_id>/check_apply', methods=['GET', 'POST'])
def check_apply(r_id):
    report = PerformanceEvaluation.get(r_id)
    if g.user not in report.creator.team_leaders:
        flash(u'对不起，您不是该绩效考核的Leader!', 'danger')
        return redirect(url_for("account_kpi.underling"))
    report.now_report_obj = json.loads(report.now_report)
    report.future_report_obj = json.loads(report.future_report)
    if request.method == 'POST':
        now_report = {}
        for k in range(1, 4):
            now_report[
                'leader_kr_' + str(k) + '_s'] = float(request.values.get('leader_kr_' + str(k) + '_s', 0.00))
            now_report[
                'leader_up_' + str(k) + '_s'] = float(request.values.get('leader_up_' + str(k) + '_s', 0.00))

            if report.type == 2:
                # 管理指标数据
                now_report['leader_manage_' + str(k) + '_s'] = float(request.values.get('leader_manage_' + str(k) +
                                                                                        '_s', 0.00))
        # 胜任能力情况
        now_report['leader_knowledge_s'] = float(
            request.values.get('leader_knowledge_s', 0.00))
        now_report['leader_positive_s'] = float(
            request.values.get('leader_positive_s', 0.00))
        now_report['leader_team_s'] = float(
            request.values.get('leader_team_s', 0.00))
        now_report['leader_teach_s'] = float(
            request.values.get('leader_teach_s', 0.00))
        now_report['leader_abide_s'] = float(
            request.values.get('leader_abide_s', 0.00))

        # 自我总结
        now_report['leader_summary'] = request.values.get('leader_summary', '')

        # 各项得分
        KR_score = 0
        upper_score = 0
        manage_score = 0
        ability_score = now_report['leader_knowledge_s'] * 0.04 + now_report['leader_positive_s'] * 0.04 + now_report[
            'leader_team_s'] * 0.04 + now_report['leader_teach_s'] * 0.04 + now_report['leader_abide_s'] * 0.04

        for k in range(1, 4):
            KR_score += report.now_report_obj['kr_' +
                                              str(k) + '_w'] * now_report['leader_kr_' + str(k) + '_s'] / 100
            upper_score += report.now_report_obj['up_' +
                                                 str(k) + '_w'] * now_report['leader_up_' + str(k) + '_s'] / 100
            if report.type == 2:
                manage_score += report.now_report_obj[
                    'manage_' + str(k) + '_w'] * now_report['leader_manage_' + str(k) + '_s'] / 100
        total_score = KR_score + upper_score + manage_score + ability_score

        report.now_report_obj.update(now_report)
        report.upper_score = upper_score
        report.KR_score = KR_score
        report.manage_score = manage_score
        report.ability_score = ability_score
        report.total_score = total_score
        report.now_report = json.dumps(report.now_report_obj)
        report.create_time = datetime.datetime.now()
        report.save()
        flash(u'绩效考核表审批成功，如果填写无误请申请HR备案!', 'success')
        return redirect(url_for("account_kpi.underling"))
    scores = [float(k) / 10 for k in range(1, 51)]
    scores.append(0.00)
    scores.reverse()
    return tpl('/account/kpi/apply.html', type=report.type, scores=scores, report=report)


def _get_all_under_users(self_user):
    under_users = []
    all_user = [user for user in User.all() if user.is_active()]

    def get_under(under_users, all_user, self_user):
        d_user = [user for user in all_user if self_user in user.team_leaders]
        for k in d_user:
            under_users.append(k)
            if k.is_kpi_leader and self_user != k:
                return get_under(under_users, all_user, k)
        return under_users
    return get_under(under_users, all_user, self_user)


@account_kpi_bp.route('/underling', methods=['GET'])
def underling():
    page = int(request.values.get('p', 1))
    status = int(request.values.get('status', 0))
    if g.user.is_HR_leader or g.user.is_super_leader():
        reports = PerformanceEvaluation.query.filter(
            PerformanceEvaluation.status > 1)
    else:
        underling_users = [k.id for k in set(_get_all_under_users(g.user))]
        reports = PerformanceEvaluation.query.filter(
            PerformanceEvaluation.creator_id.in_(underling_users),
            PerformanceEvaluation.status > 1)
    if status != 0:
        reports = [k for k in reports if k.status == status]
    paginator = Paginator(list(reports), 20)
    try:
        reports = paginator.page(page)
    except:
        reports = paginator.page(paginator.num_pages)
    return tpl('/account/kpi/underling.html', reports=reports, status=status,
               params='&status=' + str(status))


@account_kpi_bp.route('/<r_id>/info', methods=['GET'])
def info(r_id):
    report = PerformanceEvaluation.get(r_id)
    if not g.user.is_HR_leader():
        if report.creator == g.user:
            if report.status != 4:
                flash(u'对不起，您的绩效考核评分还没有完成!', 'danger')
                return redirect(url_for("account_kpi.index"))
        elif report.creator != g.user or g.user not in report.creator.team_leaders:
            flash(u'对不起，您没有权限查看别人的绩效考核!', 'danger')
            return redirect(url_for("account_kpi.index"))
    report.now_report_obj = json.loads(report.now_report)
    report.future_report_obj = json.loads(report.future_report)
    if request.values.get('action') == 'excel':
        return write_report_excel(report)
    return tpl('/account/kpi/info.html', report=report, type=report.type)


@account_kpi_bp.route('/<r_id>/delete', methods=['GET'])
def delete(r_id):
    if not g.user.is_admin():
        return jsonify({'id': ''})
    PerformanceEvaluation.get(r_id).delete()
    flash(u'删除成功!', 'success')
    return jsonify({'id': r_id})
