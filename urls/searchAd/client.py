from searchAd.controllers.client import searchAd_client_bp

def searchAd_client_register_blueprint(app):
    app.register_blueprint(searchAd_client_bp, url_prefix='/searchAd_clients')
