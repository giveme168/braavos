from searchAd.controllers.finance.searchAd_order.invoice import searchAd_finance_client_order_invoice_bp
from searchAd.controllers.finance.searchAd_order.medium_pay import searchAd_finance_client_order_medium_pay_bp
from searchAd.controllers.finance.searchAd_order.agent_pay import searchAd_finance_client_order_agent_pay_bp
from searchAd.controllers.finance.searchAd_order.back_money import searchAd_finance_client_order_back_money_bp
from searchAd.controllers.finance.searchAd_order.medium_rebate_invoice import searchAd_finance_client_order_medium_rebate_invoice_bp
from searchAd.controllers.finance.searchAd_order.data_query import searchAd_finance_client_order_data_query_bp

from searchAd.controllers.finance.searchAd_rebate_order.invoice import searchAd_finance_rebate_order_invoice_bp
from searchAd.controllers.finance.searchAd_rebate_order.agent_pay import searchAd_finance_rebate_order_agent_pay_bp
from searchAd.controllers.finance.searchAd_rebate_order.back_money import searchAd_finance_rebate_order_back_money_bp
from searchAd.controllers.finance.searchAd_rebate_order.data_query import searchAd_finance_rebate_order_data_query_bp

def searchAd_finance_register_blueprint(app):
    app.register_blueprint(searchAd_finance_client_order_invoice_bp, url_prefix='/finance/searchAd_order/invoice')
    app.register_blueprint(searchAd_finance_client_order_medium_pay_bp, url_prefix='/finance/searchAd_order/medium_pay')
    app.register_blueprint(searchAd_finance_client_order_agent_pay_bp, url_prefix='/finance/searchAd_order/agent_pay')
    app.register_blueprint(searchAd_finance_client_order_back_money_bp, url_prefix='/finance/searchAd_order/back_money')
    app.register_blueprint(searchAd_finance_client_order_medium_rebate_invoice_bp, url_prefix='/finance/searchAd_order/medium_rebate_invoice')
    app.register_blueprint(searchAd_finance_client_order_data_query_bp, url_prefix='/finance/searchAd_order/data_query')

    app.register_blueprint(searchAd_finance_rebate_order_invoice_bp, url_prefix='/finance/searchAd_rebate_order/invoice')
    app.register_blueprint(searchAd_finance_rebate_order_agent_pay_bp, url_prefix='/finance/searchAd_rebate_order/agent_pay')
    app.register_blueprint(searchAd_finance_rebate_order_back_money_bp, url_prefix='/finance/searchAd_rebate_order/back_money')
    app.register_blueprint(searchAd_finance_rebate_order_data_query_bp, url_prefix='/finance/searchAd_rebate_order/data_query')
