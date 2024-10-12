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
        self.order_status_level = [
            {'level': 0, 'from': 'created', 'to': ['created', 'canceled', 'approved']},
            {'level': 1, 'from': 'approved', 'to': ['approved', 'unavailable', 'invoiced']},
            {'level': 1, 'from': 'canceled', 'to': ['canceled']},
            {'level': 2, 'from': 'invoiced', 'to': ['invoiced', 'processing']},
            {'level': 2, 'from': 'unavailable', 'to': ['unavailable']},
            {'level': 3, 'from': 'processing', 'to': ['processing', 'shipped']},
            {'level': 4, 'from': 'shipped', 'to': ['shipped', 'delivered']}
        ]
        self.css_colors = [
            "#F0F8FF", "#FAEBD7", "#00FFFF", "#7FFFD4", "#F0FFFF", "#F5F5DC", "#FFE4C4", "#000000", "#FFEBCD", "#0000FF",
            "#8A2BE2", "#A52A2A", "#DEB887", "#5F9EA0", "#7FFF00", "#D2691E", "#FF7F50", "#6495ED", "#FFF8DC", "#DC143C",
            "#00FFFF", "#00008B", "#008B8B", "#B8860B", "#A9A9A9", "#006400", "#BDB76B", "#8B008B", "#556B2F", "#FF8C00",
            "#9932CC", "#8B0000", "#E9967A", "#8FBC8F", "#483D8B", "#2F4F4F", "#00CED1", "#9400D3", "#FF1493", "#00BFFF",
            "#696969", "#1E90FF", "#B22222", "#FFFAF0", "#228B22", "#FF00FF", "#DCDCDC", "#F8F8FF", "#FFD700", "#DAA520",
            "#808080", "#008000", "#ADFF2F", "#F0FFF0", "#FF69B4", "#CD5C5C", "#4B0082", "#FFFFF0", "#F0E68C", "#E6E6FA",
            "#FFF0F5", "#7CFC00", "#FFFACD", "#ADD8E6", "#F08080", "#E0FFFF", "#FAFAD2", "#D3D3D3", "#90EE90", "#FFB6C1",
            "#FFA07A", "#20B2AA", "#87CEFA", "#778899", "#B0C4DE", "#FFFFE0", "#00FF00", "#32CD32", "#FAF0E6", "#FF00FF",
            "#800000", "#66CDAA", "#0000CD", "#BA55D3", "#9370DB", "#3CB371", "#7B68EE", "#00FA9A", "#48D1CC", "#C71585",
            "#191970", "#F5FFFA", "#FFE4E1", "#FFE4B5", "#FFDEAD", "#000080", "#FDF5E6", "#808000", "#6B8E23", "#FFA500",
            "#FF4500", "#DA70D6", "#EEE8AA", "#98FB98", "#AFEEEE", "#DB7093", "#FFEFD5", "#FFDAB9", "#CD853F", "#FFC0CB",
            "#DDA0DD", "#B0E0E6", "#800080", "#FF0000", "#BC8F8F", "#4169E1", "#8B4513", "#FA8072", "#F4A460", "#2E8B57",
            "#FFF5EE", "#A0522D", "#C0C0C0", "#87CEEB", "#6A5ACD", "#708090", "#FFFAFA", "#00FF7F", "#4682B4", "#D2B48C",
            "#008080", "#D8BFD8", "#FF6347", "#40E0D0", "#EE82EE", "#F5DEB3", "#FFFFFF", "#F5F5F5", "#FFFF00", "#9ACD32"
        ]
