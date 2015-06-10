from controllers.mediums.product import mediums_product_bp

def mediums_register_blueprint(app):
    app.register_blueprint(mediums_product_bp, url_prefix='/mediums')