from controllers.data_query.order import data_query_order_bp
from controllers.data_query.weekly import data_query_weekly_bp

def data_query_register_blueprint(app):
    app.register_blueprint(data_query_order_bp, url_prefix='/data_query/order')
    app.register_blueprint(data_query_weekly_bp, url_prefix='/data_query/weekly')