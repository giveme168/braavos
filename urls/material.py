from controllers.material import material_bp

def materia_register_blueprint(app):
    app.register_blueprint(material_bp, url_prefix='/materials')