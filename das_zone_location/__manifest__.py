{
    "name": "Zone Location",
    "description": "Zone Location",
    'license': 'LGPL-3',
    "summary": "Zone Module Location",
    "version": "15.0.1.0.1",
    "author": "Das360",
    "depends": ['contacts', 'google_marker_icon_picker', 'das_car_driver_ok'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/zones.xml',
        'views/partner_view.xml',
        'demo/demo_map.xml',
        'wizard/zone_draw_mapp.xml',
        # 'views/warehouse.xml',
    ],
    'installable': True,
    'sequence': -100,
    'application': True,
    'auto_install': False,

}
