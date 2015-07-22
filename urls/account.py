from controllers.account.kpi import account_kpi_bp

def account_register_blueprint(app):
    app.register_blueprint(account_kpi_bp, url_prefix='/account/kpi')