#-*- coding: UTF-8 -*-
from flask import url_for


def get_relative_path(filename):
    return url_for('files.file', filename=filename)


def get_full_path(filename):
    return get_relative_path(filename)

ALLOWED_EXTENSIONS = ['.txt']


def allowed_file(filename):
    return True
    return filename and filename.endswith(ALLOWED_EXTENSIONS)
