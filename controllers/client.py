# -*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl, flash

from models.client import Client, Agent
from forms.client import NewClientForm, NewAgentForm

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
        if request.values.get('next'):
            return redirect(request.values.get('next'))
        return redirect(url_for("client.clients"))
    return tpl('client.html', form=form, title=u"新建客户")


@client_bp.route('/new_agent', methods=['GET', 'POST'])
def new_agent():
    form = NewAgentForm(request.form)
    if request.method == 'POST' and form.validate():
        db_agent_name = Agent.name_exist(form.name.data)
        if not db_agent_name:
            agent = Agent.add(form.name.data)
            flash(u'新建代理(%s)成功!' % agent.name, 'success')
        else:
            flash(u'新建代理(%s)失败，名称已经被占用!' % form.name.data, 'danger')
            return tpl('agent.html', form=form, title=u"新建甲方")
        if request.values.get('next'):
            return redirect(request.values.get('next'))
        return redirect(url_for("client.agents"))
    return tpl('agent.html', form=form, title=u"新建甲方")


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
        agent.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = agent.name
    return tpl('agent.html', form=form, title=agent.name)


@client_bp.route('/clients', methods=['GET'])
def clients():
    clients = Client.all()
    return tpl('clients.html', clients=clients)


@client_bp.route('/agents', methods=['GET'])
def agents():
    agents = Agent.all()
    return tpl('agents.html', agents=agents)
