from controllers.saler.invoice import saler_invoice_bp

def saler_register_blueprint(app):
    app.register_blueprint(saler_invoice_bp, url_prefix='/saler/invoice/order')