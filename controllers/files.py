#-*- coding: UTF-8 -*-
#import os
from flask import Blueprint, request, current_app as app, abort
from flask import jsonify, send_from_directory
from libs.files import files_set


files_bp = Blueprint('files', __name__, template_folder='../templates/files')


@files_bp.route('/<filename>', methods=['GET'])
def files(filename):
    config = app.upload_set_config.get('files')
    if config is None:
        abort(404)
    return send_from_directory(config.destination, filename)


@files_bp.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        filename = files_set.save(request.files['file'])
        return jsonify({'status': 0, 'filename': filename})
    return jsonify({'status': 1, 'msg': 'file not exits or type not allowed'})
