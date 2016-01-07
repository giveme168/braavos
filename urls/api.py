from controllers.api.order import api_bp
from controllers.api.client import api_client_bp
from controllers.api.medium import api_medium_bp
from controllers.api.account import api_account_bp


def api_register_blueprint(app):
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(api_client_bp, url_prefix='/api/clients')
    app.register_blueprint(api_medium_bp, url_prefix='/api/mediums')
    app.register_blueprint(api_account_bp, url_prefix='/api/account')
