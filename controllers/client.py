# -*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl, flash

from models.client import Client, Group, Agent
from models.medium import Medium
from forms.client import NewClientForm, NewGroupForm, NewAgentForm
from forms.medium import NewMediumForm
from models.user import Team

client_bp = Blueprint('client', __name__, template_folder='../templates/client')


@client_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('client.clients'))


@client_bp.route('/new_client', methods=['GET', 'POST'])
def new_client():
    form = NewClientForm(request.form)
    if request.method == 'POST' and form.validate():
        db_client_name = Client.name_exist(form.name.data)
        if not db_client_name:
            client = Client.add(form.name.data, form.industry.data)
            flash(u'新建客户(%s)成功!' % client.name, 'success')
        else:
            flash(u'新建客户(%s)失败,名称被占用!' % form.name.data, 'danger')
            return tpl('client.html', form=form, title=u"新建客户")
        return redirect(url_for("client.clients"))
    return tpl('client.html', form=form, title=u"新建客户")


@client_bp.route('/new_group', methods=['GET', 'POST'])
def new_group():
    form = NewGroupForm(request.form)
    if request.method == 'POST' and form.validate():
        db_group_name = Group.name_exist(form.name.data)
        if not db_group_name:
            group = Group.add(form.name.data)
            flash(u'新建甲方集团(%s)成功!' % group.name, 'success')
        else:
            flash(u'新建甲方集团(%s)失败, 名称已经被占用!' % form.name.data, 'danger')
            return tpl('group.html', form=form, group=None, title=u"新建甲方集团")
        return redirect(url_for("client.groups"))
    return tpl('group.html',
               form=form,
               group=None,
               title=u"新建甲方集团")


@client_bp.route('/new_agent', methods=['GET', 'POST'])
def new_agent():
    form = NewAgentForm(request.form)
    if request.method == 'POST' and form.validate():
        db_agent_name = Agent.name_exist(form.name.data)
        if not db_agent_name:
            agent = Agent.add(form.name.data, Group.get(form.group.data))
            flash(u'新建代理(%s)成功!' % agent.name, 'success')
        else:
            flash(u'新建代理(%s)失败, 名称已经被占用!' % form.name.data, 'danger')
            return tpl('agent.html', form=form, title=u"新建甲方")
        return redirect(url_for("client.agents"))
    return tpl('agent.html',
               form=form,
               title=u"新建甲方")


@client_bp.route('/new_medium', methods=['GET', 'POST'])
def new_medium():
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        db_medium_name = Medium.name_exist(form.name.data)
        db_medium_abbreviation = Medium.abbreviation_exist(form.abbreviation.data)
        if not db_medium_name and not db_medium_abbreviation:
            medium = Medium.add(form.name.data, Team.get(form.owner.data), form.abbreviation.data)
            flash(u'新建媒体(%s)成功!' % medium.name, 'success')
        elif db_medium_name:
            flash(u'新建媒体(%s)失败, 名称已经被占用!' % form.name.data, 'danger')
            return tpl('medium.html', form=form, title=u"新建媒体")
        else:
            flash(u'新建媒体(%s)失败, 缩写已经被占用!' % form.name.data, 'danger')
            return tpl('medium.html', form=form, title=u"新建媒体")
        return redirect(url_for("client.medium_detail", medium_id=medium.id))
    return tpl('medium.html', form=form, title=u"新建媒体")


@client_bp.route('/client/<client_id>', methods=['GET', 'POST'])
def client_detail(client_id):
    client = Client.get(client_id)
    if not client:
        abort(404)
    form = NewClientForm(request.form)
    if request.method == 'POST' and form.validate():
        client.name = form.name.data
        client.industry = form.industry.data
        client.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = client.name
        form.industry.data = client.industry
    return tpl('client.html', form=form, title=client.name)


@client_bp.route('/agent/<agent_id>', methods=['GET', 'POST'])
def agent_detail(agent_id):
    agent = Agent.get(agent_id)
    if not agent:
        abort(404)
    form = NewAgentForm(request.form)
    if request.method == 'POST' and form.validate():
        agent.name = form.name.data
        agent.group = Group.get(form.group.data)
        agent.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = agent.name
        form.group.data = agent.group.id if agent.group else None
    return tpl('agent.html',
               form=form,
               title=agent.name)


@client_bp.route('/group/<group_id>', methods=['GET', 'POST'])
def group_detail(group_id):
    group = Group.get(group_id)
    if not group:
        abort(404)
    form = NewGroupForm(request.form)
    if request.method == 'POST' and form.validate():
        group.name = form.name.data
        group.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = group.name
    return tpl('group.html',
               form=form,
               group=group,
               title=group.name)


@client_bp.route('/medium/<medium_id>', methods=['GET', 'POST'])
def medium_detail(medium_id):
    medium = Medium.get(medium_id)
    if not medium:
        abort(404)
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        medium.name = form.name.data
        medium.owner = Team.get(form.owner.data)
        medium.abbreviation = form.abbreviation.data
        medium.save()
        flash(u'保存成功!', 'success')
    else:
        form.name.data = medium.name
        form.owner.data = medium.owner_id
        form.abbreviation.data = medium.abbreviation
    return tpl('medium.html', form=form, title=medium.name)


@client_bp.route('/mediums', methods=['GET'])
def mediums():
    mediums = Medium.all()
    return tpl('mediums.html', mediums=mediums)


@client_bp.route('/clients', methods=['GET'])
def clients():
    clients = Client.all()
    return tpl('clients.html', clients=clients)


@client_bp.route('/groups', methods=['GET'])
def groups():
    groups = Group.all()
    return tpl('groups.html', groups=groups)


@client_bp.route('/agents', methods=['GET'])
def agents():
    agents = Agent.all()
    return tpl('agents.html', agents=agents)
