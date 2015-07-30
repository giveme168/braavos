from controllers.finance.client_order.invoice import finance_client_order_invoice_bp
from controllers.finance.outsource.pay import finance_outsource_pay_bp
from controllers.finance.client_order.medium_pay import finance_client_order_medium_pay_bp
from controllers.finance.client_order.agent_pay import finance_client_order_agent_pay_bp
from controllers.finance.client_order.back_money import finance_client_order_back_money_bp
from controllers.finance.client_order.medium_rebate_invoice import finance_client_order_medium_rebate_invoice_bp
from controllers.finance.douban_order.back_money import finance_douban_order_back_money_bp

def finance_register_blueprint(app):
    app.register_blueprint(finance_client_order_invoice_bp, url_prefix='/finance/client_order/invoice')
    app.register_blueprint(finance_outsource_pay_bp, url_prefix='/finance/outsource/pay')
    app.register_blueprint(finance_client_order_medium_pay_bp, url_prefix='/finance/client_order/medium_pay')
    app.register_blueprint(finance_client_order_agent_pay_bp, url_prefix='/finance/client_order/agent_pay')
    app.register_blueprint(finance_client_order_back_money_bp, url_prefix='/finance/client_order/back_money')
    app.register_blueprint(finance_client_order_medium_rebate_invoice_bp, url_prefix='/finance/client_order/medium_rebate_invoice')
    app.register_blueprint(finance_douban_order_back_money_bp, url_prefix='/finance/douban_order/back_money')
