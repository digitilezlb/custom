# -*- coding: utf-8 -*-
{
    'name': "Product Category",
    'description': """Add Fields to product categories""",
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['product','website_sale','das_sale_order_product'],
    'data': [
        'views/product_category.xml',
        # 'views/product_template.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
