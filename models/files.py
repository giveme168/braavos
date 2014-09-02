#-*- coding: UTF-8 -*-
from flask import url_for


def get_relative_path(filename):
    return url_for('files.file', filename=filename)


def get_full_path(filename):
    return get_relative_path(filename)

ALLOWED_EXTENSIONS = set(['txt'])


def allowed_file(filename):
    return True
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
