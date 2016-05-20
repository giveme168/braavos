# -*- coding: UTF-8 -*-
from flask import Blueprint, jsonify

from models.client import Client

api_client_bp = Blueprint('api_client', __name__)


@api_client_bp.route('/', methods=['GET'])
def clients():
    clients = [{'id': k.id, 'name': k.name} for k in Client.all()]
    return jsonify({'data': clients})
