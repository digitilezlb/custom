# -*- coding: utf-8 -*-

{
    'name': 'Car Driver',
    'description': 'Car Driver',
    'version': '1.0.0',
    'category': 'car',
    'author': 'Das360',
    'sequence': -100,
    'summary': '',
    'depends': ['base', 'contacts', 'fleet', 'base_geolocalize', 'hr','das_delivery_system',
                'web_google_maps'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/car_driver.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {},
}
