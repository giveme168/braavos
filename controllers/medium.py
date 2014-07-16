#-*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl

from models.medium import Medium
from forms.medium import NewMediumForm
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
