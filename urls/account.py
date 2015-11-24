from controllers.account.kpi import account_kpi_bp
from controllers.account.leave import account_leave_bp
from controllers.account.out import account_out_bp
from controllers.account.performance import account_performance_bp
from controllers.account.commission import account_commission_bp
from controllers.account.data import account_data_bp
from controllers.account.notice import account_notice_bp

def account_register_blueprint(app):
    app.register_blueprint(account_kpi_bp, url_prefix='/account/kpi')
    app.register_blueprint(account_leave_bp, url_prefix='/account/leave')
    app.register_blueprint(account_out_bp, url_prefix='/account/out')
    app.register_blueprint(account_performance_bp, url_prefix='/account/performance')
    app.register_blueprint(account_commission_bp, url_prefix='/account/commission')
    app.register_blueprint(account_data_bp, url_prefix='/account/data')
    app.register_blueprint(account_notice_bp, url_prefix='/account/notice')