from controllers.mediums.product import mediums_product_bp
from controllers.mediums.resource import mediums_resource_bp
from controllers.mediums.files import mediums_files_bp
from controllers.mediums.planning import mediums_planning_bp

def mediums_register_blueprint(app):
    app.register_blueprint(mediums_product_bp, url_prefix='/mediums')
    app.register_blueprint(mediums_resource_bp, url_prefix='/mediums')
    app.register_blueprint(mediums_files_bp, url_prefix='/mediums/files')
    app.register_blueprint(mediums_planning_bp, url_prefix='/mediums/planning')