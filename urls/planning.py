from controllers.planning.bref import planning_bref_bp

def planning_register_blueprint(app):
    app.register_blueprint(planning_bref_bp, url_prefix='/planning/bref')
