from controllers.contract import contract_bp

def contract_register_blueprint(app):
    app.register_blueprint(contract_bp, url_prefix='/contract')