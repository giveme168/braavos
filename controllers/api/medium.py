# -*- coding: UTF-8 -*-
from flask import Blueprint, jsonify

from models.medium import Medium

api_medium_bp = Blueprint('api_medium', __name__)


@api_medium_bp.route('/', methods=['GET'])
def mediums():
    mediums = [{'id': k.id, 'name': k.name, 'level': k.level, 'level_cn': k.level_cn}
               for k in Medium.all()]
    return jsonify({'data': mediums})
