# -*- coding: UTF-8 -*-
import StringIO
import mimetypes
import datetime

from flask import Response
from werkzeug.datastructures import Headers
import xlsxwriter


def write_simple_report_excel(reports):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    keys = [u'员工姓名', u'职务', u'考核周期', u'KR指标自评分', u'KR指标上级评分', u'改进提升自评分',
            u'改进提升上级评分', u'管理指标自评分', u'管理指标上级评分', u'胜任能力自评分', u'胜任能力上级评分',
            u'绩效评估自评总分', u'绩效评估上级总评分', u'同事评分', u'绩效总得分', u'填表时间']
    worksheet.set_column(0, len(keys), 18)
    for k in range(len(keys)):
        worksheet.write(0, k, keys[k], align_center)
    worksheet.set_row(0, 20)
    reports = [k for k in reports if k.status >= 3]
    th = 1
    for k in range(len(reports)):
        worksheet.write(th, 0, reports[k].creator.name, align_center)
        worksheet.write(th, 1, reports[k].creator.team.name, align_center)
        worksheet.write(th, 2, reports[k].version_cn, align_center)
        worksheet.write(th, 3, reports[k].self_KR_score, align_center)
        worksheet.write(th, 4, reports[k].KR_score, align_center)
        worksheet.write(th, 5, reports[k].self_upper_score, align_center)
        worksheet.write(th, 6, reports[k].upper_score, align_center)
        if reports[k].type == 2:
            worksheet.write(th, 7, reports[k].self_manage_score, align_center)
            worksheet.write(th, 8, reports[k].manage_score, align_center)
        else:
            worksheet.write(th, 7, u'无', align_center)
            worksheet.write(th, 8, u'无', align_center)
        worksheet.write(th, 9, reports[k].self_ability_score, align_center)
        worksheet.write(th, 10, reports[k].ability_score, align_center)
        worksheet.write(th, 11, reports[k].self_total_score, align_center)
        worksheet.write(th, 12, reports[k].total_score, align_center)
        worksheet.write(th, 13, reports[k].personnal_score, align_center)
        worksheet.write(th, 14, reports[k].personnal_score + reports[k].total_score, align_center)
        worksheet.write(th, 15, reports[k].create_time_cn, align_center)
        worksheet.set_row(th, 20)
        th += 1
    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                ("绩效考核总表", datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    mimetype_tuple = mimetypes.guess_type(filename)
    response_headers = Headers({
        'Pragma': "public",
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Cache-Control': 'private',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
    response.headers = response_headers
    response.set_cookie('fileDownload', 'true', path='/')
    return response


def write_report_excel(report):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    align_center_color = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1, 'fg_color': '#AAAAAA'})
    align_center = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter', 'border': 1})
    align_center_font = workbook.add_format(
        {'font_size': 20, 'align': 'center', 'valign': 'vcenter', 'border': 1})
    align_left = workbook.add_format(
        {'align': 'left', 'valign': 'vcenter', 'border': 1, })

    # 设置宽度为30
    worksheet.set_column(0, 15, 10)
    worksheet.set_column(12, 12, 35)
    # 设置高度
    for k in range(0, 67):
        worksheet.set_row(k, 30)

    # 个人信息
    worksheet.merge_range(0, 0, 0, 14, u'绩效目标及考核表', align_center_font)
    worksheet.merge_range(1, 0, 1, 1, u'填表日期：', align_center)
    worksheet.merge_range(1, 2, 1, 3, report.create_time_cn, align_center)
    worksheet.merge_range(1, 4, 1, 5, u'姓名：', align_center)
    worksheet.merge_range(1, 6, 1, 7, report.creator.name, align_center)
    worksheet.merge_range(1, 8, 1, 9, u'考核周期：', align_center)
    worksheet.merge_range(1, 10, 1, 11, report.version_cn, align_center)
    worksheet.write(1, 12, u'职位：', align_center)
    worksheet.merge_range(1, 13, 1, 14, report.creator.team.name, align_center)

    # 绩效考核部分
    worksheet.merge_range(2, 0, 2, 11, u'关键绩效考核指标（KPI）', align_center_color)
    worksheet.write(2, 12, u'KPI权重：', align_center_color)
    worksheet.merge_range(2, 13, 2, 14, u'80%', align_center_color)

    worksheet.merge_range(3, 0, 3, 1, u'维度', align_center)
    worksheet.merge_range(3, 2, 3, 6, u'指标说明（指标含义、计算公式或说明）', align_center)
    worksheet.merge_range(3, 7, 3, 10, u'衡量标准(请尽量量化评价标准）', align_center)
    worksheet.write(3, 11, u'权重%', align_center)
    worksheet.write(3, 12, u'实际完成情况', align_center)
    worksheet.write(3, 13, u'员工自评', align_center)
    worksheet.write(3, 14, u'上级自评', align_center)

    worksheet.merge_range(4, 0, 6, 1, u'KR指标', align_center)
    for k in range(1, 4):
        worksheet.merge_range(
            4 + k - 1, 2, 4 + k - 1, 6, report.now_report_obj['kr_' + str(k) + '_key'], align_center)
        worksheet.merge_range(
            4 + k - 1, 7, 4 + k - 1, 10, report.now_report_obj['kr_' + str(k) + '_value'], align_center)
        worksheet.write(
            4 + k - 1, 11, report.now_report_obj['kr_' + str(k) + '_w'], align_center)
        worksheet.write(
            4 + k - 1, 12, report.now_report_obj['kr_' + str(k) + '_res'], align_center)
        worksheet.write(
            4 + k - 1, 13, report.now_report_obj['kr_' + str(k) + '_s'], align_center)
        worksheet.write(
            4 + k - 1, 14, report.now_report_obj['leader_kr_' + str(k) + '_s'], align_center)
    worksheet.merge_range(7, 0, 9, 1, u'改进提升', align_center)
    for k in range(1, 4):
        worksheet.merge_range(
            7 + k - 1, 2, 7 + k - 1, 6, report.now_report_obj['up_' + str(k) + '_key'], align_center)
        worksheet.merge_range(
            7 + k - 1, 7, 7 + k - 1, 10, report.now_report_obj['up_' + str(k) + '_value'], align_center)
        worksheet.write(
            7 + k - 1, 11, report.now_report_obj['up_' + str(k) + '_w'], align_center)
        worksheet.write(
            7 + k - 1, 12, report.now_report_obj['up_' + str(k) + '_res'], align_center)
        worksheet.write(
            7 + k - 1, 13, report.now_report_obj['up_' + str(k) + '_s'], align_center)
        worksheet.write(
            7 + k - 1, 14, report.now_report_obj['leader_up_' + str(k) + '_s'], align_center)
    th = 10
    if report.type == 2:
        worksheet.merge_range(th, 0, th + 2, 1, u'管理指标', align_center)
        for k in range(1, 4):
            worksheet.merge_range(
                th + k - 1, 2, th + k - 1, 6, report.now_report_obj['manage_' + str(k) + '_key'], align_center)
            worksheet.merge_range(
                th + k - 1, 7, th + k - 1, 10, report.now_report_obj['manage_' + str(k) + '_value'], align_center)
            worksheet.write(
                th + k - 1, 11, report.now_report_obj['manage_' + str(k) + '_w'], align_center)
            worksheet.write(
                th + k - 1, 12, report.now_report_obj['manage_' + str(k) + '_res'], align_center)
            worksheet.write(
                th + k - 1, 13, report.now_report_obj['manage_' + str(k) + '_s'], align_center)
            worksheet.write(
                th + k - 1, 14, report.now_report_obj['leader_manage_' + str(k) + '_s'], align_center)
        th += 3
    worksheet.merge_range(th, 0, th, 10, u'KPI权重合计：', align_center_color)
    worksheet.write(th, 11, u'80%', align_center_color)
    worksheet.write(th, 12, u'KPI评分合计：', align_center_color)
    worksheet.write(th, 13, report.self_KR_score +
                    report.self_upper_score + report.self_manage_score, align_center_color)
    worksheet.write(th, 14, report.KR_score +
                    report.upper_score + report.manage_score, align_center_color)
    th += 1
    worksheet.merge_range(th, 0, th, 11, u'胜任能力评估', align_center_color)
    worksheet.write(th, 12, u'胜任能力权重：', align_center_color)
    worksheet.merge_range(th, 13, th, 14, u'20%', align_center_color)
    th += 1
    worksheet.merge_range(th, 0, th, 4, u'胜任能力', align_center)
    worksheet.merge_range(th, 5, th, 10, u'能力说明', align_center)
    worksheet.write(th, 11, '', align_center)
    worksheet.write(th, 12, u'实际行为表现', align_center)
    worksheet.write(th, 13, u'员工自评', align_center)
    worksheet.write(th, 14, u'上级评分', align_center)
    th += 1
    worksheet.merge_range(th, 0, th, 4, u'知识技能', align_center)
    worksheet.merge_range(
        th, 5, th, 10, u'具备胜任目前工作所需要的各项知识技能和技巧。', align_center)
    worksheet.write(th, 11, '4%', align_center)
    worksheet.write(
        th, 12, report.now_report_obj['knowledge_res'], align_center)
    worksheet.write(th, 13, report.now_report_obj['knowledge_s'], align_center)
    worksheet.write(
        th, 14, report.now_report_obj['leader_knowledge_s'], align_center)
    th += 1
    worksheet.merge_range(th, 0, th, 4, u'积极主动', align_center)
    worksheet.merge_range(th, 5, th, 10, u'工作积极主动，不计较个人得失。', align_center)
    worksheet.write(th, 11, '4%', align_center)
    worksheet.write(th, 12, report.now_report_obj[
                    'positive_res'], align_center)
    worksheet.write(th, 13, report.now_report_obj['positive_s'], align_center)
    worksheet.write(
        th, 14, report.now_report_obj['leader_positive_s'], align_center)
    th += 1
    worksheet.merge_range(th, 0, th, 4, u'团队合作', align_center)
    worksheet.merge_range(
        th, 5, th, 10, u'团队合作意识强，包括部门内部及跨部门合作。', align_center)
    worksheet.write(th, 11, '4%', align_center)
    worksheet.write(th, 12, report.now_report_obj['team_res'], align_center)
    worksheet.write(th, 13, report.now_report_obj['team_s'], align_center)
    worksheet.write(
        th, 14, report.now_report_obj['leader_team_s'], align_center)
    th += 1
    worksheet.merge_range(th, 0, th, 4, u'学习能力', align_center)
    worksheet.merge_range(
        th, 5, th, 10, u'开放心态，具备自我学习和成长的能力和意识。', align_center)
    worksheet.write(th, 11, '4%', align_center)
    worksheet.write(th, 12, report.now_report_obj['teach_res'], align_center)
    worksheet.write(th, 13, report.now_report_obj['teach_s'], align_center)
    worksheet.write(
        th, 14, report.now_report_obj['leader_teach_s'], align_center)
    th += 1
    worksheet.merge_range(th, 0, th, 4, u'遵规守纪', align_center)
    worksheet.merge_range(th, 5, th, 10, u'遵守部门工作纪律，遵循公司各项规章制度。', align_center)
    worksheet.write(th, 11, '4%', align_center)
    worksheet.write(th, 12, report.now_report_obj['abide_res'], align_center)
    worksheet.write(th, 13, report.now_report_obj['abide_s'], align_center)
    worksheet.write(
        th, 14, report.now_report_obj['leader_abide_s'], align_center)
    th += 1
    worksheet.merge_range(th, 0, th, 10, u'胜任力权重合计：', align_center_color)
    worksheet.write(th, 11, u'20%', align_center_color)
    worksheet.write(th, 12, u'胜任能力评分合计：', align_center_color)
    worksheet.write(th, 13, report.self_ability_score, align_center_color)
    worksheet.write(th, 14, report.ability_score, align_center_color)
    th += 1

    if report.version == 1:
        worksheet.merge_range(th, 0, th, 4, u'权重总计：', align_center)
        worksheet.write(th, 5, u'100%', align_center)
        worksheet.merge_range(
            th, 6, th, 12, u'ΣKPI（评分*权重）+Σ胜任力（评分*权重）=绩效评估总分', align_center)
        worksheet.write(th, 13, report.self_total_score, align_center)
        worksheet.write(th, 14, report.total_score, align_center)
        th += 1
    elif report.version == 2:
        worksheet.merge_range(th, 0, th + 2, 4, u'权重总计：', align_center)
        worksheet.merge_range(th, 5, th + 2, 5, u'100%', align_center)
        worksheet.merge_range(
            th, 6, th, 12, u'ΣKPI（评分*权重）+Σ胜任力（评分*权重）', align_center)
        worksheet.merge_range(
            th + 1, 6, th + 1, 12, u'Σ同事评分（评分*权重）', align_center)
        worksheet.merge_range(
            th + 2, 6, th + 2, 12, u'绩效总评分', align_center)
        worksheet.write(th, 13, report.self_total_score, align_center)
        worksheet.write(th, 14, report.total_score, align_center)
        worksheet.merge_range(th + 1, 13, th + 1, 14,
                              report.personnal_score, align_center)
        worksheet.merge_range(th + 2, 13, th + 2, 14, report.total_score + report.personnal_score,
                              align_center)
        th += 3

    worksheet.set_row(th, 100)
    worksheet.merge_range(th, 0, th, 4, u'自我总结：', align_center)
    worksheet.merge_range(
        th, 5, th, 14, report.now_report_obj['self_summary'], align_center)
    th += 1
    worksheet.set_row(th, 100)
    worksheet.merge_range(th, 0, th, 4, u'上级评语：', align_center)
    worksheet.merge_range(
        th, 5, th, 14, report.now_report_obj['leader_summary'], align_center)
    th += 1
    worksheet.merge_range(
        th, 0, th, 11, u'2015年6-12月关键绩效考核指标（KPI）', align_center_color)
    worksheet.write(th, 12, u'KPI权重：', align_center_color)
    worksheet.merge_range(th, 13, th, 14, u'80%', align_center_color)
    th += 1
    worksheet.merge_range(th, 0, th, 1, u'维度', align_center)
    worksheet.merge_range(th, 2, th, 6, u'指标说明（指标含义、计算公式或说明）', align_center)
    worksheet.merge_range(th, 7, th, 10, u'衡量标准(请尽量量化评价标准）', align_center)
    worksheet.write(th, 11, u'权重%', align_center)
    worksheet.write(th, 12, u'实际完成情况', align_center)
    worksheet.write(th, 13, u'员工自评', align_center)
    worksheet.write(th, 14, u'上级自评', align_center)
    th += 1
    worksheet.merge_range(th, 0, th + 2, 1, u'KR指标', align_center)
    for k in range(1, 4):
        worksheet.merge_range(
            th + k - 1, 2, th + k - 1, 6, report.future_report_obj['next_kr_' + str(k) + '_key'], align_center)
        worksheet.merge_range(
            th + k - 1, 7, th + k - 1, 10, report.future_report_obj['next_kr_' + str(k) + '_value'], align_center)
        worksheet.write(
            th + k - 1, 11, report.future_report_obj['next_kr_' + str(k) + '_w'], align_center)
        worksheet.write(th + k - 1, 12, '', align_center)
        worksheet.write(th + k - 1, 13, '', align_center)
        worksheet.write(th + k - 1, 14, '', align_center)
    th += 3
    worksheet.merge_range(th, 0, th + 2, 1, u'改进提升', align_center)
    for k in range(1, 4):
        worksheet.merge_range(
            th + k - 1, 2, th + k - 1, 6, report.future_report_obj['next_up_' + str(k) + '_key'], align_center)
        worksheet.merge_range(
            th + k - 1, 7, th + k - 1, 10, report.future_report_obj['next_up_' + str(k) + '_value'], align_center)
        worksheet.write(
            th + k - 1, 11, report.future_report_obj['next_up_' + str(k) + '_w'], align_center)
        worksheet.write(th + k - 1, 12, '', align_center)
        worksheet.write(th + k - 1, 13, '', align_center)
        worksheet.write(th + k - 1, 14, '', align_center)
    th += 3
    if report.type == 2:
        worksheet.merge_range(th, 0, th + 2, 1, u'管理指标', align_center)
        for k in range(1, 4):
            worksheet.merge_range(
                th + k - 1, 2, th + k - 1, 6, report.future_report_obj['next_manage_' + str(k) + '_key'], align_center)
            worksheet.merge_range(th + k - 1, 7, th + k - 1, 10, report.future_report_obj[
                                  'next_manage_' + str(k) + '_value'], align_center)
            worksheet.write(
                th + k - 1, 11, report.future_report_obj['next_manage_' + str(k) + '_w'], align_center)
            worksheet.write(th + k - 1, 12, '', align_center)
            worksheet.write(th + k - 1, 13, '', align_center)
            worksheet.write(th + k - 1, 14, '', align_center)
        th += 3
    worksheet.merge_range(th, 0, th, 10, u'KPI权重合计：', align_center_color)
    worksheet.write(th, 11, u'80%', align_center_color)
    worksheet.write(th, 12, u'KPI评分合计：', align_center_color)
    worksheet.write(th, 13, '', align_center_color)
    worksheet.write(th, 14, '', align_center_color)
    th += 1
    worksheet.merge_range(th, 0, th, 8, u'绩效目标确认：', align_left)
    worksheet.merge_range(th, 9, th, 14, u'绩效结果确认：', align_left)
    th += 1
    worksheet.merge_range(th, 0, th, 3, u'本人签字：', align_left)
    worksheet.merge_range(th, 4, th, 8, u'上级签字：', align_left)
    worksheet.merge_range(th, 9, th, 11, u'本人签字：', align_left)
    worksheet.merge_range(th, 12, th, 14, u'上级签字：', align_left)
    th += 1
    worksheet.merge_range(
        th, 0, th, 14, u'说明：本表在员工与上级经过充分沟通后填写，用于明确员工的绩效计划和确认绩效评估结果，由人力资源部负责留档。', align_left)

    workbook.close()
    response.data = output.getvalue()
    filename = ("%s-%s.xls" %
                (report.creator.name.encode('utf-8', 'ignore'), "的绩效考核表"))
    mimetype_tuple = mimetypes.guess_type(filename)
    response_headers = Headers({
        'Pragma': "public",
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Cache-Control': 'private',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
    response.headers = response_headers
    response.set_cookie('fileDownload', 'true', path='/')
    return response
