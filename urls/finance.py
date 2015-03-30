from controllers.finance.invoice import finance_invoice_bp
from controllers.finance.pay import finance_pay_bp
from controllers.finance.medium_pay import finance_medium_pay_bp

def finance_register_blueprint(app):
    app.register_blueprint(finance_invoice_bp, url_prefix='/finance/invoice')
    app.register_blueprint(finance_pay_bp, url_prefix='/finance/pay')
    app.register_blueprint(finance_medium_pay_bp, url_prefix='/finance/medium_pay')