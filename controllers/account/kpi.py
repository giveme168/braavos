# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, url_for, Blueprint, flash, json, jsonify, g, current_app
from flask import render_template as tpl

from models.user import User, PerformanceEvaluation, PerformanceEvaluationPersonnal, P_VERSION_CN
from libs.paginator import Paginator
from libs.email_signals import account_kpi_apply_signal
from controllers.account.helpers.kpi_helpers import write_report_excel, write_simple_report_excel

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


@account_kpi_bp.route('/create_v2', methods=['GET', 'POST'])
def create_v2():
    if PerformanceEvaluation.query.filter_by(version=2, creator=g.user).count() > 0:
        flash(u'您已经填写过绩效考核表了!', 'danger')
        return redirect(url_for("account_kpi.index"))
    if g.user.is_kpi_leader:
        type = 2
    else:
        type = 1
    if request.method == 'POST':
        if PerformanceEvaluation.query.filter_by(version=2, creator=g.user).count() > 0:
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
        now_report['positive_s'] = float(
            request.values.get('positive_s', 0.00))
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
            version=2,
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
    last_performance = PerformanceEvaluation.query.filter_by(
        version=1, creator=g.user).first()
    if last_performance:
        future_report = json.loads(last_performance.future_report)
    else:
        future_report = None
    scores = [float(k) / 10 for k in range(1, 51)]
    scores.append(0.00)
    scores.reverse()
    weights = [k for k in range(1, 41)]
    weights.append(0)
    weights.reverse()
    return tpl('/account/kpi/create_v2.html', type=type, scores=scores, weights=weights, future_report=future_report)


@account_kpi_bp.route('/create', methods=['GET', 'POST'])
def create():
    if PerformanceEvaluation.query.filter_by(version=1, creator=g.user).count() > 0:
        flash(u'您已经填写过绩效考核表了!', 'danger')
        return redirect(url_for("account_kpi.index"))
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
        now_report['positive_s'] = float(
            request.values.get('positive_s', 0.00))
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


@account_kpi_bp.route('/<r_id>/update_v2', methods=['GET', 'POST'])
def update_v2(r_id):
    report = PerformanceEvaluation.get(r_id)
    if report.creator != g.user:
        flash(u'对不起，该绩效考核不是您的!', 'danger')
        return redirect(url_for("account_kpi.index"))
    if int(report.status) != 1:
        flash(u'对不起，您的绩效考核在审批中暂时不能修改!', 'danger')
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
        now_report['positive_s'] = float(
            request.values.get('positive_s', 0.00))
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
    return tpl('/account/kpi/update_v2.html', type=report.type, scores=scores, weights=weights, report=report)


@account_kpi_bp.route('/<r_id>/update', methods=['GET', 'POST'])
def update(r_id):
    report = PerformanceEvaluation.get(r_id)
    if report.creator != g.user:
        flash(u'对不起，该绩效考核不是您的!', 'danger')
        return redirect(url_for("account_kpi.index"))
    if int(report.status) != 1:
        flash(u'对不起，您的绩效考核在审批中暂时不能修改!', 'danger')
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
        now_report['positive_s'] = float(
            request.values.get('positive_s', 0.00))
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
    account_kpi_apply_signal.send(
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
    elif int(status) == 4:
        flash(u'提交给HR成功', 'success')
        return redirect(url_for("account_kpi.underling"))
    elif int(status) == 5:
        flash(u'归档成功', 'success')
        return redirect(url_for("account_kpi.underling"))


@account_kpi_bp.route('/<r_id>/check_apply_v2', methods=['GET', 'POST'])
def check_apply_v2(r_id):
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
        try:
            users = User.gets(request.values.getlist('personnals'))
            if len(users) != 5:
                flash(u'请选择五个同事为您的下属评分!', 'danger')
                return redirect(url_for("account_kpi.check_apply_v2", r_id=r_id))
        except:
            flash(u'请选择五个同事为您的下属评分!', 'danger')
            return redirect(url_for("account_kpi.check_apply_v2", r_id=r_id))
        # 先删除之前选的员工
        if report.status != 6:
            PerformanceEvaluationPersonnal.query.filter_by(performance=report).delete()

        report.now_report_obj.update(now_report)
        report.upper_score = upper_score
        report.KR_score = KR_score
        report.manage_score = manage_score
        report.ability_score = ability_score
        report.status = 6
        report.total_score = total_score
        report.now_report = json.dumps(report.now_report_obj)
        report.create_time = datetime.datetime.now()
        report.save()

        if not PerformanceEvaluationPersonnal.query.filter_by(performance=report).first():
            for user in users:
                PerformanceEvaluationPersonnal.add(
                    user=user,
                    performance=report)
                apply_context = {}
                apply_context['report'] = report
                apply_context['user'] = user
                account_kpi_apply_signal.send(
                    current_app._get_current_object(), apply_context=apply_context)
        flash(u'绩效考核表审批成功，已分配员工评分!', 'success')
        return redirect(url_for("account_kpi.underling"))
    performance_personnals = PerformanceEvaluationPersonnal.query.filter_by(performance=report)
    p_users = [k.user.id for k in performance_personnals]
    scores = [float(k) / 10 for k in range(1, 51)]
    scores.append(0.00)
    scores.reverse()
    return tpl('/account/kpi/apply_v2.html', type=report.type, scores=scores,
               report=report, users=User.all_active(), p_users=p_users)


@account_kpi_bp.route('/<r_id>/notice', methods=['GET'])
def notice(r_id):
    report = PerformanceEvaluation.get(r_id)
    personnal_obj = report.user_preformance_evaluation_personnal_personnal
    for k in personnal_obj:
        if k.status == 1:
            apply_context = {}
            apply_context['report'] = report
            apply_context['user'] = k.user
            account_kpi_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
    return jsonify({'ret': True})


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
        report.status = 3
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


def _get_all_under_users(self_user_id):
    under_users = []
    all_user = [{'uid': user.id, 'is_kpi_leader': user.is_kpi_leader, 'leaders': [
        k.id for k in user.team_leaders]} for user in User.all() if user.is_active()]

    def get_under(under_users, all_user, self_user_id):
        d_user = [user for user in all_user if self_user_id in user['leaders']]
        for k in d_user:
            under_users.append(k)
            if k['is_kpi_leader'] and self_user_id != k['uid']:
                under_users += get_under(under_users, all_user, k['uid'])
        return under_users
    return get_under(under_users, all_user, self_user_id)


@account_kpi_bp.route('/underling', methods=['GET'])
def underling():
    page = int(request.values.get('p', 1))
    status = int(request.values.get('status', 0))
    version = int(request.values.get('version', 2))

    if g.user.is_HR_leader() or g.user.is_super_leader():
        reports = [k for k in PerformanceEvaluation.all() if k.status > 1]
    else:
        underling_users = list(
            set([k['uid'] for k in _get_all_under_users(g.user.id)]))
        reports = [k for k in PerformanceEvaluation.all(
        ) if k.status > 1 and k.creator.id in underling_users]
    total_score = str(request.values.get('total_score', 0))
    if total_score != '0':
        total_score_p = total_score.split('-')
        if len(total_score) == 1:
            reports = [
                k for k in reports if float(k.total_score + k.personnal_score) == float(total_score)]
        else:
            start, end = float(total_score_p[0]), float(total_score_p[1])
            reports = [k for k in reports if float(
                k.total_score + k.personnal_score) >= start and float(k.total_score + k.personnal_score) < end]

    if status != 0:
        reports = [k for k in reports if k.status == status]
    reports = [k for k in reports if k.version == version]
    if request.values.get('action') == 'excel':
        return write_simple_report_excel(reports)
    paginator = Paginator(list(reports), 20)
    try:
        reports = paginator.page(page)
    except:
        reports = paginator.page(paginator.num_pages)
    return tpl('/account/kpi/underling.html', reports=reports, status=status,
               params='&status=' +
               str(status) + '&total_score=' + str(total_score),
               total_score=total_score, P_VERSION_CN=P_VERSION_CN,
               version=version)


@account_kpi_bp.route('/personnal', methods=['GET'])
def personnal():
    status = int(request.values.get('status', 1))
    page = int(request.values.get('p', 1))
    if g.user.is_super_admin():
        personnal_objs = PerformanceEvaluationPersonnal.query.filter_by(status=status)
    else:
        personnal_objs = PerformanceEvaluationPersonnal.query.filter_by(user=g.user, status=status)
    paginator = Paginator(list(personnal_objs), 20)
    try:
        personnal_objs = paginator.page(page)
    except:
        personnal_objs = paginator.page(paginator.num_pages)
    return tpl('/account/kpi/personnal_index.html', personnal_objs=personnal_objs, status=status)


@account_kpi_bp.route('/personnal/<pid>/apply', methods=['GET', 'POST'])
def personnal_apply(pid):
    personnal_obj = PerformanceEvaluationPersonnal.get(pid)
    if personnal_obj.user != g.user:
        if g.user.is_super_leader():
            pass
        else:
            flash(u'对不起，您没有权限查看别人的绩效考核!', 'danger')
            return redirect(url_for('account_kpi.personnal'))
    if request.method == 'POST':
        total_score = 0.0
        attitude_param = {}
        ability_param = {}
        for k in range(6):
            key = 'work_attitude_' + str(k) + '_s'
            attitude_param[key] = float(request.values.get(key, 0))
            if k == 0:
                total_score += attitude_param[key] * 0.05
            elif k == 1:
                total_score += attitude_param[key] * 0.1
            elif k == 2:
                total_score += attitude_param[key] * 0.1
            elif k == 3:
                total_score += attitude_param[key] * 0.05
            elif k == 4:
                total_score += attitude_param[key] * 0.05
            elif k == 5:
                total_score += attitude_param[key] * 0.05
        for k in range(9):
            key = 'work_ability_' + str(k) + '_s'
            ability_param[key] = float(request.values.get(key, 0))
            if k == 0:
                total_score += ability_param[key] * 0.1
            elif k == 1:
                total_score += ability_param[key] * 0.05
            elif k == 2:
                total_score += ability_param[key] * 0.1
            elif k == 3:
                total_score += ability_param[key] * 0.05
            elif k == 4:
                total_score += ability_param[key] * 0.05
            elif k == 5:
                total_score += ability_param[key] * 0.05
            elif k == 6:
                total_score += ability_param[key] * 0.05
            elif k == 7:
                total_score += ability_param[key] * 0.1
            elif k == 8:
                total_score += ability_param[key] * 0.05
        personnal_obj.total_score = total_score * 0.2
        personnal_obj.body = json.dumps({'attitude_param': attitude_param, 'ability_param': ability_param})
        personnal_obj.status = 0
        personnal_obj.save()

        # 同事全部打分完成，自动发送HR归档
        performance = personnal_obj.performance
        if not PerformanceEvaluationPersonnal.query.filter_by(performance=performance, status=1).first():
            performance.status = 4
            performance.save()
            apply_context = {}
            apply_context['report'] = performance
            account_kpi_apply_signal.send(
                current_app._get_current_object(), apply_context=apply_context)
        flash(u'您已经为同事打分完成!', 'success')
        return redirect(url_for('account_kpi.personnal'))
    body_obj = json.loads(personnal_obj.body)
    attitude_param = {}
    ability_param = {}
    if 'attitude_param' in body_obj:
        attitude_param = body_obj['attitude_param']
    if 'ability_param' in body_obj:
        ability_param = body_obj['ability_param']
    scores = [float(k) / 10 for k in range(1, 51)]
    scores.append(0.00)
    scores.reverse()
    return tpl('/account/kpi/personnal_apply.html', personnal_obj=personnal_obj,
               scores=scores, attitude_param=attitude_param, ability_param=ability_param)


@account_kpi_bp.route('/<r_id>/info', methods=['GET'])
def info(r_id):
    report = PerformanceEvaluation.get(r_id)
    if not g.user.is_HR_leader() and not g.user.is_super_leader():
        under_users = [k['uid'] for k in _get_all_under_users(g.user.id)]
        if report.creator == g.user:
            if report.status != 5:
                flash(u'对不起，您的绩效考核评分还没有完成!', 'danger')
                return redirect(url_for("account_kpi.index"))
        elif report.creator.id not in under_users:
            flash(u'对不起，您没有权限查看别人的绩效考核!', 'danger')
            return redirect(url_for("account_kpi.index"))
    report.now_report_obj = json.loads(report.now_report)
    report.future_report_obj = json.loads(report.future_report)
    if request.values.get('action') == 'excel':
        return write_report_excel(report)
    return tpl('/account/kpi/info.html', report=report, type=report.type)


@account_kpi_bp.route('/<r_id>/info_v2', methods=['GET'])
def info_v2(r_id):
    report = PerformanceEvaluation.get(r_id)
    if not g.user.is_HR_leader() and not g.user.is_super_leader():
        under_users = [k['uid'] for k in _get_all_under_users(g.user.id)]
        if report.creator == g.user:
            if report.status != 5:
                flash(u'对不起，您的绩效考核评分还没有完成!', 'danger')
                return redirect(url_for("account_kpi.index"))
        elif report.creator.id not in under_users:
            flash(u'对不起，您没有权限查看别人的绩效考核!', 'danger')
            return redirect(url_for("account_kpi.index"))
    report.now_report_obj = json.loads(report.now_report)
    report.future_report_obj = json.loads(report.future_report)
    if request.values.get('action') == 'excel':
        return write_report_excel(report)
    return tpl('/account/kpi/info_v2.html', report=report, type=report.type)


@account_kpi_bp.route('/<r_id>/delete', methods=['GET'])
def delete(r_id):
    if not g.user.is_admin():
        return jsonify({'id': ''})
    performance = PerformanceEvaluation.get(r_id)
    PerformanceEvaluationPersonnal.query.filter_by(performance=performance).delete()
    performance.delete()
    flash(u'删除成功!', 'success')
    return jsonify({'id': r_id})
