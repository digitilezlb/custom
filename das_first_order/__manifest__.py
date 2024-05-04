{
    'name': 'Website First order discount',
    'description': 'Website First order discount',
    'version': '16.0.0.0',
    'summary': 'Website First order discount',
    'website': 'https://digitile.com',
    'depends': ['sale_management'],
    'data': [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/first_order_view.xml"
    ],
    "author": "Das360",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
