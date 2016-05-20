from controllers.kol import kol_bp


def kol_register_blueprint(app):
    app.register_blueprint(kol_bp, url_prefix='/kol')
