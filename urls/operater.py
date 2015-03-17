from controllers.operater.outsource import operater_outsource_bp

def operater_register_blueprint(app):
    app.register_blueprint(operater_outsource_bp, url_prefix='/operater/outsource')