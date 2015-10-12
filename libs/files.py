from flask import current_app as app
from .uploads import UploadSet, IMAGES, DOCUMENTS, DEFAULTS, configure_uploads

files_set = UploadSet('files', DEFAULTS)
attachment_set = UploadSet('attachment', DOCUMENTS)
all_files_set = UploadSet(name='mediums', extensions=DEFAULTS)


def uploads_conf(app):
    configure_uploads(app, [files_set, attachment_set, all_files_set])


def get_full_path(filename, domain=True):
    path = files_set.url(filename)
    if domain:
        return app.config['DOMAIN'] + path
    else:
        return path


def get_attachment_path(filename, domain=True):
    path = attachment_set.url(filename)
    if domain:
        return app.config['DOMAIN'] + path
    else:
        return path


def get_medium_path(filename, domain=True):
    path = all_files_set.url(filename)
    if domain:
        return app.config['DOMAIN'] + path
    else:
        return path
