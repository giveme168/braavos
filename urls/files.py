from controllers.files import files_bp

def files_register_blueprint(app):
    app.register_blueprint(files_bp, url_prefix='/files')