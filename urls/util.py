from controllers.util.upload_orders import util_upload_orders_bp

def util_register_blueprint(app):
    app.register_blueprint(util_upload_orders_bp, url_prefix='/util/upload_orders')