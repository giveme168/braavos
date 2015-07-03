from controllers.saler.invoice import saler_invoice_bp
from controllers.saler.medium_invoice import saler_medium_invoice_bp
from controllers.saler.client_order_back_money import saler_client_order_back_money_bp
from controllers.saler.agent_invoice import  saler_agent_invoice_bp
from controllers.saler.medium_rebate_invoice import saler_medium_rebate_invoice_bp

def saler_register_blueprint(app):
    app.register_blueprint(saler_invoice_bp, url_prefix='/saler/invoice')
    app.register_blueprint(saler_medium_invoice_bp, url_prefix='/saler/medium_invoice')
    app.register_blueprint(saler_client_order_back_money_bp, url_prefix='/saler/client_order_back_money')
    app.register_blueprint(saler_agent_invoice_bp, url_prefix='/saler/agent_invoice')
    app.register_blueprint(saler_medium_rebate_invoice_bp, url_prefix='/saler/medium_rebate_invoice')
