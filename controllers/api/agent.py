# -*- coding: UTF-8 -*-
from flask import Blueprint, jsonify

from models.client import Agent

api_agent_bp = Blueprint('api_agent', __name__)


@api_agent_bp.route('/', methods=['GET'])
def agents():
    clients = [{'id': k.id, 'name': k.name,
                'files': [f.agent_path for f in k.get_agent_attachments()]}
               for k in Agent.all()]
    return jsonify({'data': clients})
