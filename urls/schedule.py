from controllers.schedule import schedule_bp

def schedule_register_blueprint(app):
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
