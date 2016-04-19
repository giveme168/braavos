from controllers.manage.apply import manage_apply_bp

def manage_register_blueprint(app):
    app.register_blueprint(manage_apply_bp, url_prefix='/manage/apply')