from controllers.user import user_bp


def register_blueprint(app):
    app.register_blueprint(user_bp, url_prefix='/user')
