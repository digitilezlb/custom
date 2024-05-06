{
    'name': 'Event Sale Order',
    'description': 'Event Sale Order',
    'version': '16.0.0.0',
    'summary': 'Event Sale Order',
    'website': 'https://digitile.com',
    'depends': ['base','sale','das_digitile','das_sale_order_product'],
    'data': [
        'views/sale_order.xml',
        'views/sale_order_line.xml',
        'views/show_images.xml',
        "security/ir.model.access.csv",
    ],
    "author": "Digitile",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}