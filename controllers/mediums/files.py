# -*- coding: utf-8 -*-
from flask import request, redirect, url_for, Blueprint, flash, g
from flask import render_template as tpl

from models.medium import Medium
from models.user import User
from models.attachment import (ATTACHMENT_TYPE_MEDIUM_INTRODUCE, ATTACHMENT_TYPE_MEDIUM_PRODUCT,
                               ATTACHMENT_TYPE_MEDIUM_DATA, ATTACHMENT_TYPE_MEDIUM_NEW_PRODUCT,
                               ATTACHMENT_TYPE, Attachment)
from libs.files import all_files_set


mediums_files_bp = Blueprint(
    'mediums_files', __name__, template_folder='../../templates/mediums/files/')


@mediums_files_bp.route('/index', methods=['GET'])
def index():
    mediums = Medium.all()
    for k in mediums:
        all_files = list(k.get_medium_files())
        if all_files:
            k.update_time = all_files[
                0].create_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            k.update_time = u'无更新'
    return tpl('/mediums/files/index.html', mediums=mediums)


@mediums_files_bp.route('/<mid>/info', methods=['GET'])
def info(mid):
    medium = Medium.get(mid)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/mediums/files/info.html', medium=medium,
               ATTACHMENT_TYPE_MEDIUM_INTRODUCE=ATTACHMENT_TYPE_MEDIUM_INTRODUCE,
               ATTACHMENT_TYPE_MEDIUM_PRODUCT=ATTACHMENT_TYPE_MEDIUM_PRODUCT,
               ATTACHMENT_TYPE_MEDIUM_DATA=ATTACHMENT_TYPE_MEDIUM_DATA,
               ATTACHMENT_TYPE_MEDIUM_NEW_PRODUCT=ATTACHMENT_TYPE_MEDIUM_NEW_PRODUCT,
               reminder_emails=reminder_emails)


@mediums_files_bp.route('/<mid>/files_upload', methods=['POST'])
def files_upload(mid):
    medium = Medium.get(mid)
    type = int(request.values.get('type', 5))
    try:
        request.files['file'].filename.encode('gb2312')
    except:
        flash(u'文件名中包含非正常字符，请使用标准字符', 'danger')
        return redirect(url_for('mediums_files.info', mid=mid))
    filename = all_files_set.save(request.files['file'])
    medium.add_medium_files(g.user, filename, type)
    flash(ATTACHMENT_TYPE[type] + u' 上传成功', 'success')
    return redirect(url_for('mediums_files.info', mid=mid))


@mediums_files_bp.route('/<mid>/<type>/info_last', methods=['GET'])
def info_last(mid, type):
    medium = Medium.get(mid)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    return tpl('/mediums/files/info_last.html', medium=medium, type=int(type),
               title=ATTACHMENT_TYPE[int(type)],
               reminder_emails=reminder_emails)


@mediums_files_bp.route('/<mid>/files/<aid>/delete', methods=['GET'])
def files_delete(mid, aid):
    attachment = Attachment.get(aid)
    type = attachment.attachment_type
    attachment.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("mediums_files.info_last", mid=mid, type=type))
