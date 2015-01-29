# -*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl, flash

from models.outsource import OutSourceTarget
from forms.outsource import OutSourceTargetForm

outsource_bp = Blueprint('outsource', __name__, template_folder='../templates/outsource')


@outsource_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('outsource.targets'))


@outsource_bp.route('/targets', methods=['GET'])
def targets():
    targets = OutSourceTarget.all()
    return tpl('targets.html', targets=targets)


@outsource_bp.route('/new_target', methods=['GET', 'POST'])
def new_target():
    form = OutSourceTargetForm(request.form)
    if request.method == 'POST' and form.validate():
        target = OutSourceTarget.add(name=form.name.data,
                                     bank=form.bank.data,
                                     card=form.card.data,
                                     alipay=form.alipay.data,
                                     contract=form.contract.data,
                                     type=form.type.data,
                                     remark=form.remark.data)
        flash(u'新建外包收款方(%s)成功!' % target.name, 'success')
        return redirect(url_for("outsource.target_detail", target_id=target.id))
    return tpl('target.html', form=form, title=u"新建收款方")


@outsource_bp.route('/client/<target_id>', methods=['GET', 'POST'])
def target_detail(target_id):
    target = OutSourceTarget.get(target_id)
    if not target:
        abort(404)
    form = OutSourceTargetForm(request.form)
    if request.method == 'POST' and form.validate():
        target.name = form.name.data
        target.bank = form.bank.data
        target.card = form.card.data
        target.alipay = form.alipay.data
        target.contract = form.contract.data
        target.remark = form.remark.data
        target.type = form.type.data
        target.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = target.name
        form.bank.data = target.bank
        form.card.data = target.card
        form.alipay.data = target.alipay
        form.contract.data = target.contract
        form.remark.data = target.remark
        form.type.data = target.type
    return tpl('target.html', form=form, title=u"收款方-" + target.name)
