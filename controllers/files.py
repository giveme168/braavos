# -*- coding: UTF-8 -*-
from flask import Blueprint, request, current_app as app, abort, g, render_template as tpl
from flask import jsonify, send_from_directory, url_for, redirect, flash

from models.order import Order
from models.client_order import ClientOrder
from models.user import User, TEAM_TYPE_CONTRACT
from libs.files import files_set, attachment_set
from libs.signals import contract_apply_signal


files_bp = Blueprint('files', __name__, template_folder='../templates/files')


@files_bp.route('/files/<filename>', methods=['GET'])
def files(filename):
    config = app.upload_set_config.get('files')
    if config is None:
        abort(404)
    return send_from_directory(config.destination, filename)


@files_bp.route('/attachment/<filename>', methods=['GET'])
def attachment(filename):
    config = app.upload_set_config.get('attachment')
    if config is None:
        abort(404)
    return send_from_directory(config.destination, filename)


@files_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        filename = files_set.save(request.files['file'])
        return jsonify({'status': 0, 'filename': filename})
    return jsonify({'status': 1, 'msg': 'file not exits or type not allowed'})


@files_bp.route('/client/contract/upload', methods=['POST'])
def client_contract_upload():
    order_id = request.values.get('order')
    co = ClientOrder.get(order_id)
    if co and 'file' in request.files:
        filename = attachment_set.save(request.files['file'])
        attachment = co.add_contract_attachment(g.user, filename)
        flash(u'合同文件上传成功!', 'success')
        contract_email(co, attachment)
    else:
        flash(u'订单不存在，或文件上传出错!', 'danger')
    return redirect(url_for('order.order_info', order_id=co.id))


@files_bp.route('/client/schedule/upload', methods=['POST'])
def client_schedule_upload():
    order_id = request.values.get('order')
    co = ClientOrder.get(order_id)
    if co and 'file' in request.files:
        filename = attachment_set.save(request.files['file'])
        attachment = co.add_schedule_attachment(g.user, filename)
        flash(u'排期文件上传成功!', 'success')
        contract_email(co, attachment)
    else:
        flash(u'订单不存在，或文件上传出错!', 'danger')
    return redirect(url_for('order.order_info', order_id=co.id))


@files_bp.route('/medium/contract/upload', methods=['POST'])
def medium_contract_upload():
    order_id = request.values.get('order')
    order = Order.get(order_id)
    if order and 'file' in request.files:
        filename = attachment_set.save(request.files['file'])
        attachment = order.add_contract_attachment(g.user, filename)
        flash(u'合同文件上传成功!', 'success')
        contract_email(order.client_order, attachment)
    else:
        flash(u'订单不存在，或文件上传出错!', 'danger')
    return redirect(url_for('order.order_info', order_id=order.client_order.id))


@files_bp.route('/medium/schedule/upload', methods=['POST'])
def medium_schedule_upload():
    order_id = request.values.get('order')
    order = Order.get(order_id)
    if order and 'file' in request.files:
        filename = attachment_set.save(request.files['file'])
        attachment = order.add_schedule_attachment(g.user, filename)
        flash(u'排期文件上传成功!', 'success')
        contract_email(order.client_order, attachment)
    else:
        flash(u'订单不存在，或文件上传出错!', 'danger')
    return redirect(url_for('order.order_info', order_id=order.client_order.id))


@files_bp.route('/client_order/<order_id>/all_files', methods=['get'])
def client_order_files(order_id):
    co = ClientOrder.get(order_id)
    return tpl("order_files.html", order=co)


@files_bp.route('/medium_order/<order_id>/all_files', methods=['get'])
def medium_order_files(order_id):
    co = Order.get(order_id)
    return tpl("order_files.html", order=co)


def contract_email(order, attachment):
    contract_emails = [m.email for m in User.gets_by_team_type(TEAM_TYPE_CONTRACT)]
    action_msg = u"新上传%s文件:%s" % (attachment.type_cn, attachment.filename)
    msg = u"文件名:%s\n状态:%s\n上传者:%s\n" % (attachment.filename, attachment.status_cn, g.user.name)
    apply_context = {"sender": g.user,
                     "to": contract_emails,
                     "action_msg": action_msg,
                     "msg": msg,
                     "order": order}
    contract_apply_signal.send(apply_context)
