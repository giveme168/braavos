from searchAd.controllers.saler.searchAd_order.invoice import searchAd_saler_client_order_invoice_bp
from searchAd.controllers.saler.searchAd_order.medium_invoice import searchAd_saler_client_order_medium_invoice_bp
from searchAd.controllers.saler.searchAd_order.back_money import searchAd_saler_client_order_back_money_bp
from searchAd.controllers.saler.searchAd_order.agent_invoice import searchAd_saler_client_order_agent_invoice_bp
from searchAd.controllers.saler.searchAd_order.medium_rebate_invoice import searchAd_saler_client_order_medium_rebate_invoice_bp

def searchAd_saler_register_blueprint(app):
    app.register_blueprint(searchAd_saler_client_order_invoice_bp, url_prefix='/saler/searchAd_order/invoice')
    app.register_blueprint(searchAd_saler_client_order_medium_invoice_bp, url_prefix='/saler/searchAd_order/medium_invoice')
    app.register_blueprint(searchAd_saler_client_order_back_money_bp, url_prefix='/saler/searchAd_order/back_money')
    app.register_blueprint(searchAd_saler_client_order_agent_invoice_bp, url_prefix='/saler/searchAd_order/agent_invoice')
    app.register_blueprint(searchAd_saler_client_order_medium_rebate_invoice_bp, url_prefix='/saler/searchAd_order/medium_rebate_invoice')
