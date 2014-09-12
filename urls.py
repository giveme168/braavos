from controllers.user import user_bp
from controllers.client import client_bp
from controllers.medium import medium_bp
from controllers.order import order_bp
from controllers.comment import comment_bp
from controllers.material import material_bp
from controllers.files import files_bp
from controllers.api import api_bp


def register_blueprint(app):
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(client_bp, url_prefix='/clients')
    app.register_blueprint(medium_bp, url_prefix='/mediums')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(comment_bp, url_prefix='/comments')
    app.register_blueprint(material_bp, url_prefix='/materials')
    app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(api_bp, url_prefix='/api')
