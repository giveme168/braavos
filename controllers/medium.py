# -*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl, flash

from models.medium import Medium, AdSize, AdUnit, AdPosition
from forms.medium import NewMediumForm, SizeForm, UnitForm, PositionForm
from models.user import Team

from . import admin_required_before_request

medium_bp = Blueprint('medium', __name__, template_folder='../templates/medium')


@medium_bp.before_request
def request_user():
    admin_required_before_request()


@medium_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('medium.mediums'))


@medium_bp.route('/new_medium', methods=['GET', 'POST'])
def new_medium():
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        medium = Medium.add(form.name.data, Team.get(form.owner.data))
        flash(u'新建媒体(%s)成功!' % medium.name, 'success')
        return redirect(url_for("medium.medium_detail", medium_id=medium.id))
    return tpl('medium.html', form=form, title=u"新建媒体")


@medium_bp.route('/medium/<medium_id>', methods=['GET', 'POST'])
def medium_detail(medium_id):
    medium = Medium.get(medium_id)
    if not medium:
        abort(404)
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        medium.name = form.name.data
        medium.owner = Team.get(form.owner.data)
        medium.save()
        flash(u'保存成功!', 'success')
    else:
        form.name.data = medium.name
        form.owner.data = medium.owner_id
    return tpl('medium.html', form=form, title=medium.name)


@medium_bp.route('/mediums', methods=['GET'])
def mediums():
    mediums = Medium.all()
    return tpl('mediums.html', mediums=mediums)


@medium_bp.route('/new_size', methods=['GET', 'POST'])
def new_size():
    form = SizeForm(request.form)
    if request.method == 'POST' and form.validate():
        ad_size = AdSize.add(form.width.data, form.height.data)
        flash(u'新建尺寸(%sx%s)成功!' % (ad_size.width, ad_size.height), 'success')
        if request.values.get('next'):
            return redirect(request.values.get('next'))
        return redirect("/")
    return tpl('size.html', form=form)


@medium_bp.route('/new_unit', methods=['GET', 'POST'])
def new_unit():
    form = UnitForm(request.form)
    if request.method == 'POST' and form.validate():
        adUnit = AdUnit.add(name=form.name.data, description=form.description.data,
                            size=AdSize.get(form.size.data), margin=form.margin.data,
                            target=form.target.data, status=form.status.data,
                            medium=Medium.get(form.medium.data), estimate_num=form.estimate_num.data)
        adUnit.positions = AdPosition.gets(form.positions.data)
        adUnit.save()
        return redirect(url_for("medium.unit_to_position", unit_id=adUnit.id))
    return tpl('unit.html', form=form, title=u"新建广告单元")


@medium_bp.route('/unit/<unit_id>', methods=['GET', 'POST'])
def unit_detail(unit_id):
    unit = AdUnit.get(unit_id)
    if not unit:
        abort(404)
    form = UnitForm(request.form)
    if request.method == 'POST' and form.validate():
        unit.name = form.name.data
        unit.description = form.description.data
        unit.size = AdSize.get(form.size.data)
        unit.margin = form.margin.data
        unit.target = form.target.data
        unit.status = form.status.data
        unit.positions = AdPosition.gets(form.positions.data)
        unit.medium = Medium.get(form.medium.data)
        unit.estimate_num = form.estimate_num.data
        unit.save()
        flash(u'保存成功!', 'success')
    else:
        form.name.data = unit.name
        form.description.data = unit.description
        form.size.data = unit.size.id
        form.margin.data = unit.margin
        form.target.data = unit.target
        form.status.data = unit.status
        form.positions.data = [x.id for x in unit.positions]
        form.medium.data = unit.medium.id
        form.estimate_num.data = unit.estimate_num
    return tpl('unit.html', form=form, title=unit.display_name)


@medium_bp.route('/units', methods=['GET'])
def units():
    units = AdUnit.all()
    return tpl('units.html', units=units)


@medium_bp.route('/new_position', methods=['GET', 'POST'])
def new_position():
    form = PositionForm(request.form)
    form.estimate_num.hidden = True
    if request.method == 'POST' and form.validate():
        ad_position = AdPosition.add(name=form.name.data, description=form.description.data,
                                     size=AdSize.get(form.size.data), standard=form.standard.data,
                                     status=form.status.data, medium=Medium.get(form.medium.data),
                                     level=form.level.data, ad_type=form.ad_type.data,
                                     cpd_num=form.cpd_num.data, max_order_num=form.max_order_num.data,
                                     price=form.price.data)
        ad_position.units = AdUnit.gets(form.units.data)
        ad_position.save()
        flash(u'新建展示位置成功!', 'success')
        return redirect(url_for("medium.position_detail", position_id=ad_position.id))
    return tpl('position.html', form=form, title=u"新建展示位置")


@medium_bp.route('/position_by_unit/<unit_id>', methods=['GET', 'POST'])
def unit_to_position(unit_id):
    unit = AdUnit.get(unit_id)
    form = PositionForm(request.form)
    form.estimate_num.hidden = True
    if request.method == 'POST' and form.validate():
        ad_position = AdPosition.add(name=form.name.data, description=form.description.data,
                                     size=AdSize.get(form.size.data), standard=form.standard.data,
                                     status=form.status.data, medium=Medium.get(form.medium.data),
                                     level=form.level.data, ad_type=form.ad_type.data,
                                     cpd_num=form.cpd_num.data, max_order_num=form.max_order_num.data,
                                     price=form.price.data)
        adPosition.units = AdUnit.gets(form.units.data)
        adPosition.save()
        return redirect(url_for("medium.position_detail", position_id=adPosition.id))
    else:
        form.name.data = unit.name
        form.description.data = unit.description
        form.medium.data = unit.medium.id
        form.size.data = unit.size.id
        form.status.data = unit.status
        form.units.data = [unit.id]
    return tpl('position.html', form=form, title=u"创建广告单元(%s)对应的展示位置" % unit.name)


@medium_bp.route('/position/<position_id>', methods=['GET', 'POST'])
def position_detail(position_id):
    position = AdPosition.get(position_id)
    if not position:
        abort(404)
    form = PositionForm(request.form)
    if request.method == 'POST' and form.validate():
        position.name = form.name.data
        position.description = form.description.data
        position.size = AdSize.get(form.size.data)
        position.standard = form.standard.data
        position.status = form.status.data
        position.units = AdUnit.gets(form.units.data)
        position.medium = Medium.get(form.medium.data)
        position.level = form.level.data
        position.ad_type = form.ad_type.data
        position.cpd_num = form.cpd_num.data
        position.max_order_num = form.max_order_num.data
        position.price = form.price.data
        position.save()
        flash(u'保存成功!', 'success')
    else:
        form.name.data = position.name
        form.description.data = position.description
        form.size.data = position.size.id
        form.standard.data = position.standard
        form.status.data = position.status
        form.units.data = [x.id for x in position.units]
        form.medium.data = position.medium.id
        form.level.data = position.level
        form.ad_type.data = position.ad_type
        form.cpd_num.data = position.cpd_num
        form.max_order_num.data = position.max_order_num
        form.price.data = position.price
        form.estimate_num.data = position.estimate_num
        form.estimate_num.readonly = True
    return tpl('position.html', form=form, title=position.display_name)


@medium_bp.route('/positions', methods=['GET'])
def positions():
    positions = AdPosition.all()
    return tpl('positions.html', positions=positions)
