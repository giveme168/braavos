from searchAd.controllers.data_query.profit import searchAd_data_query_profit_bp

def searchAd_data_query_register_blueprint(app):
    app.register_blueprint(searchAd_data_query_profit_bp, url_prefix='/searchAd/data_query/profit')
