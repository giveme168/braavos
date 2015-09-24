# -*- coding: utf-8 -*-
import datetime
from flask import request, redirect, url_for, Blueprint, flash, g, abort
from flask import render_template as tpl

from models.medium import Medium, Tag, Case, TagCase, CASE_TYPE_CN

from libs.paginator import Paginator


mediums_planning_bp = Blueprint(
    'mediums_planning', __name__, template_folder='../../templates/mediums/planning/')


@mediums_planning_bp.route('/<type>/index', methods=['GET'])
def index(type):
    page = int(request.values.get('p', 1))
    tag = int(request.values.get('tag', 0))
    medium = int(request.values.get('medium', 0))
    info = request.values.get('info', '')
    cases = list(Case.query.filter_by(type=type))
    if medium:
        cases = [case for case in cases if case.medium.id == medium]
    if info:
        cases = [case for case in cases if info in case.info]
    if tag:
        cases = [case for case in cases if tag in case.tag_ids]
    paginator = Paginator(cases, 50)
    try:
        cases = paginator.page(page)
    except:
        cases = paginator.page(paginator.num_pages)
    return tpl('/mediums/planning/index.html', title=CASE_TYPE_CN[int(type)],
               mediums=Medium.all(), medium=medium, cases=cases, type=type,
               info=info, params="&info=%s&medium=%s&tag=%s" % (
                   info, str(medium), str(tag)),
               page=page, tags=Tag.all(), tag=tag)


@mediums_planning_bp.route('/<type>/create', methods=['GET', 'POST'])
def create(type):
    if not (g.user.is_planner() or g.user.is_operater()):
        abort(403)
    if request.method == 'POST':
        name = request.values.get('name', '')
        url = request.values.get('url', '')
        medium = int(request.values.get('medium', 0))
        brand = request.values.get('brand', '')
        industry = request.values.get('industry', '')
        desc = request.values.get('desc', '')
        tags = request.values.get('tags', '').split(',')
        if Case.query.filter_by(name=name, type=type).count() > 0:
            flash(u'名称已存在', 'danger')
            return redirect(url_for('mediums_planning.create', type=type))
        case = Case.add(name=name, url=url, medium=Medium.get(medium),
                        brand=brand, industry=industry, desc=desc,
                        creator=g.user, type=type)
        case = Case.get(case.id)
        for k in tags:
            if k:
                tag = Tag.query.filter_by(name=k)
                if tag.count() > 0:
                    tag = tag.first()
                else:
                    tag = Tag.add(name=k)
                    tag = Tag.get(tag.id)
                TagCase.add(tag=tag, case=case)
        flash(u'添加成功', 'success')
        return redirect(url_for('mediums_planning.index', type=type))
    return tpl('/mediums/planning/create.html', title=CASE_TYPE_CN[int(type)],
               mediums=Medium.all(), type=type)


@mediums_planning_bp.route('/<type>/<cid>/update', methods=['GET', 'POST'])
def update(type, cid):
    if not (g.user.is_planner() or g.user.is_operater()):
        abort(403)
    case = Case.get(cid)
    if request.method == 'POST':
        name = request.values.get('name', '')
        url = request.values.get('url', '')
        medium = int(request.values.get('medium', 0))
        brand = request.values.get('brand', '')
        industry = request.values.get('industry', '')
        desc = request.values.get('desc', '')
        tags = request.values.get('tags', '').split(',')
        case.name = name
        case.url = url
        case.medium = Medium.get(medium)
        case.brand = brand
        case.industry = industry
        case.desc = desc
        case.creator = g.user
        case.create_time = datetime.datetime.now()
        case.save()
        TagCase.query.filter_by(case=case).delete()
        for k in tags:
            if k:
                tag = Tag.query.filter_by(name=k)
                if tag.count() > 0:
                    tag = tag.first()
                else:
                    tag = Tag.add(name=k)
                    tag = Tag.get(tag.id)
                TagCase.add(tag=tag, case=case)
        flash(u'修改成功', 'success')
        return redirect(url_for('mediums_planning.update', type=type, cid=cid))
    return tpl('/mediums/planning/update.html', title=CASE_TYPE_CN[int(type)],
               mediums=Medium.all(), type=type, case=case)


@mediums_planning_bp.route('/<type>/<cid>/delete', methods=['GET'])
def delete(type, cid):
    if not (g.user.is_planner() or g.user.is_operater()):
        abort(403)
    case = Case.get(cid)
    TagCase.query.filter_by(case=case).delete()
    case.delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('mediums_planning.index', type=type))


@mediums_planning_bp.route('/<type>/<cid>/info', methods=['GET'])
def info(type, cid):
    case = Case.get(cid)
    return tpl('/mediums/planning/info.html', case=case)
