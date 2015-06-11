# -*- coding: utf-8 -*-
import datetime

from flask import request, redirect, url_for, Blueprint, flash, json, jsonify
from flask import render_template as tpl

from models.medium import Medium, MediumProductPC, MediumProductApp, MediumProductDown, MediumResource
from forms.medium import NewMediumResourceForm
from libs.paginator import Paginator

mediums_resource_bp = Blueprint(
    'mediums_resource', __name__, template_folder='../../templates/mediums/resource/')


@mediums_resource_bp.route('/resource/index', methods=['GET'])
def index():
    page = int(request.values.get('p', 1))
    resources = MediumResource.all()
    paginator = Paginator(list(resources), 50)
    try:
        resources = paginator.page(page)
    except:
        resources = paginator.page(paginator.num_pages)
    for k in resources.object_list:
        if k.type == 1:
            k.product_obj = MediumProductPC.get(k.product)
        elif k.type == 2:
            k.product_obj = MediumProductApp.get(k.product)
        elif k.type == 3:
            k.product_obj = MediumProductDown.get(k.product)
    return tpl('/mediums/resource/index.html', resources=resources)


@mediums_resource_bp.route('/resource/create', methods=['GET', 'POST'])
def create():
    form = NewMediumResourceForm(request.form)
    if request.method == 'POST' and form.validate():
        if MediumResource.query.filter_by(number=form.number.data).count() > 0:
            flash(u'资源标号已存在', 'danger')
            return tpl('/mediums/resource/create.html', form=form)
        body = []
        custom_ids = request.values.get('custom_ids', '')
        for x in custom_ids.split('|'):
            key = request.values.get('custom_key_' + str(x), '')
            value = request.values.get('custom_value_' + str(x), '')
            body.append({'c_key': key, 'c_value': value})
        MediumResource.add(medium=Medium.get(form.medium.data),
                           type=form.type.data,
                           number=form.number.data,
                           shape=form.shape.data,
                           product=form.product.data,
                           resource_type=form.resource_type.data,
                           page_postion=form.page_postion.data,
                           ad_position=form.ad_position.data,
                           cpm=form.cpm.data,
                           b_click=form.b_click.data,
                           click_rate=form.click_rate.data,
                           buy_unit=form.buy_unit.data,
                           buy_threshold=form.buy_threshold.data,
                           money=form.money.data,
                           b_directional=form.b_directional.data,
                           directional_type=form.directional_type.data,
                           directional_money=form.directional_money.data,
                           discount=form.discount.data,
                           ad_size=form.ad_size.data,
                           materiel_format=form.materiel_format.data,
                           less_buy=form.less_buy.data,
                           b_give=form.b_give.data,
                           give_desc=form.give_desc.data,
                           b_check_exposure=form.b_check_exposure.data,
                           b_check_click=form.b_check_click.data,
                           b_out_link=form.b_out_link.data,
                           b_in_link=form.b_in_link.data,
                           description=form.description.data,
                           create_time=datetime.datetime.now(),
                           update_time=datetime.datetime.now(),
                           body=json.dumps(body))
        flash(u'添加成功', 'success')
        return redirect(url_for('mediums_resource.index'))
    return tpl('/mediums/resource/create.html', form=form)


@mediums_resource_bp.route('/resource/<pid>/update', methods=['GET', 'POST'])
def update(pid):
    resource = MediumResource.get(pid)
    form = NewMediumResourceForm(request.form)
    form.medium.data = resource.medium.id
    form.type.data = resource.type
    form.number.data = resource.number
    form.shape.data = resource.shape
    form.product.data = resource.product
    form.resource_type.data = resource.resource_type
    form.page_postion.data = resource.page_postion
    form.ad_position.data = resource.ad_position
    form.cpm.data = resource.cpm
    form.b_click.data = resource.b_click
    form.click_rate.data = resource.click_rate
    form.buy_unit.data = resource.buy_unit
    form.buy_threshold.data = resource.buy_threshold
    form.money.data = resource.money
    form.b_directional.data = resource.b_directional
    form.directional_type.data = resource.directional_type
    form.directional_money.data = resource.directional_money
    form.discount.data = resource.discount
    form.ad_size.data = resource.ad_size
    form.materiel_format.data = resource.materiel_format
    form.less_buy.data = resource.less_buy
    form.b_give.data = resource.b_give
    form.give_desc.data = resource.give_desc
    form.b_check_exposure.data = resource.b_check_exposure
    form.b_check_click.data = resource.b_check_click
    form.b_out_link.data = resource.b_out_link
    form.b_in_link.data = resource.b_in_link
    form.description.data = resource.description
    resource.c_body = json.loads(resource.body)
    if request.method == 'POST' and form.validate():
        body = []
        custom_ids = request.values.get('custom_ids', '')
        for x in custom_ids.split('|'):
            key = request.values.get('custom_key_' + str(x), '')
            value = request.values.get('custom_value_' + str(x), '')
            body.append({'c_key': key, 'c_value': value})
        form = NewMediumResourceForm(request.form)
        if resource.number != form.number.data and MediumResource.query.filter_by(number=form.number.data).count() > 0:
            flash(u'资源编号已存在', 'danger')
            return tpl('/mediums/resource/update.html', form=form, resource=resource)
        resource.medium = Medium.get(form.medium.data)
        resource.type = form.type.data
        resource.number = form.number.data
        resource.shape = form.shape.data
        resource.product = form.product.data
        resource.resource_type = form.resource_type.data
        resource.page_postion = form.page_postion.data
        resource.ad_position = form.ad_position.data
        resource.cpm = form.cpm.data
        resource.b_click = form.b_click.data
        resource.click_rate = form.click_rate.data
        resource.buy_unit = form.buy_unit.data
        resource.buy_threshold = form.buy_threshold.data
        resource.money = form.money.data
        resource.b_directional = form.b_directional.data
        resource.directional_type = form.directional_type.data
        resource.directional_money = form.directional_money.data
        resource.discount = form.discount.data
        resource.ad_size = form.ad_size.data
        resource.materiel_format = form.materiel_format.data
        resource.less_buy = form.less_buy.data
        resource.b_give = form.b_give.data
        resource.give_desc = form.give_desc.data
        resource.b_check_exposure = form.b_check_exposure.data
        resource.b_check_click = form.b_check_click.data
        resource.b_out_link = form.b_out_link.data
        resource.b_in_link = form.b_in_link.data
        resource.description = form.description.data
        resource.body = json.dumps(body)
        resource.update_time = datetime.datetime.now()
        resource.save()
        flash(u'修改成功', 'success')
        return redirect(url_for('mediums_resource.update', pid=resource.id))
    return tpl('/mediums/resource/update.html', resource=resource, form=form)


@mediums_resource_bp.route('/resource/get_product', methods=['GET', 'POST'])
def get_product():
    type = int(request.values.get('type', 1))
    medium = request.values.get('medium', 1)
    if type == 1:
        products = [{'id': k.id, 'name': k.name}
                    for k in MediumProductPC.query.filter_by(medium_id=medium)]
    elif type == 2:
        products = [{'id': k.id, 'name': k.name}
                    for k in MediumProductApp.query.filter_by(medium_id=medium)]
    elif type == 3:
        products = [{'id': k.id, 'name': k.name}
                    for k in MediumProductDown.query.filter_by(medium_id=medium)]
    return jsonify({'products': products})


@mediums_resource_bp.route('/resource/<pid>/info', methods=['GET', 'POST'])
def info(pid):
    resource = MediumResource.get(pid)
    resource.c_body = json.loads(resource.body)
    if resource.type == 1:
        resource.product_obj = MediumProductPC.get(resource.product)
    elif resource.type == 2:
        resource.product_obj = MediumProductApp.get(resource.product)
    elif resource.type == 3:
        resource.product_obj = MediumProductDown.get(resource.product)
    return tpl('/mediums/resource/info.html', resource=resource)


@mediums_resource_bp.route('/resource/<pid>/delete', methods=['GET'])
def delete(pid):
    MediumResource.get(pid).delete()
    return jsonify({'id': pid})
