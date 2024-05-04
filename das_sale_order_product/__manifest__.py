{
    "name": "Sale Order",
    "summary": "Product Sale Order",
    "version": "15.0.1.0.1",
    "author": "Das360",
    "depends": ['sale','stock',   'product'],
    "data": [
        # 'security/ir.model.access.csv',
        # 'views/sale_order_line.xml',
        # 'views/stock_picking.xml',
        # 'views/location.xml',
        'views/product.xml',
        # 'wizard/places_replenishment.xml',
        # "demo/demo_code.xml",
    ],
    'installable': True,
    'sequence': -100,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': False

}
