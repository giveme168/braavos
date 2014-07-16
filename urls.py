from controllers.user import user_bp
from controllers.client import client_bp
from controllers.medium import medium_bp
#from controllers.order import order_bp


def register_blueprint(app):
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(medium_bp, url_prefix='/medium')
    #app.register_blueprint(order_bp, url_prefix='/order')
