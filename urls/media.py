from controllers.media.client_order.data_query import media_client_order_data_query_bp

def media_register_blueprint(app):
    app.register_blueprint(media_client_order_data_query_bp, url_prefix='/media/client_order/data_query')
