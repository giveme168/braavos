from controllers.comment import comment_bp

def comments_register_blueprint(app):
    app.register_blueprint(comment_bp, url_prefix='/comments')