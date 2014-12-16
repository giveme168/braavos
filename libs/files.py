from flask import current_app as app
from .uploads import UploadSet, IMAGES, DOCUMENTS, configure_uploads

files_set = UploadSet('files', IMAGES)
attachment_set = UploadSet('attachment', DOCUMENTS)


def uploads_conf(app):
    configure_uploads(app, [files_set, attachment_set])


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
