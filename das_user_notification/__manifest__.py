{
    "name": "User Notifications",
    "description": "User Notifications",
    "summary": "User Notifications mobile application",
    "version": "15.0.1.0.1",
    "author": "Das360",
    "depends": ["base", 'product', 'das_zone_location', 'das_template_settings', 'das_plat_de_jour',
                'das_promotion_ads', 'sale','das_delivery_item'],
    "data": ["data/data.xml",
             "views/notifications_views.xml",
             "security/ir.model.access.csv"],
    'installable': True,
    'sequence': -100,
    'application': True,
    'auto_install': True,
    "license": 'AGPL-3',
    "website": "https://das-360.com",

}
