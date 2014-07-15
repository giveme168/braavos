from controllers.user import user_bp
from controllers.client import client_bp


def register_blueprint(app):
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(client_bp, url_prefix='/client')
