# -*- coding: utf-8 -*-
import datetime
from flask import request, redirect, url_for, Blueprint, flash, g, abort
from flask import render_template as tpl

from models.medium import Medium, Tag, Case, TagCase, CASE_TYPE_CN, Media

from libs.paginator import Paginator
from wtforms import SelectMultipleField
from libs.wtf import Form

mediums_planning_bp = Blueprint(
    'mediums_planning', __name__, template_folder='../../templates/mediums/planning/')


INDUSTRY = [u'汽车', u'时尚', u'酒精', u'化妆品', u'奢侈品',
            u'旅游', u'IT', u'家电', u'移动', u'快消', u'金融', u'其他']


class MediasForm(Form):
    medias = SelectMultipleField(u'所属媒体', coerce=int)

    def __init__(self, *args, **kwargs):
        super(MediasForm, self).__init__(*args, **kwargs)
        self.medias.choices = [(m.id, m.name) for m in Media.all()]


@mediums_planning_bp.route('/<type>/index', methods=['GET'])
def index(type):
    page = int(request.values.get('p', 1))
    industry = request.values.get('industry', '')
    medium = int(request.values.get('medium', 0))
    info = request.values.get('info', '')
    cases = list(Case.query.filter_by(type=type))
    if medium:
        cases = [case for case in cases if medium in case.mediums_id]
    if info:
        cases = [case for case in cases if info in case.info]
    if industry:
        cases = [case for case in cases if industry == case.industry]
    paginator = Paginator(cases, 50)
    try:
        cases = paginator.page(page)
    except:
        cases = paginator.page(paginator.num_pages)
    return tpl('/mediums/planning/index.html', title=CASE_TYPE_CN[int(type)],
               mediums=Media.all(), medium=medium, cases=cases, type=type,
               info=info, params="&info=%s&medium=%s&industry=%s" % (
                   info, str(medium), industry), INDUSTRY=INDUSTRY,
               page=page, tags=Tag.all(), industry=industry)


@mediums_planning_bp.route('/<type>/create', methods=['GET', 'POST'])
def create(type):
    if not (g.user.is_planner() or g.user.is_operater()):
        abort(403)
    medias_form = MediasForm(request.form)
    if request.method == 'POST':
        name = request.values.get('name', '')
        url = request.values.get('url', '')
        brand = request.values.get('brand', '')
        industry = request.values.get('industry', '')
        desc = request.values.get('desc', '')
        pwd = request.values.get('pwd', '')
        tags = request.values.get('tags', '').split(',')
        is_win = int(request.values.get('is_win', 0))
        if Case.query.filter_by(name=name, type=type).count() > 0:
            flash(u'名称已存在', 'danger')
            return redirect(url_for('mediums_planning.create', type=type))
        case = Case.add(name=name, url=url, medium=Medium.get(1),
                        medias=Media.gets(request.values.getlist('medias')),
                        brand=brand, industry=industry, desc=desc,
                        creator=g.user, type=type, is_win=is_win,
                        pwd=pwd)
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
               mediums=Media.all(), type=type, medias_form=medias_form,
               INDUSTRY=INDUSTRY)


@mediums_planning_bp.route('/<type>/<cid>/update', methods=['GET', 'POST'])
def update(type, cid):
    if not (g.user.is_planner() or g.user.is_operater()):
        abort(403)
    case = Case.get(cid)
    medias_form = MediasForm(request.form)
    medias_form.medias.data = [u.id for u in case.medias]
    if request.method == 'POST':
        name = request.values.get('name', '')
        url = request.values.get('url', '')
        brand = request.values.get('brand', '')
        industry = request.values.get('industry', '')
        desc = request.values.get('desc', '')
        tags = request.values.get('tags', '').split(',')
        is_win = int(request.values.get('is_win', 0))
        pwd = request.values.get('pwd', '')
        case.name = name
        case.url = url
        case.medium = Medium.get(1)
        case.medias = Media.gets(request.values.getlist('medias'))
        case.brand = brand
        case.industry = industry
        case.desc = desc
        case.is_win = is_win
        case.creator = g.user
        case.create_time = datetime.datetime.now()
        case.pwd = pwd
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
               medias=Media.all(), type=type, case=case, medias_form=medias_form,
               INDUSTRY=INDUSTRY)


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
