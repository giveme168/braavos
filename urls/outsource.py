from controllers.outsource import outsource_bp

def outsource_register_blueprint(app):
    app.register_blueprint(outsource_bp, url_prefix='/outsource')