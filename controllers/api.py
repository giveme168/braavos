# -*- coding: UTF-8 -*-
import random
import itertools
from datetime import datetime
from flask import Blueprint, request, abort, Response, jsonify

from models.medium import Medium, AdPosition
from models.client import Client
from models.consts import DATE_FORMAT

api_bp = Blueprint('api', __name__)


@api_bp.route('/ad/position/<position_id>', methods=['GET'])
def ad_by_position(position_id):
    position = AdPosition.get(position_id)
    if not position:
        abort(404)
    date_str = request.values.get('date', None)
    if date_str:
        _date = datetime.strptime(date_str, DATE_FORMAT).date()
    else:
        _date = datetime.today().date()
    items = [x for x in position.order_items if x.schedule_by_date(_date)]
    if not items:
        abort(404)
    material = random.choice(
        list(itertools.chain(*[x.materials for x in items])))
    response = Response()
    response.set_data(material.html)
    return response


@api_bp.route('/mediums', methods=['GET'])
def mediums():
    mediums = [{'id': k.id, 'name': k.name} for k in Medium.all()]
    return jsonify({'date': mediums})


@api_bp.route('/clients', methods=['GET'])
def clients():
    clients = [{'id': k.id, 'name': k.name} for k in Client.all()]
    return jsonify({'date': clients})
