from controllers.finance.client_order.invoice import finance_client_order_invoice_bp
from controllers.finance.outsource.pay import finance_outsource_pay_bp
from controllers.finance.client_order.medium_pay import finance_client_order_medium_pay_bp
from controllers.finance.client_order.agent_pay import finance_client_order_agent_pay_bp
from controllers.finance.client_order.back_money import finance_client_order_back_money_bp
from controllers.finance.client_order.medium_rebate_invoice import finance_client_order_medium_rebate_invoice_bp
from controllers.finance.douban_order.back_money import finance_douban_order_back_money_bp
from controllers.finance.client_order.data_query import finance_client_order_data_query_bp
from controllers.finance.douban_order.data_query import finance_douban_order_data_query_bp
from controllers.finance.framework_order import finance_framework_order_bp
from controllers.finance.client_order.outsource_invoice import finance_client_order_outsource_invoice_bp
from controllers.finance.douban_order.outsource_invoice import finance_douban_order_outsource_invoice_bp
from controllers.finance.client_order.medium_back_money import finance_client_order_medium_back_money_bp
from controllers.finance.client_medium_order.invoice import finance_client_medium_order_invoice_bp
from controllers.finance.client_medium_order.back_money import finance_client_medium_order_back_money_bp


def finance_register_blueprint(app):
    app.register_blueprint(finance_client_order_invoice_bp, url_prefix='/finance/client_order/invoice')
    app.register_blueprint(finance_outsource_pay_bp, url_prefix='/finance/outsource/pay')
    app.register_blueprint(finance_client_order_medium_pay_bp, url_prefix='/finance/client_order/medium_pay')
    app.register_blueprint(finance_client_order_agent_pay_bp, url_prefix='/finance/client_order/agent_pay')
    app.register_blueprint(finance_client_order_back_money_bp, url_prefix='/finance/client_order/back_money')
    app.register_blueprint(finance_client_order_medium_rebate_invoice_bp, url_prefix='/finance/client_order/medium_rebate_invoice')
    app.register_blueprint(finance_douban_order_back_money_bp, url_prefix='/finance/douban_order/back_money')
    app.register_blueprint(finance_client_order_data_query_bp, url_prefix='/finance/client_order/data_query')
    app.register_blueprint(finance_douban_order_data_query_bp, url_prefix='/finance/douban_order/data_query')
    app.register_blueprint(finance_framework_order_bp, url_prefix='/finance/framework_order')
    app.register_blueprint(finance_client_order_outsource_invoice_bp, url_prefix='/finance/client_order/outsource_invoice')
    app.register_blueprint(finance_douban_order_outsource_invoice_bp, url_prefix='/finance/douban_order/outsource_invoice')
    app.register_blueprint(finance_client_order_medium_back_money_bp, url_prefix='/finance/client_order/medium_back_money')
    app.register_blueprint(finance_client_medium_order_invoice_bp, url_prefix='/finance/client_medium_order/invoice')
    app.register_blueprint(finance_client_medium_order_back_money_bp, url_prefix='/finance/client_medium_order/back_money')
