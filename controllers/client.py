#-*- coding: UTF-8 -*-
from flask import Blueprint, request, redirect, abort, url_for
from flask import render_template as tpl

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
        client = Client(form.name.data, form.industry.data)
        client.add()
        return redirect(url_for("client.clients"))
    return tpl('client.html', form=form)


@client_bp.route('/new_agent', methods=['GET', 'POST'])
def new_agent():
    form = NewAgentForm(request.form)
    if request.method == 'POST' and form.validate():
        agent = Agent(form.name.data)
        agent.add()
        return redirect(url_for("client.agents"))
    return tpl('agent.html', form=form)


@client_bp.route('/client_detail/<client_id>', methods=['GET', 'POST'])
def client_detail(client_id):
    client = Client.get(client_id)
    if not client:
        abort(404)
    form = NewClientForm(request.form)
    if request.method == 'POST' and form.validate():
        client.name = form.name.data
        client.industry = form.industry.data
        client.save()
        return redirect(url_for("client.clients"))
    else:
        form.name.data = client.name
        form.industry.data = client.industry
    return tpl('client.html', form=form)


@client_bp.route('/agent_detail/<agent_id>', methods=['GET', 'POST'])
def agent_detail(agent_id):
    agent = Agent.get(agent_id)
    if not agent:
        abort(404)
    form = NewAgentForm(request.form)
    if request.method == 'POST' and form.validate():
        agent.name = form.name.data
        agent.save()
        return redirect(url_for("client.agents"))
    else:
        form.name.data = agent.name
    return tpl('agent.html', form=form)


@client_bp.route('/clients', methods=['GET'])
def clients():
    clients = Client.all()
    return tpl('clients.html', clients=clients)


@client_bp.route('/agents', methods=['GET'])
def agents():
    agents = Agent.all()
    return tpl('agents.html', agents=agents)
