from controllers.data_query.order import data_query_order_bp
from controllers.data_query.weekly import data_query_weekly_bp
from controllers.data_query.medium import data_query_medium_bp
from controllers.data_query.outsource import data_query_outsource_bp
from controllers.data_query.finance import data_query_finance_bp
from controllers.data_query.profit import data_query_profit_bp
from controllers.data_query.commission import data_query_commission_bp

from controllers.data_query.super_leader.medium import data_query_super_leader_medium_bp
from controllers.data_query.super_leader.industry import data_query_super_leader_industry_bp


def data_query_register_blueprint(app):
    app.register_blueprint(data_query_order_bp, url_prefix='/data_query/order')
    app.register_blueprint(data_query_weekly_bp, url_prefix='/data_query/weekly')
    app.register_blueprint(data_query_medium_bp, url_prefix='/data_query/medium')
    app.register_blueprint(data_query_outsource_bp, url_prefix='/data_query/outsource')
    app.register_blueprint(data_query_finance_bp, url_prefix='/data_query/finance')
    app.register_blueprint(data_query_profit_bp, url_prefix='/data_query/profit')
    app.register_blueprint(data_query_commission_bp, url_prefix='/data_query/commission')
    app.register_blueprint(data_query_super_leader_medium_bp, url_prefix='/data_query/super_leader/medium')
    app.register_blueprint(data_query_super_leader_industry_bp, url_prefix='/data_query/super_leader/industry')
