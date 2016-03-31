from controllers.saler.client_order.invoice import saler_client_order_invoice_bp
from controllers.saler.client_order.medium_invoice import saler_client_order_medium_invoice_bp
from controllers.saler.client_order.back_money import saler_client_order_back_money_bp
from controllers.saler.client_order.agent_invoice import saler_client_order_agent_invoice_bp
from controllers.saler.client_order.medium_rebate_invoice import saler_client_order_medium_rebate_invoice_bp
from controllers.saler.douban_order.back_money import saler_douban_order_back_money_bp
from controllers.saler.client_order.outsource import saler_client_order_outsource_bp
from controllers.saler.douban_order.outsource import saler_douban_order_outsource_bp
from controllers.saler.client_order.data_query import saler_client_order_data_query_bp
from controllers.saler.douban_order.data_query import saler_douban_order_data_query_bp
from controllers.saler.client_order.medium_back_money import saler_client_order_medium_back_money_bp
from controllers.saler.douban_order.other_cost import saler_douban_order_other_cost_bp
from controllers.saler.client_order.other_cost import saler_client_order_other_cost_bp
from controllers.saler.client_order.money import saler_client_order_money_bp


def saler_register_blueprint(app):
    app.register_blueprint(saler_client_order_invoice_bp, url_prefix='/saler/client_order/invoice')
    app.register_blueprint(saler_client_order_medium_invoice_bp, url_prefix='/saler/client_order/medium_invoice')
    app.register_blueprint(saler_client_order_back_money_bp, url_prefix='/saler/client_order/back_money')
    app.register_blueprint(saler_client_order_agent_invoice_bp, url_prefix='/saler/client_order/agent_invoice')
    app.register_blueprint(saler_client_order_medium_rebate_invoice_bp, url_prefix='/saler/client_order/medium_rebate_invoice')
    app.register_blueprint(saler_douban_order_back_money_bp, url_prefix='/saler/douban_order/back_money')
    app.register_blueprint(saler_client_order_outsource_bp, url_prefix='/saler/client_order/outsource')
    app.register_blueprint(saler_douban_order_outsource_bp, url_prefix='/saler/douban_order/outsource')
    app.register_blueprint(saler_client_order_data_query_bp, url_prefix='/saler/client_order/data_query')
    app.register_blueprint(saler_douban_order_data_query_bp, url_prefix='/saler/douban_order/data_query')
    app.register_blueprint(saler_client_order_medium_back_money_bp, url_prefix='/saler/client_order/medium_back_money')
    app.register_blueprint(saler_douban_order_other_cost_bp, url_prefix='/saler/douban_order/other_cost')
    app.register_blueprint(saler_client_order_other_cost_bp, url_prefix='/saler/client_order/other_cost')
    app.register_blueprint(saler_client_order_money_bp, url_prefix='/saler/client_order/money')
