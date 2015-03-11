from controllers.api import api_bp

def api_register_blueprint(app):
    app.register_blueprint(api_bp, url_prefix='/api')