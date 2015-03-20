from controllers.finance.invoice import finance_invoice_bp

def finance_register_blueprint(app):
    app.register_blueprint(finance_invoice_bp, url_prefix='/finance/invoice')