from controllers.order import order_bp

def order_register_blueprint(app):
    app.register_blueprint(order_bp, url_prefix='/orders')