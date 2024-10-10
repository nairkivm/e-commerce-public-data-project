class Constants:
    def __init__(self) -> None:
        self.source = {
            'customers' : 'data_sources/customers_dataset.csv',
            'geolocations' : 'data_sources/geolocation_dataset.csv',
            'order_items' : 'data_sources/order_items_dataset.csv',
            'order_payments' : 'data_sources/order_payments_dataset.csv',
            'order_reviews' : 'data_sources/order_reviews_dataset.csv',
            'orders' : 'data_sources/orders_dataset.csv',
            'product_category_name_translations' : 'data_sources/product_category_name_translation.csv',
            'products' : 'data_sources/products_dataset.csv',
            'sellers' : 'data_sources/sellers_dataset.csv',
        }
        self.requirements = {
            'customers': {
                'customer_id': 'object',
                'customer_unique_id': 'object',
                'customer_zip_code_prefix': 'object',
                'customer_city': 'object',
                'customer_state': 'object'
            },
            'geolocations': {
                'geolocation_zip_code_prefix': 'object',
                'geolocation_lat': 'float64',
                'geolocation_lng': 'float64',
                'geolocation_city': 'object',
                'geolocation_state': 'object'
            },
            'order_items': {
                'order_id': 'object',
                'order_item_id': 'int64',
                'product_id': 'object',
                'seller_id': 'object',
                'shipping_limit_date': 'datetime64[ns]',
                'price': 'float64',
                'freight_value': 'float64'
            },
            'order_payments': {
                'order_id': 'object',
                'payment_sequential': 'int64',
                'payment_type': 'object',
                'payment_installments': 'int64',
                'payment_value': 'float64'
            },
            'order_reviews': {
                'review_id': 'object',
                'order_id': 'object',
                'review_score': 'float64',
                'review_comment_title': 'object',
                'review_comment_message': 'object',
                'review_creation_date': 'datetime64[ns]',
                'review_answer_timestamp': 'datetime64[ns]'
            },
            'orders': {
                'order_id': 'object',
                'customer_id': 'object',
                'order_status': 'object',
                'order_purchase_timestamp': 'datetime64[ns]',
                'order_approved_at': 'datetime64[ns]',
                'order_delivered_carrier_date': 'datetime64[ns]',
                'order_delivered_customer_date': 'datetime64[ns]',
                'order_estimated_delivery_date': 'datetime64[ns]'
            },
            'product_category_name_translations': {
                'product_category_name': 'object',
                'product_category_name_english': 'object'
            },
            'products': {
                'product_id': 'object',
                'product_category_name': 'object',
                'product_name_length': 'float64',
                'product_description_length': 'float64',
                'product_photos_qty': 'int64',
                'product_weight_g': 'float64',
                'product_length_cm': 'float64',
                'product_height_cm': 'float64',
                'product_width_cm': 'float64'
            },
            'sellers': {
                'seller_id': 'object',
                'seller_zip_code_prefix': 'object',
                'seller_city': 'object',
                'seller_state': 'object'
            }
        }
