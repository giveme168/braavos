from controllers.data_query.order import data_query_order_bp
from controllers.data_query.weekly import data_query_weekly_bp
from controllers.data_query.medium import data_query_medium_bp
from controllers.data_query.outsource import data_query_outsource_bp
from controllers.data_query.finance import data_query_finance_bp
from controllers.data_query.profit import data_query_profit_bp

def data_query_register_blueprint(app):
    app.register_blueprint(data_query_order_bp, url_prefix='/data_query/order')
    app.register_blueprint(data_query_weekly_bp, url_prefix='/data_query/weekly')
    app.register_blueprint(data_query_medium_bp, url_prefix='/data_query/medium')
    app.register_blueprint(data_query_outsource_bp, url_prefix='/data_query/outsource')
    app.register_blueprint(data_query_finance_bp, url_prefix='/data_query/finance')
    app.register_blueprint(data_query_profit_bp, url_prefix='/data_query/profit')