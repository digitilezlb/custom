{
    'name': 'Digitile Kitchen',
    'description': 'Digitile Kitchen',
    'version': '16.0.0.0',
    'summary': 'Digitile Kitchen',
    'website': 'https://digitile.com',
    'depends': ['sale_management','product','website_sale'],
    'data': [
        "views/product_template.xml",
        "views/kitchen.xml",
        "views/sale_order_template.xml",
        "views/sale_order.xml",
        "security/ir.model.access.csv",
    ],
    "author": "Digitile",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}