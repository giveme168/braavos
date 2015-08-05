from searchAd.controllers.order import searchAd_order_bp

def searchAd_order_register_blueprint(app):
    app.register_blueprint(searchAd_order_bp, url_prefix='/searchAd_orders')
