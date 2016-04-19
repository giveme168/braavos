from controllers.other import other_bp


def other_register_blueprint(app):
    app.register_blueprint(other_bp, url_prefix='/other')
