from controllers.medium import medium_bp

def medium_register_blueprint(app):
    app.register_blueprint(medium_bp, url_prefix='/mediums')