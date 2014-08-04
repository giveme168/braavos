#-*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl

from models.medium import Medium, AdSize, AdUnit, AdPosition
from forms.medium import NewMediumForm, SizeForm, UnitForm, PositionForm
from models.user import Team

medium_bp = Blueprint('medium', __name__, template_folder='../templates/medium')


@medium_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('medium.mediums'))


@medium_bp.route('/new_medium', methods=['GET', 'POST'])
def new_medium():
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        medium = Medium(form.name.data, Team.get(form.owner.data))
        medium.add()
        return redirect(url_for("medium.mediums"))
    return tpl('medium.html', form=form)


@medium_bp.route('/medium_detail/<medium_id>', methods=['GET', 'POST'])
def medium_detail(medium_id):
    medium = Medium.get(medium_id)
    if not medium:
        abort(404)
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        medium.name = form.name.data
        medium.owner = Team.get(form.owner.data)
        medium.save()
        return redirect(url_for("medium.mediums"))
    else:
        form.name.data = medium.name
        form.owner.data = medium.owner_id
    return tpl('medium.html', form=form)


@medium_bp.route('/mediums', methods=['GET'])
def mediums():
    mediums = Medium.all()
    return tpl('mediums.html', mediums=mediums)


@medium_bp.route('/new_size', methods=['GET', 'POST'])
def new_size():
    form = SizeForm(request.form)
    if request.method == 'POST' and form.validate():
        adSize = AdSize(form.width.data, form.height.data)
        adSize.add()
        if request.values.get('next'):
            return redirect(request.values.get('next'))
        return redirect("/")
    return tpl('size.html', form=form)


@medium_bp.route('/new_unit', methods=['GET', 'POST'])
def new_unit():
    form = UnitForm(request.form)
    if request.method == 'POST' and form.validate():
        adUnit = AdUnit(name=form.name.data, description=form.description.data,
                        size=AdSize.get(form.size.data), margin=form.margin.data,
                        target=form.target.data, status=form.status.data,
                        medium=Medium.get(form.medium.data), estimate_num=form.estimate_num.data)
        adUnit.positions = AdPosition.gets(form.positions.data)
        adUnit.add()
        return redirect(url_for("medium.units"))
    return tpl('unit.html', form=form)


@medium_bp.route('/unit_detail/<unit_id>', methods=['GET', 'POST'])
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
        return redirect(url_for("medium.units"))
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
    return tpl('unit.html', form=form)


@medium_bp.route('/units', methods=['GET'])
def units():
    units = AdUnit.all()
    return tpl('units.html', units=units)


@medium_bp.route('/new_position', methods=['GET', 'POST'])
def new_position():
    form = PositionForm(request.form)
    if request.method == 'POST' and form.validate():
        adPosition = AdPosition(name=form.name.data, description=form.description.data,
                                size=AdSize.get(form.size.data), status=form.status.data,
                                medium=Medium.get(form.medium.data), level=form.level.data,
                                ad_type=form.ad_type.data, cpd_num=form.cpd_num.data,
                                max_order_num=form.max_order_num.data)
        adPosition.units = AdUnit.gets(form.units.data)
        adPosition.add()
        return redirect(url_for("medium.positions"))
    return tpl('position.html', form=form, show_estimate=False)


@medium_bp.route('/position_detail/<position_id>', methods=['GET', 'POST'])
def position_detail(position_id):
    position = AdPosition.get(position_id)
    if not position:
        abort(404)
    form = PositionForm(request.form)
    if request.method == 'POST' and form.validate():
        position.name = form.name.data
        position.description = form.description.data
        position.size = AdSize.get(form.size.data)
        position.status = form.status.data
        position.units = AdUnit.gets(form.units.data)
        position.medium = Medium.get(form.medium.data)
        position.level = form.level.data
        position.ad_type = form.ad_type.data
        position.cpd_num = form.cpd_num.data
        position.max_order_num = form.max_order_num.data
        position.save()
        return redirect(url_for("medium.positions"))
    else:
        form.name.data = position.name
        form.description.data = position.description
        form.size.data = position.size.id
        form.status.data = position.status
        form.units.data = [x.id for x in position.units]
        form.medium.data = position.medium.id
        form.level.data = position.level
        form.ad_type.data = position.ad_type
        form.cpd_num.data = position.cpd_num
        form.max_order_num.data = position.max_order_num
        form.estimate_num.data = position.estimate_num
        form.estimate_num.readonly = True
    return tpl('position.html', form=form, show_estimate=True)


@medium_bp.route('/positions', methods=['GET'])
def positions():
    positions = AdPosition.all()
    return tpl('positions.html', positions=positions)
