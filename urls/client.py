from controllers.client import client_bp

def client_register_blueprint(app):
    app.register_blueprint(client_bp, url_prefix='/clients')