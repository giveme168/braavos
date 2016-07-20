# -*- coding: UTF-8 -*-
from flask import Blueprint, jsonify

from models.client import Agent

api_agent_bp = Blueprint('api_agent', __name__)


@api_agent_bp.route('/', methods=['GET'])
def agents():
    clients = []
    for k in Agent.all():
        agent_licence_file = k.get_last_client_file(100)
        if agent_licence_file:
            licence_file = agent_licence_file.agent_path
        else:
            licence_file = ''
        agent_f_certifcate_file = k.get_last_client_file(101)
        if agent_f_certifcate_file:
            f_certifcate_file = agent_f_certifcate_file.agent_path
        else:
            f_certifcate_file = ''
        agent_o_certifcate_file = k.get_last_client_file(102)
        if agent_o_certifcate_file:
            o_certifcate_file = agent_o_certifcate_file.agent_path
        else:
            o_certifcate_file = ''
        agent_tax_certifcate_file = k.get_last_client_file(103)
        if agent_tax_certifcate_file:
            tax_certifcate_file = agent_tax_certifcate_file.agent_path
        else:
            tax_certifcate_file = ''
        agent_t_info_file = k.get_last_client_file(104)
        if agent_t_info_file:
            t_info_file = agent_t_info_file.agent_path
        else:
            t_info_file = ''
        dict_agent = {}
        dict_agent['id'] = k.id
        dict_agent['name'] = k.name
        dict_agent['licence_file'] = licence_file
        dict_agent['f_certifcate_file'] = f_certifcate_file
        dict_agent['o_certifcate_file'] = o_certifcate_file
        dict_agent['tax_certifcate_file'] = tax_certifcate_file
        dict_agent['t_info_file'] = t_info_file
        dict_agent['files'] = [f.agent_path for f in k.get_agent_attachments()]
        clients.append(dict_agent)
    return jsonify({'data': clients})
