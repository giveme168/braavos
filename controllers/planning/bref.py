# -*- coding: utf-8 -*-
import datetime
from flask import request, redirect, url_for, Blueprint, flash, g, current_app
from flask import render_template as tpl

from models.planning import Bref, BREF_STATUS_CN
from models.user import User, TEAM_TYPE_PLANNER
from forms.planning import BrefForm

from libs.email_signals import planning_bref_signal
from libs.paginator import Paginator

planning_bref_bp = Blueprint(
    'planning_bref', __name__, template_folder='../../templates/planning/bref')


@planning_bref_bp.route('/', methods=['GET'])
def index():
    brefs = list(Bref.all())
    if g.user.is_leader() or g.user.is_operater_leader():
        brefs = [k for k in brefs if k.location == g.user.location and k.status != 1]
    elif g.user.is_planner():
        brefs = [k for k in brefs if k.status != 1]
    else:
        brefs = [k for k in brefs if k.creator == g.user]

    if g.user.team.type in [0, 14]:
        brefs = list(Bref.all())

    page = int(request.values.get('p', 1))
    location = int(request.values.get('location', 0))
    status = int(request.values.get('status', 100))
    info = request.values.get('info', '')

    if location != 0:
        brefs = [b for b in brefs if b.location == location]
    if status != 100:
        brefs = [b for b in brefs if b.status == status]
    if info:
        brefs = [b for b in brefs if info in b.info]
    paginator = Paginator(brefs, 20)
    try:
        brefs = paginator.page(page)
    except:
        brefs = paginator.page(paginator.num_pages)
    return tpl('/planning/bref/index.html', brefs=brefs,
               BREF_STATUS_CN=BREF_STATUS_CN, status=status,
               location=location, info=info,
               params='&location=%s&status=%s&info=%s' % (str(location), str(status), info))


@planning_bref_bp.route('/create', methods=['GET', 'POST'])
def create():
    form = BrefForm(request.form)
    if request.method == 'POST' and form.validate():
        get_time = datetime.datetime.strptime(
            request.values.get('get_time'), '%Y-%m-%d %H')
        bref = Bref.add(
            title=form.title.data,
            agent=form.agent.data,
            brand=form.brand.data,
            product=form.product.data,
            target=form.target.data,
            background=form.background.data,
            push_target=form.push_target.data,
            push_theme=form.push_theme.data,
            push_time=form.push_time.data,
            budget=form.budget.data,
            is_temp=form.is_temp.data,
            # 项目信息
            agent_type=form.agent_type.data,
            use_type=form.use_type.data,
            level=form.level.data,
            get_time=get_time,
            # 补充说明
            intent_medium=form.intent_medium.data,
            suggest=form.suggest.data,
            desc=form.desc.data,
            url='',
            status=1,
            create_time=datetime.datetime.now(),
            update_time=datetime.datetime.now(),
            creator=g.user,
            follow_id=0,
            to_id=0,
        )
        flash(u'添加成功', 'success')
        bref.add_comment(g.user, u"新建了策划单:%s" % (bref.title,), msg_channel=7)
        return redirect(url_for('planning_bref.info', bid=bref.id))
    return tpl('/planning/bref/create.html', form=form)


@planning_bref_bp.route('/<bid>/info', methods=['GET', 'POST'])
def info(bid):
    bref = Bref.get(bid)
    reminder_emails = [(u.name, u.email) for u in User.all_active()]
    planner_emails = [(u.name, u.id) for u in User.all_active()
                      if u.team.type == TEAM_TYPE_PLANNER]
    form = BrefForm(request.form)
    form.title.data = bref.title
    form.agent.data = bref.agent
    form.brand.data = bref.brand
    form.product.data = bref.product
    form.target.data = bref.target
    form.background.data = bref.background
    form.push_target.data = bref.push_target
    form.push_theme.data = bref.push_theme
    form.push_time.data = bref.push_time
    form.budget.data = bref.budget
    form.is_temp.data = bref.is_temp
    form.agent_type.data = bref.agent_type
    form.use_type.data = bref.use_type
    form.level.data = bref.level
    form.intent_medium.data = bref.intent_medium
    form.suggest.data = bref.suggest
    form.desc.data = bref.desc
    return tpl('/planning/bref/info.html', bref=bref,
               reminder_emails=reminder_emails, planner_emails=planner_emails, form=form)


@planning_bref_bp.route('/<bid>/update', methods=['GET', 'POST'])
def update(bid):
    bref = Bref.get(bid)
    form = BrefForm(request.form)
    if request.method == 'POST' and form.validate():
        get_time = datetime.datetime.strptime(
            request.values.get('get_time'), '%Y-%m-%d %H')
        bref.title = form.title.data
        bref.agent = form.agent.data
        bref.brand = form.brand.data
        bref.product = form.product.data
        bref.target = form.target.data
        bref.background = form.background.data
        bref.push_target = form.push_target.data
        bref.push_theme = form.push_theme.data
        bref.push_time = form.push_time.data
        bref.budget = form.budget.data
        bref.is_temp = form.is_temp.data
        # 项目信息
        bref.agent_type = form.agent_type.data
        bref.use_type = form.use_type.data
        bref.level = form.level.data
        bref.get_time = get_time
        # 补充说明
        bref.intent_medium = form.intent_medium.data
        bref.suggest = form.suggest.data
        bref.desc = form.desc.data

        bref.update_time = datetime.datetime.now(),
        flash(u'修改成功', 'success')
        bref.add_comment(g.user,
                         u"修改了策划单:%s \n\r " % (bref.title),
                         msg_channel=7)
        return redirect(url_for('planning_bref.info', bid=bref.id))
    return tpl('/planning/bref/update.html')


@planning_bref_bp.route('/<bid>/status', methods=['GET', 'POST'])
def status(bid):
    bref = Bref.get(bid)
    if request.method == 'POST':
        action = int(request.values.get('action', 1))
        emails = request.values.getlist('email')
        msg = request.values.get('msg', '')
        if action == 2:
            bref.status = 2
            flash(u'申请成功，请等待策划团队反馈', 'success')
            bref.add_comment(g.user, u"申请了策划单:%s \n\r%s" %
                             (bref.title, msg), msg_channel=7)
        elif action == 10:
            bref.status = 10
            flash(u'取消成功', 'success')
            bref.add_comment(g.user, u"取消了策划单:%s \n\r%s" %
                             (bref.title, msg), msg_channel=7)
        elif action == 1:
            bref.status = 1
            flash(u'打回成功', 'success')
            bref.add_comment(g.user, u"打回了策划单:%s \n\r%s" %
                             (bref.title, msg), msg_channel=7)
        elif action == 3:
            toer_id = int(request.values.get('toer', 0))
            bref.status = 3
            bref.to_id = toer_id
            bref.follow_id = g.user.id
            flash(u'分配成功', 'success')
            toers_name = User.get(toer_id).name
            bref.add_comment(g.user, u"分配了策划单:%s \n\r 分配给:%s \n\r %s" % (
                bref.title, toers_name, msg), msg_channel=7)
        elif action == 0:
            bref.status = 0
            bref.url = request.values.get('url', '')
            flash(u'恭喜你完成了策划单，辛苦了！', 'success')
            bref.add_comment(g.user, u"完成了策划单:%s \n\r%s" %
                             (bref.title, msg), msg_channel=7)
        bref.update_time = datetime.datetime.now()
        bref.cc = '|'.join(emails)
        bref.save()
        apply_context = {"sender": g.user,
                         "status": action,
                         "to_other": emails,
                         "msg": msg,
                         "bref": bref}
        planning_bref_signal.send(
            current_app._get_current_object(), apply_context=apply_context)
        return redirect(url_for('planning_bref.info', bid=bid))
    return tpl('/planning/bref/status.html')
