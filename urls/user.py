from controllers.user import user_bp

def user_register_blueprint(app):
    app.register_blueprint(user_bp, url_prefix='/users')