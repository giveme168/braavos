# -*- coding: UTF-8 -*-
from flask import Blueprint, jsonify

from models.medium import Medium, MediumGroup, Media

api_medium_bp = Blueprint('api_medium', __name__)


def _medium_to_dict(medium):
    medium_licence_file = medium.get_last_client_file(100)
    if medium_licence_file:
        licence_file = medium_licence_file.agent_path
    else:
        licence_file = ''
    medium_f_certifcate_file = medium.get_last_client_file(101)
    if medium_f_certifcate_file:
        f_certifcate_file = medium_f_certifcate_file.agent_path
    else:
        f_certifcate_file = ''
    medium_o_certifcate_file = medium.get_last_client_file(102)
    if medium_o_certifcate_file:
        o_certifcate_file = medium_o_certifcate_file.agent_path
    else:
        o_certifcate_file = ''
    medium_tax_certifcate_file = medium.get_last_client_file(103)
    if medium_tax_certifcate_file:
        tax_certifcate_file = medium_tax_certifcate_file.agent_path
    else:
        tax_certifcate_file = ''
    medium_t_info_file = medium.get_last_client_file(104)
    if medium_t_info_file:
        t_info_file = medium_t_info_file.agent_path
    else:
        t_info_file = ''
    medium_a_licence_file = medium.get_last_client_file(105)
    if medium_a_licence_file:
        a_licence_file = medium_a_licence_file.agent_path
    else:
        a_licence_file = ''
    dict_medium = {}
    dict_medium['id'] = medium.id
    dict_medium['name'] = medium.name
    dict_medium['level'] = medium.medium_group.level
    dict_medium['level_cn'] = medium.medium_group.level_cn
    dict_medium['medium_group_id'] = medium.medium_group.id
    dict_medium['medium_group_name'] = medium.medium_group.name
    dict_medium['licence_file'] = licence_file
    dict_medium['f_certifcate_file'] = f_certifcate_file
    dict_medium['o_certifcate_file'] = o_certifcate_file
    dict_medium['tax_certifcate_file'] = tax_certifcate_file
    dict_medium['a_licence_file'] = a_licence_file
    dict_medium['t_info_file'] = t_info_file
    return dict_medium


@api_medium_bp.route('/', methods=['GET'])
def mediums():
    mediums = []
    for medium in Medium.all():
        mediums.append(_medium_to_dict(medium))
    return jsonify({'data': mediums})


@api_medium_bp.route('/media', methods=['GET'])
def medias():
    mediums = []
    for media in Media.all():
        dict_media = {}
        dict_media['id'] = media.id
        try:
            dict_media['old_id'] = Medium.query.filter_by(name=media.name).first().id
        except:
            dict_media['old_id'] = 0
        dict_media['name'] = media.name
        dict_media['level_cn'] = media.level_cn
        dict_media['level'] = media.level
        mediums.append(dict_media)
    return jsonify({'data': mediums})


@api_medium_bp.route('/groups', methods=['GET'])
def groups():
    groups = []
    for mg in MediumGroup.all():
        mg_licence_file = mg.get_last_client_file(100)
        if mg_licence_file:
            licence_file = mg_licence_file.agent_path
        else:
            licence_file = ''
        mg_f_certifcate_file = mg.get_last_client_file(101)
        if mg_f_certifcate_file:
            f_certifcate_file = mg_f_certifcate_file.agent_path
        else:
            f_certifcate_file = ''
        mg_o_certifcate_file = mg.get_last_client_file(102)
        if mg_o_certifcate_file:
            o_certifcate_file = mg_o_certifcate_file.agent_path
        else:
            o_certifcate_file = ''
        mg_tax_certifcate_file = mg.get_last_client_file(103)
        if mg_tax_certifcate_file:
            tax_certifcate_file = mg_tax_certifcate_file.agent_path
        else:
            tax_certifcate_file = ''
        mg_t_info_file = mg.get_last_client_file(104)
        if mg_t_info_file:
            t_info_file = mg_t_info_file.agent_path
        else:
            t_info_file = ''
        medium_a_licence_file = mg.get_last_client_file(105)
        if medium_a_licence_file:
            a_licence_file = medium_a_licence_file.agent_path
        else:
            a_licence_file = ''
        dict_medium = {}
        dict_medium['id'] = mg.id
        dict_medium['name'] = mg.name
        dict_medium['level'] = mg.level
        dict_medium['level_cn'] = mg.level_cn
        dict_medium['licence_file'] = licence_file
        dict_medium['f_certifcate_file'] = f_certifcate_file
        dict_medium['o_certifcate_file'] = o_certifcate_file
        dict_medium['tax_certifcate_file'] = tax_certifcate_file
        dict_medium['a_licence_file'] = a_licence_file
        dict_medium['t_info_file'] = t_info_file
        dict_medium['mediums'] = [_medium_to_dict(m) for m in mg.mediums]
        groups.append(dict_medium)
    return jsonify({'data': groups})


@api_medium_bp.route('/<mid>/info', methods=['GET'])
def medium_info(mid):
    medium = Medium.get(mid)
    if not medium:
        return jsonify({'data': {}})
    return jsonify({'data': _medium_to_dict(medium)})
