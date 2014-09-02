#-*- coding: UTF-8 -*-
import os
from flask import Blueprint, request, current_app as app
from flask import jsonify, send_from_directory
from werkzeug import secure_filename

from models.files import allowed_file, get_relative_path


files_bp = Blueprint('files', __name__, template_folder='../templates/files')


@files_bp.route('/<filename>', methods=['GET'])
def file(filename):
    return send_from_directory(app.config['UPLOAD_DIR'], filename)


@files_bp.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_DIR']):
            os.makedirs(app.config['UPLOAD_DIR'])
        file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
        return jsonify({'status': 0, 'filename': filename, 'filelink': get_relative_path(filename)})
    return jsonify({'status': 1, 'msg': 'file not exits or type not allowed'})
