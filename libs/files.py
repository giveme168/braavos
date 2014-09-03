from flaskext.uploads import UploadSet, IMAGES, configure_uploads

files_set = UploadSet('files', IMAGES)


def uploads_conf(app):
    configure_uploads(app, [files_set])
