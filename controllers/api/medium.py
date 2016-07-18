# -*- coding: UTF-8 -*-
from flask import Blueprint, jsonify

from models.medium import Medium, MediumGroup

api_medium_bp = Blueprint('api_medium', __name__)


@api_medium_bp.route('/', methods=['GET'])
def mediums():
    mediums = [{'id': k.id, 'name': k.name, 'level': k.medium_group.level,
                'level_cn': k.medium_group.level_cn, 'medium_group_id': k.medium_group.id,
                'medium_group_name': k.medium_group.name}
               for k in Medium.all()]
    return jsonify({'data': mediums})


@api_medium_bp.route('/groups', methods=['GET'])
def groups():
    groups = [{'id': mg.id, 'name': mg.name, 'level': mg.level, 'level_cn': mg.level_cn,
               'mediums': [{'id': m.id, 'name': m.name} for m in mg.mediums]} for mg in MediumGroup.all()]
    return jsonify({'data': groups})


@api_medium_bp.route('/<mid>/info', methods=['GET'])
def medium_info(mid):
    medium = Medium.get(mid)
    if not medium:
        return jsonify({'data': {}})
    return jsonify({'data': {'id': medium.id, 'name': medium.name, 'medium_group_id': medium.medium_group.id,
                             'medium_group_name': medium.medium_group.name, 'level': medium.medium_group.level,
                             'level_cn': medium.medium_group.level_cn}})
