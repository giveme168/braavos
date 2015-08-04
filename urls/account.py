from controllers.account.kpi import account_kpi_bp
from controllers.account.leave import account_leave_bp
from controllers.account.out import account_out_bp

def account_register_blueprint(app):
    app.register_blueprint(account_kpi_bp, url_prefix='/account/kpi')
    app.register_blueprint(account_leave_bp, url_prefix='/account/leave')
    app.register_blueprint(account_out_bp, url_prefix='/account/out')