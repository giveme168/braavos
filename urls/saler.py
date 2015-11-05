from controllers.saler.client_order.invoice import saler_client_order_invoice_bp
from controllers.saler.client_order.medium_invoice import saler_client_order_medium_invoice_bp
from controllers.saler.client_order.back_money import saler_client_order_back_money_bp
from controllers.saler.client_order.agent_invoice import saler_client_order_agent_invoice_bp
from controllers.saler.client_order.medium_rebate_invoice import saler_client_order_medium_rebate_invoice_bp
from controllers.saler.douban_order.back_money import saler_douban_order_back_money_bp
from controllers.saler.client_order.outsource import saler_client_order_outsource_bp
from controllers.saler.douban_order.outsource import saler_douban_order_outsource_bp

def saler_register_blueprint(app):
    app.register_blueprint(saler_client_order_invoice_bp, url_prefix='/saler/client_order/invoice')
    app.register_blueprint(saler_client_order_medium_invoice_bp, url_prefix='/saler/client_order/medium_invoice')
    app.register_blueprint(saler_client_order_back_money_bp, url_prefix='/saler/client_order/back_money')
    app.register_blueprint(saler_client_order_agent_invoice_bp, url_prefix='/saler/client_order/agent_invoice')
    app.register_blueprint(saler_client_order_medium_rebate_invoice_bp, url_prefix='/saler/client_order/medium_rebate_invoice')
    app.register_blueprint(saler_douban_order_back_money_bp, url_prefix='/saler/douban_order/back_money')
    app.register_blueprint(saler_client_order_outsource_bp, url_prefix='/saler/client_order/outsource')
    app.register_blueprint(saler_douban_order_outsource_bp, url_prefix='/saler/douban_order/outsource')
