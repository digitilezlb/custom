{
    "name": "Invoice Orders Trip",
    "summary": "Invoice Orders Trip",
    'license': 'LGPL-3',
    "version": "15.0.1.0.1",
    "author": "Digitile",
    "depends": ['mass_mailing', 'account', 'fleet', 'base_geolocalize','sale','das_digitile'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/trip_view.xml',
        'views/sale_order_template.xml',
         'views/sale_order_tree.xml',
        'data/trip_reference.xml'
    ],
    'installable': True,
    'sequence': -100,
    'application': True,
    'auto_install': False

}
