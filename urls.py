from controllers.user import user_bp
from controllers.client import client_bp
from controllers.medium import medium_bp
from controllers.order import order_bp
from controllers.comment import comment_bp


def register_blueprint(app):
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(client_bp, url_prefix='/clients')
    app.register_blueprint(medium_bp, url_prefix='/mediums')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(comment_bp, url_prefix='/comments')
