# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, request, redirect, g, jsonify, flash, json, current_app as app
from flask import url_for, render_template as tpl
from wtforms import SelectMultipleField

from models.user import User, UserHandBook
from models.account.data import Notice
from libs.files import files_set
from libs.wtf import Form

account_data_bp = Blueprint(
    'account_data', __name__, template_folder='../../templates/account/data/')


class EmailsForm(Form):
    emails = SelectMultipleField(u'抄送人', coerce=int)

    def __init__(self, *args, **kwargs):
        super(EmailsForm, self).__init__(*args, **kwargs)
        self.emails.choices = [(u.email, u.name) for u in User.all_active()]


@account_data_bp.route('/handbook', methods=['GET', 'POST'])
def handbook():
    if request.method == 'POST':
        user_hand_book = UserHandBook.query.filter_by(user=g.user).first()
        if not user_hand_book:
            UserHandBook.add(user=g.user, create_time=datetime.datetime.now())
        return redirect('/')
    return tpl('/account/data/handbook.html')


@account_data_bp.route('/notice/index', methods=['GET', 'POST'])
def notice_index():
    notices = Notice.all()
    return tpl('/account/data/notice/index.html', notices=notices)


@account_data_bp.route('/notice/create', methods=['GET', 'POST'])
def notice_create():
    if request.method == 'POST':
        title = request.values.get('title', '')
        emails = request.values.getlist('emails')
        create = request.values.get(
            'create', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        content = request.values.get('content', '')
        if not title:
            flash(u'请填写标题', 'danger')
            return tpl('/account/data/notice.html', to_emails=User.all_active())
        if not content:
            flash(u'请填写内容', 'danger')
            return tpl('/account/data/notice.html', to_emails=User.all_active())
        Notice.add(
            title=title,
            emails=json.dumps(emails),
            create_time=create,
            creator=g.user,
            content=content
        )
        flash(u'添加成功', 'success')
        return redirect(url_for('account_data.notice_index'))
    return tpl('/account/data/notice/create.html', to_emails=User.all_active())


@account_data_bp.route('/notice/<nid>/delete', methods=['GET'])
def notice_delete(nid):
    Notice.get(nid).delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('account_data.notice_index'))


@account_data_bp.route('/notice/<nid>/update', methods=['GET', 'POST'])
def notice_update(nid):
    notice = Notice.get(nid)
    notice.emails_s = json.loads(notice.emails)
    if request.method == 'POST':
        title = request.values.get('title', '')
        emails = request.values.getlist('emails')
        create = request.values.get(
            'create', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        content = request.values.get('content', '')
        if not title:
            flash(u'请填写标题', 'danger')
            return tpl('/account/data/notice.html', notice=notice, to_emails=User.all_active())
        if not content:
            flash(u'请填写内容', 'danger')
            return tpl('/account/data/notice.html', notice=notice, to_emails=User.all_active())
        notice.title = title
        notice.emails = json.dumps(emails)
        notice.create_time = create
        notice.creator = g.user
        notice.content = content
        notice.save()
        flash(u'修改成功', 'success')
        return redirect(url_for('account_data.notice_index'))
    return tpl('/account/data/notice/create.html', notice=notice, to_emails=User.all_active())


@account_data_bp.route('/upload', methods=['POST'])
def upload():
    try:
        request.files['imgFile'].filename.encode('gb2312')
    except:
        return jsonify({"error": 1, "message": "文件名中包含非正常字符，请使用标准字符"})
    filename = files_set.save(request.files['imgFile'])
    url = app.config['DOMAIN'] + files_set.url(filename)
    return jsonify({"error": 0, "url": url})
