from controllers.saler.invoice import saler_invoice_bp
from controllers.saler.medium_invoice import saler_medium_invoice_bp

def saler_register_blueprint(app):
    app.register_blueprint(saler_invoice_bp, url_prefix='/saler/invoice')
    app.register_blueprint(saler_medium_invoice_bp, url_prefix='/saler/medium_invoice')