from controllers.storage import storage_bp

def storage_register_blueprint(app):
    app.register_blueprint(storage_bp, url_prefix='/storage')